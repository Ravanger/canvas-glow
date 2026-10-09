#include "HoverSensor.h"

#include <Arduino.h>
#include <soc/gpio_reg.h>

namespace {
portMUX_TYPE senseMux = portMUX_INITIALIZER_UNLOCKED;
}

void HoverSensor::begin(Print& log)
{
    cpuMhz_ = getCpuFrequencyMhz();
    chargeCycles_ = cfg::SENSE_CHARGE_US * cpuMhz_;
    timeoutCycles_ = cfg::SENSE_TIMEOUT_US * cpuMhz_;
    marginCycles_ = (int32_t)(cfg::TRIG_MARGIN_US * cpuMhz_);
    faultMinCycles_ = (int32_t)(cfg::SENSE_FAULT_MIN_US * cpuMhz_);

    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
        // OUTPUT first routes the pad to plain GPIO; INPUT then leaves it high-Z with no pulls.
        pinMode(cfg::SENSE_PINS[i], OUTPUT);
        pinMode(cfg::SENSE_PINS[i], INPUT);
        padBit_[i] = 1UL << cfg::SENSE_PINS[i];
        allMask_ |= padBit_[i];
    }

    int32_t sum[cfg::SENSE_COUNT] = {};
    uint16_t n[cfg::SENSE_COUNT] = {};
    for (uint16_t k = 0; k < cfg::CALIBRATION_SAMPLES; ++k) {
        int32_t s[cfg::SENSE_COUNT];
        sample(allMask_, s);
        for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
            if (s[i] >= 0) {
                sum[i] += s[i];
                ++n[i];
            }
        }
        delay(1);
    }

    const unsigned long now = millis();
    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
        const int32_t base = n[i] ? sum[i] / n[i] : (int32_t)(50 * cpuMhz_);
        baseQ_[i] = base << cfg::BASE_Q;
        lastV_[i] = base;
        for (uint8_t k = 0; k < cfg::FILTER_LEN; ++k)
            ring_[i][k] = base;
        ringSum_[i] = base * cfg::FILTER_LEN;
        faulted_[i] = n[i] == 0 || base < faultMinCycles_;
        faultMs_[i] = now;
        const long b = tenthsUs(base);
        log.printf("  sensor %u (GPIO %u) baseline %ld.%ld us%s\n", i, cfg::SENSE_PINS[i], b / 10, b % 10,
            faulted_[i] ? " FAULT" : "");
    }
}

bool HoverSensor::update(unsigned long now, bool lightSettling)
{
    uint32_t mask = 0;
    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
        if (faulted_[i] && now - faultMs_[i] >= cfg::SENSE_RETRY_MS)
            faulted_[i] = false;
        if (!faulted_[i])
            mask |= padBit_[i];
    }
    int32_t s[cfg::SENSE_COUNT];
    sample(mask, s);

    bool any = false;
    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
        if (!(mask & padBit_[i]))
            continue;
        if (s[i] < faultMinCycles_) {
            faulted_[i] = true;
            faultMs_[i] = now;
            hovering_[i] = false;
            continue;
        }
        const int32_t v = filterPush(i, s[i]);
        lastV_[i] = v;
        int32_t base = baseQ_[i] >> cfg::BASE_Q;
        if (!hovering_[i]) {
            // While the light fades, PWM coupling shifts the reading: follow it fast and don't trigger.
            const int32_t vq = v << cfg::BASE_Q;
            const uint8_t shift = (vq < baseQ_[i] || lightSettling) ? cfg::BASE_DOWN_SHIFT : cfg::BASE_UP_SHIFT;
            baseQ_[i] += (vq - baseQ_[i]) >> shift;
            base = baseQ_[i] >> cfg::BASE_Q;
            if (!lightSettling && v * 100 > base * cfg::TRIG_PCT && v > base + marginCycles_) {
                hovering_[i] = true;
                hoverStartMs_[i] = now;
            }
        } else if (v * 100 < base * cfg::REL_PCT) {
            hovering_[i] = false;
        } else if (now - hoverStartMs_[i] >= cfg::HOVER_RESET_MS) {
            baseQ_[i] = v << cfg::BASE_Q;
            hovering_[i] = false;
        }
        any = any || hovering_[i];
    }
    return any;
}

void HoverSensor::printStatus(Print& out) const
{
    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i) {
        const long b = tenthsUs(baseQ_[i] >> cfg::BASE_Q);
        const long v = tenthsUs(lastV_[i]);
        out.printf("s%u base=%ld.%ld v=%ld.%ld %s  ", i, b / 10, b % 10, v / 10, v % 10,
            faulted_[i] ? "FAULT" : hovering_[i] ? "HOVER" : "----");
    }
}

// Charges every pad in mask, releases them together and times each fall in CPU cycles.
// out[i] is -1 when the pad was skipped or never fell before the timeout.
void IRAM_ATTR HoverSensor::sample(uint32_t mask, int32_t out[])
{
    uint32_t fallAt[cfg::SENSE_COUNT] = {};
    uint32_t pending = mask;

    portENTER_CRITICAL(&senseMux);
    REG_WRITE(GPIO_OUT_W1TS_REG, mask);
    REG_WRITE(GPIO_ENABLE_W1TS_REG, mask);
    uint32_t t0 = ESP.getCycleCount();
    while (ESP.getCycleCount() - t0 < chargeCycles_) { }
    REG_WRITE(GPIO_ENABLE_W1TC_REG, mask);
    t0 = ESP.getCycleCount();
    uint32_t dt;
    do {
        const uint32_t fell = pending & ~REG_READ(GPIO_IN_REG);
        dt = ESP.getCycleCount() - t0;
        if (fell) {
            for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i)
                if (fell & padBit_[i])
                    fallAt[i] = dt;
            pending &= ~fell;
        }
    } while (pending && dt < timeoutCycles_);
    portEXIT_CRITICAL(&senseMux);

    for (uint8_t i = 0; i < cfg::SENSE_COUNT; ++i)
        out[i] = ((mask & ~pending) & padBit_[i]) ? (int32_t)fallAt[i] : -1;
}

int32_t HoverSensor::filterPush(uint8_t pad, int32_t s)
{
    int32_t& slot = ring_[pad][ringIdx_[pad]];
    ringSum_[pad] += s - slot;
    slot = s;
    if (++ringIdx_[pad] == cfg::FILTER_LEN)
        ringIdx_[pad] = 0;
    return ringSum_[pad] / cfg::FILTER_LEN;
}

long HoverSensor::tenthsUs(int32_t cycles) const
{
    return (long)cycles * 10 / (long)cpuMhz_;
}

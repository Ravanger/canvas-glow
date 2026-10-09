#include "Knob.h"

#include <Arduino.h>

#include "Config.h"

void Knob::begin()
{
    pinMode(cfg::KNOB_PIN, INPUT);
    smoothMv_ = analogReadMilliVolts(cfg::KNOB_PIN);
    level_ = levelFor(smoothMv_);
    lastMs_ = millis();
}

void Knob::update(unsigned long now)
{
    if (now - lastMs_ < cfg::KNOB_PERIOD_MS)
        return;
    lastMs_ = now;

    smoothMv_ += (analogReadMilliVolts(cfg::KNOB_PIN) - smoothMv_) * 0.2f;
    const uint16_t next = levelFor(smoothMv_);
    const uint16_t delta = next > level_ ? next - level_ : level_ - next;
    // Ends always snap so "off" and "full" are reachable; the light treats any change as a fade.
    if (delta > cfg::KNOB_HYSTERESIS || ((next == 0 || next == 65535) && delta > 0))
        level_ = next;
}

uint16_t Knob::levelFor(float mv) const
{
    float frac = (mv - cfg::KNOB_MIN_MV) / (float)(cfg::KNOB_MAX_MV - cfg::KNOB_MIN_MV);
    if (frac * 100.0f < cfg::KNOB_OFF_PCT)
        return 0;
    if (frac >= 1.0f)
        return 65535;
    return (uint16_t)(frac * 65535.0f);
}

#include "Light.h"

#include <Arduino.h>
#include <driver/gpio.h>
#include <driver/ledc.h>

#include "Config.h"

void Light::begin()
{
    float metres = 0.0f;
    for (float m : cfg::LED_SEGMENT_M)
        metres += m;
    cap_ = min(1.0f, cfg::STRIP_BUDGET_A / (metres * cfg::STRIP_AMPS_PER_M));

    const float maxDuty = ((1 << cfg::PWM_BITS) - 1) * cap_;
    for (uint16_t i = 0; i < 257; ++i)
        lut_[i] = (uint16_t)lroundf(powf(i / 256.0f, cfg::GAMMA) * maxDuty);

    ledc_timer_config_t timer = {};
    timer.speed_mode = LEDC_LOW_SPEED_MODE;
    timer.duty_resolution = (ledc_timer_bit_t)cfg::PWM_BITS;
    timer.timer_num = LEDC_TIMER_0;
    timer.freq_hz = cfg::PWM_FREQ_HZ;
    timer.clk_cfg = LEDC_AUTO_CLK;
    ok_ = ledc_timer_config(&timer) == ESP_OK;

    for (uint8_t i = 0; i < cfg::LED_COUNT; ++i) {
        ledc_channel_config_t channel = {};
        channel.gpio_num = cfg::LED_PINS[i];
        channel.speed_mode = LEDC_LOW_SPEED_MODE;
        channel.channel = (ledc_channel_t)i;
        channel.intr_type = LEDC_INTR_DISABLE;
        channel.timer_sel = LEDC_TIMER_0;
        channel.duty = 0;
        channel.hpoint = 0;
        ok_ = ok_ && ledc_channel_config(&channel) == ESP_OK;
        // Each pin sources ~15-21 mA of base current.
        gpio_set_drive_capability((gpio_num_t)cfg::LED_PINS[i], GPIO_DRIVE_CAP_3);
    }
}

void Light::tick()
{
    constexpr uint16_t upStep = 65535UL * cfg::TICK_MS / cfg::FADE_UP_MS;
    constexpr uint16_t downStep = 65535UL * cfg::TICK_MS / cfg::FADE_DOWN_MS;
    if (level_ < target_)
        level_ = (target_ - level_ > upStep) ? level_ + upStep : target_;
    else if (level_ > target_)
        level_ = (level_ - target_ > downStep) ? level_ - downStep : target_;

    const uint16_t d = dutyFor(level_);
    if (d != duty_)
        write(d);
}

void Light::flash(uint16_t level)
{
    write(dutyFor(level));
}

uint16_t Light::dutyFor(uint16_t level) const
{
    const uint16_t i = level >> 8;
    const uint32_t frac = level & 0xFF;
    return lut_[i] + (uint16_t)(((uint32_t)(lut_[i + 1] - lut_[i]) * frac) >> 8);
}

void Light::write(uint16_t duty)
{
    duty_ = duty;
    for (uint8_t i = 0; i < cfg::LED_COUNT; ++i) {
        ledc_set_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)i, duty);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)i);
    }
}

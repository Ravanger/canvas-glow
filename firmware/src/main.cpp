#include <Arduino.h>

#include "Config.h"
#include "HoverSensor.h"
#include "Knob.h"
#include "Light.h"

#ifndef CANVAS_DEBUG
#define CANVAS_DEBUG 0
#endif
#ifndef CANVAS_SELF_TEST
#define CANVAS_SELF_TEST 0
#endif

class CanvasGlow {
public:
    void begin()
    {
        Serial.begin(115200);
#if ARDUINO_USB_MODE && ARDUINO_USB_CDC_ON_BOOT
        Serial.setTxTimeoutMs(0);
#endif
#if CANVAS_DEBUG
        while (!Serial && millis() < 2000) { }
#endif
        pinMode(cfg::MODE_PIN, INPUT_PULLUP);
        light_.begin();
        knob_.begin();

        Serial.println("Canvas Glow: calibrating, keep hands away...");
        sensor_.begin(Serial);
        Serial.printf("Light: %u segments, brightness cap %.0f%%%s\n", cfg::LED_COUNT, light_.cap() * 100.0f,
            light_.ok() ? "" : ", LEDC SETUP FAILED");

#if CANVAS_SELF_TEST
        for (uint16_t l = 0; l < 65535 - 255; l += 256) {
            light_.flash(l);
            delay(2);
        }
        light_.flash(0);
#endif
        enableLoopWDT();
        Serial.println("Ready.");
        lastWake_ = xTaskGetTickCount();
    }

    void tick()
    {
        vTaskDelayUntil(&lastWake_, pdMS_TO_TICKS(cfg::TICK_MS));
        const unsigned long now = millis();
        const bool night = digitalRead(cfg::MODE_PIN) == LOW;
        if (night && !wasNight_)
            nightStartMs_ = now;
        wasNight_ = night;

        knob_.update(now);
        if (sensor_.update(now, light_.settling())) {
            lastHoverMs_ = now;
            everHovered_ = true;
            nightStartMs_ = now;
        }

        const bool held = everHovered_ && now - lastHoverMs_ < cfg::HOVER_HOLD_MS;
        const bool nightAwake = cfg::NIGHT_AUTO_OFF_MIN == 0 || now - nightStartMs_ < cfg::NIGHT_AUTO_OFF_MIN * 60000UL;
        uint16_t target = (night && nightAwake) ? knob_.level() : 0;
        if (held && target < cfg::HOVER_LEVEL)
            target = cfg::HOVER_LEVEL;
        light_.setTarget(target);
        light_.tick();

#if CANVAS_DEBUG
        if (now - lastLogMs_ >= 500) {
            lastLogMs_ = now;
            sensor_.printStatus(Serial);
            Serial.printf("%s knob=%umV level=%u duty=%u/%u%s\n", night ? "NIGHT" : "hover", knob_.millivolts(),
                light_.level(), light_.duty(), (1u << cfg::PWM_BITS) - 1, held ? " HOLD" : "");
        }
#endif
    }

private:
    Light light_;
    HoverSensor sensor_;
    Knob knob_;
    bool wasNight_ = false;
    bool everHovered_ = false;
    unsigned long lastHoverMs_ = 0;
    unsigned long nightStartMs_ = 0;
    unsigned long lastLogMs_ = 0;
    TickType_t lastWake_ = 0;
};

CanvasGlow app;

void setup()
{
    app.begin();
}

void loop()
{
    app.tick();
}

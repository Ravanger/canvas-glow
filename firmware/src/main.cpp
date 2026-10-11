#include <Arduino.h>

#include "Config.h"
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
        light_.begin();
        knob_.begin();

        Serial.printf("Canvas Glow: %u segments, brightness cap %.0f%%%s\n", cfg::LED_COUNT, light_.cap() * 100.0f,
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

        knob_.update(now);
        light_.setTarget(knob_.level());
        light_.tick();

#if CANVAS_DEBUG
        if (now - lastLogMs_ >= 500) {
            lastLogMs_ = now;
            Serial.printf("knob=%umV level=%u duty=%u/%u\n", knob_.millivolts(), light_.level(), light_.duty(),
                (1u << cfg::PWM_BITS) - 1);
        }
#endif
    }

private:
    Light light_;
    Knob knob_;
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

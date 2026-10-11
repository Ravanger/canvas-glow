#pragma once

#include <stdint.h>

namespace cfg {

// One driver transistor per strip segment; all segments get the same brightness.
constexpr uint8_t LED_PINS[] = { 3, 4, 5, 10 };
constexpr float LED_SEGMENT_M[] = { 0.34f, 0.24f, 0.34f, 0.24f };
constexpr uint8_t LED_COUNT = sizeof(LED_PINS) / sizeof(LED_PINS[0]);
static_assert(sizeof(LED_SEGMENT_M) / sizeof(LED_SEGMENT_M[0]) == LED_COUNT, "one length per LED pin");

constexpr uint8_t KNOB_PIN = 1;

// Power budget: brightness is capped so the whole strip at 100% never exceeds STRIP_BUDGET_A.
constexpr float STRIP_AMPS_PER_M = 1.6f;
constexpr float STRIP_BUDGET_A = 1.5f;

constexpr uint32_t PWM_FREQ_HZ = 20000;
constexpr uint8_t PWM_BITS = 11;
constexpr float GAMMA = 2.2f;

constexpr uint16_t TICK_MS = 1;
constexpr uint16_t FADE_UP_MS = 800;
constexpr uint16_t FADE_DOWN_MS = 1500;

constexpr uint16_t KNOB_MIN_MV = 20;
constexpr uint16_t KNOB_MAX_MV = 1000;
constexpr uint8_t KNOB_OFF_PCT = 3;
constexpr uint16_t KNOB_HYSTERESIS = 900;
constexpr uint16_t KNOB_PERIOD_MS = 20;

}

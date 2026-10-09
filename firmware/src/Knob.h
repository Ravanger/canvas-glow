#pragma once

#include <stdint.h>

class Knob {
public:
    void begin();
    void update(unsigned long now);

    uint16_t level() const { return level_; }
    uint16_t millivolts() const { return (uint16_t)smoothMv_; }

private:
    uint16_t levelFor(float mv) const;

    float smoothMv_ = 0.0f;
    uint16_t level_ = 0;
    unsigned long lastMs_ = 0;
};

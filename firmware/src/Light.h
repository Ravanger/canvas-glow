#pragma once

#include <stdint.h>

class Light {
public:
    void begin();
    void setTarget(uint16_t level) { target_ = level; }
    void tick();
    void flash(uint16_t level);

    bool settling() const { return level_ != target_; }
    uint16_t level() const { return level_; }
    uint16_t duty() const { return duty_; }
    float cap() const { return cap_; }
    bool ok() const { return ok_; }

private:
    uint16_t dutyFor(uint16_t level) const;
    void write(uint16_t duty);

    uint16_t lut_[257] = {};
    uint16_t level_ = 0;
    uint16_t target_ = 0;
    uint16_t duty_ = 0;
    float cap_ = 1.0f;
    bool ok_ = false;
};

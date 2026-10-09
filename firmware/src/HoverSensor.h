#pragma once

#include <Print.h>
#include <stdint.h>

#include "Config.h"

class HoverSensor {
public:
    void begin(Print& log);
    bool update(unsigned long now, bool lightSettling);
    void printStatus(Print& out) const;

private:
    void sample(uint32_t mask, int32_t out[]);
    int32_t filterPush(uint8_t pad, int32_t s);
    long tenthsUs(int32_t cycles) const;

    uint32_t padBit_[cfg::SENSE_COUNT] = {};
    uint32_t allMask_ = 0;
    uint32_t cpuMhz_ = 160;
    uint32_t chargeCycles_ = 0;
    uint32_t timeoutCycles_ = 0;
    int32_t marginCycles_ = 0;
    int32_t faultMinCycles_ = 0;

    int32_t ring_[cfg::SENSE_COUNT][cfg::FILTER_LEN] = {};
    int32_t ringSum_[cfg::SENSE_COUNT] = {};
    uint8_t ringIdx_[cfg::SENSE_COUNT] = {};
    int32_t baseQ_[cfg::SENSE_COUNT] = {};
    int32_t lastV_[cfg::SENSE_COUNT] = {};
    bool faulted_[cfg::SENSE_COUNT] = {};
    unsigned long faultMs_[cfg::SENSE_COUNT] = {};
    bool hovering_[cfg::SENSE_COUNT] = {};
    unsigned long hoverStartMs_[cfg::SENSE_COUNT] = {};
};

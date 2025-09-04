#pragma once
#include <atomic>

namespace Control {
    // Vehicle control variables
    extern std::atomic<float> steering_angle;
    extern std::atomic<float> throttle_position;
    extern std::atomic<bool> brake_applied;
    extern std::atomic<int> gear_position;
    
    void initialize();
    void update(int cycle);
    void printStatus();
}
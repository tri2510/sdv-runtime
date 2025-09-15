#pragma once
#include <atomic>
#include <cstdint>

class VehicleController {
public:
    VehicleController();
    void updateControlSystems();
    void displayStatus();
    
    // Atomic control variables for thread-safe access
    std::atomic<float> target_speed{0.0f};
    std::atomic<float> actual_speed{0.0f};
    std::atomic<int> throttle_position{0}; // 0-1000 (0-100.0%)
    std::atomic<int> brake_pressure{0};    // 0-1000 bar scaled
    std::atomic<bool> cruise_control_active{false};
    std::atomic<bool> abs_active{false};
    std::atomic<bool> esp_active{false};
    
    // Engine control
    std::atomic<int> engine_rpm{0};
    std::atomic<char> engine_load{0};  // 0-100%
    std::atomic<char> engine_temp{0};   // Celsius
    
    // Transmission
    std::atomic<char> gear_number{0};  // 0=Park, 1-8=Forward gears
    std::atomic<bool> transmission_locked{false};
    
private:
    int update_cycle = 0;
};
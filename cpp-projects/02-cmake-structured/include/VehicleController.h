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
    std::atomic<int16_t> throttle_position{0}; // 0-1000 (0-100.0%)
    std::atomic<int16_t> brake_pressure{0};    // 0-1000 bar scaled
    std::atomic<bool> cruise_control_active{false};
    std::atomic<bool> abs_active{false};
    std::atomic<bool> esp_active{false};
    
    // Engine control
    std::atomic<uint16_t> engine_rpm{0};
    std::atomic<uint8_t> engine_load{0};  // 0-100%
    std::atomic<int8_t> engine_temp{0};   // Celsius
    
    // Transmission
    std::atomic<uint8_t> gear_number{0};  // 0=Park, 1-8=Forward gears
    std::atomic<bool> transmission_locked{false};
    
private:
    int update_cycle = 0;
};
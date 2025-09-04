#include "vehicle_control.h"
#include <iostream>
#include <iomanip>
#include <cmath>

namespace Control {
    // Define atomic variables
    std::atomic<float> steering_angle{0.0f};
    std::atomic<float> throttle_position{0.0f};
    std::atomic<bool> brake_applied{false};
    std::atomic<int> gear_position{1};
    
    void initialize() {
        std::cout << "🔧 Vehicle Control initialized" << std::endl;
        gear_position = 1;
    }
    
    void update(int cycle) {
        // Simulate driving maneuvers
        steering_angle = std::sin(cycle * 0.05f) * 15.0f; // -15 to +15 degrees
        throttle_position = 20.0f + (cycle % 60) * 1.0f; // 20-80% throttle
        brake_applied = (cycle % 25 < 3); // Occasional braking
        gear_position = std::min(5, (cycle / 20) + 1); // Shift up over time
    }
    
    void printStatus() {
        std::cout << std::fixed << std::setprecision(1)
                  << "🚗 Steer: " << steering_angle.load() << "° | "
                  << "Throttle: " << throttle_position.load() << "% | "
                  << "Brake: " << (brake_applied.load() ? "ON" : "OFF") << " | "
                  << "Gear: " << gear_position.load()
                  << std::endl;
    }
}
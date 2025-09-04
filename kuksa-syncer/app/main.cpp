#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Automotive variables for monitoring (matching kit server expectations)
std::atomic<float> ego_speed{0.0f};
std::atomic<int> current_lane{2};
std::atomic<float> steering_angle{0.0f};
std::atomic<float> collision_risk{0.0f};

int main() {
    std::cout << "Automotive Safety System - Memory Monitoring Test" << std::endl;
    std::cout << "Monitoring variables: ego_speed, current_lane, steering_angle, collision_risk" << std::endl;
    
    // Simulate automotive scenario
    for (int i = 0; i < 20; i++) {
        // Simulate varying vehicle state
        ego_speed = 30.0f + i * 2.5f;  // Speed from 30 to 77.5 km/h
        current_lane = (i % 3) + 1;    // Lane 1, 2, or 3
        steering_angle = -15.0f + (i % 10) * 3.0f;  // Steering -15° to +15°
        collision_risk = (i > 10) ? (i - 10) * 0.1f : 0.0f;  // Risk increases over time
        
        std::cout << "Iteration " << i << ": ";
        std::cout << "ego_speed=" << ego_speed.load() << "km/h, ";
        std::cout << "current_lane=" << current_lane.load() << ", ";
        std::cout << "steering_angle=" << steering_angle.load() << "°, ";
        std::cout << "collision_risk=" << collision_risk.load() << std::endl;
        
        // Sleep for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "Automotive simulation completed successfully!" << std::endl;
    return 0;
}
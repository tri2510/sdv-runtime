#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <cmath>
#include <iomanip>

// Vehicle state variables
std::atomic<float> ego_speed{0.0f};
std::atomic<float> engine_rpm{800.0f};
std::atomic<float> fuel_level{75.5f};
std::atomic<float> engine_temp{90.0f};
std::atomic<int> gear{1};
std::atomic<bool> abs_active{false};
std::atomic<bool> traction_control{false};
std::atomic<float> steering_angle{0.0f};

void simulateAcceleration() {
    std::cout << "Vehicle acceleration simulation" << std::endl;
    std::cout << "Monitoring: ego_speed, engine_rpm, fuel_level, engine_temp, gear, abs_active" << std::endl;
    
    for (int cycle = 0; cycle < 20; ++cycle) {
        float time = cycle * 0.5f;
        
        // Acceleration phase
        if (cycle < 10) {
            ego_speed = cycle * 7.0f; // 0 to 70 km/h
            engine_rpm = 800.0f + cycle * 200.0f;
            gear = std::min(5, 1 + cycle / 3);
            fuel_level = 75.5f - cycle * 0.2f;
            engine_temp = 90.0f + cycle * 3.0f;
        } else {
            // Braking phase with ABS
            ego_speed = std::max(0.0f, 70.0f - (cycle - 10) * 7.0f);
            engine_rpm = std::max(800.0f, 2800.0f - (cycle - 10) * 200.0f);
            abs_active = ego_speed > 10.0f;
            traction_control = abs_active;
            steering_angle = std::sin(time) * 15.0f;
        }
        
        std::cout << "T+" << std::fixed << std::setprecision(1) << time 
                  << "s: Speed=" << ego_speed.load() << "km/h, RPM=" << engine_rpm.load()
                  << ", Gear=" << gear.load() << ", Fuel=" << fuel_level.load() << "%";
                  
        if (abs_active.load()) {
            std::cout << " [ABS]";
        }
        if (traction_control.load()) {
            std::cout << " [TC]";
        }
        std::cout << std::endl;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    std::cout << "Vehicle simulation complete" << std::endl;
}

int main() {
    simulateAcceleration();
    return 0;
}
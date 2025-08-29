#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include "shm_wrapper.h"

// Global variables for monitoring (using atomic for thread safety)
std::atomic<float> ego_speed{50.0f};
std::atomic<int> collision_risk{0};
std::atomic<int> current_lane{2};
std::atomic<bool> warning_active{false};
std::atomic<float> brake_pressure{0.0f};

int main() {
    std::cout << "=== FCW ADAS Demo System ===" << std::endl;
    std::cout << "Initializing shared memory..." << std::endl;
    
    // Initialize shared memory and register variables for monitoring
    INIT_SHM();
    WATCH_VAR(ego_speed, "float");
    WATCH_VAR(collision_risk, "int");
    WATCH_VAR(current_lane, "int");
    WATCH_VAR(warning_active, "bool");
    WATCH_VAR(brake_pressure, "float");
    
    std::cout << "C++ app connected to shared memory." << std::endl;
    std::cout << "Monitored variables: ego_speed, collision_risk, current_lane, warning_active, brake_pressure" << std::endl;
    std::cout << "\nStarting FCW ADAS simulation..." << std::endl;
    
    for (int i = 0; i < 100; i++) {
        std::cout << "\n=== FCW ADAS Status (Time: " << i << "s) ===" << std::endl;
        std::cout << "Ego Speed: " << ego_speed.load() << " km/h" << std::endl;
        std::cout << "Current Lane: " << current_lane.load() << " (of 4)" << std::endl;
        std::cout << "Collision Risk: " << collision_risk.load() << "%" << std::endl;
        std::cout << "Warning Active: " << (warning_active.load() ? "YES" : "NO") << std::endl;
        std::cout << "Brake Pressure: " << brake_pressure.load() << "%" << std::endl;
        
        // Simulate realistic ADAS behavior
        if (i % 10 == 0) {
            std::cout << "\n>>> SCENARIO CHANGE <<<" << std::endl;
            switch ((i / 10) % 4) {
                case 0:
                    std::cout << "Normal driving" << std::endl;
                    ego_speed = 60.0f;
                    collision_risk = 10;
                    warning_active = false;
                    brake_pressure = 0.0f;
                    break;
                case 1:
                    std::cout << "Approaching slower vehicle" << std::endl;
                    ego_speed = 80.0f;
                    collision_risk = 45;
                    warning_active = true;
                    brake_pressure = 20.0f;
                    break;
                case 2:
                    std::cout << "Lane change maneuver" << std::endl;
                    current_lane = (current_lane.load() % 4) + 1;
                    collision_risk = 25;
                    warning_active = false;
                    brake_pressure = 10.0f;
                    break;
                case 3:
                    std::cout << "Emergency braking!" << std::endl;
                    collision_risk = 95;
                    warning_active = true;
                    brake_pressure = 90.0f;
                    ego_speed = ego_speed.load() * 0.8f; // Reduce speed
                    break;
            }
        } else {
            // Gradual changes
            collision_risk = std::max(0, collision_risk.load() - 2);
            if (collision_risk < 30) {
                warning_active = false;
                brake_pressure = std::max(0.0f, brake_pressure.load() - 5.0f);
            }
        }
        
        std::cout << "[Variables can be modified via shared memory interface]" << std::endl;
        
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "\nDemo completed. Cleaning up shared memory..." << std::endl;
    CLEANUP_SHM();
    std::cout << "FCW ADAS Demo finished successfully!" << std::endl;
    
    return 0;
}
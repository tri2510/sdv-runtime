#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <cmath>

// Forward Collision Warning namespace
namespace FCW {
    std::atomic<float> front_distance{50.0f};        // meters
    std::atomic<float> closing_velocity{0.0f};       // m/s
    std::atomic<bool> collision_warning{false};
    std::atomic<uint8_t> warning_level{0};           // 0-3: None, Low, Medium, High
    std::atomic<float> time_to_collision{10.0f};     // seconds
    
    void updateSystem(int cycle) {
        // Simulate varying front distance
        front_distance.store(30.0f + 20.0f * sin(cycle * 0.1f));
        
        // Simulate closing velocity
        float velocity = -2.0f + (cycle % 50) * 0.1f;
        closing_velocity.store(velocity);
        
        // Calculate time to collision
        float distance = front_distance.load();
        float vel = closing_velocity.load();
        
        if (vel > 0.1f) {
            time_to_collision.store(distance / vel);
        } else {
            time_to_collision.store(99.9f);
        }
        
        // Warning logic
        float ttc = time_to_collision.load();
        if (ttc < 1.5f) {
            warning_level.store(3); // High
            collision_warning.store(true);
        } else if (ttc < 2.5f) {
            warning_level.store(2); // Medium
            collision_warning.store(true);
        } else if (ttc < 4.0f) {
            warning_level.store(1); // Low
            collision_warning.store(false);
        } else {
            warning_level.store(0); // None
            collision_warning.store(false);
        }
    }
}

// Lane Keeping Assist namespace
namespace LKA {
    std::atomic<float> lane_position{0.0f};          // -1.0 to +1.0 (left to right)
    std::atomic<float> lane_angle{0.0f};             // degrees
    std::atomic<bool> left_lane_detected{true};
    std::atomic<bool> right_lane_detected{true};
    std::atomic<float> steering_torque{0.0f};        // Nm
    std::atomic<bool> lka_active{false};
    std::atomic<uint8_t> lane_departure_warning{0};  // 0=none, 1=left, 2=right
    
    void updateSystem(int cycle) {
        // Simulate lane position drift
        lane_position.store(sin(cycle * 0.05f) * 0.8f);
        
        // Simulate lane angle
        lane_angle.store(cos(cycle * 0.07f) * 5.0f);
        
        // Lane detection simulation
        left_lane_detected.store((cycle % 100) > 10);
        right_lane_detected.store((cycle % 120) > 15);
        
        // LKA activation logic
        lka_active.store(left_lane_detected.load() && right_lane_detected.load());
        
        // Lane departure warning
        float pos = lane_position.load();
        if (pos < -0.7f) {
            lane_departure_warning.store(1); // Left departure
        } else if (pos > 0.7f) {
            lane_departure_warning.store(2); // Right departure
        } else {
            lane_departure_warning.store(0); // No warning
        }
        
        // Calculate corrective steering torque
        if (lka_active.load()) {
            steering_torque.store(-lane_position.load() * 2.5f - lane_angle.load() * 0.3f);
        } else {
            steering_torque.store(0.0f);
        }
    }
}

// Adaptive Cruise Control namespace  
namespace ACC {
    std::atomic<float> set_speed{100.0f};            // km/h
    std::atomic<float> current_speed{95.0f};         // km/h
    std::atomic<float> target_distance{50.0f};       // meters
    std::atomic<float> actual_distance{55.0f};       // meters
    std::atomic<bool> acc_enabled{true};
    std::atomic<uint8_t> following_mode{2};          // 1=close, 2=normal, 3=far
    std::atomic<float> acceleration_command{0.0f};   // m/s²
    std::atomic<bool> brake_request{false};
    
    void updateSystem(int cycle) {
        // Simulate target vehicle behavior
        actual_distance.store(40.0f + 30.0f * sin(cycle * 0.08f));
        
        // Update current speed based on control
        float current = current_speed.load();
        float accel = acceleration_command.load();
        current_speed.store(std::max(0.0f, std::min(130.0f, current + accel * 0.1f)));
        
        // ACC control logic
        if (acc_enabled.load()) {
            float distance_error = actual_distance.load() - target_distance.load();
            float speed_error = set_speed.load() - current_speed.load();
            
            // Simple PD controller
            float distance_gain = 0.1f;
            float speed_gain = 0.05f;
            
            acceleration_command.store(distance_error * distance_gain + speed_error * speed_gain);
            
            // Brake request for emergency situations
            brake_request.store(actual_distance.load() < 20.0f);
        } else {
            acceleration_command.store(0.0f);
            brake_request.store(false);
        }
        
        // Update target distance based on following mode
        switch (following_mode.load()) {
            case 1: target_distance.store(30.0f); break; // Close
            case 2: target_distance.store(50.0f); break; // Normal  
            case 3: target_distance.store(70.0f); break; // Far
        }
        
        // Mode switching logic
        if (cycle % 200 < 50) {
            following_mode.store(1);
        } else if (cycle % 200 < 100) {
            following_mode.store(2);
        } else {
            following_mode.store(3);
        }
    }
}

void displayADASStatus() {
    std::cout << "=== ADAS Systems Status ===" << std::endl;
    
    std::cout << "FCW: Distance=" << FCW::front_distance.load() << "m, "
              << "TTC=" << FCW::time_to_collision.load() << "s, "
              << "Warning=" << static_cast<int>(FCW::warning_level.load()) << std::endl;
              
    std::cout << "LKA: Position=" << LKA::lane_position.load() << ", "
              << "Angle=" << LKA::lane_angle.load() << "°, "
              << "Torque=" << LKA::steering_torque.load() << "Nm, "
              << "Active=" << LKA::lka_active.load() << std::endl;
              
    std::cout << "ACC: Speed=" << ACC::current_speed.load() << "/" << ACC::set_speed.load() << "km/h, "
              << "Distance=" << ACC::actual_distance.load() << "/" << ACC::target_distance.load() << "m, "
              << "Mode=" << static_cast<int>(ACC::following_mode.load()) << std::endl;
}

int main() {
    std::cout << "ADAS Systems Monitor - Makefile Build" << std::endl;
    std::cout << "Testing FCW, LKA, and ACC systems with namespaced variables" << std::endl;
    
    for (int cycle = 0; cycle < 50; ++cycle) {
        // Update all ADAS systems
        FCW::updateSystem(cycle);
        LKA::updateSystem(cycle);
        ACC::updateSystem(cycle);
        
        // Display status every 10 cycles
        if ((cycle + 1) % 10 == 0) {
            std::cout << "\n--- Cycle " << cycle + 1 << " ---" << std::endl;
            displayADASStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(600));
    }
    
    std::cout << "\nADAS Systems monitoring completed." << std::endl;
    return 0;
}
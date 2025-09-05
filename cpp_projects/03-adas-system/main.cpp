#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <cmath>
#include <vector>
#include <random>

// ADAS System variables
std::atomic<float> front_distance{100.0f};
std::atomic<float> rear_distance{50.0f};
std::atomic<float> left_distance{30.0f};
std::atomic<float> right_distance{30.0f};
std::atomic<bool> emergency_brake{false};
std::atomic<bool> lane_keep_assist{false};
std::atomic<bool> blind_spot_left{false};
std::atomic<bool> blind_spot_right{false};
std::atomic<int> traffic_sign{0}; // 0=none, 1=stop, 2=yield, 3=speed_limit
std::atomic<float> adaptive_cruise_speed{60.0f};

void simulateADAS() {
    std::cout << "ADAS System Simulation" << std::endl;
    std::cout << "Monitoring: distances, emergency_brake, lane_keep_assist, blind_spot detection" << std::endl;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);
    
    for (int cycle = 0; cycle < 30; ++cycle) {
        float time = cycle * 0.3f;
        
        // Simulate approaching vehicle scenario
        if (cycle < 15) {
            front_distance = 100.0f - cycle * 6.0f; // Approaching vehicle
            emergency_brake = front_distance < 20.0f;
            adaptive_cruise_speed = emergency_brake ? 0.0f : std::max(30.0f, 60.0f - cycle * 2.0f);
        } else {
            // Lane change scenario
            front_distance = std::min(100.0f, 10.0f + (cycle - 15) * 6.0f);
            left_distance = 15.0f + std::sin(time) * 10.0f;
            right_distance = 25.0f + std::cos(time) * 8.0f;
            
            blind_spot_left = left_distance < 20.0f;
            blind_spot_right = right_distance < 20.0f;
            lane_keep_assist = blind_spot_left || blind_spot_right;
            
            emergency_brake = false;
            adaptive_cruise_speed = 60.0f;
        }
        
        // Random traffic sign detection
        if (dis(gen) < 0.1) {
            traffic_sign = 1 + (cycle % 3);
        } else if (cycle % 10 == 0) {
            traffic_sign = 0;
        }
        
        std::cout << "T+" << std::fixed << std::setprecision(1) << time << "s: ";
        std::cout << "Front=" << front_distance.load() << "m, ";
        std::cout << "L=" << left_distance.load() << "m, ";
        std::cout << "R=" << right_distance.load() << "m";
        
        if (emergency_brake.load()) {
            std::cout << " [EMERGENCY_BRAKE]";
        }
        if (lane_keep_assist.load()) {
            std::cout << " [LANE_KEEP]";
        }
        if (blind_spot_left.load()) {
            std::cout << " [BLIND_L]";
        }
        if (blind_spot_right.load()) {
            std::cout << " [BLIND_R]";
        }
        if (traffic_sign.load() > 0) {
            std::cout << " [SIGN:" << traffic_sign.load() << "]";
        }
        
        std::cout << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }
    
    std::cout << "ADAS simulation complete" << std::endl;
}

int main() {
    simulateADAS();
    return 0;
}
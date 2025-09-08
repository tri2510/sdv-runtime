#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <iomanip>
#include <cmath>

// Global monitoring variables for SDV runtime (inspired by FCW showcase)
std::atomic<float> ego_speed{60.0f};           // km/h - Current vehicle speed
std::atomic<float> front_vehicle_speed{45.0f}; // km/h - Front vehicle speed
std::atomic<float> distance_to_front{120.0f};  // meters - Distance to front vehicle
std::atomic<float> time_to_collision{5.0f};    // seconds - TTC calculation
std::atomic<int> warning_level{0};             // 0=None, 1=Caution, 2=Warning, 3=Critical
std::atomic<bool> brake_assist_active{false};  // Emergency brake assist status
std::atomic<float> deceleration_rate{0.0f};    // m/s² - Applied deceleration
std::atomic<int> current_lane{2};              // Current lane (1-3)
std::atomic<float> collision_probability{0.0f}; // 0.0-1.0 - Collision risk probability

// Additional ADAS variables
std::atomic<bool> adaptive_cruise_active{true};
std::atomic<float> target_following_distance{80.0f}; // meters
std::atomic<int> detected_objects{1}; // Number of detected objects ahead

void printBanner() {
    std::cout << R"(
    ╔═════════════════════════════════════════════════════════════════╗
    ║                   ADVANCED FCW SYSTEM DEMO                     ║
    ║              Forward Collision Warning + ADAS                  ║
    ║                                                                ║
    ║  🚗 Real-time Monitoring  🚨 Collision Prediction  📊 Analytics ║
    ╚═════════════════════════════════════════════════════════════════╝
    )" << std::endl;
}

void simulateRealisticScenario() {
    std::cout << "🚗 Starting realistic highway driving scenario..." << std::endl;
    std::cout << "📊 Monitoring: ego_speed, front_vehicle_speed, distance_to_front, time_to_collision, warning_level, brake_assist_active, collision_probability" << std::endl;
    
    for (int cycle = 0; cycle < 100; ++cycle) {
        // Simulate various driving scenarios
        float time_factor = cycle * 0.1f;
        
        // Scenario 1: Normal following (cycles 0-30)
        if (cycle <= 30) {
            ego_speed = 60.0f + std::sin(time_factor) * 5.0f; // Slight speed variation
            front_vehicle_speed = 58.0f + std::cos(time_factor * 0.8f) * 3.0f;
            distance_to_front = 80.0f + std::sin(time_factor * 0.5f) * 15.0f;
            warning_level = 0; // No warning
            adaptive_cruise_active = true;
        }
        // Scenario 2: Traffic slowing down (cycles 31-60)
        else if (cycle <= 60) {
            float slowdown_factor = (cycle - 30) / 30.0f;
            ego_speed = 60.0f - slowdown_factor * 25.0f; // Slow down to 35 km/h
            front_vehicle_speed = 58.0f - slowdown_factor * 30.0f; // Slow down to 28 km/h
            distance_to_front = std::max(30.0f, 80.0f - slowdown_factor * 35.0f);
            
            if (distance_to_front < 50.0f) {
                warning_level = 1; // Caution
            }
            if (distance_to_front < 35.0f) {
                warning_level = 2; // Warning
                brake_assist_active = true;
                deceleration_rate = 2.5f;
            }
        }
        // Scenario 3: Emergency braking situation (cycles 61-80)
        else if (cycle <= 80) {
            ego_speed = std::max(10.0f, ego_speed.load() - 2.5f);
            front_vehicle_speed = std::max(5.0f, front_vehicle_speed.load() - 3.0f);
            distance_to_front = std::max(15.0f, distance_to_front.load() - 1.8f);
            
            if (distance_to_front < 25.0f) {
                warning_level = 3; // Critical
                brake_assist_active = true;
                deceleration_rate = 6.5f;
                collision_probability = std::min(0.95f, collision_probability.load() + 0.05f);
            }
        }
        // Scenario 4: Recovery and lane change (cycles 81-100)
        else {
            ego_speed = std::min(55.0f, ego_speed.load() + 1.5f);
            front_vehicle_speed = std::min(50.0f, front_vehicle_speed.load() + 1.2f);
            distance_to_front = std::min(90.0f, distance_to_front.load() + 2.5f);
            
            warning_level = 0;
            brake_assist_active = false;
            deceleration_rate = 0.0f;
            collision_probability = std::max(0.0f, collision_probability.load() - 0.08f);
            
            // Simulate lane change
            if (cycle == 85) {
                current_lane = 3; // Change to right lane
                detected_objects = 0; // Clear path after lane change
            }
        }
        
        // Calculate time to collision
        float speed_diff = ego_speed.load() - front_vehicle_speed.load();
        if (speed_diff > 0 && distance_to_front > 0) {
            time_to_collision = (distance_to_front.load() / (speed_diff / 3.6f)); // Convert km/h to m/s
        } else {
            time_to_collision = 99.9f; // No collision risk
        }
        
        // Update target following distance based on speed
        target_following_distance = ego_speed.load() * 0.8f; // Rule of thumb: 0.8m per km/h
        
        // Print status every 5 cycles
        if (cycle % 5 == 0) {
            std::cout << "\n--- Cycle " << std::setw(3) << cycle + 1 << " ---" << std::endl;
            std::cout << "🚗 Ego: " << std::fixed << std::setprecision(1) 
                      << ego_speed.load() << " km/h | Front: " << front_vehicle_speed.load() << " km/h" << std::endl;
            std::cout << "📏 Distance: " << distance_to_front.load() << "m | TTC: " 
                      << time_to_collision.load() << "s" << std::endl;
            std::cout << "⚠️  Warning: Level " << warning_level.load();
            if (brake_assist_active.load()) {
                std::cout << " | 🛑 BRAKE ASSIST: " << deceleration_rate.load() << " m/s²";
            }
            std::cout << std::endl;
            std::cout << "🎯 Collision Risk: " << std::setprecision(2) 
                      << collision_probability.load() * 100 << "% | Lane: " << current_lane.load() << std::endl;
        }
        
        // Sleep for realistic timing
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    std::cout << "\n🏁 FCW Advanced System Demo Complete!" << std::endl;
    std::cout << "📊 All monitoring variables demonstrated successfully" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🚀 Initializing Advanced FCW System..." << std::endl;
    std::cout << "📡 ADAS features: Adaptive Cruise Control, Emergency Braking, Lane Monitoring" << std::endl;
    std::cout << "🔧 System configured for highway driving scenarios" << std::endl;
    
    // Wait for initialization
    std::this_thread::sleep_for(std::chrono::seconds(1));
    
    simulateRealisticScenario();
    
    return 0;
}
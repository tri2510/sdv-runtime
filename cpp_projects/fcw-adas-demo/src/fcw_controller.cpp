#include "fcw_controller.h"
#include <cmath>
#include <algorithm>
#include <iostream>
#include <iomanip>

FCWController::FCWController() 
    : warning_system_enabled(true)
    , warning_threshold_distance(30.0f)  // 30 meters
    , critical_threshold_distance(15.0f) // 15 meters
    , last_warning_time(0.0f) {
}

void FCWController::initialize() {
    std::cout << "FCW Controller: Forward Collision Warning system initialized" << std::endl;
    std::cout << "Warning threshold: " << warning_threshold_distance << "m" << std::endl;
    std::cout << "Critical threshold: " << critical_threshold_distance << "m" << std::endl;
}

void FCWController::update(const VehicleSystem& vehicle_sys, const Environment& env, float dt) {
    if (!warning_system_enabled) return;
    
    process_warning_logic(vehicle_sys, dt);
    
    // Check environmental factors that might affect FCW
    const auto& current_light = env.get_traffic_light(vehicle_sys.get_lane_info().lane_id);
    const auto& speed_limit = env.get_speed_limit(vehicle_sys.get_lane_info().lane_id);
    
    // Adjust thresholds based on environmental conditions
    float adjusted_warning_threshold = warning_threshold_distance;
    
    // Increase warning distance in adverse conditions
    if (current_light.state == TrafficLight::YELLOW) {
        adjusted_warning_threshold *= 1.5f;
    }
    if (speed_limit.gradient < -1.0f) { // Downhill
        adjusted_warning_threshold *= 1.2f;
    }
    
    warning_threshold_distance = adjusted_warning_threshold;
}

bool FCWController::is_collision_imminent(const VehicleSystem& vehicle_sys) const {
    if (!warning_system_enabled) return false;
    
    float distance = vehicle_sys.get_distance_to_front_vehicle();
    if (distance < 0) return false; // No vehicle ahead
    
    float ego_speed = vehicle_sys.get_ego_vehicle().motion.velocity.x;
    float safe_distance = calculate_safe_following_distance(ego_speed);
    
    return distance < std::max(critical_threshold_distance, safe_distance * 0.5f);
}

int FCWController::calculate_collision_risk(const VehicleSystem& vehicle_sys) const {
    if (!warning_system_enabled) return 0;
    
    float distance = vehicle_sys.get_distance_to_front_vehicle();
    if (distance < 0) return 0; // No vehicle ahead
    
    float ego_speed = vehicle_sys.get_ego_vehicle().motion.velocity.x;
    float safe_distance = calculate_safe_following_distance(ego_speed);
    
    // Calculate risk as percentage (0-100)
    if (distance >= safe_distance) {
        return 0;
    } else if (distance <= critical_threshold_distance) {
        return 100;
    } else {
        // Linear interpolation between safe distance and critical threshold
        float risk_factor = 1.0f - (distance - critical_threshold_distance) / 
                           (safe_distance - critical_threshold_distance);
        return static_cast<int>(risk_factor * 100);
    }
}

void FCWController::process_warning_logic(const VehicleSystem& vehicle_sys, float dt) {
    float distance = vehicle_sys.get_distance_to_front_vehicle();
    if (distance < 0) return; // No vehicle ahead
    
    float ego_speed = vehicle_sys.get_ego_vehicle().motion.velocity.x;
    int risk_level = calculate_collision_risk(vehicle_sys);
    
    // Determine warning level
    if (risk_level > 80) {
        // Critical warning - suggest immediate action
        if (last_warning_time == 0.0f || (dt - last_warning_time) > 1.0f) {
            std::cout << "⚠️  CRITICAL WARNING: Collision imminent! Distance: " 
                      << std::fixed << std::setprecision(1) << distance << "m" << std::endl;
            trigger_emergency_brake(vehicle_sys);
            last_warning_time = dt;
        }
    } else if (risk_level > 50) {
        // High warning - suggest lane change or braking
        if (last_warning_time == 0.0f || (dt - last_warning_time) > 2.0f) {
            std::cout << "⚠️  HIGH WARNING: Reduce speed or change lanes. Distance: " 
                      << std::fixed << std::setprecision(1) << distance << "m" << std::endl;
            suggest_lane_change(vehicle_sys);
            last_warning_time = dt;
        }
    } else if (risk_level > 20) {
        // Low warning - informational
        if (last_warning_time == 0.0f || (dt - last_warning_time) > 5.0f) {
            std::cout << "ℹ️  INFO: Following too close. Distance: " 
                      << std::fixed << std::setprecision(1) << distance << "m" << std::endl;
            last_warning_time = dt;
        }
    }
}

void FCWController::trigger_emergency_brake(const VehicleSystem& vehicle_sys) {
    // In a real system, this would interface with the brake system
    std::cout << "🚨 EMERGENCY BRAKE ACTIVATED!" << std::endl;
}

void FCWController::suggest_lane_change(const VehicleSystem& vehicle_sys) {
    int current_lane = vehicle_sys.get_lane_info().lane_id;
    std::cout << "💡 Suggestion: Consider changing from lane " << current_lane;
    
    if (current_lane > 1) {
        std::cout << " to lane " << (current_lane - 1);
    } else if (current_lane < 4) {
        std::cout << " to lane " << (current_lane + 1);
    }
    std::cout << " when safe" << std::endl;
}

float FCWController::calculate_time_to_collision(const Vehicle& ego, const Vehicle& target) const {
    float relative_velocity = ego.motion.velocity.x - target.motion.velocity.x;
    float distance = target.position.x - ego.position.x;
    
    if (relative_velocity <= 0) return -1.0f; // No collision if not approaching
    
    return distance / relative_velocity;
}

float FCWController::calculate_safe_following_distance(float ego_speed) const {
    // Safe following distance: 2-second rule + reaction time
    float reaction_time = 1.5f; // seconds
    float following_time = 2.0f; // seconds
    
    return ego_speed * (reaction_time + following_time);
}
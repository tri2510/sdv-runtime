#include "vehicle_system.h"
#include <random>
#include <cmath>
#include <iostream>

VehicleSystem::VehicleSystem() {
    ego_vehicle.is_ego = true;
    ego_vehicle.mass = 1500.0f; // kg
    ego_vehicle.position = {0.0f, 0.0f, 0.0f};
    ego_vehicle.motion.velocity = {16.7f, 0.0f, 0.0f}; // 60 km/h initial speed
    
    lane_info.lane_id = 2;
    lane_info.target_lane = 2;
    lane_info.offset_to_center = 0.0f;
}

void VehicleSystem::initialize() {
    generate_realistic_traffic();
    std::cout << "Vehicle System: Initialized with ego vehicle in lane " << lane_info.lane_id << std::endl;
}

void VehicleSystem::update(float dt) {
    update_ego_vehicle(dt);
    update_surrounding_vehicles(dt);
}

void VehicleSystem::update_ego_vehicle(float dt) {
    // Update position based on velocity
    ego_vehicle.position.x += ego_vehicle.motion.velocity.x * dt;
    ego_vehicle.position.y += ego_vehicle.motion.velocity.y * dt;
    
    // Lane change logic
    if (lane_info.lane_id != lane_info.target_lane) {
        float lane_change_speed = 2.0f; // m/s lateral speed
        float target_y = (lane_info.target_lane - 1) * 3.5f; // 3.5m lane width
        float current_y = ego_vehicle.position.y;
        
        if (std::abs(target_y - current_y) > 0.1f) {
            float direction = (target_y > current_y) ? 1.0f : -1.0f;
            ego_vehicle.position.y += direction * lane_change_speed * dt;
            ego_vehicle.motion.velocity.y = direction * lane_change_speed;
        } else {
            lane_info.lane_id = lane_info.target_lane;
            ego_vehicle.motion.velocity.y = 0.0f;
        }
    }
}

void VehicleSystem::update_surrounding_vehicles(float dt) {
    for (auto& vehicle : surrounding_vehicles) {
        // Simple forward movement with some random variation
        vehicle.position.x += vehicle.motion.velocity.x * dt;
        
        // Add some realistic behavior variation
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_real_distribution<> speed_variation(-0.5, 0.5);
        
        vehicle.motion.velocity.x += speed_variation(gen) * dt;
        vehicle.motion.velocity.x = std::max(5.0f, std::min(25.0f, vehicle.motion.velocity.x));
    }
}

void VehicleSystem::generate_realistic_traffic() {
    surrounding_vehicles.clear();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> speed_dist(12.0, 20.0); // 40-70 km/h
    std::uniform_real_distribution<> pos_dist(-50.0, 100.0);
    
    // Generate vehicles in different lanes
    for (int lane = 1; lane <= 4; ++lane) {
        for (int i = 0; i < 3; ++i) { // 3 vehicles per lane
            Vehicle vehicle;
            vehicle.position.x = pos_dist(gen);
            vehicle.position.y = (lane - 1) * 3.5f; // Lane positioning
            vehicle.position.z = 0.0f;
            
            vehicle.motion.velocity.x = speed_dist(gen);
            vehicle.motion.velocity.y = 0.0f;
            vehicle.motion.velocity.z = 0.0f;
            
            vehicle.mass = 1200.0f + i * 300.0f; // Different vehicle masses
            vehicle.is_ego = false;
            
            surrounding_vehicles.push_back(vehicle);
        }
    }
    
    std::cout << "Generated " << surrounding_vehicles.size() << " surrounding vehicles" << std::endl;
}

void VehicleSystem::set_ego_speed(float speed) {
    ego_vehicle.motion.velocity.x = speed; // speed in m/s
}

float VehicleSystem::get_distance_to_front_vehicle() const {
    float min_distance = 1000.0f; // Very large initial value
    float ego_lane_y = (lane_info.lane_id - 1) * 3.5f;
    
    for (const auto& vehicle : surrounding_vehicles) {
        // Check if vehicle is in the same lane and ahead
        if (std::abs(vehicle.position.y - ego_lane_y) < 1.75f && // Same lane (half lane width tolerance)
            vehicle.position.x > ego_vehicle.position.x) { // Ahead of ego
            float distance = vehicle.position.x - ego_vehicle.position.x;
            min_distance = std::min(min_distance, distance);
        }
    }
    
    return min_distance == 1000.0f ? -1.0f : min_distance; // -1 if no vehicle found
}

void VehicleSystem::apply_brake(float pressure) {
    // Simulate braking: reduce speed based on brake pressure (0-100%)
    float max_deceleration = 8.0f; // m/s²
    float deceleration = (pressure / 100.0f) * max_deceleration;
    float current_speed = ego_vehicle.motion.velocity.x;
    
    ego_vehicle.motion.velocity.x = std::max(0.0f, current_speed - deceleration * 0.1f);
    ego_vehicle.motion.acceleration.x = -deceleration;
}

void VehicleSystem::change_lane(int target_lane) {
    if (target_lane >= 1 && target_lane <= 4 && target_lane != lane_info.lane_id) {
        lane_info.target_lane = target_lane;
        std::cout << "Initiating lane change from " << lane_info.lane_id 
                  << " to " << target_lane << std::endl;
    }
}
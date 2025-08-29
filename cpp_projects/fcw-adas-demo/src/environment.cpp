#include "environment.h"
#include <iostream>
#include <iomanip>

Environment::Environment() : simulation_time(0.0f) {
    // Initialize traffic lights
    for (int i = 0; i < 4; ++i) {
        traffic_lights[i].state = TrafficLight::GREEN;
        traffic_lights[i].time_remaining = 30.0f + i * 10.0f; // Staggered timing
    }
    
    // Initialize speed limits
    speed_limits[0] = {50.0f, -2.0f}; // Lane 1: 50 km/h, downhill
    speed_limits[1] = {60.0f, 0.0f};  // Lane 2: 60 km/h, flat
    speed_limits[2] = {60.0f, 0.0f};  // Lane 3: 60 km/h, flat  
    speed_limits[3] = {70.0f, 1.5f};  // Lane 4: 70 km/h, uphill
}

void Environment::initialize() {
    simulate_realistic_environment();
    std::cout << "Environment: Initialized 4-lane scenario with traffic infrastructure" << std::endl;
}

void Environment::update(float dt) {
    simulation_time += dt;
    update_traffic_lights(dt);
}

void Environment::update_traffic_lights(float dt) {
    for (auto& light : traffic_lights) {
        light.time_remaining -= dt;
        
        if (light.time_remaining <= 0.0f) {
            // Cycle through traffic light states
            switch (light.state) {
                case TrafficLight::GREEN:
                    light.state = TrafficLight::YELLOW;
                    light.time_remaining = 5.0f; // Yellow for 5 seconds
                    break;
                case TrafficLight::YELLOW:
                    light.state = TrafficLight::RED;
                    light.time_remaining = 25.0f; // Red for 25 seconds
                    break;
                case TrafficLight::RED:
                    light.state = TrafficLight::GREEN;
                    light.time_remaining = 30.0f; // Green for 30 seconds
                    break;
            }
        }
    }
}

const TrafficLight& Environment::get_traffic_light(int lane) const {
    return traffic_lights[std::max(0, std::min(3, lane - 1))];
}

const SpeedLimit& Environment::get_speed_limit(int lane) const {
    return speed_limits[std::max(0, std::min(3, lane - 1))];
}

void Environment::print_environment_status() const {
    std::cout << "\n--- Environment Status ---" << std::endl;
    
    for (int i = 0; i < 4; ++i) {
        const auto& light = traffic_lights[i];
        const auto& limit = speed_limits[i];
        
        std::string light_str;
        switch (light.state) {
            case TrafficLight::RED: light_str = "RED"; break;
            case TrafficLight::YELLOW: light_str = "YELLOW"; break;
            case TrafficLight::GREEN: light_str = "GREEN"; break;
        }
        
        std::cout << "Lane " << (i + 1) << ": " 
                  << light_str << " (" << std::fixed << std::setprecision(1) 
                  << light.time_remaining << "s) | "
                  << "Speed: " << limit.limit << " km/h | "
                  << "Gradient: " << std::showpos << limit.gradient << "%" << std::noshowpos
                  << std::endl;
    }
}

void Environment::simulate_realistic_environment() {
    // This could be expanded to include more realistic environmental factors
    // such as weather, road conditions, construction zones, etc.
    std::cout << "Simulating realistic multi-lane highway environment" << std::endl;
}
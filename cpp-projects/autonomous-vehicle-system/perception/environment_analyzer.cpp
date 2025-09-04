#include "environment_analyzer.h"
#include <iostream>
#include <cmath>
#include <algorithm>

EnvironmentAnalyzer::EnvironmentAnalyzer() {
    std::cout << "👁️  EnvironmentAnalyzer initialized" << std::endl;
}

EnvironmentAnalyzer::~EnvironmentAnalyzer() {
    std::cout << "👁️  EnvironmentAnalyzer shutdown" << std::endl;
}

void EnvironmentAnalyzer::processEnvironment() {
    cycle_count++;
    
    // Simulate dynamic environment detection
    
    // Object detection simulation (varies over time)
    int base_objects = 2 + (cycle_count % 8);
    detected_objects = base_objects + (cycle_count % 3);  // 2-10 objects
    
    // Nearest object distance (simulate approaching/departing vehicles)
    float distance_variation = 40.0f * std::sin(cycle_count * 0.12f);
    nearest_object_distance = std::max(5.0f, 50.0f + distance_variation);  // 5-90m
    
    // Traffic light state (realistic timing)
    int light_cycle = cycle_count % 60;  // 30 second cycles
    if (light_cycle < 20) {
        traffic_light_state = 1;  // Green
    } else if (light_cycle < 25) {
        traffic_light_state = 2;  // Yellow
    } else {
        traffic_light_state = 0;  // Red
    }
    
    // Lane deviation (simulate slight corrections)
    lane_deviation = std::sin(cycle_count * 0.15f) * 0.3f;  // ±0.3m
    
    if (cycle_count % 12 == 0) {
        std::string light_color = (traffic_light_state.load() == 0) ? "RED" :
                                 (traffic_light_state.load() == 1) ? "GREEN" : "YELLOW";
        
        std::cout << "👁️  Environment: Objects=" << detected_objects.load()
                  << " | Nearest=" << nearest_object_distance.load() << "m"
                  << " | Light=" << light_color
                  << " | Lane deviation=" << lane_deviation.load() << "m" << std::endl;
    }
}
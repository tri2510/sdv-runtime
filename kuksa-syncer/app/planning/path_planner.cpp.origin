#include "path_planner.h"
#include <iostream>
#include <cmath>
#include <algorithm>

PathPlanner::PathPlanner() {
    std::cout << "🗺️  PathPlanner initialized" << std::endl;
}

PathPlanner::~PathPlanner() {
    std::cout << "🗺️  PathPlanner shutdown" << std::endl;
}

void PathPlanner::updatePath() {
    cycle_count++;
    planning_cycles = planning_cycles.load() + 1;
    
    // Simulate dynamic path planning
    
    // Waypoint generation (varies based on road complexity)
    int base_waypoints = 10 + (cycle_count % 6);
    waypoint_count = base_waypoints + std::abs((int)(std::sin(cycle_count * 0.1f) * 5));
    
    // Total path distance (simulate route changes)
    float base_distance = 1500.0f;  // 1.5km base route
    float distance_variation = 500.0f * std::cos(cycle_count * 0.08f);
    total_path_distance = base_distance + distance_variation;  // 1-2km range
    
    // Path validity (occasional recalculation needed)
    path_valid = (cycle_count % 25) != 0;  // Invalid every 25 cycles (recalculation)
    
    // Dynamic target speed based on conditions
    float speed_base = 60.0f;
    float speed_adjustment = 0.0f;
    
    // Slow down for curves or obstacles (simulated)
    if (cycle_count % 15 < 5) {
        speed_adjustment = -15.0f;  // Curve ahead
    } else if (cycle_count % 20 < 3) {
        speed_adjustment = -25.0f;  // Obstacle/traffic
    }
    
    target_speed = std::max(20.0f, std::min(80.0f, speed_base + speed_adjustment));
    
    if (cycle_count % 8 == 0) {
        std::cout << "🗺️  Planning: Waypoints=" << waypoint_count.load()
                  << " | Distance=" << total_path_distance.load() << "m"
                  << " | Valid=" << (path_valid.load() ? "YES" : "RECALC")
                  << " | Target=" << target_speed.load() << "km/h"
                  << " | Cycles=" << planning_cycles.load() << std::endl;
    }
}
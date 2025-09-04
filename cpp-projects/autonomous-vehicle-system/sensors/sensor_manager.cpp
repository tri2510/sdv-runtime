#include "sensor_manager.h"
#include <iostream>
#include <cmath>

extern std::atomic<int> active_sensors;

SensorManager::SensorManager() {
    std::cout << "🔍 SensorManager initialized" << std::endl;
}

SensorManager::~SensorManager() {
    std::cout << "🔍 SensorManager shutdown" << std::endl;
}

void SensorManager::updateSensors() {
    cycle_count++;
    
    // Simulate sensor readings with realistic automotive patterns
    lidar_range = 50.0f + std::sin(cycle_count * 0.1f) * 30.0f;  // 20-80m range
    camera_distance = 25.0f + (cycle_count % 15) * 2.0f;         // 25-55m distance
    radar_speed = 60.0f + std::cos(cycle_count * 0.15f) * 25.0f; // 35-85 km/h
    gps_active = (cycle_count % 20) != 0;  // Occasional GPS dropout
    
    // Count active sensors
    int count = 0;
    if (lidar_range.load() > 30.0f) count++;
    if (camera_distance.load() > 0.0f) count++;
    if (radar_speed.load() > 0.0f) count++;
    if (gps_active.load()) count++;
    
    active_sensors = count;
    
    if (cycle_count % 10 == 0) {
        std::cout << "🔍 Sensors: LIDAR=" << lidar_range.load() << "m"
                  << " | Camera=" << camera_distance.load() << "m"
                  << " | Radar=" << radar_speed.load() << "km/h"
                  << " | GPS=" << (gps_active.load() ? "Active" : "Lost") << std::endl;
    }
}

int SensorManager::getActiveSensorCount() const {
    return active_sensors.load();
}
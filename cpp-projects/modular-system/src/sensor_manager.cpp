#include "sensor_manager.h"
#include <iostream>
#include <iomanip>
#include <cmath>

// Define static members
std::atomic<float> SensorManager::lidar_distance{150.0f};
std::atomic<int> SensorManager::object_count{0};
std::atomic<bool> SensorManager::emergency_brake{false};
std::atomic<double> SensorManager::gps_latitude{37.7749};
std::atomic<float> SensorManager::battery_voltage{12.6f};
bool SensorManager::initialized = false;

void SensorManager::initialize() {
    if (!initialized) {
        std::cout << "🔧 Initializing Sensor Manager..." << std::endl;
        initialized = true;
    }
}

void SensorManager::updateSensors(int cycle) {
    // Simulate realistic sensor data
    lidar_distance = 150.0f - (cycle % 100) * 1.2f; // Approaching object
    object_count = (cycle / 20) % 5; // 0-4 objects detected
    emergency_brake = (lidar_distance.load() < 30.0f);
    gps_latitude = 37.7749 + cycle * 0.00001; // Moving north
    battery_voltage = 12.6f - (cycle * 0.001f); // Slowly draining
}

void SensorManager::printStatus() {
    std::cout << std::fixed << std::setprecision(2)
              << "📡 Lidar: " << lidar_distance.load() << "m | "
              << "Objects: " << object_count.load() << " | "
              << "E-Brake: " << (emergency_brake.load() ? "ON" : "OFF") << " | "
              << "GPS: " << gps_latitude.load() << " | "
              << "Battery: " << battery_voltage.load() << "V" << std::endl;
}
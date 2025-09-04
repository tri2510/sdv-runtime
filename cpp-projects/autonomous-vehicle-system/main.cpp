#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include "sensors/sensor_manager.h"
#include "control/vehicle_controller.h"
#include "perception/environment_analyzer.h"
#include "planning/path_planner.h"

// Global monitoring variables for SDV runtime
std::atomic<float> vehicle_speed{0.0f};
std::atomic<int> current_gear{1};
std::atomic<float> engine_rpm{800.0f};
std::atomic<bool> autonomous_mode{false};
std::atomic<float> fuel_level{75.5f};
std::atomic<int> active_sensors{0};
std::atomic<float> cpu_temperature{45.0f};

int main() {
    std::cout << "🚗 Autonomous Vehicle System Starting..." << std::endl;
    std::cout << "Initializing subsystems..." << std::endl;
    
    // Initialize subsystems
    SensorManager sensors;
    VehicleController controller;
    EnvironmentAnalyzer analyzer;
    PathPlanner planner;
    
    std::cout << "✅ All subsystems initialized" << std::endl;
    std::cout << "📊 Monitoring variables: vehicle_speed, current_gear, engine_rpm, autonomous_mode, fuel_level, active_sensors, cpu_temperature" << std::endl;
    
    // Main control loop
    for (int cycle = 0; cycle < 60; ++cycle) {
        std::cout << "\n--- Control Cycle " << (cycle + 1) << " ---" << std::endl;
        
        // Update sensor data
        sensors.updateSensors();
        active_sensors = sensors.getActiveSensorCount();
        
        // Analyze environment
        analyzer.processEnvironment();
        
        // Plan path if autonomous
        if (cycle > 10) {
            autonomous_mode = true;
            planner.updatePath();
        }
        
        // Control vehicle
        controller.updateControl();
        
        // Update monitored variables with realistic automotive data
        vehicle_speed = 20.0f + (cycle % 25) * 2.5f;  // Speed: 20-80 km/h
        current_gear = std::min(5, 1 + cycle / 10);    // Gear: 1-5
        engine_rpm = 800.0f + (cycle % 15) * 200.0f;   // RPM: 800-3600
        fuel_level = std::max(15.0f, 75.5f - cycle * 0.8f); // Fuel: 75.5 -> 27.5
        cpu_temperature = 45.0f + (cycle % 8) * 3.0f;  // Temp: 45-66°C
        
        std::cout << "📊 Status: Speed=" << vehicle_speed.load() << "km/h"
                  << " | Gear=" << current_gear.load()
                  << " | RPM=" << engine_rpm.load()
                  << " | Auto=" << (autonomous_mode.load() ? "ON" : "OFF")
                  << " | Fuel=" << fuel_level.load() << "%"
                  << " | Sensors=" << active_sensors.load()
                  << " | CPU=" << cpu_temperature.load() << "°C" << std::endl;
        
        // Sleep between cycles
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    
    std::cout << "\n🏁 Autonomous Vehicle System Shutdown Complete" << std::endl;
    return 0;
}
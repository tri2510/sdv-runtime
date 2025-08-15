#include <iostream>
#include "vehicle/Vehicle.h"
#include "sensors/SpeedSensor.h"
#include "utils/Logger.h"
#include "config/SystemConfig.h"

int main() {
    Logger logger("SDV_SYSTEM");
    logger.info("=== MULTI-FILE SDV SYSTEM TEST ===");
    
    // Initialize vehicle system
    Vehicle vehicle("SDV-PROD-001", "Production Test Vehicle");
    logger.info("Vehicle initialized: " + vehicle.getId());
    
    // Setup speed sensor
    SpeedSensor speedSensor(1, "Primary Speed Sensor");
    logger.info("Speed sensor created: " + speedSensor.getName());
    
    // Test sensor functionality
    speedSensor.setSpeed(65.5);
    double currentSpeed = speedSensor.getSpeed();
    logger.info("Current speed: " + std::to_string(currentSpeed) + " km/h");
    
    // Test vehicle operations
    vehicle.setSpeed(currentSpeed);
    vehicle.updateStatus();
    
    std::cout << "Vehicle ID: " << vehicle.getId() << std::endl;
    std::cout << "Vehicle Name: " << vehicle.getName() << std::endl;
    std::cout << "Current Speed: " << vehicle.getSpeed() << " km/h" << std::endl;
    std::cout << "Vehicle Status: " << (vehicle.isMoving() ? "Moving" : "Stopped") << std::endl;
    
    // Test system configuration
    SystemConfig config;
    std::cout << "System Version: " << config.getVersion() << std::endl;
    std::cout << "Max Speed: " << config.getMaxSpeed() << " km/h" << std::endl;
    
    // Mathematical verification
    double distance = currentSpeed * 2.5; // Distance in 2.5 hours
    std::cout << "Distance in 2.5h: " << distance << " km" << std::endl;
    
    logger.info("=== MULTI-FILE TEST COMPLETED SUCCESSFULLY ===");
    
    return 0;
}
#include "vehicle_controller.h"
#include <iostream>
#include <cmath>

extern std::atomic<float> vehicle_speed;
extern std::atomic<int> current_gear;
extern std::atomic<float> engine_rpm;

VehicleController::VehicleController() {
    std::cout << "🎮 VehicleController initialized" << std::endl;
}

VehicleController::~VehicleController() {
    std::cout << "🎮 VehicleController shutdown" << std::endl;
}

void VehicleController::updateControl() {
    cycle_count++;
    
    // Simulate realistic vehicle control behavior
    float current_speed = vehicle_speed.load();
    
    // Adaptive throttle control
    if (current_speed < target_speed) {
        throttle_position = std::min(1.0f, throttle_position.load() + 0.05f);
        brake_force = 0.0f;
    } else if (current_speed > target_speed + 5.0f) {
        throttle_position = std::max(0.0f, throttle_position.load() - 0.03f);
        brake_force = std::min(1.0f, brake_force.load() + 0.02f);
    }
    
    // Dynamic steering simulation (lane keeping, curves)
    steering_angle = std::sin(cycle_count * 0.08f) * 15.0f;  // ±15 degrees
    
    // Gear control based on RPM
    float rpm = engine_rpm.load();
    if (rpm > 3000 && current_gear.load() < 5) {
        current_gear = current_gear.load() + 1;
    } else if (rpm < 1500 && current_gear.load() > 1) {
        current_gear = current_gear.load() - 1;
    }
    
    if (cycle_count % 15 == 0) {
        std::cout << "🎮 Control: Throttle=" << throttle_position.load() * 100 << "%"
                  << " | Brake=" << brake_force.load() * 100 << "%"
                  << " | Steering=" << steering_angle.load() << "°" << std::endl;
    }
}

void VehicleController::setTargetSpeed(float speed) {
    target_speed = speed;
}

void VehicleController::setTargetGear(int gear) {
    target_gear = gear;
}
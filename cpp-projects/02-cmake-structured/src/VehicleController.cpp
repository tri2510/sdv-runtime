#include "VehicleController.h"
#include <iostream>
#include <cmath>

VehicleController::VehicleController() {
    std::cout << "VehicleController initialized" << std::endl;
}

void VehicleController::updateControlSystems() {
    update_cycle++;
    
    // Simulate speed control system
    float target = 50.0f + 20.0f * sin(update_cycle * 0.1f);
    target_speed.store(target);
    
    // Simulate PID-like speed control
    float current = actual_speed.load();
    float error = target - current;
    float new_speed = current + error * 0.1f; // Simple proportional control
    actual_speed.store(std::max(0.0f, new_speed));
    
    // Update throttle and brake based on speed error
    if (error > 5.0f) {
        throttle_position.store(std::min(static_cast<int16_t>(1000), static_cast<int16_t>(error * 20)));
        brake_pressure.store(0);
    } else if (error < -5.0f) {
        throttle_position.store(0);
        brake_pressure.store(std::min(static_cast<int16_t>(1000), static_cast<int16_t>(-error * 15)));
    } else {
        throttle_position.store(static_cast<int16_t>(500 + error * 10));
        brake_pressure.store(0);
    }
    
    // Cruise control logic
    cruise_control_active.store(update_cycle % 100 < 70);
    
    // ABS simulation (activate when hard braking)
    abs_active.store(brake_pressure.load() > 800);
    
    // ESP simulation (activate during aggressive maneuvers)
    esp_active.store((update_cycle % 150) < 10);
    
    // Engine RPM based on speed and load
    float speed = actual_speed.load();
    uint16_t base_rpm = static_cast<uint16_t>(800 + speed * 25); // Base RPM
    engine_rpm.store(base_rpm + (update_cycle % 200));
    
    // Engine load based on throttle
    engine_load.store(static_cast<uint8_t>(throttle_position.load() / 10));
    
    // Engine temperature simulation
    int8_t temp = static_cast<int8_t>(80 + (engine_load.load() / 10) + (update_cycle % 40) - 20);
    engine_temp.store(std::max(static_cast<int8_t>(60), std::min(static_cast<int8_t>(110), temp)));
    
    // Transmission gear selection
    float current_speed = actual_speed.load();
    if (current_speed < 5.0f) {
        gear_number.store(1);
    } else if (current_speed < 20.0f) {
        gear_number.store(2);
    } else if (current_speed < 40.0f) {
        gear_number.store(3);
    } else if (current_speed < 60.0f) {
        gear_number.store(4);
    } else if (current_speed < 80.0f) {
        gear_number.store(5);
    } else {
        gear_number.store(6);
    }
    
    // Transmission lock during gear changes
    transmission_locked.store((update_cycle % 200) < 5);
}

void VehicleController::displayStatus() {
    std::cout << "=== Vehicle Controller Status ===" << std::endl;
    std::cout << "Speed: " << actual_speed.load() << "/" << target_speed.load() << " km/h" << std::endl;
    std::cout << "Throttle: " << throttle_position.load()/10.0f << "%, Brake: " << brake_pressure.load() << " bar" << std::endl;
    std::cout << "Engine: " << engine_rpm.load() << " RPM, " << static_cast<int>(engine_load.load()) << "% load, " 
              << static_cast<int>(engine_temp.load()) << "°C" << std::endl;
    std::cout << "Gear: " << static_cast<int>(gear_number.load()) << (transmission_locked.load() ? " (LOCKED)" : "") << std::endl;
    std::cout << "Systems: CC:" << cruise_control_active.load() << " ABS:" << abs_active.load() 
              << " ESP:" << esp_active.load() << std::endl;
}
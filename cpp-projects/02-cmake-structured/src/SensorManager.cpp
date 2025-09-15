#include "SensorManager.h"
#include <iostream>
#include <cmath>
#include <random>

SensorManager::SensorManager() {
    std::cout << "SensorManager initialized" << std::endl;
}

void SensorManager::updateSensors() {
    sensor_cycle++;
    
    // GPS simulation (driving around Berlin)
    double base_lat = 52.520008;
    double base_lon = 13.404954;
    gps_latitude.store(base_lat + sin(sensor_cycle * 0.01) * 0.01);
    gps_longitude.store(base_lon + cos(sensor_cycle * 0.01) * 0.01);
    gps_altitude.store(50.0f + sin(sensor_cycle * 0.05) * 10.0f);
    gps_satellites.store(8 + (sensor_cycle % 6));
    
    // IMU sensors - simulate vehicle dynamics
    float vehicle_speed = 30.0f + 20.0f * sin(sensor_cycle * 0.1f);
    
    // Acceleration simulation
    accel_x.store(-0.5f + (sensor_cycle % 20) * 0.1f); // Forward/backward
    accel_y.store(-0.2f + (sensor_cycle % 10) * 0.04f); // Left/right  
    accel_z.store(9.81f + sin(sensor_cycle * 0.2f) * 0.5f); // Vertical
    
    // Gyroscope simulation (angular velocities)
    gyro_roll.store(sin(sensor_cycle * 0.15f) * 2.0f);
    gyro_pitch.store(cos(sensor_cycle * 0.12f) * 1.5f);
    gyro_yaw.store(sin(sensor_cycle * 0.08f) * 5.0f);
    
    // Environmental sensors
    int temp = static_cast<int>(200 + sin(sensor_cycle * 0.01) * 100); // 10-30°C
    ambient_temperature.store(temp);
    
    int humidity = static_cast<int>(500 + cos(sensor_cycle * 0.02) * 200); // 30-70%
    ambient_humidity.store(humidity);
    
    int pressure = static_cast<int>(101325 + sin(sensor_cycle * 0.005) * 1000);
    ambient_pressure.store(pressure);
    
    // Distance sensors (obstacle detection simulation)
    int front_dist = static_cast<int>(1000 + (sensor_cycle % 100) * 40);
    front_distance.store(std::min(static_cast<int>(5000), front_dist));
    
    rear_distance.store(static_cast<int>(2000 + (sensor_cycle % 80) * 30));
    left_distance.store(static_cast<int>(1500 + sin(sensor_cycle * 0.3f) * 500));
    right_distance.store(static_cast<int>(1500 + cos(sensor_cycle * 0.3f) * 500));
    
    // TPMS simulation
    int base_pressure = 220; // 2.2 bar = 220 kPa
    tire_pressure_fl.store(base_pressure + (sensor_cycle % 20) - 10);
    tire_pressure_fr.store(base_pressure + ((sensor_cycle + 5) % 20) - 10);
    tire_pressure_rl.store(base_pressure + ((sensor_cycle + 10) % 20) - 10);
    tire_pressure_rr.store(base_pressure + ((sensor_cycle + 15) % 20) - 10);
    
    // Battery Management System
    float voltage = 12.6f + sin(sensor_cycle * 0.1f) * 0.4f; // 12.2-13.0V
    battery_voltage.store(voltage);
    
    float current = -5.0f + (sensor_cycle % 100) * 0.2f; // -5 to +15 A
    battery_current.store(current);
    
    char soc = static_cast<char>(std::max(10, 90 - (sensor_cycle / 50)));
    battery_soc.store(soc);
    
    char bat_temp = static_cast<char>(25 + sin(sensor_cycle * 0.05f) * 15);
    battery_temperature.store(bat_temp);
}

void SensorManager::displaySensorData() {
    std::cout << "=== Sensor Manager Status ===" << std::endl;
    std::cout << "GPS: " << gps_latitude.load() << ", " << gps_longitude.load() 
              << " (Alt: " << gps_altitude.load() << "m, Sats: " << static_cast<int>(gps_satellites.load()) << ")" << std::endl;
    
    std::cout << "IMU - Accel: (" << accel_x.load() << ", " << accel_y.load() << ", " << accel_z.load() << ") m/s²" << std::endl;
    std::cout << "IMU - Gyro: (" << gyro_roll.load() << ", " << gyro_pitch.load() << ", " << gyro_yaw.load() << ") °/s" << std::endl;
    
    std::cout << "Environment: " << ambient_temperature.load()/10.0f << "°C, " 
              << ambient_humidity.load()/10.0f << "% RH, " << ambient_pressure.load() << " Pa" << std::endl;
    
    std::cout << "Distance: F:" << front_distance.load() << "mm R:" << rear_distance.load() 
              << "mm L:" << left_distance.load() << "mm R:" << right_distance.load() << "mm" << std::endl;
              
    std::cout << "TPMS: FL:" << tire_pressure_fl.load() << " FR:" << tire_pressure_fr.load()
              << " RL:" << tire_pressure_rl.load() << " RR:" << tire_pressure_rr.load() << " kPa" << std::endl;
              
    std::cout << "Battery: " << battery_voltage.load() << "V, " << battery_current.load() << "A, "
              << static_cast<int>(battery_soc.load()) << "%, " << static_cast<int>(battery_temperature.load()) << "°C" << std::endl;
}
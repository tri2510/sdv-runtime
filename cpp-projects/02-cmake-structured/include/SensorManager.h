#pragma once
#include <atomic>
#include <cstdint>
#include <array>

class SensorManager {
public:
    SensorManager();
    void updateSensors();
    void displaySensorData();
    
    // GPS and Navigation
    std::atomic<double> gps_latitude{0.0};
    std::atomic<double> gps_longitude{0.0};
    std::atomic<float> gps_altitude{0.0f};
    std::atomic<char> gps_satellites{0};
    
    // IMU and Motion Sensors
    std::atomic<float> accel_x{0.0f};        // m/s²
    std::atomic<float> accel_y{0.0f};
    std::atomic<float> accel_z{0.0f};
    std::atomic<float> gyro_roll{0.0f};      // degrees/s
    std::atomic<float> gyro_pitch{0.0f};
    std::atomic<float> gyro_yaw{0.0f};
    
    // Environmental Sensors
    std::atomic<int> ambient_temperature{200}; // Celsius * 10
    std::atomic<int> ambient_humidity{500};   // % * 10
    std::atomic<int> ambient_pressure{101325}; // Pa
    
    // Distance Sensors (automotive LIDAR/ultrasonic)
    std::atomic<int> front_distance{5000};  // mm
    std::atomic<int> rear_distance{5000};
    std::atomic<int> left_distance{2000};
    std::atomic<int> right_distance{2000};
    
    // Tire Pressure Monitoring System (TPMS)
    std::atomic<int> tire_pressure_fl{220}; // kPa
    std::atomic<int> tire_pressure_fr{220};
    std::atomic<int> tire_pressure_rl{220};
    std::atomic<int> tire_pressure_rr{220};
    
    // Battery Management System
    std::atomic<float> battery_voltage{12.6f};
    std::atomic<float> battery_current{0.0f};
    std::atomic<char> battery_soc{80}; // State of Charge %
    std::atomic<char> battery_temperature{25};
    
private:
    int sensor_cycle = 0;
};
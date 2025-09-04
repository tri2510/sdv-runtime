#pragma once
#include <atomic>

class SensorManager {
public:
    static void initialize();
    static void updateSensors(int cycle);
    static void printStatus();
    
    // Global atomic variables for monitoring
    static std::atomic<float> lidar_distance;
    static std::atomic<int> object_count;
    static std::atomic<bool> emergency_brake;
    static std::atomic<double> gps_latitude;
    static std::atomic<float> battery_voltage;
    
private:
    static bool initialized;
};
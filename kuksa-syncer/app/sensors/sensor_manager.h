#pragma once
#include <atomic>
#include <vector>
#include <memory>

class SensorManager {
public:
    SensorManager();
    ~SensorManager();
    
    void updateSensors();
    int getActiveSensorCount() const;
    
    // Individual sensor data
    float getLidarRange() const { return lidar_range.load(); }
    float getCameraDistance() const { return camera_distance.load(); }
    float getRadarSpeed() const { return radar_speed.load(); }
    bool isGpsActive() const { return gps_active.load(); }

private:
    std::atomic<float> lidar_range{150.0f};
    std::atomic<float> camera_distance{50.0f};
    std::atomic<float> radar_speed{65.0f};
    std::atomic<bool> gps_active{true};
    
    int cycle_count{0};
};
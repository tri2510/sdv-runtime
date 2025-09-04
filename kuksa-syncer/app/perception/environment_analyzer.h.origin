#pragma once
#include <atomic>
#include <vector>

struct DetectedObject {
    float distance;
    float angle;
    int type; // 0=car, 1=pedestrian, 2=bicycle, 3=obstacle
};

class EnvironmentAnalyzer {
public:
    EnvironmentAnalyzer();
    ~EnvironmentAnalyzer();
    
    void processEnvironment();
    int getDetectedObjectCount() const { return detected_objects.load(); }
    float getNearestObjectDistance() const { return nearest_object_distance.load(); }
    int getTrafficLightState() const { return traffic_light_state.load(); }

private:
    std::atomic<int> detected_objects{0};
    std::atomic<float> nearest_object_distance{100.0f};
    std::atomic<int> traffic_light_state{1}; // 0=red, 1=green, 2=yellow
    std::atomic<float> lane_deviation{0.0f};
    
    int cycle_count{0};
};
#pragma once
#include <atomic>
#include <vector>

struct Waypoint {
    float x, y;
    float speed_limit;
};

class PathPlanner {
public:
    PathPlanner();
    ~PathPlanner();
    
    void updatePath();
    int getWaypointCount() const { return waypoint_count.load(); }
    float getPathDistance() const { return total_path_distance.load(); }
    bool isPathValid() const { return path_valid.load(); }
    float getTargetSpeed() const { return target_speed.load(); }

private:
    std::atomic<int> waypoint_count{0};
    std::atomic<float> total_path_distance{0.0f};
    std::atomic<bool> path_valid{true};
    std::atomic<float> target_speed{50.0f};
    std::atomic<int> planning_cycles{0};
    
    int cycle_count{0};
};
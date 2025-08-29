#ifndef TYPES_H
#define TYPES_H

#include <atomic>

// Basic types similar to customer's environment
struct Position3D {
    float x, y, z;
    Position3D(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}
};

struct Motion {
    Position3D velocity;
    Position3D acceleration;
    float angular_velocity = 0.0f;
};

struct LaneInfo {
    int lane_id = 2;  // Current lane (1-4)
    int target_lane = 2;  // Target lane for lane change
    float offset_to_center = 0.0f;
};

struct TrafficLight {
    enum State { RED = 0, YELLOW = 1, GREEN = 2 };
    State state = GREEN;
    float time_remaining = 30.0f;
};

struct SpeedLimit {
    float limit = 60.0f;  // km/h
    float gradient = 0.0f;  // Road slope percentage
};

struct Vehicle {
    Position3D position;
    Motion motion;
    float mass = 1500.0f;  // kg
    bool is_ego = false;
};

// Global variables for monitoring (using atomic for thread safety)
extern std::atomic<float> ego_speed;
extern std::atomic<int> collision_risk;
extern std::atomic<int> current_lane;
extern std::atomic<bool> warning_active;
extern std::atomic<float> brake_pressure;

#endif // TYPES_H
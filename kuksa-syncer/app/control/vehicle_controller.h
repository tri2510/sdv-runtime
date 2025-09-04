#pragma once
#include <atomic>

class VehicleController {
public:
    VehicleController();
    ~VehicleController();
    
    void updateControl();
    void setTargetSpeed(float speed);
    void setTargetGear(int gear);
    
    float getThrottlePosition() const { return throttle_position.load(); }
    float getBrakeForce() const { return brake_force.load(); }
    float getSteeringAngle() const { return steering_angle.load(); }

private:
    std::atomic<float> throttle_position{0.2f};
    std::atomic<float> brake_force{0.0f};
    std::atomic<float> steering_angle{0.0f};
    
    float target_speed{50.0f};
    int target_gear{3};
    int cycle_count{0};
};
#ifndef FCW_CONTROLLER_H
#define FCW_CONTROLLER_H

#include "types.h"
#include "vehicle_system.h"
#include "environment.h"

class FCWController {
private:
    bool warning_system_enabled;
    float warning_threshold_distance;  // meters
    float critical_threshold_distance; // meters
    float last_warning_time;
    
public:
    FCWController();
    
    void initialize();
    void update(const VehicleSystem& vehicle_sys, const Environment& env, float dt);
    
    bool is_collision_imminent(const VehicleSystem& vehicle_sys) const;
    int calculate_collision_risk(const VehicleSystem& vehicle_sys) const;
    
    void enable_warning_system(bool enabled) { warning_system_enabled = enabled; }
    bool is_warning_system_enabled() const { return warning_system_enabled; }
    
private:
    void process_warning_logic(const VehicleSystem& vehicle_sys, float dt);
    void trigger_emergency_brake(const VehicleSystem& vehicle_sys);
    void suggest_lane_change(const VehicleSystem& vehicle_sys);
    
    float calculate_time_to_collision(const Vehicle& ego, const Vehicle& target) const;
    float calculate_safe_following_distance(float ego_speed) const;
};

#endif // FCW_CONTROLLER_H
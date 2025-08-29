#ifndef VEHICLE_SYSTEM_H
#define VEHICLE_SYSTEM_H

#include "types.h"
#include <vector>

class VehicleSystem {
private:
    Vehicle ego_vehicle;
    std::vector<Vehicle> surrounding_vehicles;
    LaneInfo lane_info;
    
public:
    VehicleSystem();
    
    void initialize();
    void update(float dt);
    void apply_brake(float pressure);
    void change_lane(int target_lane);
    
    const Vehicle& get_ego_vehicle() const { return ego_vehicle; }
    const std::vector<Vehicle>& get_surrounding_vehicles() const { return surrounding_vehicles; }
    const LaneInfo& get_lane_info() const { return lane_info; }
    
    void set_ego_speed(float speed);
    float get_distance_to_front_vehicle() const;
    
private:
    void update_surrounding_vehicles(float dt);
    void update_ego_vehicle(float dt);
    void generate_realistic_traffic();
};

#endif // VEHICLE_SYSTEM_H
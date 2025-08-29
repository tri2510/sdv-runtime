#ifndef ENVIRONMENT_H
#define ENVIRONMENT_H

#include "types.h"
#include <array>

class Environment {
private:
    std::array<TrafficLight, 4> traffic_lights;  // One per lane
    std::array<SpeedLimit, 4> speed_limits;      // One per lane
    float simulation_time;
    
public:
    Environment();
    
    void initialize();
    void update(float dt);
    
    const TrafficLight& get_traffic_light(int lane) const;
    const SpeedLimit& get_speed_limit(int lane) const;
    float get_simulation_time() const { return simulation_time; }
    
    void print_environment_status() const;
    
private:
    void update_traffic_lights(float dt);
    void simulate_realistic_environment();
};

#endif // ENVIRONMENT_H
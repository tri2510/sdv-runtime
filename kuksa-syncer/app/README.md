# Customer FCW ADAS System

This project implements a Forward Collision Warning (FCW) system based on customer requirements for a 4-lane highway scenario with comprehensive vehicle monitoring.

## Project Overview

Based on the customer specifications from `/customer-files/requirements/detail_envrionment.md`:

- **4-lane highway simulation** (Lane 1-4, ego vehicle in Lane 2 or 3)
- **Comprehensive vehicle environment** with front/rear/left/right vehicles
- **Infrastructure elements** including traffic lights, speed limits, road gradients
- **Two scenarios**: With/without warning system
- **Collision avoidance** through deceleration and lane change maneuvers

## Monitored Variables (20+ Variables)

### 🚗 Vehicle State Variables
- `ego_speed` (float) - Current vehicle speed in km/h
- `current_lane` (int) - Current lane position (1-4)
- `ego_acceleration` (float) - Vehicle acceleration in m/s²
- `steering_angle` (float) - Steering wheel angle in degrees

### ⚠️ FCW Warning System Variables
- `collision_risk` (int) - Collision probability percentage (0-100%)
- `warning_active` (bool) - FCW warning system status
- `critical_warning` (bool) - Critical collision warning flag
- `time_to_collision` (float) - Time to collision in seconds

### 🎛️ Vehicle Control Variables
- `brake_pressure` (float) - Brake application percentage (0-100%)
- `throttle_position` (float) - Accelerator pedal position (0-100%)
- `emergency_brake_active` (bool) - Emergency braking system status

### 🌍 Environment Variables
- `traffic_light_state` (int) - Traffic light status (0=Red, 1=Yellow, 2=Green)
- `speed_limit` (float) - Current speed limit in km/h
- `road_gradient` (float) - Road slope in degrees (uphill/downhill)
- `weather_condition_good` (bool) - Weather visibility impact

### 🚙 Surrounding Vehicle Variables
- `front_vehicle_distance` (float) - Distance to front vehicle in meters
- `front_vehicle_speed` (float) - Front vehicle speed in km/h
- `left_vehicle_distance` (float) - Distance to left lane vehicle
- `right_vehicle_distance` (float) - Distance to right lane vehicle

### 📡 V2X Communication Variables
- `v2x_connected` (bool) - V2X communication system status
- `received_warnings` (int) - Number of V2X warnings received
- `infrastructure_warning` (bool) - Infrastructure collision warning

## System Features

### 1. **Realistic FCW Collision Detection**
- Time-to-Collision (TTC) calculations
- Risk assessment based on distance and relative speed
- Progressive warning levels (info → warning → critical)

### 2. **Collision Avoidance Responses**
- **Scenario 1 (Without Warning)**: Natural collision progression
- **Scenario 2 (With Warning)**: Active collision avoidance through:
  - Emergency braking with variable pressure
  - Lane change maneuvers when safe
  - Speed adjustment based on traffic conditions

### 3. **Environmental Integration**
- Traffic light awareness affecting behavior
- Speed limit compliance
- Road gradient impact on braking distance
- Weather condition considerations

### 4. **V2X Communication Simulation**
- Infrastructure-to-vehicle warnings
- Communication reliability simulation
- Warning message processing

## Usage with Memory Monitoring

### Variables to Monitor:
```
ego_speed,collision_risk,current_lane,warning_active,brake_pressure,critical_warning,time_to_collision,front_vehicle_distance,v2x_connected,traffic_light_state
```

### Compilation:
```bash
g++ -g -O0 -std=c++11 -pthread main.cpp -o fcw_adas_system
```

### Expected Monitoring Output:
- **Real-time speed changes** as system responds to warnings
- **Collision risk fluctuations** from 0-100% based on traffic
- **Lane changes** from 2→1 or 2→3 during overtaking
- **Warning state transitions** from false→true during hazards
- **Brake pressure variations** during collision avoidance
- **V2X communication status** and warning counts

## Customer Requirements Compliance

✅ **4-lane environment** with ego vehicle in Lane 2/3  
✅ **Surrounding vehicles** in all directions with realistic movement  
✅ **Infrastructure elements** (traffic lights, speed limits, gradients)  
✅ **Two scenarios** implemented (with/without warning system)  
✅ **Collision avoidance** through deceleration and lane changes  
✅ **Real-time monitoring** of all critical system variables  

This project provides comprehensive testing of the C++ memory monitoring system with realistic automotive ADAS scenarios matching customer specifications.
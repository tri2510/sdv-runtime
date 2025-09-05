# ADAS System Simulation

Advanced Driver Assistance System simulation using direct G++ compilation.

## Monitored Variables
- `front_distance`: Distance to front vehicle (0-100m)
- `rear_distance`: Distance to rear vehicle (50m)
- `left_distance`: Distance to left side (15-25m)
- `right_distance`: Distance to right side (17-33m)
- `emergency_brake`: Emergency braking system status
- `lane_keep_assist`: Lane keeping assistance active
- `blind_spot_left`: Left blind spot detection
- `blind_spot_right`: Right blind spot detection
- `traffic_sign`: Traffic sign recognition (0-3)
- `adaptive_cruise_speed`: Adaptive cruise control speed

## Build System
Direct G++ compilation with C++17 standards

## Usage
```bash
g++ -std=c++17 -g -O0 -Wall -o adas_system main.cpp
./adas_system
```

## Expected Output
ADAS system simulation showing approaching vehicle scenario (0-15 cycles) followed by lane change scenario (15-30 cycles) with various safety systems activation.
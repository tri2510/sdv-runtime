# FCW ADAS Demo Project

This demo project simulates a Forward Collision Warning (FCW) system similar to customer requirements.

## Features

- Real-time vehicle position and motion monitoring
- Multi-lane environment simulation (4 lanes)
- Collision detection and warning system
- V2X communication simulation
- Traffic light and speed limit monitoring
- Shared memory integration for real-time variable monitoring

## Structure

- `src/` - Source files
- `include/` - Header files
- `CMakeLists.txt` - Build configuration
- `README.md` - This file

## Key Components

1. **Vehicle System**: Manages ego vehicle position and motion
2. **Environment**: Simulates traffic lights, speed limits, and surrounding vehicles
3. **FCW Logic**: Collision detection and warning algorithms
4. **V2X Communication**: Vehicle-to-infrastructure communication simulation

## Build Instructions

```bash
mkdir build
cd build
cmake ..
make
./fcw_demo
```

## Monitored Variables

The following variables can be monitored in real-time via shared memory:

- `ego_speed` - Current vehicle speed (km/h)
- `collision_risk` - Risk level (0-100)
- `current_lane` - Lane number (1-4)
- `warning_active` - Warning system status (0/1)
- `brake_pressure` - Brake system pressure (0-100)
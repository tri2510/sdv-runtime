# Autonomous Vehicle System

A complex, multi-module C++ project simulating an autonomous vehicle control system for testing the SDV runtime monitoring mechanism.

## Project Structure

```
autonomous-vehicle-system/
├── main.cpp                 # Main application entry point
├── sensors/                 # Sensor management subsystem
│   ├── sensor_manager.h
│   └── sensor_manager.cpp
├── control/                 # Vehicle control subsystem
│   ├── vehicle_controller.h
│   └── vehicle_controller.cpp
├── perception/              # Environment perception subsystem
│   ├── environment_analyzer.h
│   └── environment_analyzer.cpp
├── planning/                # Path planning subsystem
│   ├── path_planner.h
│   └── path_planner.cpp
├── utils/                   # Utility classes
│   ├── logger.h
│   └── logger.cpp
├── CMakeLists.txt          # Build configuration
└── README.md               # This file
```

## Monitored Variables

The system exposes the following atomic variables for SDV runtime monitoring:

### Global Variables (main.cpp)
- `vehicle_speed` (float) - Current vehicle speed in km/h
- `current_gear` (int) - Current transmission gear (1-5)
- `engine_rpm` (float) - Engine RPM
- `autonomous_mode` (bool) - Autonomous driving mode status
- `fuel_level` (float) - Fuel level percentage
- `active_sensors` (int) - Number of active sensors
- `cpu_temperature` (float) - System CPU temperature

### Subsystem Variables
Each subsystem contains additional atomic variables that change during execution:
- **Sensors**: LIDAR range, camera distance, radar speed, GPS status
- **Control**: Throttle position, brake force, steering angle
- **Perception**: Detected objects, nearest object distance, traffic light state
- **Planning**: Waypoint count, path distance, path validity, target speed
- **Utils**: Log counts, error counts, warning counts

## Features

- **Multi-threaded Architecture**: Uses std::thread for concurrent operations
- **Realistic Simulation**: Variables change with automotive-realistic patterns
- **Complex Interactions**: Subsystems interact and affect each other's state
- **Comprehensive Logging**: Detailed logging with atomic counters
- **Build System**: CMake-based build with proper debug symbol generation

## Building

```bash
cd autonomous-vehicle-system
mkdir build && cd build
cmake ..
make
```

## Running

```bash
./autonomous_vehicle_system
```

The system runs for 60 control cycles (30 seconds), updating all monitored variables with realistic automotive data patterns.

## SDV Runtime Integration

This project is specifically designed to test the SDV runtime monitoring mechanism with:
- Complex multi-file project structure
- Multiple atomic variables across different modules
- Realistic data patterns that change over time
- External symbol references between compilation units
- CMake build system integration
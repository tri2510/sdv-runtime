# Automotive Safety System - Simple C++ Project

## Overview

A simple single-file C++ project demonstrating real-time monitoring of automotive variables using atomic types. This project is designed to work with the SDV runtime C++ memory monitoring system.

## Features

- Single-file implementation for easy compilation
- Atomic variables for thread-safe monitoring
- Simulates realistic automotive data:
  - Vehicle speed (30-77.5 km/h)
  - Lane position (1-3)
  - Steering angle (-15° to +15°)
  - Collision risk (0.0-1.0)
  - Incrementing counter (tri_value)

## Variables Monitored

```cpp
std::atomic<float> ego_speed{0.0f};      // Vehicle speed in km/h
std::atomic<int> current_lane{2};        // Current lane (1, 2, or 3)
std::atomic<float> steering_angle{0.0f}; // Steering angle in degrees
std::atomic<float> collision_risk{0.0f}; // Risk level (0.0 to 1.0)
std::atomic<int> tri_value{3};          // Test counter
```

## Building

### Using Make
```bash
# Standard build with debug symbols
make

# Release build with optimizations
make release

# Debug build with address sanitizer
make debug

# Clean build artifacts
make clean
```

### Using g++ directly
```bash
g++ -std=c++17 -g -pthread -o automotive_safety main.cpp
```

## Running

```bash
# Run directly
./automotive_safety

# Run with make
make run
```

## Monitoring with SDV Runtime

From the kuksa-syncer directory:

```bash
# Monitor all variables with default settings
python3 auto_memory_monitor.py

# Monitor specific variables with custom interval
python3 auto_memory_monitor.py -v "ego_speed,tri_value" -i 0.1

# Verbose monitoring for debugging
python3 auto_memory_monitor.py --verbose
```

## Expected Output

### Program Output:
```
Automotive Safety System - Memory Monitoring Test
Monitoring variables: ego_speed, current_lane, steering_angle, collision_risk
Iteration 0: ego_speed=30km/h, current_lane=1, steering_angle=-15°, collision_risk=0
tri_value=4
Iteration 1: ego_speed=32.5km/h, current_lane=2, steering_angle=-12°, collision_risk=0
tri_value=5
...
```

### Monitoring Output:
```
[Auto-Report #1] Variables: {'ego_speed': 30.0, 'current_lane': 1, 'tri_value': 4}
[Auto-Report #2] Variables: {'ego_speed': 32.5, 'current_lane': 2, 'tri_value': 5}
...
```

## Simulation Details

The program runs for 20 iterations with 1-second intervals, simulating:

1. **Speed variations**: Increases from 30 to 77.5 km/h
2. **Lane changes**: Cycles through lanes 1, 2, and 3
3. **Steering adjustments**: Varies from -15° to +15° in steps
4. **Risk assessment**: Increases after iteration 10
5. **Counter increment**: tri_value increases by 1 each iteration

## Use Cases

- Testing memory monitoring systems
- Demonstrating atomic variable usage
- Simulating automotive telemetry
- Debugging SDV runtime integration
- Performance testing of monitoring tools

## Notes

- Requires C++17 or later
- Uses pthread for threading support
- Compiled with debug symbols (-g) for monitoring
- Runs for approximately 20 seconds total
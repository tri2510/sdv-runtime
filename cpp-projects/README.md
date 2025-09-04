# C++ Projects for SDV Runtime Testing

This directory contains various C++ projects designed to test and demonstrate the SDV runtime memory monitoring capabilities.

## Project Structure

```
cpp-projects/
├── automotive-safety-system/     # Simple single-file project
│   ├── main.cpp                 # Automotive safety monitoring demo
│   ├── Makefile                  # Build configuration
│   └── README.md                 # Project documentation
│
└── autonomous-vehicle-system/   # Complex multi-file CMake project
    ├── main.cpp                  # Main entry point
    ├── CMakeLists.txt           # CMake build configuration
    ├── control/                 # Vehicle control subsystem
    │   ├── vehicle_controller.cpp
    │   └── vehicle_controller.h
    ├── perception/              # Environment perception subsystem
    │   ├── environment_analyzer.cpp
    │   └── environment_analyzer.h
    ├── planning/                # Path planning subsystem
    │   ├── path_planner.cpp
    │   └── path_planner.h
    ├── sensors/                 # Sensor management subsystem
    │   ├── sensor_manager.cpp
    │   └── sensor_manager.h
    └── utils/                   # Utility functions
        ├── logger.cpp
        └── logger.h
```

## Projects Overview

### 1. Automotive Safety System (Simple)
- **Type**: Single-file C++ project
- **Build**: Makefile-based
- **Variables**: 5 atomic variables (ego_speed, current_lane, steering_angle, collision_risk, tri_value)
- **Use Case**: Quick testing, simple demonstrations, debugging

### 2. Autonomous Vehicle System (Complex)
- **Type**: Multi-file C++ project with modular architecture
- **Build**: CMake-based
- **Variables**: 7 atomic variables (vehicle_speed, current_gear, engine_rpm, etc.)
- **Use Case**: Production-like testing, complex scenarios, CMake integration

## Building Projects

### Simple Project (Makefile)
```bash
cd automotive-safety-system
make              # Standard build
make release      # Optimized build
make debug        # Debug with sanitizers
make run          # Build and run
```

### Complex Project (CMake)
```bash
cd autonomous-vehicle-system
mkdir build && cd build
cmake ..
make
./autonomous_vehicle_system
```

## Monitoring with SDV Runtime

From the kuksa-syncer directory:

```bash
# Monitor simple project
python3 auto_memory_monitor.py --variables "ego_speed,tri_value"

# Monitor complex project with custom settings
python3 auto_memory_monitor.py --interval 0.1 --duration 60

# Verbose monitoring for debugging
python3 auto_memory_monitor.py --verbose
```

## Adding New Projects

To add a new C++ test project:

1. Create a new directory under `cpp-projects/`
2. Add your C++ source files
3. Create either a Makefile (simple) or CMakeLists.txt (complex)
4. Add atomic variables for monitoring
5. Include a README.md with project details
6. Test with the monitoring system

## Requirements

- C++17 or later
- g++ or clang++ compiler
- CMake 3.10+ (for complex projects)
- pthread support
- Debug symbols (-g flag) for monitoring

## Notes

- All projects use `std::atomic` variables for thread-safe monitoring
- Binaries must be compiled with debug symbols (-g) for proper symbol resolution
- The monitoring system automatically detects variables from source code
- Both simple (g++) and complex (CMake) build systems are supported
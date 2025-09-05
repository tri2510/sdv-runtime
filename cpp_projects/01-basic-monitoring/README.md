# Basic Memory Monitor

Simple C++ project demonstrating basic memory monitoring with CMake build system.

## Monitored Variables
- `counter`: Integer counter (0-49)
- `sensor_value`: Float sensor reading (25.5-30.4)
- `system_active`: Boolean system status

## Build System
CMake with modern C++17 standards

## Usage
```bash
mkdir build && cd build
cmake ..
make
./basic_monitor
```

## Expected Output
Real-time monitoring of three atomic variables showing different data types.
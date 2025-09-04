# Complex Project Monitoring Test

This directory contains tests for monitoring a complex, multi-file C++ project with hierarchical structure and CMake build system.

## Files

- **`test_complex_project_monitoring.py`** - Complete test of autonomous vehicle system monitoring

## Project Under Test

**Target**: `cpp-projects/autonomous-vehicle-system/`

A complex C++ project featuring:
- **Multi-file structure**: 12+ source and header files across 5 subdirectories
- **CMake build system**: Professional build configuration with debug symbols
- **Multiple subsystems**: Sensors, Control, Perception, Planning, Utilities
- **Complex interactions**: Inter-module dependencies and shared variables
- **Real-world simulation**: Autonomous vehicle control system

## Monitored Variables

### Primary Variables (7)
- `vehicle_speed` - Current speed in km/h
- `current_gear` - Transmission gear (1-5)  
- `engine_rpm` - Engine RPM
- `autonomous_mode` - Autonomous driving status
- `fuel_level` - Fuel percentage
- `active_sensors` - Active sensor count
- `cpu_temperature` - System temperature

### Subsystem Variables (20+)
- **Sensors**: LIDAR range, camera distance, radar speed, GPS status
- **Control**: Throttle position, brake force, steering angle
- **Perception**: Object detection, traffic lights, lane deviation
- **Planning**: Waypoints, path distance, target speed
- **Logging**: Log counts by severity level

## Test Process

1. **Project Discovery**: Scans complex project directory structure
2. **Tree Generation**: Creates kit server tree format from all source files
3. **Project Creation**: Uses ProjectUtils to recreate project in app directory
4. **CMake Build**: Configures and builds using CMake + make
5. **Variable Detection**: Auto-detects variables from multi-file sources
6. **Live Monitoring**: Monitors variables during complex system execution
7. **Validation**: Verifies 75%+ success rate over 20 readings

## Expected Results

- **Build Success**: CMake configuration and compilation without errors
- **Variable Detection**: 7+ primary variables plus subsystem variables detected
- **Live Monitoring**: Real-time data updates from running autonomous vehicle simulation
- **Data Validation**: Realistic automotive data patterns (speeds, RPM, gear changes)
- **System Stability**: Process runs for full duration without crashes

## Usage

```bash
# Run from sdv-runtime root directory
python3 test/13-complex-project-monitoring/test_complex_project_monitoring.py
```

## Success Criteria

- ✅ CMake build system integration
- ✅ Multi-file project compilation  
- ✅ Variable detection across source files
- ✅ 15/20 successful monitoring readings
- ✅ Realistic automotive data patterns
- ✅ No process crashes or build failures

## Benefits

- **Real-world testing**: Complex project structure like production systems
- **Build system validation**: CMake integration proves professional workflow support
- **Scalability proof**: Demonstrates monitoring works beyond simple single-file projects
- **Subsystem verification**: Tests variable detection across multiple compilation units
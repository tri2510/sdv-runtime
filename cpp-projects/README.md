# Comprehensive C++ Variable Monitoring Test Suite

This test suite contains 5 different C++ projects designed to thoroughly test the universal variable monitoring system across various project structures, build systems, and variable types commonly found in automotive and embedded software development.

## Test Projects Overview

### 1. **01-basic-types** - Fundamental Types Test
- **Purpose**: Test monitoring of all fundamental C++ atomic types
- **Build System**: Simple g++ with build.sh
- **Key Features**:
  - All fundamental types: int8_t, uint64_t, float, double, bool, char, etc.
  - Realistic automotive variable names and ranges
  - Simple single-file architecture
- **Variables**: ~20 fundamental type variables
- **Update Rate**: 2Hz (500ms intervals)

### 2. **02-cmake-structured** - CMake Multi-Directory Project
- **Purpose**: Test CMake-based builds with multiple source files and classes
- **Build System**: CMake with separate src/, include/ directories
- **Key Features**:
  - VehicleController and SensorManager classes
  - std::atomic variables for thread safety
  - Professional automotive system simulation
  - GPS, IMU, TPMS, BMS systems
- **Variables**: ~30 atomic variables across classes
- **Update Rate**: 1.3Hz (750ms intervals)

### 3. **03-makefile-build** - Traditional Makefile with Namespaces
- **Purpose**: Test Makefile builds and namespace variable detection
- **Build System**: Traditional Makefile
- **Key Features**:
  - ADAS systems: FCW (Forward Collision Warning), LKA (Lane Keeping Assist), ACC (Adaptive Cruise Control)
  - Namespace organization (FCW::, LKA::, ACC::)
  - Realistic automotive safety system logic
- **Variables**: ~20 namespaced variables
- **Update Rate**: 1.7Hz (600ms intervals)

### 4. **04-complex-structures** - Complex Nested Namespaces
- **Purpose**: Test deep namespace hierarchies and complex class structures
- **Build System**: Simple g++ with build.sh
- **Key Features**:
  - Multi-level namespaces: Vehicle::Monitoring::, Vehicle::Powertrain::, Vehicle::Safety::
  - SystemMonitor, EngineSystem, TransmissionSystem, EmergencySystems classes
  - Realistic automotive subsystem interactions
  - Fire suppression, airbag, rollover detection systems
- **Variables**: ~40 variables in nested namespaces
- **Update Rate**: 2Hz (500ms intervals)

### 5. **05-embedded-style** - Embedded ECU System
- **Purpose**: Test embedded automotive programming patterns
- **Build System**: Simple g++ with build.sh
- **Key Features**:
  - Fixed-point arithmetic (Q15, Q31 notation)
  - Bit-packed register structures
  - CAN/LIN communication counters
  - Diagnostic trouble codes (DTCs)
  - RTOS-style timing and memory management
  - Typical ECU variable patterns
- **Variables**: ~25 embedded-style variables
- **Update Rate**: 4Hz (250ms intervals) - typical ECU rate

## Current Limitations

**Note**: Array variable monitoring is not yet supported. The monitoring system currently supports individual scalar variables (int, char, float, double, bool) and their atomic variants. Array support is planned for future development.

## Build Systems Tested

1. **Direct g++ compilation** (Projects 1, 4, 5)
2. **CMake** (Project 2)
3. **Traditional Makefile** (Project 3)

All projects compile with `-g -O0` flags for optimal debugging symbol generation.

## Variable Types Tested

### Fundamental Types
- `int8_t`, `int16_t`, `int32_t`, `int64_t`
- `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`
- `float`, `double`
- `bool`
- `char`
- `int`, `long`, `short`

### Advanced Types
- `std::atomic<T>` for thread-safe variables
- Fixed-point types (Q15, Q31 notation)
- Bit-packed structures
- Arrays of atomic variables
- Namespaced variables

## Running the Test Suite

### Prerequisites
```bash
# Ensure you have the required tools
sudo apt-get install build-essential cmake python3
```

### Quick Start
```bash
cd /path/to/cpp-projects
./run_comprehensive_tests.py
```

### Manual Testing
```bash
# Test individual projects
cd 01-basic-types
./build.sh
./basic_types_monitor

# CMake project
cd 02-cmake-structured  
./build.sh
cd build && ./vehicle_systems

# Makefile project
cd 03-makefile-build
make
./adas_monitor
```

## Test Runner Features

The `run_comprehensive_tests.py` script provides:

- **Automated Building**: Builds all 6 projects using their respective build systems
- **Smart Adaptive Syncer Integration**: Automatically starts the variable monitoring system
- **Concurrent Testing**: Runs projects while monitoring variables in real-time
- **Validation**: Verifies that expected variables are detected and monitored
- **Comprehensive Reporting**: Generates detailed success/failure reports
- **Process Management**: Clean shutdown of all processes

### Expected Output
```
[16:30:15] INFO: Starting Comprehensive C++ Variable Monitoring Test Suite
[16:30:15] INFO: Starting smart adaptive syncer...
[16:30:17] INFO: Syncer started successfully

============================================================
TESTING: Basic Types Monitor (01-basic-types)
============================================================
[16:30:18] INFO: Building Basic Types Monitor...
[16:30:19] INFO: Build successful: Basic Types Monitor
[16:30:19] INFO: Starting test: Basic Types Monitor
[16:30:19] INFO: Running Basic Types Monitor for 20 seconds...
[16:30:39] INFO: Test completed: Basic Types Monitor
[16:30:39] INFO: Validating monitoring for Basic Types Monitor
[16:30:39] INFO: Variable detection: 6/6 (100.0%)

... (continues for all 6 projects)

============================================================
COMPREHENSIVE TEST SUITE RESULTS
============================================================
Total Projects: 5
Successful Builds: 5/5
Successful Tests: 5/5
Successful Monitoring: 5/5

DETAILED RESULTS:
------------------------------------------------------------
✓ Basic Types Monitor
    Build: ✓
    Test:  ✓
    Monitor: ✓
✓ CMake Vehicle Systems
    Build: ✓
    Test:  ✓
    Monitor: ✓

... (all projects)

============================================================
OVERALL RESULT: SUCCESS - Universal monitoring system validated!
============================================================
```

## Integration with Smart Adaptive Syncer

This test suite is specifically designed to work with the smart adaptive syncer system located in `../kuksa-syncer/`. The syncer:

1. **Auto-detects** C++ processes with debugging symbols
2. **Parses** variable names, types, and memory locations
3. **Monitors** variable changes in real-time
4. **Adapts** monitoring frequency based on update patterns
5. **Reports** variable statistics and behavior patterns

## Automotive Use Cases Covered

1. **Basic Vehicle Data**: Speed, RPM, temperature, fuel level
2. **Advanced Driver Assistance**: FCW, LKA, ACC systems
3. **Vehicle Dynamics**: Wheel speeds, acceleration, yaw rate
4. **Engine Management**: Fuel injection, ignition timing, turbo control
5. **Safety Systems**: Airbags, rollover detection, fire suppression
6. **Embedded Control**: Fixed-point arithmetic, bit manipulation, CAN communication
7. **High-Frequency Control**: PID loops, real-time sensor processing

## Performance Characteristics

| Project | Variables | Update Rate | Duration | Memory Pattern |
|---------|-----------|-------------|----------|----------------|
| 01-basic-types | ~20 | 2Hz | 30s | Steady updates |
| 02-cmake-structured | ~30 | 1.3Hz | 30s | Class-based |
| 03-makefile-build | ~20 | 1.7Hz | 30s | Namespace groups |
| 04-complex-structures | ~40 | 2Hz | 30s | Nested hierarchies |
| 05-embedded-style | ~25 | 4Hz | 20s | Fixed-point/packed |

## Success Criteria

The test suite validates:

1. **Build Success**: All projects compile without errors
2. **Runtime Success**: All executables run without crashes
3. **Variable Detection**: ≥80% of expected variables are detected
4. **Monitoring Accuracy**: Variables are correctly tracked and updated
5. **Performance**: System handles high-frequency updates without degradation

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   sudo apt-get install build-essential cmake python3 gdb
   ```

2. **Permission Issues**
   ```bash
   chmod +x *.sh
   chmod +x run_comprehensive_tests.py
   ```

3. **Syncer Not Starting**
   - Check if `../kuksa-syncer/syncer.py` exists
   - Verify Python dependencies are installed
   - Ensure proper permissions on syncer directory

### Debug Mode
```bash
# Run individual projects with debug output
cd 01-basic-types
gdb ./basic_types_monitor
(gdb) run
```

## Files Structure
```
cpp-projects/
├── 01-basic-types/
│   ├── basic_types_monitor.cpp
│   └── build.sh
├── 02-cmake-structured/
│   ├── CMakeLists.txt
│   ├── build.sh
│   ├── include/
│   │   ├── VehicleController.h
│   │   └── SensorManager.h
│   └── src/
│       ├── main.cpp
│       ├── VehicleController.cpp
│       └── SensorManager.cpp
├── 03-makefile-build/
│   ├── adas_systems.cpp
│   └── Makefile
├── 04-complex-structures/
│   ├── complex_vehicle_system.cpp
│   └── build.sh
├── 05-embedded-style/
│   ├── embedded_ecu_system.cpp
│   └── build.sh
├── run_comprehensive_tests.py
└── README.md
```

This comprehensive test suite ensures the universal monitoring system works reliably across all common C++ automotive and embedded programming patterns.
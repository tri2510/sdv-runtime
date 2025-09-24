# SDV C++ Global Variable Tracing Guide

## Overview

This guide explains how to set up C++ projects with **SDV (Software Defined Vehicle) minimal types** for reliable global variable tracing using ptrace monitoring. The system supports automatic variable detection and real-time memory reading for automotive applications.

## Supported SDV Minimal Types

### ✅ Supported Types (SDV Minimal Set)

Our tracing system supports **only** these 5 basic types to ensure simplicity, portability, and SDV signal compatibility:

| Type | Size | Usage | Example |
|------|------|-------|---------|
| `int` | 4 bytes | Integer values, counters, IDs | `int engine_rpm = 2500;` |
| `char` | 1 byte | Small integers (-128 to +127), status codes | `char gear_position = 3;` |
| `float` | 4 bytes | Floating-point values, measurements | `float temperature = 23.5f;` |
| `double` | 8 bytes | High-precision floating-point | `double gps_latitude = 52.520008;` |
| `bool` | 1 byte | Boolean flags, status indicators | `bool engine_running = true;` |

### ✅ Atomic Variants (Thread-Safe)

For multi-threaded applications, use atomic versions:

```cpp
std::atomic<int> atomic_counter{0};
std::atomic<char> atomic_status{65};
std::atomic<float> atomic_temperature{23.5f};
std::atomic<double> atomic_precision{3.14159};
std::atomic<bool> atomic_enabled{true};
```

### ❌ NOT Supported (Removed from SDV)

These types are **not supported** and will be ignored by the tracing system:

- `int8_t`, `uint8_t`, `int16_t`, `uint16_t`, `int32_t`, `uint32_t`, `int64_t`, `uint64_t`
- `size_t`, `intptr_t`, `uintptr_t`
- Custom typedefs ending in `_t`
- Complex types (structs, classes, arrays, pointers)

## Project Setup Guidelines

### 1. Basic Project Structure

```
my_vehicle_project/
├── src/
│   └── main.cpp              # Your main C++ file
├── build.sh                  # Build script
└── CMakeLists.txt           # Or Makefile
```

### 2. Global Variable Declaration

**✅ CORRECT - Global scope variables:**

```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// SDV Global Variables (regular types)
int vehicle_speed = 0;           // Current speed in km/h
char current_gear = 1;           // Gear position (1-8)
float fuel_level = 85.5f;        // Fuel level percentage
double gps_latitude = 52.520008; // GPS coordinates
bool engine_running = true;      // Engine status

// SDV Global Variables (atomic for thread safety)
std::atomic<int> engine_rpm{2500};
std::atomic<char> warning_level{0};
std::atomic<float> oil_temperature{90.5f};
std::atomic<double> trip_distance{0.0};
std::atomic<bool> abs_active{false};

void updateVehicleState() {
    // Update your variables here
    vehicle_speed = 60;
    engine_rpm.store(3000);
    // ...
}

int main() {
    while (true) {
        updateVehicleState();

        // Print current values
        std::cout << "Speed: " << vehicle_speed << " km/h" << std::endl;
        std::cout << "RPM: " << engine_rpm.load() << std::endl;

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    return 0;
}
```

**❌ INCORRECT examples:**

```cpp
// ❌ Wrong: Local variables (not traceable)
int main() {
    int local_speed = 60;  // Cannot be traced - not global
    return 0;
}

// ❌ Wrong: Using _t types (not supported)
std::atomic<uint32_t> bad_counter{0};  // Use std::atomic<int> instead
int16_t bad_temperature = 25;          // Use char or int instead

// ❌ Wrong: Complex types (not supported)
struct VehicleData {  // Structs not supported
    int speed;
    float fuel;
};
```

### 3. Build Configuration

**Essential compiler flags:**

```bash
g++ -std=c++17 -pthread -O0 -g -o my_app main.cpp
```

**Explanation:**
- `-std=c++17`: C++17 standard (required for atomic support)
- `-pthread`: Thread support (required for atomic variables)
- `-O0`: No optimization (preserves variable layout)
- `-g`: Debug symbols (required for symbol detection)

### 4. Example Build Scripts

**Simple build.sh:**
```bash
#!/bin/bash
echo "Building Vehicle Monitor..."
g++ -std=c++17 -pthread -O0 -g -o vehicle_monitor main.cpp
echo "Build successful! Run with: ./vehicle_monitor"
```

**CMakeLists.txt:**
```cmake
cmake_minimum_required(VERSION 3.10)
project(VehicleMonitor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -g -pthread")

add_executable(vehicle_monitor src/main.cpp)
```

**Makefile:**
```makefile
CXX = g++
CXXFLAGS = -std=c++17 -O0 -g -pthread -Wall -Wextra
TARGET = vehicle_monitor
SOURCES = main.cpp

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)
```

## Namespace Support

The tracing system supports namespaced variables:

```cpp
namespace Vehicle {
    std::atomic<int> engine_rpm{0};
    std::atomic<float> speed{0.0f};
}

namespace Safety {
    std::atomic<bool> abs_active{false};
    std::atomic<bool> esp_active{false};
}
```

Both `Vehicle::engine_rpm` and simple `engine_rpm` will be detected.

## Testing Your Setup

### 1. Verify Compilation

```bash
./build.sh
# Should compile without errors
```

### 2. Test Variable Detection

```bash
# Run the detection test
python3 ../kuksa-syncer/auto_variable_detector.py

# Expected output:
# ✅ Detected X SDV variables from source
# ✅ Found Y variables with binary symbols
# 📊 Success rate: Z%
```

### 3. Run Your Application

```bash
./your_app
# Your app should run and display variable values
```

## Complete Working Example

Here's a minimal complete example:

**main.cpp:**
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <unistd.h>

// SDV Global Variables - ONLY use these 5 types
std::atomic<int> vehicle_speed{0};
std::atomic<char> gear_position{1};
std::atomic<float> engine_temperature{85.5f};
std::atomic<double> fuel_efficiency{15.2};
std::atomic<bool> lights_on{false};

// Regular (non-atomic) global variables also supported
int trip_odometer = 0;
char drive_mode = 'D';
float oil_pressure = 45.2f;
double total_distance = 1234.56;
bool parking_brake = false;

void simulateVehicle() {
    static int cycle = 0;
    cycle++;

    // Update atomic variables
    vehicle_speed.store(50 + (cycle % 30));
    gear_position.store(1 + (cycle % 6));
    engine_temperature.store(85.0f + (cycle % 20));
    fuel_efficiency.store(15.0 + (cycle % 5) * 0.1);
    lights_on.store((cycle % 10) < 5);

    // Update regular variables
    trip_odometer += cycle;
    drive_mode = (cycle % 3 == 0) ? 'P' : 'D';
    oil_pressure = 40.0f + (cycle % 15);
    total_distance += 0.1;
    parking_brake = (cycle % 20) == 0;
}

void printStatus() {
    std::cout << "=== Vehicle Status ===" << std::endl;
    std::cout << "Speed: " << vehicle_speed.load() << " km/h" << std::endl;
    std::cout << "Gear: " << (int)gear_position.load() << std::endl;
    std::cout << "Engine Temp: " << engine_temperature.load() << "°C" << std::endl;
    std::cout << "Fuel Efficiency: " << fuel_efficiency.load() << " L/100km" << std::endl;
    std::cout << "Lights: " << (lights_on.load() ? "ON" : "OFF") << std::endl;
    std::cout << "Trip: " << trip_odometer << " km" << std::endl;
    std::cout << "PID: " << getpid() << std::endl << std::endl;
}

int main() {
    std::cout << "SDV Vehicle Monitor Starting..." << std::endl;
    std::cout << "Monitoring 10 global variables (5 atomic + 5 regular)" << std::endl;
    std::cout << "PID: " << getpid() << std::endl;

    for (int i = 0; i < 30; i++) {
        simulateVehicle();
        printStatus();
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    return 0;
}
```

**build.sh:**
```bash
#!/bin/bash
echo "Building SDV Vehicle Monitor..."
g++ -std=c++17 -pthread -O0 -g main.cpp -o vehicle_monitor
echo "✅ Build successful! Run with: ./vehicle_monitor"
```

## Best Practices

### ✅ DO:
- Use only SDV minimal types (`int`, `char`, `float`, `double`, `bool`)
- Declare variables in global scope
- Use atomic variants for thread safety
- Include debug symbols (`-g` flag)
- Disable optimization (`-O0` flag)
- Use meaningful variable names
- Group related variables in namespaces

### ❌ DON'T:
- Use `_t` suffix types (`uint32_t`, `int16_t`, etc.)
- Declare variables in local scope or inside functions
- Use complex types (structs, arrays, pointers)
- Enable aggressive optimization
- Forget thread synchronization for shared variables

## Troubleshooting

### Problem: Variables not detected
**Solution:** Ensure variables are global and use only SDV minimal types.

### Problem: Compilation errors
**Solution:** Check compiler flags include `-std=c++17 -pthread -O0 -g`.

### Problem: Binary symbols not found
**Solution:** Make sure debug symbols are included (`-g` flag) and optimization is disabled (`-O0`).

### Problem: Thread safety issues
**Solution:** Use `std::atomic<>` variants for variables accessed by multiple threads.

## Integration with SDV Runtime

Once your C++ project follows this guide:

1. **Build** your application with correct flags
2. **Run** your application (it will display its PID)
3. **Launch** the SDV tracing system pointing to your binary
4. **Monitor** real-time variable values via ptrace

The tracing system will automatically:
- Detect all SDV minimal type variables
- Resolve their memory addresses
- Provide real-time monitoring
- Handle both atomic and regular variables
- Support namespaced variables

## Example Projects

See the `cpp-projects/` directory for complete working examples:

- `01-basic-types/` - Simple SDV types demonstration
- `02-cmake-structured/` - CMake-based vehicle system
- `03-makefile-build/` - ADAS systems with namespaces
- `04-complex-structures/` - Complex vehicle monitoring
- `05-embedded-style/` - ECU-style embedded system
- `06-matlab-style/` - MATLAB-style controller patterns
- `07-simulink-blocks/` - Simulink block execution model

All examples follow this guide and work with the SDV tracing system.

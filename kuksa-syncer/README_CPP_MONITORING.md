# C++ Memory Monitoring System for SDV Runtime

## Overview

This system provides automatic detection and real-time monitoring of C++ atomic variables in Software Defined Vehicle (SDV) applications. It uses ptrace-based memory reading to monitor live variable values without modifying the source code, making it ideal for automotive system monitoring and debugging.

## Key Features

- **Automatic Variable Detection**: Automatically detects `std::atomic` variables in C++ source code
- **Real-time Monitoring**: Monitors variable values in running processes with configurable intervals (0.1s default)
- **Dynamic Binary Support**: Works with both simple g++ binaries and CMake-built projects
- **ELF Address Resolution**: Dynamically detects data section addresses for accurate memory reading
- **Configurable Parameters**: Command-line arguments for interval, duration, and report limits
- **Multi-file Project Support**: Handles complex C++ projects with multiple source files

## Architecture

### Components

1. **`auto_variable_detector.py`**: Core variable detection and memory reading
   - `AutoVariableDetector`: Parses C++ source to find atomic variables
   - `SmartMemoryReader`: Reads process memory using ptrace/proc

2. **`auto_memory_monitor.py`**: Monitoring orchestration
   - Process management and lifecycle
   - Configurable monitoring loops
   - Variable filtering and reporting

3. **`project_utils.py`**: Project structure handling
   - Multi-file project creation
   - CMake build system integration

## Installation

### Prerequisites

```bash
# Required system packages
sudo apt-get install build-essential g++ cmake python3-pip

# Python dependencies
pip3 install asyncio pathlib
```

## Usage

### Basic Monitoring

```bash
# Monitor with default settings (0.1s interval, 5 min duration)
python3 auto_memory_monitor.py

# Monitor specific variables
python3 auto_memory_monitor.py --variables "ego_speed,tri_value"
```

### Advanced Configuration

```bash
# Real-time monitoring (50ms interval) for 1 minute
python3 auto_memory_monitor.py --interval 0.05 --duration 60

# Conservative monitoring (2s interval) for 10 minutes
python3 auto_memory_monitor.py -i 2 -d 600 -m 50000

# Verbose debugging output
python3 auto_memory_monitor.py --verbose
```

### Command-Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--interval` | `-i` | 0.1 | Monitoring interval in seconds |
| `--duration` | `-d` | 300 | Maximum duration in seconds |
| `--max-reports` | `-m` | 10000 | Maximum number of reports |
| `--variables` | `-v` | "" | Comma-separated variables (empty=all) |
| `--verbose` | | False | Enable verbose debugging output |

## Supported Variable Types

The system automatically detects and monitors:

- `std::atomic<int>` - Integer values
- `std::atomic<float>` - Floating-point values  
- `std::atomic<bool>` - Boolean flags
- `std::atomic<double>` - Double precision (future)

### Example C++ Code

```cpp
#include <atomic>
#include <thread>
#include <chrono>

// These variables will be automatically detected and monitored
std::atomic<float> ego_speed{0.0f};
std::atomic<int> current_lane{2};
std::atomic<float> steering_angle{0.0f};
std::atomic<bool> autonomous_mode{false};

int main() {
    // Simulate automotive system
    for (int i = 0; i < 100; i++) {
        ego_speed = 30.0f + i * 0.5f;
        current_lane = (i % 3) + 1;
        steering_angle = -15.0f + (i % 30);
        autonomous_mode = (i > 50);
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    return 0;
}
```

## Technical Implementation

### Memory Address Resolution

The system uses a multi-step process to resolve variable addresses:

1. **Source Parsing**: Extract variable declarations from C++ code using regex
2. **Symbol Table**: Use `nm` to get symbol addresses from compiled binary
3. **ELF Analysis**: Use `readelf` to find data section start address
4. **Runtime Mapping**: Read `/proc/[pid]/maps` to get runtime memory layout
5. **Address Calculation**: `runtime_address = base_address + (symbol_offset - elf_data_start)`

### Dynamic ELF Detection

The system dynamically detects ELF data section layout:
- Simple g++ binaries: Data section typically starts at `0x4000`
- CMake binaries: Data section may start at `0x8000`
- Automatic detection via `readelf -S [binary]`

### Memory Reading Methods

Two approaches with automatic fallback:

1. **Primary**: `/proc/[pid]/mem` direct reading (fast, preferred)
2. **Fallback**: `ptrace(PTRACE_PEEKDATA)` with process pause/continue

## Build Systems Support

### Simple G++ Build
```bash
g++ -g -o app main.cpp
```

### CMake Projects
```cmake
cmake_minimum_required(VERSION 3.10)
project(AutonomousVehicle)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Debug)

add_executable(autonomous_vehicle_system
    main.cpp
    sensors/sensor_manager.cpp
    control/vehicle_controller.cpp
)

target_compile_options(autonomous_vehicle_system PRIVATE -g)
```

## Testing

### Run Test Suite

```bash
# Test simple binary monitoring
python3 test/test_simple_monitoring.py

# Test complex CMake project
python3 test/13-complex-project-monitoring/test_complex_project_monitoring.py

# Debug memory reading issues
python3 test/14-cmake-memory-debug/debug_cmake_memory.py
```

### Expected Output

```
🔍 Auto-discovering C++ variables...
📄 Found 6 variables in source code:
   - ego_speed (float) [atomic]
   - current_lane (int) [atomic]
   - steering_angle (float) [atomic]
✅ 3 variables available for monitoring
🚀 Process started with PID 12345
✅ Memory reader attached successfully

[Auto-Report #1] Variables: {'ego_speed': 30.0, 'current_lane': 1, 'steering_angle': -15.0}
[Auto-Report #2] Variables: {'ego_speed': 30.5, 'current_lane': 2, 'steering_angle': -14.0}
...
```

## Troubleshooting

### Common Issues

1. **"No variables detected"**
   - Ensure variables are declared as `std::atomic<type>`
   - Check that binary was compiled with debug symbols (`-g` flag)

2. **"Failed to attach memory reader"**
   - May need to run with `sudo` for ptrace permissions
   - Check `/proc/sys/kernel/yama/ptrace_scope` (set to 0 for development)

3. **Incorrect variable values**
   - Verify ELF data section detection is correct
   - Check address calculations with debug script

4. **Process exits immediately**
   - Ensure C++ program has a main loop or sleep
   - Check for runtime errors in the monitored program

### Debug Commands

```bash
# Check symbol table
nm -C your_binary | grep variable_name

# View ELF sections
readelf -S your_binary | grep -E "(\.data|\.bss)"

# Check process memory maps
cat /proc/[pid]/maps | grep your_binary
```

## Performance Considerations

- **0.1s interval**: Real-time monitoring, higher CPU usage
- **1.0s interval**: Normal monitoring, balanced performance
- **2.0s interval**: Conservative, minimal system impact

Memory reading via `/proc/[pid]/mem` is preferred over ptrace for performance.

## Future Enhancements

- [ ] Support for non-atomic variables
- [ ] Memory write capabilities for testing
- [ ] GUI dashboard for variable visualization
- [ ] Integration with KUKSA.val databroker
- [ ] Remote monitoring over network
- [ ] Historical data logging and analysis

## License

Part of the SDV Runtime project. See main repository for license details.

## Contributors

Developed as part of the SDV (Software Defined Vehicle) runtime C++ integration project for real-time automotive system monitoring.
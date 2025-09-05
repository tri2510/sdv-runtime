# Error Handling and Recovery System

Comprehensive error simulation and recovery testing with CMake build system.

## Monitored Variables
- `error_count`: Total number of errors encountered
- `critical_error`: Critical system error flag
- `memory_usage`: Memory utilization percentage (45-98%)
- `cpu_usage`: CPU utilization percentage (20-98%)
- `network_latency`: Network response time (15-500ms)
- `recovery_mode`: System recovery mode active
- `system_stable`: Overall system stability flag

## Error Scenarios
1. **Memory Allocation Failure** (Cycle 8): Memory usage spikes to 95%
2. **Network Timeout** (Cycle 15): Network latency jumps to 500ms
3. **System Overload** (Cycle 20): Critical error triggers recovery mode
4. **Automatic Recovery** (Cycles 22+): System self-recovery process

## Build System
CMake with C++17 standards and error handling

## Usage
```bash
mkdir build && cd build
cmake ..
make
./error_system
```

## Expected Output
Error handling simulation showing gradual system stress increase, specific error scenarios, recovery activation, and final system stabilization.
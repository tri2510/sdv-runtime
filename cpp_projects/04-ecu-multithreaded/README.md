# ECU Multithreaded System

Complex ECU simulation with multiple threads using CMake build system.

## Monitored Variables
- `engine_load`: Engine load percentage (20-100%)
- `throttle_position`: Throttle position (24-120%)
- `brake_pressure`: Brake system pressure (10-120 psi)
- `engine_temp`: Engine temperature (85-100°C)
- `oil_pressure`: Oil pressure (45-55 psi)
- `check_engine`: Check engine light status
- `system_ready`: Overall system readiness

## Threads
1. **Engine Control Thread**: Manages engine load, throttle, temperature
2. **Brake System Thread**: Handles brake pressure and oil pressure
3. **Diagnostics Thread**: Overall system health monitoring

## Build System
CMake with C++17 standards and pthread support

## Usage
```bash
mkdir build && cd build
cmake ..
make
./ecu_system
```

## Expected Output
Multi-threaded ECU simulation with synchronized logging showing engine, brake, and diagnostic information from separate threads running concurrently.
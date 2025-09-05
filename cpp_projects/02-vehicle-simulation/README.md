# Vehicle Simulation

Comprehensive vehicle state simulation with Makefile build system.

## Monitored Variables
- `ego_speed`: Vehicle speed (0-70 km/h)
- `engine_rpm`: Engine RPM (800-2800)
- `fuel_level`: Fuel level percentage (75.5% decreasing)
- `engine_temp`: Engine temperature (90-120°C)
- `gear`: Current gear (1-5)
- `abs_active`: ABS system status
- `traction_control`: Traction control status
- `steering_angle`: Steering wheel angle (-15° to +15°)

## Build System
Makefile with C++17 standards and debugging symbols

## Usage
```bash
make
./vehicle_sim
```

## Expected Output
Real-time vehicle acceleration simulation showing acceleration phase (0-10 cycles) followed by braking phase (10-20 cycles) with ABS activation.
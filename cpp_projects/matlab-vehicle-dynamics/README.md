# MATLAB to SDV Runtime: Vehicle Dynamics Control Example

This example demonstrates how to transition MATLAB/Simulink-generated C++ code to run on the Kit Server platform, enabling real-time monitoring and parameter tuning in a cloud-based development environment.

## 🎯 Overview

This project simulates a typical MATLAB workflow for automotive control systems:
1. **MATLAB Development** → Vehicle dynamics model with PID control
2. **Code Generation** → C++ code (simulating MATLAB Coder output)
3. **SDV Integration** → Adding shared memory for real-time monitoring
4. **Kit Server Deployment** → Running on cloud platform with live tuning

## 📊 System Architecture

```
MATLAB/Simulink                    SDV Runtime
┌─────────────────┐               ┌─────────────────┐
│ Vehicle Model   │               │ C++ Application │
│ ┌─────────────┐ │   Generate    │ ┌─────────────┐ │
│ │ Dynamics    │ ├──────C++─────>│ │ Generated   │ │
│ │ Equations   │ │               │ │ Code        │ │
│ └─────────────┘ │               │ └─────────────┘ │
│ ┌─────────────┐ │               │ ┌─────────────┐ │
│ │ PID Control │ │               │ │ Shared Mem  │ │
│ └─────────────┘ │               │ │ Interface   │ │
└─────────────────┘               └─────────────────┘
        ↓                                 ↓
   Simulink Params                   Kit Server UI
   & Visualization                   & Monitoring
```

## 🚗 Vehicle Dynamics Model

The example implements a simplified vehicle longitudinal dynamics model, similar to what would be developed in MATLAB/Simulink:

### Model Equations (as in MATLAB)
```matlab
% Vehicle Dynamics (MATLAB notation)
F_drive = throttle * engine_torque * gear_ratio / wheel_radius
F_drag = 0.5 * air_density * Cd * frontal_area * velocity^2  
F_rolling = rolling_resistance * mass * gravity
acceleration = (F_drive - F_drag - F_rolling - F_brake) / mass
velocity = velocity + acceleration * dt
position = position + velocity * dt
```

### Control System
- **PID Speed Controller**: Maintains target speed
- **ABS Brake Controller**: Prevents wheel lockup
- **Traction Control**: Limits acceleration

## 📁 Project Structure

```
matlab-vehicle-dynamics/
├── README.md                    # This file
├── CMakeLists.txt              # Build configuration
├── matlab_params.json          # Parameter file (like .mat file)
│
├── include/
│   ├── vehicle_dynamics.h     # MATLAB-generated dynamics model
│   ├── pid_controller.h       # MATLAB-generated PID controller
│   ├── lookup_tables.h        # Calibration tables (like Simulink)
│   ├── matlab_types.h         # MATLAB-compatible data types
│   └── shm_wrapper.h          # SDV runtime integration
│
├── src/
│   ├── main.cpp               # Main application with SDV integration
│   ├── vehicle_dynamics.cpp   # Vehicle model implementation
│   ├── pid_controller.cpp     # Control algorithms
│   └── data_logger.cpp        # Data recording (like MATLAB logging)
│
└── test_scenarios/
    ├── city_driving.json      # Urban cycle test
    ├── highway_cruise.json    # Highway scenario
    └── emergency_brake.json   # Safety test scenario
```

## 🔧 Workflow Steps

### Step 1: MATLAB Development (Original)
```matlab
% In MATLAB/Simulink
mdl = 'vehicle_dynamics_model';
open_system(mdl);
sim(mdl);

% Generate C++ code
cfg = coder.config('lib');
cfg.TargetLang = 'C++';
codegen -config cfg vehicle_dynamics -args {0, 0, 0}
```

### Step 2: Prepare Generated Code for SDV
```cpp
// Original MATLAB-generated code
void vehicle_dynamics(double throttle, double brake, 
                      double steering, double *outputs) {
    // Generated dynamics calculations
}

// Add SDV monitoring capabilities
std::atomic<double> vehicle_speed{0.0};
std::atomic<double> target_speed{60.0};
std::atomic<double> throttle_cmd{0.0};
std::atomic<double> brake_pressure{0.0};
```

### Step 3: Add Shared Memory Interface
```cpp
// Initialize monitoring - variables are automatically detected by Python syncer
INIT_SHM();
// No need for manual WATCH_VAR calls - Python syncer handles variable detection
```

### Step 4: Deploy to Kit Server
```bash
# Package the project
zip -r matlab-vehicle-dynamics.zip matlab-vehicle-dynamics/

# Upload to Kit Server
# Select "C++ Application" → Upload ZIP → Run
```

### Step 5: Real-time Monitoring & Tuning
- **Monitor Variables**: View live data in Kit Server UI
- **Tune Parameters**: Adjust PID gains, speed targets
- **Run Scenarios**: Execute test sequences
- **Log Data**: Export results for MATLAB analysis

## 🎮 Monitored Variables

| Variable | Type | Unit | Description | MATLAB Equivalent |
|----------|------|------|-------------|-------------------|
| `vehicle_speed` | double | m/s | Current vehicle velocity | Simulink Signal |
| `target_speed` | double | m/s | Desired velocity setpoint | Constant Block |
| `throttle_cmd` | double | % | Throttle command (0-100) | Control Output |
| `brake_pressure` | double | bar | Brake pressure (0-200) | Control Output |
| `acceleration` | double | m/s^2 | Vehicle acceleration | Scope Signal |
| `pid_error` | double | m/s | Speed tracking error | Error Signal |
| `pid_kp` | double | - | Proportional gain | Tunable Parameter |
| `pid_ki` | double | - | Integral gain | Tunable Parameter |
| `pid_kd` | double | - | Derivative gain | Tunable Parameter |
| `distance_traveled` | double | m | Total distance | Integrator Output |
| `fuel_consumption` | double | L/100km | Fuel efficiency | Calculated Signal |
| `engine_rpm` | double | RPM | Engine speed | State Variable |

## 🔄 Parameter Tuning

### Original MATLAB Approach
```matlab
% In MATLAB
set_param('model/PID Controller', 'P', '1.5');
set_param('model/PID Controller', 'I', '0.1');
```

### SDV Runtime Approach
```cpp
// Via shared memory (real-time)
pid_kp = 1.5;  // Updates immediately
pid_ki = 0.1;   // No recompilation needed
```

### Via Kit Server UI
1. Navigate to Variables panel
2. Select `pid_kp`
3. Enter new value: `1.5`
4. Observe immediate response

## 📈 Test Scenarios

### 1. City Driving Cycle
- Speed changes: 0 → 30 → 50 → 0 km/h
- Frequent stops and starts
- Tests PID tracking performance

### 2. Highway Cruise Control
- Maintain 120 km/h
- Handle grade changes (+/- 5%)
- Optimize fuel consumption

### 3. Emergency Braking
- Speed: 100 → 0 km/h
- Maximum deceleration
- ABS activation

## 🛠️ Building Locally

```bash
# Navigate to project directory
cd matlab-vehicle-dynamics

# Create build directory
mkdir build && cd build

# Configure with CMake
cmake ..

# Build the project
make

# Run locally (for testing)
./vehicle_dynamics_sim
```

## 📊 Data Logging & Analysis

### Export Format (CSV)
```csv
timestamp,vehicle_speed,target_speed,throttle,brake,acceleration
0.000,0.00,60.00,0.00,0.00,0.00
0.010,0.10,60.00,75.00,0.00,10.00
0.020,0.30,60.00,75.00,0.00,10.00
```

### Import to MATLAB
```matlab
% Load data from SDV runtime
data = readtable('vehicle_data.csv');

% Analyze in MATLAB
figure;
subplot(2,1,1);
plot(data.timestamp, data.vehicle_speed, 'b-');
hold on;
plot(data.timestamp, data.target_speed, 'r--');
legend('Actual', 'Target');
ylabel('Speed (m/s)');

subplot(2,1,2);
plot(data.timestamp, data.throttle, 'g-');
hold on;
plot(data.timestamp, data.brake, 'r-');
legend('Throttle %', 'Brake %');
xlabel('Time (s)');
```

## 🔍 Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Compilation errors | Missing MATLAB types | Include `matlab_types.h` |
| No variable updates | Shared memory not initialized | Check `INIT_SHM()` is called |
| Performance issues | Update rate too high | Adjust `dt` (timestep) |
| PID oscillation | Gains too high | Reduce `pid_kp` value |
| Data not logging | Buffer overflow | Increase log buffer size |

## 🚀 Advanced Features

### 1. Lookup Tables (Like Simulink)
```cpp
// Engine torque map (RPM vs Throttle)
double engine_map[10][10] = {
    // Similar to Simulink 2D Lookup Table
    {100, 120, 140, ...},
    {150, 180, 210, ...},
    ...
};
```

### 2. State Machines (Like Stateflow)
```cpp
enum VehicleState {
    IDLE,
    ACCELERATING,
    CRUISING,
    BRAKING,
    EMERGENCY_STOP
};
```

### 3. Multi-rate Execution
```cpp
// Fast loop (100 Hz) - Control
if (counter % 1 == 0) {
    update_pid_controller();
}

// Medium loop (10 Hz) - Dynamics
if (counter % 10 == 0) {
    update_vehicle_dynamics();
}

// Slow loop (1 Hz) - Diagnostics
if (counter % 100 == 0) {
    update_diagnostics();
}
```

## 📚 References

- [MATLAB Coder Documentation](https://www.mathworks.com/help/coder/)
- [Simulink Code Generation](https://www.mathworks.com/help/ecoder/)
- [SDV Runtime Documentation](https://github.com/eclipse-autowrx/sdv-runtime)
- [ISO 26262 Functional Safety](https://www.iso.org/standard/68383.html)

## 💡 Tips for MATLAB Users

1. **Preserve MATLAB Variable Names**: Keep original names for traceability
2. **Use Compatible Data Types**: `double` for MATLAB `real_T`
3. **Maintain Sample Times**: Match MATLAB solver timestep
4. **Document Units**: Include physical units in comments
5. **Version Control**: Track both .m/.slx and generated C++ files

## 📞 Support

For questions about transitioning MATLAB models to SDV Runtime:
- GitHub Issues: [sdv-runtime/issues](https://github.com/eclipse-autowrx/sdv-runtime/issues)
- Documentation: [Kit Server Guide](https://docs.kit-server.io)

---

*This example demonstrates the complete workflow from MATLAB/Simulink development to cloud-based deployment on Kit Server, enabling modern SDV development practices while maintaining familiar MATLAB workflows.*
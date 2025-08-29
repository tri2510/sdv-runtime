#include "vehicle_dynamics.h"
#include <cmath>
#include <algorithm>

// Default vehicle parameters (similar to MATLAB parameter script)
VehicleDynamics::VehicleDynamics() : previous_time_(0.0) {
    // Initialize with typical passenger car parameters
    // These would normally be loaded from a MATLAB .mat file or parameter script
    params_.mass = 1500.0;                  // kg (typical mid-size car)
    params_.wheel_radius = 0.3;             // m  
    params_.frontal_area = 2.5;             // m^2
    params_.drag_coefficient = 0.3;         // Cd
    params_.rolling_resistance = 0.015;     // coefficient
    params_.air_density = 1.225;            // kg/m^3 (sea level)
    params_.gravity = 9.81;                 // m/s^2
    params_.max_engine_torque = 300.0;      // Nm
    params_.gear_ratio = 3.5;               // final drive ratio
    params_.max_brake_force = 8000.0;       // N
    
    // Initialize states to zero (like MATLAB initial conditions)
    reset();
}

void VehicleDynamics::initialize(const VehicleParams& params) {
    params_ = params;
    reset();
}

void VehicleDynamics::reset() {
    // Reset all states to initial conditions
    // Equivalent to MATLAB: set_initial_conditions.m
    states_.position = 0.0;
    states_.velocity = 0.0;
    states_.acceleration = 0.0;
    states_.engine_rpm = 800.0;     // Idle RPM
    states_.wheel_speed = 0.0;
    states_.fuel_consumed = 0.0;
    
    // Reset internal variables
    engine_force_ = 0.0;
    brake_force_ = 0.0;
    drag_force_ = 0.0;
    rolling_resistance_force_ = 0.0;
    total_force_ = 0.0;
    
    previous_time_ = 0.0;
}

void VehicleDynamics::step(const ControlInputs& inputs, SystemOutputs& outputs, real_T dt) {
    // Main vehicle dynamics calculation - MATLAB-generated style
    // This function would be auto-generated from Simulink model
    
    // 1. Calculate forces acting on vehicle
    engine_force_ = calculateEngineForce(inputs.throttle_cmd);
    brake_force_ = calculateBrakeForce(inputs.brake_cmd);
    drag_force_ = calculateDragForce(states_.velocity);
    rolling_resistance_force_ = calculateRollingResistance();
    
    // 2. Sum of forces (Newton's second law)
    // F_total = F_drive - F_drag - F_rolling - F_brake
    total_force_ = engine_force_ - drag_force_ - rolling_resistance_force_ - brake_force_;
    
    // 3. Calculate acceleration (F = ma)
    states_.acceleration = total_force_ / params_.mass;
    
    // 4. Integrate acceleration to get velocity (Euler integration)
    // In MATLAB: velocity = velocity + acceleration * dt
    states_.velocity = std::max(0.0, states_.velocity + states_.acceleration * dt);
    
    // 5. Integrate velocity to get position
    // In MATLAB: position = position + velocity * dt  
    states_.position += states_.velocity * dt;
    
    // 6. Update engine RPM based on vehicle speed
    updateEngineRPM();
    
    // 7. Calculate fuel consumption
    real_T engine_power = (engine_force_ * states_.velocity) / 1000.0; // kW
    states_.fuel_consumed += calculateFuelConsumption(engine_power, dt);
    
    // 8. Prepare outputs (similar to MATLAB Outport blocks)
    outputs.vehicle_speed = states_.velocity;
    outputs.distance_traveled = states_.position;
    outputs.engine_power = engine_power;
    outputs.brake_pressure = (brake_force_ / params_.max_brake_force) * 200.0; // bar
    
    // Calculate fuel consumption rate (L/100km)
    if (states_.position > 0.001) {  // Avoid division by zero
        outputs.fuel_consumption = (states_.fuel_consumed / (states_.position / 1000.0)) * 100.0;
    } else {
        outputs.fuel_consumption = 0.0;
    }
    
    // For PID controller (will be set externally)
    outputs.pid_error = inputs.target_speed - states_.velocity;
    
    previous_time_ += dt;
}

real_T VehicleDynamics::calculateEngineForce(real_T throttle_percent) {
    // Engine force calculation - equivalent to MATLAB engine map
    // F_engine = (throttle/100) * max_torque * gear_ratio / wheel_radius
    
    // Saturate throttle command
    throttle_percent = saturate(throttle_percent, 0.0, 100.0);
    
    // Simple engine model (in MATLAB this would be a lookup table)
    real_T throttle_fraction = throttle_percent / 100.0;
    real_T engine_torque = throttle_fraction * params_.max_engine_torque;
    
    // Convert torque to force at wheels
    real_T wheel_torque = engine_torque * params_.gear_ratio;
    real_T force = wheel_torque / params_.wheel_radius;
    
    return force;
}

real_T VehicleDynamics::calculateBrakeForce(real_T brake_percent) {
    // Brake force calculation - equivalent to MATLAB brake model
    // F_brake = (brake_cmd/100) * max_brake_force
    
    brake_percent = saturate(brake_percent, 0.0, 100.0);
    real_T brake_fraction = brake_percent / 100.0;
    
    // Apply brake force (always positive, opposes motion)
    real_T force = brake_fraction * params_.max_brake_force;
    
    // Simple ABS model - prevent wheel lockup
    real_T max_decel_force = params_.mass * 9.0; // ~0.9g max deceleration
    force = std::min(force, max_decel_force);
    
    return force;
}

real_T VehicleDynamics::calculateDragForce(real_T velocity) {
    // Aerodynamic drag calculation
    // MATLAB: F_drag = 0.5 * rho * Cd * A * v^2
    
    if (velocity < 0.1) return 0.0; // Avoid small velocity noise
    
    real_T force = 0.5 * params_.air_density * params_.drag_coefficient * 
                   params_.frontal_area * velocity * velocity;
    
    return force;
}

real_T VehicleDynamics::calculateRollingResistance() {
    // Rolling resistance calculation
    // MATLAB: F_rolling = Cr * m * g * sign(velocity)
    
    real_T force = params_.rolling_resistance * params_.mass * params_.gravity;
    
    // Rolling resistance opposes motion direction
    force *= sign(states_.velocity);
    
    return force;
}

void VehicleDynamics::updateEngineRPM() {
    // Calculate engine RPM from vehicle speed
    // MATLAB: rpm = (velocity / wheel_radius) * gear_ratio * (60/(2*pi))
    
    real_T wheel_angular_velocity = states_.velocity / params_.wheel_radius; // rad/s
    states_.engine_rpm = wheel_angular_velocity * params_.gear_ratio * (60.0 / (2.0 * M_PI));
    
    // Ensure minimum idle RPM
    states_.engine_rpm = std::max(states_.engine_rpm, 800.0);
    
    // Maximum RPM limit
    states_.engine_rpm = std::min(states_.engine_rpm, 7000.0);
    
    states_.wheel_speed = wheel_angular_velocity;
}

real_T VehicleDynamics::calculateFuelConsumption(real_T engine_power, real_T dt) {
    // Fuel consumption model - equivalent to MATLAB fuel map
    // This would normally be a 2D lookup table: fuel_rate = f(rpm, power)
    
    if (engine_power < 0.1) {
        // Idle fuel consumption
        return 0.8 * dt / 3600.0; // L/h -> L/s
    }
    
    // Simplified BSFC (Brake Specific Fuel Consumption) model
    // MATLAB: fuel_rate = power * BSFC / fuel_density
    real_T bsfc = 250.0; // g/kWh (typical gasoline engine)
    real_T fuel_density = 0.75; // kg/L (gasoline)
    
    real_T fuel_rate_kg_per_s = (engine_power * bsfc / 1000.0) / 3600.0; // kg/s
    real_T fuel_rate_L_per_s = fuel_rate_kg_per_s / fuel_density; // L/s
    
    return fuel_rate_L_per_s * dt; // L
}
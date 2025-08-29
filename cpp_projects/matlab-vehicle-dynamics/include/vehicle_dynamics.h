#ifndef VEHICLE_DYNAMICS_H
#define VEHICLE_DYNAMICS_H

#include "matlab_types.h"

/**
 * Vehicle Dynamics Model
 * 
 * This class simulates MATLAB-generated code for vehicle longitudinal dynamics.
 * It implements the mathematical model that would typically be developed in
 * MATLAB/Simulink and then code-generated using MATLAB Coder.
 * 
 * MATLAB Equivalent:
 * - Simulink Vehicle Dynamics block
 * - Generated from: vehicle_dynamics.slx
 * - Code generation target: C++
 */
class VehicleDynamics {
private:
    VehicleParams params_;
    VehicleStates states_;
    real_T previous_time_;
    
    // Internal calculations (like MATLAB local variables)
    real_T engine_force_;
    real_T brake_force_;
    real_T drag_force_;
    real_T rolling_resistance_force_;
    real_T total_force_;
    
public:
    /**
     * Constructor - Initialize vehicle parameters
     * Equivalent to MATLAB initialization script or Simulink InitFcn
     */
    VehicleDynamics();
    
    /**
     * Initialize vehicle parameters
     * Equivalent to: load_vehicle_params.m
     */
    void initialize(const VehicleParams& params);
    
    /**
     * Main dynamics calculation step
     * This is the equivalent of the MATLAB-generated step function
     * 
     * MATLAB Generated Function Signature:
     * void vehicle_dynamics_step(const ControlInputs *inputs, 
     *                           SystemOutputs *outputs,
     *                           VehicleStates *states)
     * 
     * @param inputs Control commands (throttle, brake, etc.)
     * @param outputs System outputs (speed, distance, etc.)
     * @param dt Time step (simulation sample time)
     */
    void step(const ControlInputs& inputs, SystemOutputs& outputs, real_T dt);
    
    /**
     * Reset vehicle to initial conditions
     * Equivalent to MATLAB: reset_vehicle_states.m
     */
    void reset();
    
    /**
     * Get current vehicle states
     * Equivalent to MATLAB structure access: vehicle.states
     */
    const VehicleStates& getStates() const { return states_; }
    
    /**
     * Update vehicle parameters during runtime
     * Equivalent to MATLAB: set_param(model, parameter, value)
     */
    void updateParams(const VehicleParams& params) { params_ = params; }
    
private:
    /**
     * Calculate engine force based on throttle command
     * Equivalent to MATLAB function: calculate_engine_force.m
     */
    real_T calculateEngineForce(real_T throttle_percent);
    
    /**
     * Calculate brake force based on brake command  
     * Equivalent to MATLAB function: calculate_brake_force.m
     */
    real_T calculateBrakeForce(real_T brake_percent);
    
    /**
     * Calculate aerodynamic drag force
     * Equivalent to MATLAB: F_drag = 0.5 * rho * Cd * A * v^2
     */
    real_T calculateDragForce(real_T velocity);
    
    /**
     * Calculate rolling resistance force
     * Equivalent to MATLAB: F_rolling = Cr * m * g
     */
    real_T calculateRollingResistance();
    
    /**
     * Update engine RPM based on vehicle speed
     * Equivalent to MATLAB: rpm = velocity * gear_ratio * 60 / (2*pi*r)
     */
    void updateEngineRPM();
    
    /**
     * Calculate fuel consumption rate
     * Equivalent to MATLAB lookup table: fuel_map(rpm, torque)
     */
    real_T calculateFuelConsumption(real_T engine_power, real_T dt);
};

/**
 * Utility Functions (MATLAB-style)
 * These would typically be separate .m files in MATLAB
 */

/**
 * Saturate value between min and max
 * Equivalent to MATLAB: saturate.m or Saturation block
 */
inline real_T saturate(real_T value, real_T min_val, real_T max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

/**
 * Convert km/h to m/s
 * Equivalent to MATLAB: kmh2ms.m
 */
inline real_T kmh_to_ms(real_T kmh) {
    return kmh / 3.6;
}

/**
 * Convert m/s to km/h  
 * Equivalent to MATLAB: ms2kmh.m
 */
inline real_T ms_to_kmh(real_T ms) {
    return ms * 3.6;
}

/**
 * Sign function
 * Equivalent to MATLAB: sign.m or Sign block
 */
inline real_T sign(real_T value) {
    if (value > 0) return 1.0;
    if (value < 0) return -1.0;
    return 0.0;
}

#endif // VEHICLE_DYNAMICS_H
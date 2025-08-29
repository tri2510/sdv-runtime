#ifndef PID_CONTROLLER_H
#define PID_CONTROLLER_H

#include "matlab_types.h"

/**
 * PID Controller Implementation
 * 
 * This class simulates a MATLAB/Simulink PID Controller block.
 * It implements the discrete PID algorithm that would be generated
 * from a Simulink PID Controller block using MATLAB Coder.
 * 
 * MATLAB Equivalent:
 * - Simulink: PID Controller block
 * - MATLAB Function: pid.m
 * - Generated from: speed_controller.slx
 */
class PIDController {
private:
    PIDParams params_;
    
    // PID internal states (like MATLAB persistent variables)
    real_T integral_sum_;       // Integral accumulator
    real_T previous_error_;     // Previous error for derivative
    real_T previous_output_;    // Previous output (for derivative kick prevention)
    boolean_T first_run_;       // Initialization flag
    
    // Anti-windup and filtering
    real_T integral_min_;       // Integral limits
    real_T integral_max_;
    real_T derivative_filter_;  // Low-pass filter for derivative term
    
public:
    /**
     * Constructor
     * Equivalent to MATLAB PID controller initialization
     */
    PIDController();
    
    /**
     * Initialize PID parameters
     * Equivalent to: pid_config.m or Simulink mask parameters
     * 
     * @param params PID gains and configuration
     */
    void initialize(const PIDParams& params);
    
    /**
     * PID control step function
     * This is the main MATLAB-generated control algorithm
     * 
     * MATLAB Generated Function:
     * real_T pid_controller_step(real_T setpoint, real_T feedback,
     *                           PIDParams *params, PIDStates *states)
     * 
     * @param setpoint Desired value (reference)
     * @param feedback Current measured value
     * @param dt Sample time (must match MATLAB sample time)
     * @return Control output
     */
    real_T step(real_T setpoint, real_T feedback, real_T dt);
    
    /**
     * Reset PID controller to initial state
     * Equivalent to MATLAB: reset_pid_states.m
     */
    void reset();
    
    /**
     * Update PID gains during runtime (online tuning)
     * Equivalent to MATLAB: set_param(pid_block, 'P', value)
     */
    void updateGains(real_T kp, real_T ki, real_T kd);
    
    /**
     * Get current PID parameters
     * Equivalent to MATLAB: get_param(pid_block, 'P')
     */
    const PIDParams& getParams() const { return params_; }
    
    /**
     * Get current error value
     * Equivalent to MATLAB signal tap: error_signal
     */
    real_T getCurrentError() const { return previous_error_; }
    
    /**
     * Get integral term value  
     * Equivalent to MATLAB signal tap: integral_term
     */
    real_T getIntegralTerm() const { return integral_sum_ * params_.ki; }
    
    /**
     * Get derivative term value
     * Equivalent to MATLAB signal tap: derivative_term  
     */
    real_T getDerivativeTerm() const;
    
    /**
     * Enable/disable anti-windup
     * Equivalent to MATLAB PID block: 'IgnoreLimit' parameter
     */
    void setAntiWindup(boolean_T enable);
    
private:
    /**
     * Proportional term calculation
     * Equivalent to MATLAB: P_term = Kp * error
     */
    real_T calculateProportional(real_T error);
    
    /**
     * Integral term calculation with anti-windup
     * Equivalent to MATLAB: I_term = Ki * sum(error * dt)
     */
    real_T calculateIntegral(real_T error, real_T dt, real_T output);
    
    /**
     * Derivative term calculation with filtering
     * Equivalent to MATLAB: D_term = Kd * d(error)/dt
     */
    real_T calculateDerivative(real_T error, real_T dt);
    
    /**
     * Apply output saturation
     * Equivalent to MATLAB Saturation block
     */
    real_T applySaturation(real_T value);
    
    /**
     * Apply anti-windup logic
     * Equivalent to MATLAB conditional integrator
     */
    void applyAntiWindup(real_T output, real_T unsaturated_output);
};

/**
 * PID Auto-Tuning Class (Optional Advanced Feature)
 * Simulates MATLAB PID Tuner or Auto-Tune functionality
 */
class PIDAutoTuner {
private:
    real_T settling_time_target_;
    real_T overshoot_limit_;
    boolean_T tuning_active_;
    
public:
    PIDAutoTuner();
    
    /**
     * Start auto-tuning process
     * Equivalent to MATLAB: pidtune() or PID Tuner app
     */
    void startTuning(real_T settling_time, real_T max_overshoot);
    
    /**
     * Auto-tune step (call during simulation)
     * Equivalent to MATLAB auto-tuning algorithm
     */
    boolean_T tuneStep(real_T setpoint, real_T feedback, 
                      PIDController& controller);
    
    /**
     * Get recommended PID gains
     * Equivalent to MATLAB tuning results
     */
    PIDParams getRecommendedGains() const;
};

#endif // PID_CONTROLLER_H
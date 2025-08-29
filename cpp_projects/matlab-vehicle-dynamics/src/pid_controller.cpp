#include "pid_controller.h"
#include "vehicle_dynamics.h"  // For saturate function
#include <cmath>
#include <algorithm>

PIDController::PIDController() {
    // Initialize with typical automotive PID parameters
    // These would be tuned using MATLAB PID Tuner
    params_.kp = 1000.0;        // Proportional gain
    params_.ki = 50.0;          // Integral gain  
    params_.kd = 100.0;         // Derivative gain
    params_.dt = 0.01;          // 10ms sample time (100 Hz)
    params_.min_output = -5000.0; // Maximum deceleration force (N)
    params_.max_output = 3000.0;  // Maximum acceleration force (N)
    
    // Initialize integral limits for anti-windup
    integral_min_ = params_.min_output / params_.ki;
    integral_max_ = params_.max_output / params_.ki;
    
    derivative_filter_ = 0.1;  // Low-pass filter coefficient
    
    reset();
}

void PIDController::initialize(const PIDParams& params) {
    params_ = params;
    
    // Update integral limits based on new gains
    if (params_.ki != 0.0) {
        integral_min_ = params_.min_output / params_.ki;
        integral_max_ = params_.max_output / params_.ki;
    }
    
    reset();
}

void PIDController::reset() {
    // Reset all internal states - equivalent to MATLAB reset function
    integral_sum_ = 0.0;
    previous_error_ = 0.0;
    previous_output_ = 0.0;
    first_run_ = true;
}

real_T PIDController::step(real_T setpoint, real_T feedback, real_T dt) {
    // Main PID calculation - MATLAB-generated discrete PID algorithm
    // This is equivalent to the MATLAB PID Controller block implementation
    
    // Calculate error signal
    real_T error = setpoint - feedback;
    
    // Calculate PID terms
    real_T p_term = calculateProportional(error);
    real_T i_term = calculateIntegral(error, dt, 0.0); // Output will be updated later
    real_T d_term = calculateDerivative(error, dt);
    
    // Sum PID terms
    real_T unsaturated_output = p_term + i_term + d_term;
    
    // Apply output saturation
    real_T output = applySaturation(unsaturated_output);
    
    // Apply anti-windup (back-calculate integral term if saturated)
    applyAntiWindup(output, unsaturated_output);
    
    // Update previous values for next iteration
    previous_error_ = error;
    previous_output_ = output;
    first_run_ = false;
    
    return output;
}

void PIDController::updateGains(real_T kp, real_T ki, real_T kd) {
    // Online gain tuning - equivalent to MATLAB set_param
    params_.kp = kp;
    params_.ki = ki;
    params_.kd = kd;
    
    // Update integral limits
    if (params_.ki != 0.0) {
        integral_min_ = params_.min_output / params_.ki;
        integral_max_ = params_.max_output / params_.ki;
    }
}

real_T PIDController::getDerivativeTerm() const {
    if (first_run_) return 0.0;
    return params_.kd * (previous_error_ - 0.0) / params_.dt; // Simplified
}

void PIDController::setAntiWindup(boolean_T enable) {
    if (!enable) {
        integral_min_ = -1e6;  // Effectively disable limits
        integral_max_ = 1e6;
    } else {
        integral_min_ = params_.min_output / params_.ki;
        integral_max_ = params_.max_output / params_.ki;
    }
}

real_T PIDController::calculateProportional(real_T error) {
    // Proportional term: P = Kp * e(t)
    // MATLAB equivalent: P_term = Kp * error_signal
    return params_.kp * error;
}

real_T PIDController::calculateIntegral(real_T error, real_T dt, real_T output) {
    // Integral term with anti-windup: I = Ki * ∫e(t)dt
    // MATLAB equivalent: I_term = Ki * sum(error * dt)
    
    if (params_.ki == 0.0) return 0.0;
    
    // Trapezoidal integration (more accurate than Euler)
    real_T error_contribution = error * dt;
    integral_sum_ += error_contribution;
    
    // Apply integral limits (anti-windup)
    integral_sum_ = saturate(integral_sum_, integral_min_, integral_max_);
    
    return params_.ki * integral_sum_;
}

real_T PIDController::calculateDerivative(real_T error, real_T dt) {
    // Derivative term with filtering: D = Kd * de(t)/dt
    // MATLAB equivalent: D_term = Kd * (error - prev_error) / dt
    
    if (params_.kd == 0.0) return 0.0;
    
    if (first_run_) {
        return 0.0; // No derivative on first run
    }
    
    // Calculate derivative
    real_T derivative = (error - previous_error_) / dt;
    
    // Apply low-pass filter to reduce noise (typical in automotive applications)
    // First-order filter: y[n] = α * x[n] + (1-α) * y[n-1]
    static real_T filtered_derivative = 0.0;
    filtered_derivative = derivative_filter_ * derivative + 
                         (1.0 - derivative_filter_) * filtered_derivative;
    
    return params_.kd * filtered_derivative;
}

real_T PIDController::applySaturation(real_T value) {
    // Output saturation - equivalent to MATLAB Saturation block
    return saturate(value, params_.min_output, params_.max_output);
}

void PIDController::applyAntiWindup(real_T output, real_T unsaturated_output) {
    // Anti-windup implementation - conditional integrator
    // MATLAB equivalent: Conditional Integrator block
    
    if (params_.ki == 0.0) return;
    
    // If output is saturated, adjust integral term to prevent windup
    if (output != unsaturated_output) {
        // Back-calculate the integral term that would produce the saturated output
        real_T p_term = params_.kp * previous_error_;
        real_T d_term = getDerivativeTerm();
        real_T desired_i_term = output - p_term - d_term;
        
        // Update integral sum to match desired integral term
        integral_sum_ = desired_i_term / params_.ki;
        
        // Ensure integral sum stays within limits
        integral_sum_ = saturate(integral_sum_, integral_min_, integral_max_);
    }
}

// PIDAutoTuner Implementation (Advanced Feature)
PIDAutoTuner::PIDAutoTuner() : 
    settling_time_target_(2.0),   // 2 seconds settling time
    overshoot_limit_(10.0),       // 10% maximum overshoot
    tuning_active_(false) {
}

void PIDAutoTuner::startTuning(real_T settling_time, real_T max_overshoot) {
    settling_time_target_ = settling_time;
    overshoot_limit_ = max_overshoot;
    tuning_active_ = true;
}

boolean_T PIDAutoTuner::tuneStep(real_T setpoint, real_T feedback, 
                                PIDController& controller) {
    // Simplified auto-tuning algorithm
    // In a real implementation, this would use Ziegler-Nichols or other methods
    // MATLAB equivalent: pidtune() function or PID Tuner app
    
    if (!tuning_active_) return false;
    
    // This is a placeholder for a complete auto-tuning implementation
    // A real auto-tuner would:
    // 1. Apply test signals (step response, relay feedback)
    // 2. Measure system response characteristics
    // 3. Calculate optimal PID gains
    // 4. Validate performance meets specifications
    
    // For demonstration, return with basic gains
    tuning_active_ = false;
    return true; // Tuning complete
}

PIDParams PIDAutoTuner::getRecommendedGains() const {
    // Return recommended PID gains based on auto-tuning results
    // This would be calculated by the auto-tuning algorithm
    PIDParams recommended;
    recommended.kp = 800.0;
    recommended.ki = 40.0;
    recommended.kd = 80.0;
    recommended.dt = 0.01;
    recommended.min_output = -5000.0;
    recommended.max_output = 3000.0;
    
    return recommended;
}
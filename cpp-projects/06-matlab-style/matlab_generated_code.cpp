#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <thread>

// MATLAB-style generated C++ code with straightforward global variables
// Typical patterns from MATLAB Coder and Simulink Coder output

// Global variables - MATLAB-style simple declarations
double throttle_position = 0.0;        // Input signal
double brake_pressure = 0.0;           // Input signal
double steering_angle = 0.0;           // Input signal
double vehicle_speed = 0.0;            // State variable

// Controller outputs
double engine_torque_cmd = 0.0;        // Control output
double brake_torque_cmd = 0.0;         // Control output
double steering_torque_cmd = 0.0;      // Control output

// Internal controller states
double speed_error = 0.0;              // PI controller error
double speed_integral = 0.0;           // PI controller integral state
double prev_speed_error = 0.0;         // Previous error for derivative

// System parameters (typically constants in MATLAB)
double kp_speed = 2.5;                 // Proportional gain
double ki_speed = 0.8;                 // Integral gain
double kd_speed = 0.1;                 // Derivative gain

// Simple arrays - common in MATLAB generated code
double wheel_speeds[4] = {0.0, 0.0, 0.0, 0.0};  // FL, FR, RL, RR
double tire_forces[4] = {0.0, 0.0, 0.0, 0.0};   // Tire force estimates

// Boolean flags - MATLAB logical outputs
bool engine_enable = false;            // Engine enable flag
bool brake_enable = false;             // Brake enable flag
bool safety_override = false;          // Safety system override

// Simple integer counters
int control_cycle_count = 0;           // Control loop counter
int fault_count = 0;                   // Fault counter

// MATLAB-style function: Simple PI controller
void pi_speed_controller() {
    // Calculate error
    speed_error = throttle_position * 100.0 - vehicle_speed;  // Target vs actual

    // PI control law
    speed_integral += speed_error * 0.01;  // dt = 10ms

    // Anti-windup
    if (speed_integral > 50.0) speed_integral = 50.0;
    if (speed_integral < -50.0) speed_integral = -50.0;

    // Calculate derivative
    double speed_derivative = (speed_error - prev_speed_error) / 0.01;

    // PID output
    engine_torque_cmd = kp_speed * speed_error +
                       ki_speed * speed_integral +
                       kd_speed * speed_derivative;

    // Output limits
    if (engine_torque_cmd > 200.0) engine_torque_cmd = 200.0;
    if (engine_torque_cmd < 0.0) engine_torque_cmd = 0.0;

    prev_speed_error = speed_error;
}

// MATLAB-style function: Vehicle dynamics simulation
void vehicle_dynamics_step() {
    // Simple vehicle model - typical MATLAB/Simulink block
    double acceleration = (engine_torque_cmd - brake_torque_cmd * brake_pressure) / 1500.0;  // mass = 1500kg

    // Integrate to get speed
    vehicle_speed += acceleration * 0.01;  // dt = 10ms

    // Speed limits
    if (vehicle_speed < 0.0) vehicle_speed = 0.0;
    if (vehicle_speed > 150.0) vehicle_speed = 150.0;

    // Update wheel speeds (assuming no slip)
    for (int i = 0; i < 4; i++) {
        wheel_speeds[i] = vehicle_speed + (rand() % 10 - 5) * 0.1;  // Small variations
        tire_forces[i] = wheel_speeds[i] * 50.0;  // Simple tire model
    }
}

// MATLAB-style function: Safety monitoring
void safety_monitor() {
    // Simple fault detection
    if (vehicle_speed > 120.0 && throttle_position > 0.8) {
        safety_override = true;
        fault_count++;
    } else {
        safety_override = false;
    }

    // Enable flags based on conditions
    engine_enable = (throttle_position > 0.01) && !safety_override;
    brake_enable = (brake_pressure > 0.01) || safety_override;
}

// MATLAB-style function: Input simulation
void simulate_inputs() {
    static double time = 0.0;
    time += 0.01;  // 10ms timestep

    // Simulate driver inputs
    throttle_position = 0.3 + 0.2 * sin(time * 0.5);  // Varying throttle
    brake_pressure = (sin(time * 0.3) > 0.8) ? 0.6 : 0.0;  // Occasional braking
    steering_angle = 15.0 * sin(time * 0.2);  // Gentle steering

    // Keep inputs in valid range
    if (throttle_position < 0.0) throttle_position = 0.0;
    if (throttle_position > 1.0) throttle_position = 1.0;
}

void print_status() {
    std::cout << "\n=== MATLAB-Style Vehicle Controller Status ===" << std::endl;
    std::cout << "Throttle: " << throttle_position * 100 << "%" << std::endl;
    std::cout << "Vehicle Speed: " << vehicle_speed << " km/h" << std::endl;
    std::cout << "Engine Torque: " << engine_torque_cmd << " Nm" << std::endl;
    std::cout << "Speed Error: " << speed_error << " km/h" << std::endl;
    std::cout << "Control Cycles: " << control_cycle_count << std::endl;
    std::cout << "Engine Enable: " << (engine_enable ? "ON" : "OFF") << std::endl;
    std::cout << "Safety Override: " << (safety_override ? "ACTIVE" : "NORMAL") << std::endl;

    std::cout << "Wheel Speeds: ";
    for (int i = 0; i < 4; i++) {
        std::cout << wheel_speeds[i] << " ";
    }
    std::cout << "km/h" << std::endl;
}

int main() {
    std::cout << "MATLAB-Style Vehicle Controller Starting" << std::endl;
    std::cout << "Monitoring " << 20 << " global variables..." << std::endl;
    std::cout << "Simple types: double, bool, int, arrays" << std::endl;

    while (true) {
        // MATLAB-style execution order
        simulate_inputs();
        pi_speed_controller();
        vehicle_dynamics_step();
        safety_monitor();

        control_cycle_count++;

        // Print status every 100 cycles (1 second at 10ms)
        if (control_cycle_count % 100 == 0) {
            print_status();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(10));  // 100Hz typical MATLAB rate
    }

    return 0;
}

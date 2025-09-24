#include <iostream>
#include <thread>
#include <chrono>
#include <cmath>

// Simulink-style generated code with block-based global variables
// Typical patterns from Simulink Coder Real-Time Workshop

// Input signals (from Simulink input blocks)
double accelerator_pedal = 0.0;        // Driver accelerator input [0-1]
double brake_pedal = 0.0;              // Driver brake input [0-1]
double steering_input = 0.0;           // Driver steering input [-1 to 1]

// Output signals (to Simulink output blocks)
double vehicle_velocity = 0.0;         // Vehicle longitudinal velocity [m/s]
double lateral_acceleration = 0.0;     // Vehicle lateral acceleration [m/s^2]
double yaw_rate = 0.0;                 // Vehicle yaw rate [rad/s]

// Controller block outputs
double throttle_command = 0.0;         // Engine throttle command [0-1]
double brake_command = 0.0;            // Brake system command [0-1]
double steering_command = 0.0;         // Steering actuator command [rad]

// State variables (from Simulink integrator blocks)
double engine_speed = 0.0;             // Engine RPM
double transmission_ratio = 1.0;       // Current gear ratio
double wheel_angular_velocity = 0.0;   // Wheel rotation [rad/s]

// Sensor feedback (typical Simulink sensor blocks)
double speed_sensor = 0.0;             // Speed sensor reading [km/h]
double acceleration_sensor = 0.0;      // Acceleration sensor [m/s^2]
double gyro_sensor = 0.0;              // Gyroscope reading [rad/s]

// System parameters (Simulink constant blocks)
double vehicle_mass = 1500.0;          // Vehicle mass [kg]
double wheel_radius = 0.3;             // Wheel radius [m]
double air_density = 1.225;            // Air density [kg/m^3]
double drag_coefficient = 0.3;         // Aerodynamic drag coefficient

// Control gains (tunable parameters)
double throttle_gain = 1.2;            // Throttle response gain
double brake_gain = 2.5;               // Brake response gain
double steering_gain = 0.8;            // Steering response gain

// Arrays for multi-signal buses (Simulink bus objects)
double wheel_torques[4] = {0, 0, 0, 0};       // Individual wheel torques [Nm]
double suspension_forces[4] = {0, 0, 0, 0};   // Suspension forces [N]

// Boolean control flags (Simulink logic blocks)
bool cruise_control_active = false;    // Cruise control state
bool abs_intervention = false;         // ABS activation flag
bool stability_control = false;        // ESC activation flag

// Simple counters (Simulink counter blocks)
int simulation_step = 0;               // Simulation time step counter
int control_updates = 0;               // Control update counter

// Simulink-style block: Engine model
void engine_model_block() {
    // Simple engine dynamics
    double target_rpm = accelerator_pedal * 6000.0;  // Max 6000 RPM

    // First-order lag (typical Simulink transfer function)
    double tau = 0.2;  // Time constant
    double dt = 0.001; // 1ms timestep
    engine_speed += (target_rpm - engine_speed) * dt / tau;

    // Convert to throttle command
    throttle_command = accelerator_pedal * throttle_gain;
    if (throttle_command > 1.0) throttle_command = 1.0;
}

// Simulink-style block: Brake model
void brake_model_block() {
    // Simple brake dynamics
    brake_command = brake_pedal * brake_gain;
    if (brake_command > 1.0) brake_command = 1.0;

    // ABS logic (simple threshold)
    if (brake_command > 0.8 && vehicle_velocity > 10.0) {
        abs_intervention = true;
        brake_command *= 0.7;  // Reduce brake force
    } else {
        abs_intervention = false;
    }
}

// Simulink-style block: Vehicle dynamics
void vehicle_dynamics_block() {
    // Longitudinal dynamics
    double engine_force = throttle_command * 3000.0;  // Max 3000N
    double brake_force = brake_command * 8000.0;      // Max 8000N
    double drag_force = 0.5 * air_density * drag_coefficient * vehicle_velocity * vehicle_velocity;

    double net_force = engine_force - brake_force - drag_force;
    acceleration_sensor = net_force / vehicle_mass;

    // Integrate acceleration to get velocity
    double dt = 0.001;
    vehicle_velocity += acceleration_sensor * dt;
    if (vehicle_velocity < 0.0) vehicle_velocity = 0.0;

    // Convert to wheel speed
    wheel_angular_velocity = vehicle_velocity / wheel_radius;

    // Update sensor readings
    speed_sensor = vehicle_velocity * 3.6;  // Convert m/s to km/h

    // Simple lateral dynamics
    lateral_acceleration = steering_input * vehicle_velocity * 0.1;
    yaw_rate = steering_input * vehicle_velocity * 0.05;
    gyro_sensor = yaw_rate;
}

// Simulink-style block: Control system
void control_system_block() {
    // Simple cruise control logic
    if (accelerator_pedal < 0.1 && vehicle_velocity > 5.0) {
        cruise_control_active = true;
        // Simple PI controller for cruise
        static double target_speed = 15.0;  // 54 km/h
        double error = target_speed - vehicle_velocity;
        throttle_command = 0.2 + error * 0.1;
        if (throttle_command > 1.0) throttle_command = 1.0;
        if (throttle_command < 0.0) throttle_command = 0.0;
    } else {
        cruise_control_active = false;
    }

    // Stability control
    if (fabs(lateral_acceleration) > 8.0) {
        stability_control = true;
    } else {
        stability_control = false;
    }

    // Steering command
    steering_command = steering_input * steering_gain;
}

// Simulink-style block: Wheel torque distribution
void wheel_torque_distribution_block() {
    double base_torque = throttle_command * 500.0;  // Base torque per wheel

    // Distribute torque to wheels
    wheel_torques[0] = base_torque;  // Front left
    wheel_torques[1] = base_torque;  // Front right
    wheel_torques[2] = base_torque;  // Rear left
    wheel_torques[3] = base_torque;  // Rear right

    // Simple torque vectoring based on steering
    if (steering_input > 0.1) {  // Right turn
        wheel_torques[0] *= 1.1;  // Increase left wheels
        wheel_torques[2] *= 1.1;
        wheel_torques[1] *= 0.9;  // Decrease right wheels
        wheel_torques[3] *= 0.9;
    } else if (steering_input < -0.1) {  // Left turn
        wheel_torques[1] *= 1.1;  // Increase right wheels
        wheel_torques[3] *= 1.1;
        wheel_torques[0] *= 0.9;  // Decrease left wheels
        wheel_torques[2] *= 0.9;
    }
}

// Input simulation (would be external in real Simulink)
void simulate_driver_inputs() {
    static double time = 0.0;
    time += 0.001;  // 1ms timestep

    // Realistic driving pattern
    accelerator_pedal = 0.3 + 0.2 * sin(time * 0.5);
    if (accelerator_pedal < 0.0) accelerator_pedal = 0.0;
    if (accelerator_pedal > 1.0) accelerator_pedal = 1.0;

    brake_pedal = (sin(time * 0.3) > 0.9) ? 0.5 : 0.0;
    steering_input = 0.2 * sin(time * 0.8);
}

void print_simulink_status() {
    std::cout << "\n=== Simulink Vehicle Model Status ===" << std::endl;
    std::cout << "Accelerator: " << accelerator_pedal * 100 << "%" << std::endl;
    std::cout << "Vehicle Speed: " << speed_sensor << " km/h" << std::endl;
    std::cout << "Engine Speed: " << engine_speed << " RPM" << std::endl;
    std::cout << "Throttle Cmd: " << throttle_command * 100 << "%" << std::endl;
    std::cout << "Brake Cmd: " << brake_command * 100 << "%" << std::endl;
    std::cout << "Cruise Control: " << (cruise_control_active ? "ON" : "OFF") << std::endl;
    std::cout << "ABS Active: " << (abs_intervention ? "YES" : "NO") << std::endl;
    std::cout << "Sim Steps: " << simulation_step << std::endl;

    std::cout << "Wheel Torques: ";
    for (int i = 0; i < 4; i++) {
        std::cout << wheel_torques[i] << " ";
    }
    std::cout << "Nm" << std::endl;
}

int main() {
    std::cout << "Simulink Vehicle Model Starting" << std::endl;
    std::cout << "Monitoring " << 25 << " global variables..." << std::endl;
    std::cout << "Block-based execution with 1ms timestep" << std::endl;

    while (true) {
        // Execute Simulink-style blocks in order
        simulate_driver_inputs();
        engine_model_block();
        brake_model_block();
        control_system_block();
        vehicle_dynamics_block();
        wheel_torque_distribution_block();

        simulation_step++;
        control_updates++;

        // Print status every 1000 steps (1 second)
        if (simulation_step % 1000 == 0) {
            print_simulink_status();
        }

        std::this_thread::sleep_for(std::chrono::microseconds(1000));  // 1ms = 1000Hz
    }

    return 0;
}
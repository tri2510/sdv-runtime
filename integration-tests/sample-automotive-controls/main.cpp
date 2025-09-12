/*
 * Sample Automotive Controls Application
 * Demonstrates PID controllers and automotive systems with Kit Server integration
 */

#include <atomic>
#include <iostream>
#include <thread>
#include <chrono>
#include <random>
#include <cmath>
#include <signal.h>
#include <unistd.h>
#include <iomanip>

// Automotive control global variables for Kit Server monitoring
std::atomic<double> g_vehicle_speed{0.0};        // km/h
std::atomic<double> g_engine_rpm{800.0};         // RPM
std::atomic<double> g_throttle_position{0.0};    // 0-100%
std::atomic<double> g_brake_pressure{0.0};       // Bar
std::atomic<double> g_steering_angle{0.0};       // Degrees
std::atomic<double> g_target_speed{0.0};         // km/h setpoint
std::atomic<double> g_engine_load{15.0};         // %
std::atomic<double> g_fuel_consumption{8.5};     // L/100km
std::atomic<bool> g_cruise_control{false};       // Cruise control status
std::atomic<bool> g_abs_active{false};           // ABS system status
std::atomic<int> g_gear_position{1};             // Current gear
std::atomic<double> g_coolant_temp{85.0};        // Celsius

// Control system variables
std::atomic<bool> g_running{true};
std::atomic<bool> g_engine_running{false};

// Simple PID Controller structure
struct PIDController {
    double kp, ki, kd;
    double integral{0.0};
    double previous_error{0.0};
    
    PIDController(double p, double i, double d) : kp(p), ki(i), kd(d) {}
    
    double compute(double setpoint, double measured, double dt) {
        double error = setpoint - measured;
        integral += error * dt;
        double derivative = (error - previous_error) / dt;
        
        // Anti-windup
        if (integral > 100.0) integral = 100.0;
        if (integral < -100.0) integral = -100.0;
        
        double output = kp * error + ki * integral + kd * derivative;
        previous_error = error;
        
        return output;
    }
    
    void reset() {
        integral = 0.0;
        previous_error = 0.0;
    }
};

// Global PID controllers
PIDController speed_controller(2.0, 0.5, 0.1);
PIDController rpm_controller(1.5, 0.3, 0.05);

void signal_handler(int signal) {
    std::cout << "\nShutdown signal received. Stopping automotive system..." << std::endl;
    g_running = false;
}

// Engine control thread
void engine_control_thread() {
    const double dt = 0.1; // 10Hz control loop
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> noise(0.0, 0.1);
    
    while (g_running) {
        if (g_engine_running) {
            // Speed control system
            double target_speed = g_target_speed.load();
            double current_speed = g_vehicle_speed.load();
            
            if (g_cruise_control.load() && target_speed > 0) {
                // PID control for cruise control
                double speed_error = target_speed - current_speed;
                double throttle_cmd = speed_controller.compute(target_speed, current_speed, dt);
                
                // Clamp throttle command
                throttle_cmd = std::max(0.0, std::min(100.0, throttle_cmd));
                g_throttle_position.store(throttle_cmd);
                
                // If speed error is large and negative, reduce throttle
                if (speed_error < -10.0) {
                    g_throttle_position.store(0.0);
                    g_brake_pressure.store(std::min(50.0, -speed_error * 2.0));
                } else {
                    g_brake_pressure.store(0.0);
                }
            }
            
            // Engine RPM simulation based on throttle and load
            double throttle = g_throttle_position.load();
            double load = g_engine_load.load();
            
            double target_rpm = 800.0 + (throttle * 30.0) + (load * 10.0);
            double current_rpm = g_engine_rpm.load();
            
            // Simulate engine response
            double rpm_delta = (target_rpm - current_rpm) * 0.1;
            g_engine_rpm.store(current_rpm + rpm_delta + noise(gen) * 20);
            
            // Vehicle speed based on RPM and gear
            int gear = g_gear_position.load();
            double rpm = g_engine_rpm.load();
            double speed_factor = gear * 0.05;
            double new_speed = (rpm - 800) * speed_factor;
            new_speed = std::max(0.0, new_speed);
            
            // Apply brake effect
            double brake = g_brake_pressure.load();
            if (brake > 0) {
                new_speed *= (1.0 - brake / 100.0);
                
                // ABS simulation
                if (brake > 30.0 && new_speed > 20.0) {
                    g_abs_active.store(true);
                } else {
                    g_abs_active.store(false);
                }
            }
            
            g_vehicle_speed.store(new_speed);
            
            // Automatic transmission simulation
            double speed = g_vehicle_speed.load();
            if (speed < 20.0 && gear > 1) {
                g_gear_position.store(gear - 1);
            } else if (speed > 40.0 * gear && gear < 5) {
                g_gear_position.store(gear + 1);
            }
            
            // Engine load simulation
            double base_load = 15.0 + (throttle * 0.8) + (speed * 0.2);
            g_engine_load.store(base_load + noise(gen) * 5);
            
            // Fuel consumption
            double fuel_rate = 5.0 + (throttle * 0.15) + (load * 0.1);
            g_fuel_consumption.store(fuel_rate + noise(gen) * 0.5);
            
            // Coolant temperature
            double base_temp = 85.0 + (load * 0.5) + (throttle * 0.2);
            g_coolant_temp.store(base_temp + noise(gen) * 2);
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

// Input simulation thread (simulates driver inputs)
void input_simulation_thread() {
    int cycle = 0;
    
    while (g_running) {
        cycle++;
        
        if (g_engine_running) {
            // Simulate driving scenarios
            int scenario = (cycle / 100) % 4;
            
            switch (scenario) {
                case 0: // City driving
                    g_target_speed.store(50.0);
                    g_cruise_control.store(false);
                    // Manual throttle control
                    if (cycle % 50 < 25) {
                        g_throttle_position.store(30.0 + (cycle % 25) * 1.0);
                    } else {
                        g_throttle_position.store(45.0 - (cycle % 25) * 1.0);
                    }
                    break;
                    
                case 1: // Highway cruise
                    g_target_speed.store(120.0);
                    g_cruise_control.store(true);
                    break;
                    
                case 2: // Traffic situation
                    g_target_speed.store(30.0);
                    g_cruise_control.store(false);
                    if (cycle % 30 < 15) {
                        g_brake_pressure.store(20.0);
                        g_throttle_position.store(0.0);
                    }
                    break;
                    
                case 3: // Parking/idle
                    g_target_speed.store(0.0);
                    g_cruise_control.store(false);
                    g_throttle_position.store(0.0);
                    g_brake_pressure.store(100.0);
                    break;
            }
            
            // Steering simulation (for completeness)
            g_steering_angle.store(10.0 * std::sin(cycle * 0.05));
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

// Display thread
void display_thread() {
    while (g_running) {
        system("clear");
        
        std::cout << "=== Automotive Controls Sample ===" << std::endl;
        std::cout << "Process ID: " << getpid() << std::endl;
        std::cout << "Engine: " << (g_engine_running.load() ? "RUNNING" : "STOPPED") << std::endl;
        std::cout << std::endl;
        
        // Vehicle status
        std::cout << "Vehicle Status:" << std::endl;
        std::cout << "  Speed:        " << std::fixed << std::setprecision(1) 
                  << g_vehicle_speed.load() << " km/h" << std::endl;
        std::cout << "  Target:       " << std::fixed << std::setprecision(1) 
                  << g_target_speed.load() << " km/h" << std::endl;
        std::cout << "  Gear:         " << g_gear_position.load() << std::endl;
        std::cout << "  Steering:     " << std::fixed << std::setprecision(1) 
                  << g_steering_angle.load() << "°" << std::endl;
        
        std::cout << std::endl;
        
        // Engine status  
        std::cout << "Engine Status:" << std::endl;
        std::cout << "  RPM:          " << std::fixed << std::setprecision(0) 
                  << g_engine_rpm.load() << " RPM" << std::endl;
        std::cout << "  Load:         " << std::fixed << std::setprecision(1) 
                  << g_engine_load.load() << " %" << std::endl;
        std::cout << "  Coolant:      " << std::fixed << std::setprecision(1) 
                  << g_coolant_temp.load() << " °C" << std::endl;
        std::cout << "  Fuel:         " << std::fixed << std::setprecision(1) 
                  << g_fuel_consumption.load() << " L/100km" << std::endl;
        
        std::cout << std::endl;
        
        // Control inputs
        std::cout << "Control Inputs:" << std::endl;
        std::cout << "  Throttle:     " << std::fixed << std::setprecision(1) 
                  << g_throttle_position.load() << " %" << std::endl;
        std::cout << "  Brake:        " << std::fixed << std::setprecision(1) 
                  << g_brake_pressure.load() << " bar" << std::endl;
        std::cout << "  Cruise Ctrl:  " << (g_cruise_control.load() ? "ON" : "OFF") << std::endl;
        std::cout << "  ABS:          " << (g_abs_active.load() ? "ACTIVE" : "OFF") << std::endl;
        
        std::cout << std::endl;
        std::cout << "Kit Server Monitoring:" << std::endl;
        std::cout << "  Variables:    12 automotive variables" << std::endl;
        std::cout << "  Update Rate:  10 Hz control loop" << std::endl;
        std::cout << "  PID Control:  Speed & RPM controllers active" << std::endl;
        
        std::cout << std::endl;
        std::cout << "Commands: [e] Start/Stop Engine, [c] Toggle Cruise, [Ctrl+C] Exit" << std::endl;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}

int main(int argc, char* argv[]) {
    std::cout << "Starting Automotive Controls Sample..." << std::endl;
    std::cout << "Process ID: " << getpid() << std::endl;
    std::cout << "Monitoring 12 automotive control variables" << std::endl;
    std::cout << std::endl;
    
    // Set up signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Start engine by default
    g_engine_running = true;
    g_target_speed = 60.0;
    
    // Start control threads
    std::thread engine_thread(engine_control_thread);
    std::thread input_thread(input_simulation_thread);
    std::thread display_thread_handle(display_thread);
    
    // Main loop for user input (simplified)
    while (g_running) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // Simulate kit server communication
        static int heartbeat = 0;
        if (++heartbeat % 100 == 0) {
            // Kit server would read all atomic variables here
            // This demonstrates the variables are accessible
        }
    }
    
    // Clean shutdown
    std::cout << "\nShutting down automotive control system..." << std::endl;
    
    engine_thread.join();
    input_thread.join();
    display_thread_handle.join();
    
    std::cout << "Automotive Controls Sample stopped." << std::endl;
    
    return 0;
}
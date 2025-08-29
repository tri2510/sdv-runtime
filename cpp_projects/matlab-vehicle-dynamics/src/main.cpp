#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <iomanip>
#include <fstream>
#include <vector>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string>
#include <map>
#include <cstring>

// MATLAB-generated model includes
#include "vehicle_dynamics.h"
#include "pid_controller.h"
#include "matlab_types.h"

// Shared memory constants (must match shm_util.py)
const char* SHM_NAME = "/my_shm";
const int MAX_VARS = 10;
const int VAR_NAME_SIZE = 32;
const int VAR_VALUE_SIZE = 64;
const int METADATA_SIZE = 4;
const int ENTRY_SIZE = VAR_NAME_SIZE + VAR_VALUE_SIZE;
const int SHM_SIZE = METADATA_SIZE + (MAX_VARS * ENTRY_SIZE);

// Global variables for SDV monitoring (atomic for thread safety)
// These represent the key signals that would be monitored in MATLAB/Simulink

// Vehicle States (equivalent to Simulink signal monitoring)
std::atomic<double> vehicle_speed{0.0};        // m/s - Current speed
std::atomic<double> target_speed{16.67};       // m/s - Setpoint (60 km/h)
std::atomic<double> distance_traveled{0.0};    // m - Odometer
std::atomic<double> acceleration{0.0};         // m/s^2 - Acceleration
std::atomic<double> engine_rpm{800.0};         // RPM - Engine speed

// Control Commands (equivalent to MATLAB manual switches/sliders)
std::atomic<double> throttle_cmd{0.0};         // % - Throttle position
std::atomic<double> brake_cmd{0.0};            // % - Brake pedal position
std::atomic<double> manual_throttle{0.0};      // % - Manual override
std::atomic<double> manual_brake{0.0};         // % - Manual override

// PID Controller Variables (equivalent to MATLAB PID block signals)
std::atomic<double> pid_error{0.0};            // m/s - Speed error
std::atomic<double> pid_output{0.0};           // N - Force command
std::atomic<double> pid_kp{1000.0};            // - Proportional gain
std::atomic<double> pid_ki{50.0};              // - Integral gain
std::atomic<double> pid_kd{100.0};             // - Derivative gain

// System Performance (equivalent to MATLAB calculated signals)
std::atomic<double> fuel_consumption{0.0};     // L/100km - Efficiency
std::atomic<double> engine_power{0.0};         // kW - Engine power
std::atomic<double> brake_pressure{0.0};       // bar - Brake pressure

// Control Modes (equivalent to MATLAB mode switches)
std::atomic<int> control_mode{1};              // 1=PID, 0=Manual
std::atomic<int> scenario_mode{0};             // Test scenario selector
std::atomic<int> enable_logging{1};            // Enable data logging

// Simulation Parameters (equivalent to Simulink configuration)
const double SIMULATION_TIMESTEP = 0.01;       // 10ms (100 Hz)
const double DISPLAY_UPDATE_RATE = 1.0;        // 1 Hz display updates
const int MAX_SIMULATION_STEPS = 10000;        // 100 seconds max

// Map to associate variable names with their pointers and types
std::map<std::string, std::pair<void*, std::string>> var_map;

void setup_variable_map() {
    // Vehicle States
    var_map["vehicle_speed"] = {&vehicle_speed, "double"};
    var_map["target_speed"] = {&target_speed, "double"};
    var_map["distance_traveled"] = {&distance_traveled, "double"};
    var_map["acceleration"] = {&acceleration, "double"};
    var_map["engine_rpm"] = {&engine_rpm, "double"};
    
    // Control Commands
    var_map["throttle_cmd"] = {&throttle_cmd, "double"};
    var_map["brake_cmd"] = {&brake_cmd, "double"};
    var_map["manual_throttle"] = {&manual_throttle, "double"};
    var_map["manual_brake"] = {&manual_brake, "double"};
    
    // PID Controller
    var_map["pid_error"] = {&pid_error, "double"};
    var_map["pid_output"] = {&pid_output, "double"};
    var_map["pid_kp"] = {&pid_kp, "double"};
    var_map["pid_ki"] = {&pid_ki, "double"};
    var_map["pid_kd"] = {&pid_kd, "double"};
    
    // Performance Metrics
    var_map["fuel_consumption"] = {&fuel_consumption, "double"};
    var_map["engine_power"] = {&engine_power, "double"};
    var_map["brake_pressure"] = {&brake_pressure, "double"};
    
    // Control Modes
    var_map["control_mode"] = {&control_mode, "int"};
    var_map["scenario_mode"] = {&scenario_mode, "int"};
    var_map["enable_logging"] = {&enable_logging, "int"};
}

void handle_set_request(const std::string& var_name, const std::string& new_value_str) {
    if (var_map.find(var_name) == var_map.end()) {
        return; // Variable not found
    }

    auto& var_info = var_map[var_name];
    void* var_ptr = var_info.first;
    const std::string& type = var_info.second;

    try {
        if (type == "int") {
            *static_cast<std::atomic<int>*>(var_ptr) = std::stoi(new_value_str);
        } else if (type == "double") {
            *static_cast<std::atomic<double>*>(var_ptr) = std::stod(new_value_str);
        }
    } catch (const std::exception& e) {
        // Handle conversion error if necessary
    }
}

void shared_memory_loop() {
    int shm_fd = shm_open(SHM_NAME, O_RDWR, 0666);
    if (shm_fd == -1) {
        return; // Shared memory not available, continue without it
    }

    void* shm_ptr = mmap(0, SHM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (shm_ptr == MAP_FAILED) {
        close(shm_fd);
        return;
    }
    close(shm_fd);

    while (true) {
        // Read number of variables to watch
        int num_vars;
        memcpy(&num_vars, shm_ptr, METADATA_SIZE);

        if (num_vars > 0 && num_vars <= MAX_VARS) {
            for (int i = 0; i < num_vars; ++i) {
                char* entry_ptr = (char*)shm_ptr + METADATA_SIZE + i * ENTRY_SIZE;
                
                // Read variable name
                char var_name_buf[VAR_NAME_SIZE];
                memcpy(var_name_buf, entry_ptr, VAR_NAME_SIZE);
                std::string var_name(var_name_buf);

                if (var_map.count(var_name)) {
                    auto& var_info = var_map[var_name];
                    void* var_ptr = var_info.first;
                    const std::string& type = var_info.second;

                    char* value_ptr = entry_ptr + VAR_NAME_SIZE;

                    // Check for a set request
                    char current_value_buf[VAR_VALUE_SIZE];
                    memcpy(current_value_buf, value_ptr, VAR_VALUE_SIZE);
                    std::string current_value_str(current_value_buf);

                    if (current_value_str.rfind("SET:", 0) == 0) {
                        std::string new_val = current_value_str.substr(4);
                        handle_set_request(var_name, new_val);
                        // Clear the set request
                        memset(value_ptr, 0, VAR_VALUE_SIZE);
                    }

                    // Write back the current value
                    std::string value_str;
                    if (type == "int") {
                        value_str = std::to_string(*static_cast<std::atomic<int>*>(var_ptr));
                    } else if (type == "double") {
                        value_str = std::to_string(*static_cast<std::atomic<double>*>(var_ptr));
                    }
                    
                    strncpy(value_ptr, value_str.c_str(), VAR_VALUE_SIZE - 1);
                    value_ptr[VAR_VALUE_SIZE - 1] = '\0';
                }
            }
        }
        usleep(100000); // 100ms
    }
    
    munmap(shm_ptr, SHM_SIZE);
}

// Data logging (equivalent to MATLAB To Workspace blocks)
struct DataLogEntry {
    double timestamp;
    double vehicle_speed;
    double target_speed;
    double throttle_cmd;
    double brake_cmd;
    double pid_error;
    double acceleration;
    double fuel_consumption;
    double engine_power;
};

std::vector<DataLogEntry> data_log;

// Forward declarations
void runVehicleSimulation();
void updateTestScenario(int step, ControlInputs& inputs);
void logData(double time, const SystemOutputs& outputs, const ControlInputs& inputs);
void saveDataToCSV(const std::string& filename);
void displayStatus(int step, const SystemOutputs& outputs, const ControlInputs& inputs);

int main() {
    std::cout << "=== MATLAB Vehicle Dynamics → SDV Runtime Demo ===" << std::endl;
    std::cout << "Simulating MATLAB/Simulink-generated vehicle control system" << std::endl;
    std::cout << "Integration: SDV Runtime shared memory monitoring" << std::endl;
    std::cout << std::endl;
    
    // Initialize variable mapping for shared memory monitoring
    setup_variable_map();
    
    // Start shared memory monitoring in background thread
    std::thread shm_thread(shared_memory_loop);
    shm_thread.detach();
    
    std::cout << "SDV Runtime variables are automatically monitored by Python syncer" << std::endl;
    std::cout << "- vehicle_speed, target_speed, pid gains, control modes, etc." << std::endl;
    std::cout << std::endl;
    
    std::cout << "Starting vehicle dynamics simulation..." << std::endl;
    std::cout << "You can modify parameters in real-time via Kit Server interface" << std::endl;
    std::cout << std::endl;
    
    // Run the main simulation (equivalent to MATLAB sim() command)
    runVehicleSimulation();
    
    // Save logged data (equivalent to MATLAB save() or To Workspace)
    if (enable_logging.load() && !data_log.empty()) {
        std::cout << "Saving simulation data to CSV file..." << std::endl;
        saveDataToCSV("matlab_vehicle_simulation.csv");
        std::cout << "✓ Data saved - import to MATLAB for analysis" << std::endl;
    }
    
    std::cout << std::endl;
    std::cout << "Simulation completed." << std::endl;
    std::cout << "MATLAB Vehicle Dynamics Demo finished successfully!" << std::endl;
    
    return 0;
}

void runVehicleSimulation() {
    // Initialize MATLAB-generated models
    VehicleDynamics vehicle;
    PIDController pid_controller;
    
    // Initialize with default parameters (equivalent to MATLAB initialization)
    VehicleParams vehicle_params;
    vehicle_params.mass = 1500.0;              // kg
    vehicle_params.wheel_radius = 0.3;         // m
    vehicle_params.frontal_area = 2.5;         // m^2
    vehicle_params.drag_coefficient = 0.3;     // Cd
    vehicle_params.rolling_resistance = 0.015; // coefficient
    vehicle_params.air_density = 1.225;        // kg/m^3
    vehicle_params.gravity = 9.81;             // m/s^2
    vehicle_params.max_engine_torque = 300.0;  // Nm
    vehicle_params.gear_ratio = 3.5;           // ratio
    vehicle_params.max_brake_force = 8000.0;   // N
    
    vehicle.initialize(vehicle_params);
    
    PIDParams pid_params;
    pid_params.kp = pid_kp.load();
    pid_params.ki = pid_ki.load();
    pid_params.kd = pid_kd.load();
    pid_params.dt = SIMULATION_TIMESTEP;
    pid_params.min_output = -5000.0;           // Max decel force
    pid_params.max_output = 3000.0;            // Max accel force
    
    pid_controller.initialize(pid_params);
    
    // Simulation loop (equivalent to MATLAB simulation engine)
    std::cout << "Running simulation at " << (1.0/SIMULATION_TIMESTEP) << " Hz..." << std::endl;
    
    for (int step = 0; step < MAX_SIMULATION_STEPS; step++) {
        double sim_time = step * SIMULATION_TIMESTEP;
        
        // Update PID gains if changed via SDV interface (online tuning)
        if (pid_kp.load() != pid_params.kp || 
            pid_ki.load() != pid_params.ki || 
            pid_kd.load() != pid_params.kd) {
            
            pid_controller.updateGains(pid_kp.load(), pid_ki.load(), pid_kd.load());
            pid_params.kp = pid_kp.load();
            pid_params.ki = pid_ki.load(); 
            pid_params.kd = pid_kd.load();
        }
        
        // Prepare control inputs
        ControlInputs inputs;
        inputs.target_speed = target_speed.load();
        inputs.enable_pid = (control_mode.load() == 1);
        inputs.enable_abs = true;
        
        // Update test scenario (equivalent to MATLAB test harness)
        updateTestScenario(step, inputs);
        
        // Run PID controller if enabled (MATLAB-generated control algorithm)
        if (inputs.enable_pid) {
            double current_speed = vehicle.getStates().velocity;
            double pid_force = pid_controller.step(inputs.target_speed, current_speed, SIMULATION_TIMESTEP);
            
            // Convert PID force output to throttle/brake commands
            if (pid_force > 0) {
                inputs.throttle_cmd = std::min(100.0, (pid_force / 3000.0) * 100.0);
                inputs.brake_cmd = 0.0;
            } else {
                inputs.throttle_cmd = 0.0;
                inputs.brake_cmd = std::min(100.0, (-pid_force / 5000.0) * 100.0);
            }
            
            pid_output = pid_force;
        } else {
            // Manual control mode
            inputs.throttle_cmd = manual_throttle.load();
            inputs.brake_cmd = manual_brake.load();
            pid_output = 0.0;
        }
        
        // Run vehicle dynamics model (MATLAB-generated physics)
        SystemOutputs outputs;
        vehicle.step(inputs, outputs, SIMULATION_TIMESTEP);
        
        // Update shared memory variables for SDV monitoring
        vehicle_speed = outputs.vehicle_speed;
        distance_traveled = outputs.distance_traveled;
        acceleration = vehicle.getStates().acceleration;
        engine_rpm = vehicle.getStates().engine_rpm;
        throttle_cmd = inputs.throttle_cmd;
        brake_cmd = inputs.brake_cmd;
        pid_error = outputs.pid_error;
        fuel_consumption = outputs.fuel_consumption;
        engine_power = outputs.engine_power;
        brake_pressure = outputs.brake_pressure;
        
        // Data logging (equivalent to MATLAB To Workspace blocks)
        if (enable_logging.load() && step % 10 == 0) { // Log at 10 Hz
            logData(sim_time, outputs, inputs);
        }
        
        // Display status at 1 Hz (equivalent to MATLAB display/scope blocks)
        if (step % int(DISPLAY_UPDATE_RATE / SIMULATION_TIMESTEP) == 0) {
            displayStatus(step, outputs, inputs);
        }
        
        // Real-time execution (maintain simulation timestep)
        std::this_thread::sleep_for(std::chrono::milliseconds(int(SIMULATION_TIMESTEP * 1000)));
    }
}

void updateTestScenario(int step, ControlInputs& inputs) {
    // Test scenario generator (equivalent to MATLAB Test Sequence block)
    int scenario = scenario_mode.load();
    double sim_time = step * SIMULATION_TIMESTEP;
    
    switch (scenario) {
        case 0: // Constant speed cruise
            target_speed = 16.67; // 60 km/h
            break;
            
        case 1: // City driving cycle
            if (sim_time < 10.0) target_speed = 8.33;      // 30 km/h
            else if (sim_time < 20.0) target_speed = 13.89; // 50 km/h
            else if (sim_time < 30.0) target_speed = 0.0;   // Stop
            else if (sim_time < 40.0) target_speed = 11.11; // 40 km/h
            else target_speed = 16.67;                       // 60 km/h
            break;
            
        case 2: // Highway acceleration
            target_speed = std::min(33.33, sim_time * 1.5); // Ramp to 120 km/h
            break;
            
        case 3: // Emergency braking test
            if (sim_time < 20.0) target_speed = 27.78;      // 100 km/h
            else target_speed = 0.0;                         // Emergency stop
            break;
            
        default:
            target_speed = 16.67; // Default 60 km/h
    }
}

void logData(double time, const SystemOutputs& outputs, const ControlInputs& inputs) {
    // Data logging (equivalent to MATLAB logging/To Workspace)
    DataLogEntry entry;
    entry.timestamp = time;
    entry.vehicle_speed = outputs.vehicle_speed;
    entry.target_speed = inputs.target_speed;
    entry.throttle_cmd = inputs.throttle_cmd;
    entry.brake_cmd = inputs.brake_cmd;
    entry.pid_error = outputs.pid_error;
    entry.acceleration = acceleration.load();
    entry.fuel_consumption = outputs.fuel_consumption;
    entry.engine_power = outputs.engine_power;
    
    data_log.push_back(entry);
}

void saveDataToCSV(const std::string& filename) {
    // Export data in MATLAB-compatible CSV format
    std::ofstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not create CSV file: " << filename << std::endl;
        return;
    }
    
    // CSV header (MATLAB variable names)
    file << "timestamp,vehicle_speed,target_speed,throttle_cmd,brake_cmd,";
    file << "pid_error,acceleration,fuel_consumption,engine_power" << std::endl;
    
    // Data rows
    for (const auto& entry : data_log) {
        file << std::fixed << std::setprecision(4);
        file << entry.timestamp << ",";
        file << entry.vehicle_speed << ",";
        file << entry.target_speed << ",";
        file << entry.throttle_cmd << ",";
        file << entry.brake_cmd << ",";
        file << entry.pid_error << ",";
        file << entry.acceleration << ",";
        file << entry.fuel_consumption << ",";
        file << entry.engine_power << std::endl;
    }
    
    file.close();
    std::cout << "✓ Exported " << data_log.size() << " data points to: " << filename << std::endl;
}

void displayStatus(int step, const SystemOutputs& outputs, const ControlInputs& inputs) {
    // Real-time display (equivalent to MATLAB Display blocks or scopes)
    double sim_time = step * SIMULATION_TIMESTEP;
    
    std::cout << "\n=== Vehicle Status (t=" << std::fixed << std::setprecision(1) 
              << sim_time << "s) ===" << std::endl;
    std::cout << "Speed: " << std::setprecision(2) << outputs.vehicle_speed << " m/s ("
              << outputs.vehicle_speed * 3.6 << " km/h)" << std::endl;
    std::cout << "Target: " << inputs.target_speed << " m/s ("
              << inputs.target_speed * 3.6 << " km/h)" << std::endl;
    std::cout << "PID Error: " << outputs.pid_error << " m/s" << std::endl;
    std::cout << "Control: Throttle=" << std::setprecision(1) << inputs.throttle_cmd 
              << "%, Brake=" << inputs.brake_cmd << "%" << std::endl;
    std::cout << "Distance: " << std::setprecision(0) << outputs.distance_traveled << " m" << std::endl;
    std::cout << "Fuel: " << std::setprecision(2) << outputs.fuel_consumption << " L/100km" << std::endl;
    std::cout << "Mode: " << (control_mode.load() ? "PID Control" : "Manual") 
              << ", Scenario: " << scenario_mode.load() << std::endl;
    std::cout << "[Variables can be modified via Kit Server interface]" << std::endl;
}
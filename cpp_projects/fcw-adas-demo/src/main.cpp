#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <string>
#include <vector>
#include <map>
#include <cstring>

// Shared memory constants (must match shm_util.py)
const char* SHM_NAME = "/my_shm";
const int MAX_VARS = 10;
const int VAR_NAME_SIZE = 32;
const int VAR_VALUE_SIZE = 64;
const int METADATA_SIZE = 4;
const int ENTRY_SIZE = VAR_NAME_SIZE + VAR_VALUE_SIZE;
const int SHM_SIZE = METADATA_SIZE + (MAX_VARS * ENTRY_SIZE);

// Global variables for monitoring (using atomic for thread safety)
std::atomic<float> ego_speed{50.0f};
std::atomic<int> collision_risk{0};
std::atomic<int> current_lane{2};
std::atomic<bool> warning_active{false};
std::atomic<float> brake_pressure{0.0f};

// Map to associate variable names with their pointers and types
std::map<std::string, std::pair<void*, std::string>> var_map;

void setup_variable_map() {
    var_map["ego_speed"] = {&ego_speed, "float"};
    var_map["collision_risk"] = {&collision_risk, "int"};
    var_map["current_lane"] = {&current_lane, "int"};
    var_map["warning_active"] = {&warning_active, "bool"};
    var_map["brake_pressure"] = {&brake_pressure, "float"};
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
        } else if (type == "float") {
            *static_cast<std::atomic<float>*>(var_ptr) = std::stof(new_value_str);
        } else if (type == "bool") {
            *static_cast<std::atomic<bool>*>(var_ptr) = (new_value_str == "1" || new_value_str == "true");
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
                    } else if (type == "float") {
                        value_str = std::to_string(*static_cast<std::atomic<float>*>(var_ptr));
                    } else if (type == "bool") {
                        value_str = (*static_cast<std::atomic<bool>*>(var_ptr)) ? "1" : "0";
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

int main() {
    std::cout << "=== FCW ADAS Demo System ===" << std::endl;
    std::cout << "Variables automatically monitored by Python syncer: ego_speed, collision_risk, current_lane, warning_active, brake_pressure" << std::endl;
    std::cout << "\nStarting FCW ADAS simulation..." << std::endl;
    
    setup_variable_map();
    
    // Start shared memory monitoring in background thread
    std::thread shm_thread(shared_memory_loop);
    shm_thread.detach();
    
    for (int i = 0; i < 100; i++) {
        std::cout << "\n=== FCW ADAS Status (Time: " << i << "s) ===" << std::endl;
        std::cout << "Ego Speed: " << ego_speed.load() << " km/h" << std::endl;
        std::cout << "Current Lane: " << current_lane.load() << " (of 4)" << std::endl;
        std::cout << "Collision Risk: " << collision_risk.load() << "%" << std::endl;
        std::cout << "Warning Active: " << (warning_active.load() ? "YES" : "NO") << std::endl;
        std::cout << "Brake Pressure: " << brake_pressure.load() << "%" << std::endl;
        
        // Simulate realistic ADAS behavior
        if (i % 10 == 0) {
            std::cout << "\n>>> SCENARIO CHANGE <<<" << std::endl;
            switch ((i / 10) % 4) {
                case 0:
                    std::cout << "Normal driving" << std::endl;
                    ego_speed = 60.0f;
                    collision_risk = 10;
                    warning_active = false;
                    brake_pressure = 0.0f;
                    break;
                case 1:
                    std::cout << "Approaching slower vehicle" << std::endl;
                    ego_speed = 80.0f;
                    collision_risk = 45;
                    warning_active = true;
                    brake_pressure = 20.0f;
                    break;
                case 2:
                    std::cout << "Lane change maneuver" << std::endl;
                    current_lane = (current_lane.load() % 4) + 1;
                    collision_risk = 25;
                    warning_active = false;
                    brake_pressure = 10.0f;
                    break;
                case 3:
                    std::cout << "Emergency braking!" << std::endl;
                    collision_risk = 95;
                    warning_active = true;
                    brake_pressure = 90.0f;
                    ego_speed = ego_speed.load() * 0.8f; // Reduce speed
                    break;
            }
        } else {
            // Gradual changes
            collision_risk = std::max(0, collision_risk.load() - 2);
            if (collision_risk < 30) {
                warning_active = false;
                brake_pressure = std::max(0.0f, brake_pressure.load() - 5.0f);
            }
        }
        
        std::cout << "[Variables can be modified via shared memory interface]" << std::endl;
        
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "\nDemo completed." << std::endl;
    std::cout << "FCW ADAS Demo finished successfully!" << std::endl;
    
    return 0;
}
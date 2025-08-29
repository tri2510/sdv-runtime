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

// Global counter variables (using atomic for thread safety)
std::atomic<int> counter{0};
std::atomic<int> test{0};

// Map to associate variable names with their pointers and types
std::map<std::string, std::pair<void*, std::string>> var_map;

void setup_variable_map() {
    var_map["counter"] = {&counter, "int"};
    var_map["test"] = {&test, "int"};
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

int main() {
    std::cout << "=== Simple Counter App ===" << std::endl;
    std::cout << "Variables 'counter' and 'test' are automatically monitored by Python syncer" << std::endl;
    std::cout << "\nStarting counter..." << std::endl;
    
    setup_variable_map();
    
    // Start shared memory monitoring in background thread
    std::thread shm_thread(shared_memory_loop);
    shm_thread.detach();
    
    for (int i = 0; i < 100; i++) {
        std::cout << "Counter: " << counter.load() << ", Test: " << test.load() << std::endl;
        
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        // Increase counter by 1
        counter++;
    }
    
    std::cout << "\nDemo completed." << std::endl;
    
    return 0;
}
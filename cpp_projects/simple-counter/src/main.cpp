#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>
#include "shm_wrapper.h"

// Global counter variables (using atomic for thread safety)
std::atomic<int> counter{0};
std::atomic<int> test{0};

int main() {
    std::cout << "=== Simple Counter App with Shared Memory ===" << std::endl;
    
    // Initialize shared memory and register variables for monitoring
    INIT_SHM();
    WATCH_VAR(counter, "int");
    WATCH_VAR(test, "int");
    
    std::cout << "Variables 'counter' and 'test' are now monitored via shared memory" << std::endl;
    std::cout << "You can modify these variables through the Kit Manager interface" << std::endl;
    std::cout << "\nStarting counter..." << std::endl;
    
    for (int i = 0; i < 100; i++) {
        std::cout << "Counter: " << counter.load() << ", Test: " << test.load() << std::endl;
        
        // Wait for 1 second
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        // Increase counter by 1
        counter++;
    }
    
    std::cout << "\nDemo completed. Cleaning up shared memory..." << std::endl;
    CLEANUP_SHM();
    
    return 0;
}
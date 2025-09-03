#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Shared memory variables for monitoring
std::atomic<int> counter{0};
std::atomic<double> sensor_value{25.5};

int main() {
    std::cout << "Starting C++ app with memory monitoring..." << std::endl;
    
    for(int i = 0; i < 10; i++) {
        counter.store(i);
        sensor_value.store(25.5 + i * 0.5);
        
        std::cout << "Iteration " << i << ": counter=" << counter.load() 
                  << ", sensor=" << sensor_value.load() << std::endl;
        
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
    
    std::cout << "C++ app finished." << std::endl;
    return 0;
}
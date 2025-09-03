#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>

// Test variables for monitoring
std::atomic<int> counter{0};
std::atomic<float> speed{50.0f};
std::atomic<bool> active{true};

int main() {
    std::cout << "=== Feature 1 Test: Frontend Data Structure Fix ===" << std::endl;
    std::cout << "Testing C++ variable transmission to frontend" << std::endl;
    
    for(int i = 0; i < 20; i++) {
        counter = i;
        speed = 50.0f + (i * 2.5f);
        active = (i % 3) != 0;
        
        std::cout << "Iteration " << i 
                  << ": counter=" << counter 
                  << ", speed=" << speed 
                  << ", active=" << (active ? "true" : "false") << std::endl;
        
        // Sleep for 1 second to allow monitoring
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "=== Test completed ===" << std::endl;
    return 0;
}
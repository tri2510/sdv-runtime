#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Simple global variables for testing
std::atomic<int> test_counter{42};
std::atomic<float> test_value{3.14f};

int main() {
    std::cout << "Simple test program for memory reading" << std::endl;
    
    // Infinite loop to keep process alive for testing
    int i = 0;
    while (true) {
        test_counter = 100 + i;
        test_value = 2.5f + i * 0.1f;
        
        if (i % 10 == 0) {
            std::cout << "Update " << i << ": counter=" << test_counter.load() 
                      << ", value=" << test_value.load() << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        i++;
    }
    
    return 0;
}
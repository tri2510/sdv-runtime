#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Monitoring variables
std::atomic<int> counter{0};
std::atomic<float> sensor_value{25.5f};
std::atomic<bool> system_active{true};

int main() {
    std::cout << "🔧 Basic Memory Monitor Started" << std::endl;
    std::cout << "Variables: counter, sensor_value, system_active" << std::endl;
    
    for (int i = 0; i < 50; ++i) {
        counter = i;
        sensor_value = 25.5f + (i * 0.1f);
        system_active = (i % 2 == 0);
        
        std::cout << "Cycle " << i + 1 << ": counter=" << counter.load() 
                  << ", sensor=" << sensor_value.load() 
                  << ", active=" << (system_active.load() ? "true" : "false") << std::endl;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    std::cout << "✅ Basic monitoring complete" << std::endl;
    return 0;
}
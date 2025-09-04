#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <iomanip>

// Simple monitoring variables for basic demonstration
std::atomic<int> counter{0};
std::atomic<float> sensor_value{25.5f};
std::atomic<bool> system_active{true};
std::atomic<double> precision_measurement{3.14159};
int global_state = 42; // Non-atomic for comparison

void printBanner() {
    std::cout << "╔════════════════════════════════════════════════╗" << std::endl;
    std::cout << "║          SIMPLE MEMORY MONITORING DEMO        ║" << std::endl;
    std::cout << "║            Basic Variable Tracking            ║" << std::endl;
    std::cout << "╚════════════════════════════════════════════════╝" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🚀 Starting simple memory monitoring demonstration..." << std::endl;
    std::cout << "📊 Monitoring variables: counter, sensor_value, system_active, precision_measurement" << std::endl;
    std::cout << "🔧 Running for 30 iterations with realistic value changes\n" << std::endl;
    
    for (int i = 0; i < 30; ++i) {
        // Update variables with realistic patterns
        counter = i;
        sensor_value = 25.5f + (i % 10) * 1.2f; // Oscillate between 25.5 and 36.3
        system_active = (i % 3 != 0); // Toggle every 3 iterations
        precision_measurement = 3.14159 + (i * 0.001); // Slowly increasing precision
        global_state = 42 + i; // Regular int for comparison
        
        // Print current state
        std::cout << "Iteration " << std::setw(2) << i + 1 << ": "
                  << "counter=" << counter.load() << ", "
                  << "sensor=" << sensor_value.load() << ", "
                  << "active=" << (system_active.load() ? "true" : "false") << ", "
                  << "precision=" << precision_measurement.load() << ", "
                  << "state=" << global_state << std::endl;
        
        // Sleep for monitoring
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    std::cout << "\n✅ Simple monitoring demonstration completed!" << std::endl;
    std::cout << "📊 Final values - Counter: " << counter.load() 
              << ", Sensor: " << sensor_value.load() 
              << ", Active: " << (system_active.load() ? "true" : "false") << std::endl;
    
    return 0;
}
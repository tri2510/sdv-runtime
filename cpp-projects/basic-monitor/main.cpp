#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <iomanip>

// Simple atomic variables for basic monitoring test
std::atomic<int> counter{0};
std::atomic<float> temperature{22.5f};
std::atomic<bool> system_active{true};

void printBanner() {
    std::cout << "╔══════════════════════════════════════╗" << std::endl;
    std::cout << "║         BASIC MONITORING TEST        ║" << std::endl;
    std::cout << "║       Single File Project Test       ║" << std::endl;
    std::cout << "╚══════════════════════════════════════╝" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🔧 Testing single-file C++ project compilation..." << std::endl;
    std::cout << "📊 Monitoring: counter, temperature, system_active" << std::endl;
    std::cout << "⏱️  Running for 25 seconds with 200ms intervals\n" << std::endl;
    
    for (int i = 0; i < 125; ++i) {
        // Update variables with simple patterns
        counter = i;
        temperature = 22.5f + (i % 20) * 0.3f; // Oscillate between 22.5-28.5°C
        system_active = (i % 5 != 0); // Toggle pattern
        
        // Print every 10 cycles to reduce output spam
        if (i % 10 == 0) {
            std::cout << std::fixed << std::setprecision(1)
                      << "Cycle " << std::setw(3) << i << ": "
                      << "counter=" << counter.load() << ", "
                      << "temp=" << temperature.load() << "°C, "
                      << "active=" << (system_active.load() ? "true" : "false")
                      << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    std::cout << "\n✅ Basic monitoring test completed!" << std::endl;
    std::cout << "📈 Final: counter=" << counter.load()
              << ", temp=" << temperature.load()
              << ", active=" << (system_active.load() ? "true" : "false") << std::endl;
    
    return 0;
}
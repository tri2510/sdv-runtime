#include "engine_controller.h"
#include <iostream>
#include <iomanip>
#include <cmath>
#include <algorithm>

namespace Engine {
    // Define atomic variables
    std::atomic<float> rpm{800.0f};
    std::atomic<float> oil_pressure{2.5f};
    std::atomic<bool> engine_running{true};
    std::atomic<int> engine_temp{85};
    
    void initialize() {
        std::cout << "🔧 Engine Controller initialized" << std::endl;
        engine_running = true;
    }
    
    void update(int cycle) {
        // Simulate engine behavior
        rpm = 800.0f + std::sin(cycle * 0.1f) * 1200.0f; // 800-2000 RPM
        oil_pressure = 2.5f + (rpm.load() / 1000.0f) * 0.8f; // Pressure correlates with RPM
        engine_temp = 85 + (cycle % 40); // Temperature oscillation
        
        // Engine running logic
        if (cycle > 80 && cycle < 85) {
            engine_running = false; // Simulate brief engine stop
        } else {
            engine_running = true;
        }
    }
    
    void printStatus() {
        std::cout << std::fixed << std::setprecision(1)
                  << "🏎️  RPM: " << rpm.load() << " | "
                  << "Oil: " << oil_pressure.load() << " bar | "
                  << "Temp: " << engine_temp.load() << "°C | "
                  << "Running: " << (engine_running.load() ? "YES" : "NO")
                  << std::endl;
    }
}
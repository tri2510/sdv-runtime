#include "sensor_manager.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <iomanip>

void printBanner() {
    std::cout << "╔═══════════════════════════════════════════╗" << std::endl;
    std::cout << "║        MODULAR SYSTEM MONITORING         ║" << std::endl;
    std::cout << "║      Header/Source Split Test Project    ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════╝" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🔧 Testing modular C++ project with header/source separation..." << std::endl;
    std::cout << "📊 Monitoring: lidar_distance, object_count, emergency_brake, gps_latitude, battery_voltage" << std::endl;
    std::cout << "⏱️  Running for 30 seconds with 300ms intervals\n" << std::endl;
    
    SensorManager::initialize();
    
    for (int cycle = 0; cycle < 100; ++cycle) {
        SensorManager::updateSensors(cycle);
        
        // Print status every 8 cycles
        if (cycle % 8 == 0) {
            std::cout << "Cycle " << std::setw(3) << cycle << ": ";
            SensorManager::printStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
    
    std::cout << "\n✅ Modular system monitoring test completed!" << std::endl;
    std::cout << "📊 Final sensor readings:" << std::endl;
    SensorManager::printStatus();
    
    return 0;
}
#include "engine_controller.h"
#include "vehicle_control.h"
#include "data_logger.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <iomanip>

void printBanner() {
    std::cout << "╔═══════════════════════════════════════════════╗" << std::endl;
    std::cout << "║      CMAKE MULTI-DIRECTORY PROJECT TEST      ║" << std::endl;
    std::cout << "║         Advanced Build System Test           ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════════╝" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🔧 Testing CMake multi-directory project..." << std::endl;
    std::cout << "📊 Monitoring across namespaces: Engine::, Control::, Utils::" << std::endl;
    std::cout << "📊 Variables: rpm, oil_pressure, engine_running, engine_temp," << std::endl;
    std::cout << "             steering_angle, throttle_position, brake_applied, gear_position," << std::endl;
    std::cout << "             log_entries, logging_active, disk_usage" << std::endl;
    std::cout << "⏱️  Running for 35 seconds with 350ms intervals\n" << std::endl;
    
    // Initialize all subsystems
    Engine::initialize();
    Control::initialize();
    Utils::initialize();
    
    for (int cycle = 0; cycle < 100; ++cycle) {
        // Update all subsystems
        Engine::update(cycle);
        Control::update(cycle);
        Utils::update(cycle);
        
        // Print comprehensive status every 12 cycles
        if (cycle % 12 == 0) {
            std::cout << "\n--- Cycle " << std::setw(3) << cycle << " ---" << std::endl;
            Engine::printStatus();
            Control::printStatus();
            Utils::printStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(350));
    }
    
    std::cout << "\n✅ CMake multi-directory project test completed!" << std::endl;
    std::cout << "📊 Final system status:" << std::endl;
    Engine::printStatus();
    Control::printStatus();
    Utils::printStatus();
    
    return 0;
}
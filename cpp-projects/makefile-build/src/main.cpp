#include "network_monitor.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <iomanip>

void printBanner() {
    std::cout << "╔═══════════════════════════════════════════╗" << std::endl;
    std::cout << "║         MAKEFILE BUILD SYSTEM TEST       ║" << std::endl;
    std::cout << "║        Network Monitoring Simulation     ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════╝" << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🔧 Testing Makefile-based build system..." << std::endl;
    std::cout << "📊 Monitoring: packets_sent, packets_received, connection_active, bandwidth_usage, ping_latency" << std::endl;
    std::cout << "⏱️  Running for 40 seconds with 400ms intervals\n" << std::endl;
    
    Network::initialize();
    
    for (int cycle = 0; cycle < 100; ++cycle) {
        Network::simulateNetworkActivity(cycle);
        
        // Print status every 10 cycles
        if (cycle % 10 == 0) {
            std::cout << "Cycle " << std::setw(3) << cycle << ": ";
            Network::printStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(400));
    }
    
    std::cout << "\n✅ Makefile build system test completed!" << std::endl;
    std::cout << "📊 Final network status:" << std::endl;
    Network::printStatus();
    
    return 0;
}
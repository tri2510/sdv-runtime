#include "network_monitor.h"
#include <iostream>
#include <iomanip>
#include <random>

namespace Network {
    // Define atomic variables
    std::atomic<int> packets_sent{0};
    std::atomic<int> packets_received{0};
    std::atomic<bool> connection_active{true};
    std::atomic<float> bandwidth_usage{0.0f};
    std::atomic<int> ping_latency{25};
    
    void initialize() {
        std::cout << "🌐 Network Monitor initialized" << std::endl;
        connection_active = true;
        packets_sent = 0;
        packets_received = 0;
    }
    
    void simulateNetworkActivity(int cycle) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> packet_dist(5, 50);
        static std::uniform_real_distribution<float> bandwidth_dist(0.1f, 95.5f);
        static std::uniform_int_distribution<> ping_dist(15, 150);
        
        // Simulate network activity
        int new_packets = packet_dist(gen);
        packets_sent = packets_sent.load() + new_packets;
        packets_received = packets_received.load() + (new_packets * 0.95f); // 5% packet loss
        
        bandwidth_usage = bandwidth_dist(gen);
        ping_latency = ping_dist(gen);
        
        // Simulate occasional disconnections
        if (cycle % 45 == 0 && cycle > 0) {
            connection_active = false;
        } else if (cycle % 45 == 3) {
            connection_active = true;
        }
    }
    
    void printStatus() {
        std::cout << std::fixed << std::setprecision(1)
                  << "🌐 Sent: " << packets_sent.load() << " | "
                  << "Rcvd: " << packets_received.load() << " | "
                  << "Connected: " << (connection_active.load() ? "YES" : "NO") << " | "
                  << "BW: " << bandwidth_usage.load() << "% | "
                  << "Ping: " << ping_latency.load() << "ms"
                  << std::endl;
    }
}
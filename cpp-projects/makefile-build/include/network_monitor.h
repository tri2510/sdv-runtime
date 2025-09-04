#pragma once
#include <atomic>
#include <string>

namespace Network {
    // Network monitoring variables
    extern std::atomic<int> packets_sent;
    extern std::atomic<int> packets_received;
    extern std::atomic<bool> connection_active;
    extern std::atomic<float> bandwidth_usage;
    extern std::atomic<int> ping_latency;
    
    void initialize();
    void simulateNetworkActivity(int cycle);
    void printStatus();
}
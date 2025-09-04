#pragma once
#include <atomic>

namespace Utils {
    // Data logging variables
    extern std::atomic<int> log_entries;
    extern std::atomic<bool> logging_active;
    extern std::atomic<float> disk_usage;
    
    void initialize();
    void update(int cycle);
    void printStatus();
}
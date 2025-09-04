#pragma once
#include <atomic>

namespace Engine {
    // Engine monitoring variables
    extern std::atomic<float> rpm;
    extern std::atomic<float> oil_pressure;
    extern std::atomic<bool> engine_running;
    extern std::atomic<int> engine_temp;
    
    void initialize();
    void update(int cycle);
    void printStatus();
}
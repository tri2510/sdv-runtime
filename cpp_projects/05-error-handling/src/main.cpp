#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <random>

// System monitoring variables
std::atomic<int> error_count{0};
std::atomic<bool> critical_error{false};
std::atomic<float> memory_usage{45.0f};
std::atomic<float> cpu_usage{20.0f};
std::atomic<int> network_latency{15};
std::atomic<bool> recovery_mode{false};
std::atomic<bool> system_stable{true};

void simulateErrors() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.0, 1.0);
    
    for (int cycle = 0; cycle < 25; ++cycle) {
        // Gradually increase system stress
        memory_usage = 45.0f + cycle * 2.0f;
        cpu_usage = 20.0f + cycle * 1.5f;
        network_latency = 15 + cycle;
        
        // Introduce errors at various points
        bool error_occurred = false;
        
        if (cycle == 8) {
            std::cout << "SIMULATED ERROR: Memory allocation failure" << std::endl;
            error_count++;
            memory_usage = 95.0f;
            error_occurred = true;
        }
        
        if (cycle == 15) {
            std::cout << "SIMULATED ERROR: Network timeout" << std::endl;
            error_count++;
            network_latency = 500;
            error_occurred = true;
        }
        
        if (cycle == 20) {
            std::cout << "CRITICAL ERROR: System overload detected" << std::endl;
            critical_error = true;
            recovery_mode = true;
            cpu_usage = 98.0f;
            system_stable = false;
            error_occurred = true;
        }
        
        // Recovery logic
        if (recovery_mode.load() && cycle > 22) {
            std::cout << "RECOVERY: Reducing system load" << std::endl;
            memory_usage = std::max(50.0f, memory_usage - 10.0f);
            cpu_usage = std::max(30.0f, cpu_usage - 15.0f);
            network_latency = std::max(20, network_latency - 50);
            
            if (memory_usage < 60.0f && cpu_usage < 50.0f) {
                critical_error = false;
                system_stable = true;
                recovery_mode = false;
                std::cout << "RECOVERY COMPLETE: System stabilized" << std::endl;
            }
        }
        
        std::cout << "Cycle " << cycle + 1 << ": ";
        std::cout << "Mem=" << std::fixed << std::setprecision(1) << memory_usage.load() << "%, ";
        std::cout << "CPU=" << cpu_usage.load() << "%, ";
        std::cout << "Latency=" << network_latency.load() << "ms, ";
        std::cout << "Errors=" << error_count.load();
        
        if (critical_error.load()) {
            std::cout << " [CRITICAL]";
        }
        if (recovery_mode.load()) {
            std::cout << " [RECOVERY]";
        }
        if (!system_stable.load()) {
            std::cout << " [UNSTABLE]";
        }
        
        std::cout << std::endl;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

int main() {
    std::cout << "Error Handling and Recovery System" << std::endl;
    std::cout << "Monitoring: error_count, critical_error, memory_usage, cpu_usage, recovery_mode" << std::endl;
    
    try {
        simulateErrors();
    } catch (const std::exception& e) {
        std::cerr << "Exception caught: " << e.what() << std::endl;
        critical_error = true;
        error_count++;
    }
    
    std::cout << "Final system state:" << std::endl;
    std::cout << "- Total errors: " << error_count.load() << std::endl;
    std::cout << "- Critical error: " << (critical_error.load() ? "Yes" : "No") << std::endl;
    std::cout << "- System stable: " << (system_stable.load() ? "Yes" : "No") << std::endl;
    std::cout << "Error handling simulation complete" << std::endl;
    
    return 0;
}
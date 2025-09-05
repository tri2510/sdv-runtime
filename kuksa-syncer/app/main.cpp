#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <stdexcept>
#include <vector>
#include <random>

// Error simulation variables
std::atomic<int> error_counter{0};
std::atomic<bool> system_healthy{true};
std::atomic<float> memory_usage{0.0f};
std::atomic<int> failed_operations{0};
std::atomic<bool> recovery_mode{false};

class SystemException : public std::exception {
public:
    explicit SystemException(const std::string& msg) : message(msg) {}
    const char* what() const noexcept override { return message.c_str(); }
private:
    std::string message;
};

void simulateMemoryPressure() {
    std::vector<std::vector<int>> memory_hog;
    
    for (int i = 0; i < 10; ++i) {
        try {
            // Simulate memory allocation
            memory_hog.emplace_back(1000000, i);
            memory_usage = i * 10.0f;
            
            std::cout << \"💾 Allocated memory block \" << i + 1 << \"/10 (\" 
                      << memory_usage.load() << \"% usage)\
\";
            
            if (memory_usage.load() > 70.0f) {
                system_healthy = false;
                recovery_mode = true;
                throw SystemException(\"Memory pressure detected\");
            }
            
        } catch (const SystemException& e) {
            error_counter++;
            failed_operations++;
            std::cout << \"❌ Error \" << error_counter.load() << \": \" << e.what() << \"\
\";
            
            // Recovery: free some memory
            if (memory_hog.size() > 5) {
                memory_hog.erase(memory_hog.begin(), memory_hog.begin() + 3);
                memory_usage = memory_usage.load() * 0.6f;
                std::cout << \"🔧 Recovery: Memory freed, usage now \" 
                          << memory_usage.load() << \"%\
\";
            }
            
        } catch (const std::exception& e) {
            error_counter++;
            std::cout << \"💥 Unexpected error: \" << e.what() << \"\
\";
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

void randomFailureSimulation() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    
    for (int test = 0; test < 20; ++test) {
        int random_val = dis(gen);
        
        try {
            if (random_val < 15) {  // 15% failure rate
                throw std::runtime_error(\"Random system fault\");
            }
            
            if (random_val < 25) {  // Additional 10% warning
                system_healthy = false;
                std::cout << \"⚠️  System warning: performance degraded\
\";
            } else {
                system_healthy = true;
            }
            
            std::cout << \"✓ Test \" << test + 1 << \"/20 passed\
\";
            
        } catch (const std::exception& e) {
            error_counter++;
            failed_operations++;
            std::cout << \"❌ Test \" << test + 1 << \"/20 failed: \" << e.what() << \"\
\";
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }
}

int main() {
    std::cout << \"🧪 Error Handling and Recovery Test\
\";
    std::cout << \"📊 Monitoring: error_counter, system_healthy, memory_usage, failed_operations, recovery_mode\
\";
    
    try {
        std::cout << \"\
--- Phase 1: Memory Pressure Test ---\
\";
        simulateMemoryPressure();
        
        std::cout << \"\
--- Phase 2: Random Failure Test ---\
\";
        randomFailureSimulation();
        
        // Final recovery
        if (error_counter.load() > 0) {
            recovery_mode = true;
            std::cout << \"\
🔄 Initiating system recovery...\
\";
            std::this_thread::sleep_for(std::chrono::seconds(1));
            
            system_healthy = true;
            recovery_mode = false;
            memory_usage = 10.0f; // Reset to normal
            std::cout << \"✅ System recovery complete\
\";
        }
        
    } catch (const std::exception& e) {
        std::cout << \"💥 Fatal error: \" << e.what() << \"\
\";
        return 1;
    }
    
    std::cout << \"\
📈 Test Summary:\
\";
    std::cout << \"  Total errors: \" << error_counter.load() << \"\
\";
    std::cout << \"  Failed operations: \" << failed_operations.load() << \"\
\";
    std::cout << \"  Final system status: \" 
              << (system_healthy.load() ? \"HEALTHY\" : \"DEGRADED\") << \"\
\";
    std::cout << \"  Memory usage: \" << memory_usage.load() << \"%\
\";
    
    return 0;
}

#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <vector>
#include <mutex>
#include <condition_variable>

// ECU shared variables across threads
std::atomic<float> engine_load{0.0f};
std::atomic<float> throttle_position{0.0f};
std::atomic<float> brake_pressure{0.0f};
std::atomic<int> engine_temp{85};
std::atomic<int> oil_pressure{45};
std::atomic<bool> check_engine{false};
std::atomic<bool> system_ready{false};

// Thread synchronization
std::mutex log_mutex;
std::condition_variable cv;
bool stop_simulation = false;

void engineControlThread() {
    for (int i = 0; i < 25; ++i) {
        if (stop_simulation) break;
        
        engine_load = 20.0f + (i % 10) * 8.0f;
        throttle_position = engine_load * 1.2f;
        engine_temp = 85 + (engine_load > 80.0f ? 15 : 5);
        
        check_engine = (engine_temp > 100 || engine_load > 95.0f);
        
        {
            std::lock_guard<std::mutex> lock(log_mutex);
            std::cout << "[ENGINE] Cycle " << i + 1 
                      << ": Load=" << engine_load.load() << "%, "
                      << "Throttle=" << throttle_position.load() << "%, "
                      << "Temp=" << engine_temp.load() << "°C";
            if (check_engine.load()) {
                std::cout << " [CHECK_ENGINE]";
            }
            std::cout << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

void brakeSystemThread() {
    for (int i = 0; i < 20; ++i) {
        if (stop_simulation) break;
        
        brake_pressure = (i % 5 == 0) ? 80.0f + i * 2.0f : 10.0f + i * 1.5f;
        oil_pressure = brake_pressure > 50.0f ? 55 : 45;
        
        {
            std::lock_guard<std::mutex> lock(log_mutex);
            std::cout << "[BRAKE] Cycle " << i + 1 
                      << ": Pressure=" << brake_pressure.load() << "psi, "
                      << "Oil=" << oil_pressure.load() << "psi" << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(250));
    }
}

void diagnosticsThread() {
    for (int i = 0; i < 15; ++i) {
        if (stop_simulation) break;
        
        bool all_systems_ok = !check_engine.load() && 
                             engine_temp.load() < 100 && 
                             oil_pressure.load() > 40;
        
        system_ready = all_systems_ok;
        
        {
            std::lock_guard<std::mutex> lock(log_mutex);
            std::cout << "[DIAG] System Status: " 
                      << (system_ready.load() ? "READY" : "WARNING")
                      << " (Engine:" << engine_temp.load() 
                      << "°C, Oil:" << oil_pressure.load() << "psi)" << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(400));
    }
}

int main() {
    std::cout << "Multi-threaded ECU Simulation" << std::endl;
    std::cout << "Monitoring across 3 threads: engine_load, throttle_position, brake_pressure, engine_temp" << std::endl;
    
    std::vector<std::thread> threads;
    
    threads.emplace_back(engineControlThread);
    threads.emplace_back(brakeSystemThread);
    threads.emplace_back(diagnosticsThread);
    
    // Let threads run for a while
    std::this_thread::sleep_for(std::chrono::seconds(6));
    
    {
        std::lock_guard<std::mutex> lock(log_mutex);
        std::cout << "Stopping ECU simulation..." << std::endl;
    }
    
    stop_simulation = true;
    
    for (auto& thread : threads) {
        if (thread.joinable()) {
            thread.join();
        }
    }
    
    std::cout << "ECU simulation complete" << std::endl;
    return 0;
}
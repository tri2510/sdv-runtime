#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <array>
#include <cmath>

// Complex nested namespaces with global variables
// Demonstrating ptrace monitoring with namespace organization

namespace Vehicle {
    namespace Monitoring {
        // Global monitoring variables
        std::atomic<uint64_t> system_uptime{0};        // milliseconds
        std::atomic<uint32_t> total_errors{0};
        std::atomic<uint16_t> active_warnings{0};
        std::atomic<uint8_t> system_health{100};       // 0-100%
        std::atomic<bool> diagnostics_active{false};
        std::atomic<float> cpu_usage{0.0f};           // 0-100%
        std::atomic<float> memory_usage{0.0f};        // 0-100%
        std::atomic<int16_t> system_temperature{250}; // Celsius * 10
        
        void updateMonitoring(int cycle) {
            system_uptime.fetch_add(100); // +100ms per cycle
            
            // Simulate CPU usage
            cpu_usage.store(30.0f + 20.0f * sin(cycle * 0.1f));
            
            // Simulate memory usage
            memory_usage.store(45.0f + 15.0f * cos(cycle * 0.05f));
            
            // System temperature
            system_temperature.store(250 + static_cast<int16_t>(sin(cycle * 0.08f) * 100));
            
            // Error simulation
            if (cycle % 200 == 0) {
                total_errors.fetch_add(1);
            }
            
            // Warning simulation
            active_warnings.store(static_cast<uint16_t>((cycle % 50) / 10));
            
            // Health calculation
            float health = 100.0f - (cpu_usage.load() * 0.2f) - (memory_usage.load() * 0.1f);
            system_health.store(static_cast<uint8_t>(std::max(0.0f, std::min(100.0f, health))));
            
            diagnostics_active.store((cycle % 100) < 10);
        }
    }
    
    namespace Powertrain {
        // Engine global variables
        std::atomic<uint16_t> engine_rpm{0};
        std::atomic<float> engine_torque{0.0f};       // Nm
        std::atomic<float> fuel_consumption{0.0f};    // L/100km
        std::atomic<float> oil_pressure{0.0f};        // bar
        std::atomic<int16_t> oil_temperature{0};      // Celsius
        std::atomic<int16_t> coolant_temperature{0};  // Celsius
        std::atomic<bool> engine_fault{false};
        std::atomic<uint8_t> emission_level{0};       // 0-5
        
        void updateEngine(int cycle) {
            engine_rpm.store(800 + static_cast<uint16_t>((cycle * 73) % 6200));
            engine_torque.store(50.0f + 150.0f * sin(cycle * 0.2f));
            fuel_consumption.store(5.0f + 8.0f * (engine_rpm.load() / 6000.0f));
            oil_pressure.store(2.0f + 3.0f * (engine_rpm.load() / 6000.0f));
            oil_temperature.store(60 + static_cast<int16_t>(cycle * 0.1f) % 40);
            coolant_temperature.store(70 + static_cast<int16_t>(cycle * 0.08f) % 30);
            engine_fault.store((cycle % 500) < 5);
            emission_level.store((cycle / 100) % 6);
        }
        
        // Transmission global variables
        std::atomic<uint8_t> current_gear{0};
        std::atomic<float> gear_ratio{0.0f};
        std::atomic<int16_t> transmission_temp{0};    // Celsius
        std::atomic<bool> clutch_engaged{true};
        std::atomic<uint8_t> shift_mode{0};           // 0=Economy, 1=Normal, 2=Sport
        std::atomic<bool> transmission_fault{false};
        
        void updateTransmission(int cycle) {
            current_gear.store((cycle / 50) % 8);
            
            float ratios[] = {3.82f, 2.20f, 1.52f, 1.13f, 0.86f, 0.69f, 0.56f, 0.48f};
            gear_ratio.store(ratios[current_gear.load() % 8]);
            
            transmission_temp.store(50 + static_cast<int16_t>(cycle * 0.05f) % 60);
            clutch_engaged.store((cycle % 20) > 2);
            shift_mode.store((cycle / 200) % 3);
            transmission_fault.store((cycle % 1000) < 3);
        }
    }
    
    namespace Safety {
        // Emergency systems global variables
        std::atomic<bool> abs_active{false};
        std::atomic<bool> esp_active{false};
        std::atomic<bool> tcs_active{false};          // Traction control
        std::atomic<uint8_t> airbag_status{0};        // Bitmap of airbag states
        std::atomic<bool> seatbelt_warning{false};
        std::atomic<bool> emergency_brake{false};
        std::atomic<float> impact_sensor_x{0.0f};     // G-force
        std::atomic<float> impact_sensor_y{0.0f};
        std::atomic<float> impact_sensor_z{0.0f};
        std::atomic<bool> fire_detected{false};
        std::atomic<bool> rollover_detected{false};
        std::atomic<uint16_t> safety_score{1000};     // 0-1000
        
        void updateEmergencySystems(int cycle) {
            abs_active.store((cycle % 30) < 3);
            esp_active.store((cycle % 40) < 2);
            tcs_active.store((cycle % 25) < 4);
            
            airbag_status.store(cycle % 256);
            seatbelt_warning.store((cycle % 100) < 20);
            emergency_brake.store((cycle % 200) < 5);
            
            impact_sensor_x.store(sin(cycle * 0.3f) * 0.5f);
            impact_sensor_y.store(cos(cycle * 0.2f) * 0.3f);
            impact_sensor_z.store(sin(cycle * 0.1f) * 0.2f);
            
            fire_detected.store((cycle % 2000) < 2);
            rollover_detected.store((cycle % 3000) < 1);
            
            // Calculate safety score
            int score = 1000;
            if (abs_active.load()) score -= 50;
            if (esp_active.load()) score -= 75;
            if (emergency_brake.load()) score -= 200;
            if (fire_detected.load()) score -= 500;
            if (rollover_detected.load()) score -= 400;
            safety_score.store(std::max(0, score));
        }
    }
}

void printSystemStatus() {
    using namespace Vehicle;
    
    std::cout << "\n=== Complex Vehicle System Status (Global Variables) ===" << std::endl;
    
    std::cout << "System Monitoring:" << std::endl;
    std::cout << "  Uptime: " << Monitoring::system_uptime.load() << " ms" << std::endl;
    std::cout << "  CPU: " << Monitoring::cpu_usage.load() << "%" << std::endl;
    std::cout << "  Health: " << (int)Monitoring::system_health.load() << "%" << std::endl;
    
    std::cout << "Powertrain:" << std::endl;
    std::cout << "  RPM: " << Powertrain::engine_rpm.load() << std::endl;
    std::cout << "  Gear: " << (int)Powertrain::current_gear.load() << std::endl;
    std::cout << "  Torque: " << Powertrain::engine_torque.load() << " Nm" << std::endl;
    
    std::cout << "Safety Systems:" << std::endl;
    std::cout << "  Safety Score: " << Safety::safety_score.load() << "/1000" << std::endl;
    std::cout << "  ABS: " << (Safety::abs_active.load() ? "Active" : "Inactive") << std::endl;
    std::cout << "  ESP: " << (Safety::esp_active.load() ? "Active" : "Inactive") << std::endl;
}

int main() {
    std::cout << "Complex Vehicle System Monitor Starting (Global Variables Demo)" << std::endl;
    std::cout << "Monitoring " << 45 << " global variables in nested namespaces..." << std::endl;
    
    int cycle = 0;
    while (true) {
        using namespace Vehicle;
        
        // Update all subsystems
        Monitoring::updateMonitoring(cycle);
        Powertrain::updateEngine(cycle);
        Powertrain::updateTransmission(cycle);
        Safety::updateEmergencySystems(cycle);
        
        if (cycle % 10 == 0) {
            printSystemStatus();
        }
        
        cycle++;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    
    return 0;
}
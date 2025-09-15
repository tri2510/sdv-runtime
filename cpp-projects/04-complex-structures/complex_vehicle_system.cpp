#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <array>
#include <cmath>

// Complex nested namespaces with global variables - SDV minimal types
// Demonstrating ptrace monitoring with namespace organization
// CONSTRAINT: Only int, char, float, double, bool and their atomic variants

namespace Vehicle {
    namespace Monitoring {
        // Global monitoring variables using SDV minimal types
        std::atomic<int> system_uptime{0};           // seconds (reduced precision)
        std::atomic<int> total_errors{0};
        std::atomic<int> active_warnings{0};
        std::atomic<int> system_health{100};         // 0-100%
        std::atomic<bool> diagnostics_active{false};
        std::atomic<float> cpu_usage{0.0f};         // 0-100%
        std::atomic<float> memory_usage{0.0f};      // 0-100%
        char system_temperature{25};                 // Celsius (-128 to +127 range)
        
        void updateMonitoring(int cycle) {
            system_uptime.fetch_add(1); // +1 second per cycle

            // Simulate CPU usage
            cpu_usage.store(30.0f + 20.0f * sin(cycle * 0.1f));

            // Simulate memory usage
            memory_usage.store(45.0f + 15.0f * cos(cycle * 0.05f));

            // System temperature (char range: -128 to +127)
            system_temperature = 25 + static_cast<char>(sin(cycle * 0.08f) * 50);

            // Error simulation
            if (cycle % 200 == 0) {
                total_errors.fetch_add(1);
            }

            // Warning simulation
            active_warnings.store((cycle % 50) / 10);

            // Health calculation
            float health = 100.0f - (cpu_usage.load() * 0.2f) - (memory_usage.load() * 0.1f);
            system_health.store(static_cast<int>(std::max(0.0f, std::min(100.0f, health))));

            diagnostics_active.store((cycle % 100) < 10);
        }
    }
    
    namespace Powertrain {
        // Engine global variables using SDV minimal types
        std::atomic<int> engine_rpm{0};
        std::atomic<float> engine_torque{0.0f};       // Nm
        std::atomic<float> fuel_consumption{0.0f};    // L/100km
        std::atomic<float> oil_pressure{0.0f};        // bar
        char oil_temperature{0};                      // Celsius (-128 to +127)
        char coolant_temperature{0};                  // Celsius (-128 to +127)
        std::atomic<bool> engine_fault{false};
        int emission_level{0};                        // 0-5
        
        void updateEngine(int cycle) {
            engine_rpm.store(800 + ((cycle * 73) % 6200));
            engine_torque.store(50.0f + 150.0f * sin(cycle * 0.2f));
            fuel_consumption.store(5.0f + 8.0f * (engine_rpm.load() / 6000.0f));
            oil_pressure.store(2.0f + 3.0f * (engine_rpm.load() / 6000.0f));
            oil_temperature = 60 + static_cast<char>((cycle * 0.1f)) % 40;
            coolant_temperature = 70 + static_cast<char>((cycle * 0.08f)) % 30;
            engine_fault.store((cycle % 500) < 5);
            emission_level = (cycle / 100) % 6;
        }
        
        // Transmission global variables using SDV minimal types
        int current_gear{0};
        std::atomic<float> gear_ratio{0.0f};
        char transmission_temp{0};                    // Celsius (-128 to +127)
        std::atomic<bool> clutch_engaged{true};
        int shift_mode{0};                            // 0=Economy, 1=Normal, 2=Sport
        std::atomic<bool> transmission_fault{false};
        
        void updateTransmission(int cycle) {
            current_gear = (cycle / 50) % 8;

            float ratios[] = {3.82f, 2.20f, 1.52f, 1.13f, 0.86f, 0.69f, 0.56f, 0.48f};
            gear_ratio.store(ratios[current_gear % 8]);

            transmission_temp = 50 + static_cast<char>((cycle * 0.05f)) % 60;
            clutch_engaged.store((cycle % 20) > 2);
            shift_mode = (cycle / 200) % 3;
            transmission_fault.store((cycle % 1000) < 3);
        }
    }
    
    namespace Safety {
        // Emergency systems global variables using SDV minimal types
        std::atomic<bool> abs_active{false};
        std::atomic<bool> esp_active{false};
        std::atomic<bool> tcs_active{false};          // Traction control
        int airbag_status{0};                         // Bitmap of airbag states
        std::atomic<bool> seatbelt_warning{false};
        std::atomic<bool> emergency_brake{false};
        std::atomic<float> impact_sensor_x{0.0f};     // G-force
        std::atomic<float> impact_sensor_y{0.0f};
        std::atomic<float> impact_sensor_z{0.0f};
        std::atomic<bool> fire_detected{false};
        std::atomic<bool> rollover_detected{false};
        int safety_score{1000};                      // 0-1000
        
        void updateEmergencySystems(int cycle) {
            abs_active.store((cycle % 30) < 3);
            esp_active.store((cycle % 40) < 2);
            tcs_active.store((cycle % 25) < 4);

            airbag_status = cycle % 256;
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
            safety_score = std::max(0, score);
        }
    }
}

void printSystemStatus() {
    using namespace Vehicle;

    std::cout << "\n=== Complex Vehicle System Status (SDV Minimal Types) ===" << std::endl;

    std::cout << "System Monitoring:" << std::endl;
    std::cout << "  Uptime: " << Monitoring::system_uptime.load() << " seconds" << std::endl;
    std::cout << "  CPU: " << Monitoring::cpu_usage.load() << "%" << std::endl;
    std::cout << "  Health: " << Monitoring::system_health.load() << "%" << std::endl;
    std::cout << "  Temperature: " << (int)Monitoring::system_temperature << "°C" << std::endl;

    std::cout << "Powertrain:" << std::endl;
    std::cout << "  RPM: " << Powertrain::engine_rpm.load() << std::endl;
    std::cout << "  Gear: " << Powertrain::current_gear << std::endl;
    std::cout << "  Torque: " << Powertrain::engine_torque.load() << " Nm" << std::endl;
    std::cout << "  Oil Temp: " << (int)Powertrain::oil_temperature << "°C" << std::endl;

    std::cout << "Safety Systems:" << std::endl;
    std::cout << "  Safety Score: " << Safety::safety_score << "/1000" << std::endl;
    std::cout << "  ABS: " << (Safety::abs_active.load() ? "Active" : "Inactive") << std::endl;
    std::cout << "  ESP: " << (Safety::esp_active.load() ? "Active" : "Inactive") << std::endl;
}

int main() {
    std::cout << "Complex Vehicle System Monitor Starting (SDV Minimal Types)" << std::endl;
    std::cout << "Monitoring global variables using SDV-compatible types (int, char, float, double, bool, atomic variants)..." << std::endl;
    
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
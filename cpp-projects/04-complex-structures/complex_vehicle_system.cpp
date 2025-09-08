#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <array>
#include <cmath>

namespace Vehicle {
    namespace Monitoring {
        class SystemMonitor {
        public:
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
        };
    }
    
    namespace Powertrain {
        class EngineSystem {
        public:
            std::atomic<uint16_t> engine_rpm{0};
            std::atomic<float> engine_load{0.0f};         // 0-100%
            std::atomic<int8_t> coolant_temp{90};         // Celsius
            std::atomic<uint16_t> manifold_pressure{1000}; // mbar
            std::atomic<float> fuel_flow_rate{0.0f};      // L/h
            std::atomic<bool> turbo_active{false};
            std::atomic<uint8_t> throttle_position{0};    // 0-100%
            
            void updateEngine(int cycle) {
                // Engine RPM simulation
                engine_rpm.store(800 + static_cast<uint16_t>((cycle % 100) * 50));
                
                // Engine load
                engine_load.store(20.0f + 30.0f * sin(cycle * 0.12f));
                
                // Coolant temperature
                coolant_temp.store(85 + static_cast<int8_t>(sin(cycle * 0.02f) * 15));
                
                // Manifold pressure (turbo simulation)
                if (engine_load.load() > 40.0f) {
                    turbo_active.store(true);
                    manifold_pressure.store(1500 + static_cast<uint16_t>(engine_load.load() * 10));
                } else {
                    turbo_active.store(false);
                    manifold_pressure.store(1000 + static_cast<uint16_t>(engine_load.load() * 5));
                }
                
                // Fuel flow rate
                fuel_flow_rate.store(engine_load.load() * 0.3f + engine_rpm.load() * 0.01f);
                
                // Throttle position
                throttle_position.store(static_cast<uint8_t>(engine_load.load() * 0.8f));
            }
        };
        
        class TransmissionSystem {
        public:
            std::atomic<uint8_t> current_gear{1};
            std::atomic<float> gear_ratio{3.5f};
            std::atomic<int16_t> transmission_temp{450};   // Celsius * 10  
            std::atomic<uint16_t> torque_converter_rpm{0};
            std::atomic<bool> lock_up_engaged{false};
            std::atomic<float> transmission_efficiency{0.95f};
            
            void updateTransmission(int cycle) {
                // Gear selection simulation
                float engine_load = 30.0f + 20.0f * sin(cycle * 0.1f); // Simulated load
                
                if (engine_load < 20.0f) current_gear.store(1);
                else if (engine_load < 40.0f) current_gear.store(2);
                else if (engine_load < 60.0f) current_gear.store(3);
                else if (engine_load < 80.0f) current_gear.store(4);
                else current_gear.store(5);
                
                // Gear ratio based on current gear
                switch (current_gear.load()) {
                    case 1: gear_ratio.store(3.5f); break;
                    case 2: gear_ratio.store(2.1f); break;
                    case 3: gear_ratio.store(1.4f); break;
                    case 4: gear_ratio.store(1.0f); break;
                    case 5: gear_ratio.store(0.8f); break;
                }
                
                // Transmission temperature
                transmission_temp.store(450 + static_cast<int16_t>(sin(cycle * 0.03f) * 200));
                
                // Torque converter
                torque_converter_rpm.store(800 + static_cast<uint16_t>((cycle % 150) * 20));
                
                // Lock-up clutch
                lock_up_engaged.store(current_gear.load() >= 3 && engine_load > 30.0f);
                
                // Efficiency calculation
                float base_eff = 0.95f;
                if (lock_up_engaged.load()) base_eff += 0.03f;
                transmission_efficiency.store(std::max(0.85f, std::min(0.98f, 
                    base_eff - (transmission_temp.load() - 450) * 0.0001f)));
            }
        };
    }
    
    namespace Safety {
        class EmergencySystems {
        public:
            std::atomic<bool> airbag_armed{true};
            std::atomic<uint8_t> seatbelt_status{0b11110000}; // Bitmask for 8 seats
            std::atomic<float> impact_sensor_x{0.0f};     // G-force
            std::atomic<float> impact_sensor_y{0.0f};     // G-force  
            std::atomic<float> impact_sensor_z{0.0f};     // G-force
            std::atomic<bool> rollover_detected{false};
            std::atomic<uint16_t> emergency_call_timer{0};
            std::atomic<bool> hazard_lights_active{false};
            
            // Fire suppression system
            std::atomic<bool> fire_detected{false};
            std::atomic<uint8_t> extinguisher_pressure{100}; // 0-100%
            std::atomic<bool> suppression_activated{false};
            
            void updateSafetySystems(int cycle) {
                // Impact sensors simulation
                impact_sensor_x.store(sin(cycle * 0.3f) * 0.5f);
                impact_sensor_y.store(cos(cycle * 0.25f) * 0.3f);  
                impact_sensor_z.store(1.0f + sin(cycle * 0.1f) * 0.2f); // +1G gravity
                
                // Rollover detection
                float lateral_g = sqrt(impact_sensor_x.load() * impact_sensor_x.load() + 
                                     impact_sensor_y.load() * impact_sensor_y.load());
                rollover_detected.store(lateral_g > 1.2f);
                
                // Emergency scenarios
                bool emergency_condition = rollover_detected.load() || 
                                          abs(impact_sensor_x.load()) > 2.0f;
                
                if (emergency_condition) {
                    hazard_lights_active.store(true);
                    if (emergency_call_timer.load() == 0) {
                        emergency_call_timer.store(1);
                    } else {
                        emergency_call_timer.fetch_add(1);
                    }
                } else {
                    hazard_lights_active.store(false);
                    emergency_call_timer.store(0);
                }
                
                // Seatbelt simulation (random changes)
                if (cycle % 50 == 0) {
                    uint8_t current = seatbelt_status.load();
                    current ^= (1 << (cycle % 8)); // Toggle random seatbelt
                    seatbelt_status.store(current);
                }
                
                // Fire detection simulation
                fire_detected.store((cycle % 500) < 5); // Rare event
                
                if (fire_detected.load() && !suppression_activated.load()) {
                    suppression_activated.store(true);
                    extinguisher_pressure.store(80); // Pressure drops
                } else if (!fire_detected.load()) {
                    suppression_activated.store(false);
                    extinguisher_pressure.store(std::min(100, static_cast<int>(extinguisher_pressure.load() + 1)));
                }
                
                // Airbag status
                airbag_armed.store(!suppression_activated.load()); // Disarm during fire suppression
            }
        };
    }
}

void displayComplexSystemStatus(Vehicle::Monitoring::SystemMonitor& monitor,
                               Vehicle::Powertrain::EngineSystem& engine,
                               Vehicle::Powertrain::TransmissionSystem& trans,
                               Vehicle::Safety::EmergencySystems& safety) {
    std::cout << "=== Complex Vehicle Systems Status ===" << std::endl;
    
    std::cout << "MONITOR: Uptime=" << monitor.system_uptime.load() << "ms, "
              << "Health=" << static_cast<int>(monitor.system_health.load()) << "%, "
              << "CPU=" << monitor.cpu_usage.load() << "%, "
              << "Errors=" << monitor.total_errors.load() << std::endl;
              
    std::cout << "ENGINE: RPM=" << engine.engine_rpm.load() << ", "
              << "Load=" << engine.engine_load.load() << "%, "
              << "Temp=" << static_cast<int>(engine.coolant_temp.load()) << "°C, "
              << "Turbo=" << engine.turbo_active.load() << std::endl;
              
    std::cout << "TRANS: Gear=" << static_cast<int>(trans.current_gear.load()) << ", "
              << "Ratio=" << trans.gear_ratio.load() << ", "
              << "Temp=" << trans.transmission_temp.load()/10.0f << "°C, "
              << "LockUp=" << trans.lock_up_engaged.load() << std::endl;
              
    std::cout << "SAFETY: Impact=(" << safety.impact_sensor_x.load() << "," 
              << safety.impact_sensor_y.load() << "," << safety.impact_sensor_z.load() << ")G, "
              << "Rollover=" << safety.rollover_detected.load() << ", "
              << "Fire=" << safety.fire_detected.load() << ", "
              << "EmergTimer=" << safety.emergency_call_timer.load() << std::endl;
}

int main() {
    std::cout << "Complex Vehicle System Monitor" << std::endl;
    std::cout << "Testing nested namespaces: Vehicle::Monitoring, Vehicle::Powertrain, Vehicle::Safety" << std::endl;
    
    Vehicle::Monitoring::SystemMonitor monitor;
    Vehicle::Powertrain::EngineSystem engine;
    Vehicle::Powertrain::TransmissionSystem transmission;
    Vehicle::Safety::EmergencySystems safety;
    
    for (int cycle = 0; cycle < 60; ++cycle) {
        // Update all subsystems
        monitor.updateMonitoring(cycle);
        engine.updateEngine(cycle);
        transmission.updateTransmission(cycle);
        safety.updateSafetySystems(cycle);
        
        // Display status every 12 cycles
        if ((cycle + 1) % 12 == 0) {
            std::cout << "\n--- Cycle " << cycle + 1 << " ---" << std::endl;
            displayComplexSystemStatus(monitor, engine, transmission, safety);
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    
    std::cout << "\nComplex vehicle system monitoring completed." << std::endl;
    return 0;
}
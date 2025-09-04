#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <random>
#include <iomanip>
#include <cmath>

// IoT Sensor Monitoring Variables (Global for memory monitoring)
std::atomic<float> temperature_celsius{22.5f};     // °C - Room temperature
std::atomic<float> humidity_percent{45.0f};        // % - Relative humidity  
std::atomic<float> pressure_hpa{1013.25f};         // hPa - Atmospheric pressure
std::atomic<float> co2_ppm{400.0f};                // ppm - CO2 concentration
std::atomic<float> light_lux{300.0f};              // lux - Light intensity
std::atomic<int> motion_detected{0};               // Boolean as int (0/1)
std::atomic<float> noise_level_db{35.0f};          // dB - Sound level
std::atomic<float> air_quality_index{50.0f};       // AQI - Air quality (0-500)

// System status variables  
std::atomic<int> active_sensors{8};                // Number of active sensors
std::atomic<int> alert_count{0};                   // Number of active alerts
std::atomic<bool> hvac_system_active{false};       // HVAC control status
std::atomic<float> power_consumption_watts{125.5f}; // W - Current power usage
std::atomic<int> data_packets_sent{0};             // Network transmission counter
std::atomic<float> battery_voltage{3.7f};          // V - Battery level

// Environmental thresholds and alerts
std::atomic<bool> temperature_alert{false};
std::atomic<bool> humidity_alert{false};
std::atomic<bool> air_quality_alert{false};

void printBanner() {
    std::cout << R"(
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                 IoT ENVIRONMENTAL MONITORING SYSTEM               ║
    ║                    Smart Building Sensor Network                  ║
    ║                                                                   ║
    ║  🌡️ Temperature  💧 Humidity  🌪️ Pressure  🍃 Air Quality  💡 Light ║
    ╚═══════════════════════════════════════════════════════════════════╝
    )" << std::endl;
}

class EnvironmentalSimulator {
private:
    std::random_device rd;
    std::mt19937 gen;
    
public:
    EnvironmentalSimulator() : gen(rd()) {}
    
    void simulateRealisticEnvironment(int cycle) {
        // Base values with realistic daily variations
        float time_of_day = (cycle % 144) / 144.0f; // 144 cycles = 24 hours simulation
        float daily_temp_variation = 5.0f * std::sin(time_of_day * 2 * M_PI - M_PI/2); // Peak at noon
        
        // Temperature simulation (18-28°C range)
        std::normal_distribution<float> temp_noise(0.0f, 0.5f);
        float base_temp = 23.0f + daily_temp_variation + temp_noise(gen);
        temperature_celsius = std::max(15.0f, std::min(35.0f, base_temp));
        
        // Humidity (inverse relationship with temperature)
        std::normal_distribution<float> humidity_noise(0.0f, 2.0f);
        float base_humidity = 60.0f - daily_temp_variation * 2 + humidity_noise(gen);
        humidity_percent = std::max(20.0f, std::min(80.0f, base_humidity));
        
        // Atmospheric pressure (realistic variations)
        std::normal_distribution<float> pressure_noise(0.0f, 2.0f);
        pressure_hpa = 1013.25f + std::sin(time_of_day * M_PI) * 5 + pressure_noise(gen);
        
        // CO2 levels (higher during occupied hours)
        bool occupied_hours = (time_of_day > 0.33f && time_of_day < 0.75f); // 8am-6pm
        std::normal_distribution<float> co2_noise(0.0f, 20.0f);
        float base_co2 = occupied_hours ? 650.0f + cycle % 200 : 420.0f;
        co2_ppm = std::max(380.0f, base_co2 + co2_noise(gen));
        
        // Light levels (natural + artificial)
        std::normal_distribution<float> light_noise(0.0f, 20.0f);
        float natural_light = 500.0f * std::max(0.0f, (float)std::sin(time_of_day * M_PI));
        float artificial_light = occupied_hours ? 200.0f : 50.0f;
        light_lux = natural_light + artificial_light + light_noise(gen);
        
        // Motion detection (probability based on occupancy)
        std::bernoulli_distribution motion_dist(occupied_hours ? 0.3 : 0.05);
        motion_detected = motion_dist(gen) ? 1 : 0;
        
        // Noise levels
        std::normal_distribution<float> noise_noise(0.0f, 3.0f);
        float base_noise = occupied_hours ? 45.0f + (motion_detected * 10) : 30.0f;
        noise_level_db = std::max(25.0f, base_noise + noise_noise(gen));
        
        // Air quality index (based on CO2 and other factors)
        float aqi_base = (co2_ppm.load() - 400) / 10 + (noise_level_db.load() - 30) / 2;
        air_quality_index = std::max(0.0f, std::min(200.0f, aqi_base));
        
        // Power consumption (varies with HVAC usage)
        float hvac_power = hvac_system_active ? 500.0f : 0.0f;
        float base_power = 125.0f + occupied_hours * 75.0f + hvac_power;
        std::normal_distribution<float> power_noise(0.0f, 15.0f);
        power_consumption_watts = std::max(50.0f, base_power + power_noise(gen));
        
        // Battery voltage (slowly depleting)
        battery_voltage = std::max(3.2f, 3.8f - (cycle * 0.001f));
        
        // Data transmission counter
        if (cycle % 5 == 0) { // Send data every 5 cycles
            data_packets_sent = data_packets_sent.load() + 1;
        }
    }
    
    void checkAlerts() {
        alert_count = 0;
        
        // Temperature alerts
        if (temperature_celsius.load() > 26.0f || temperature_celsius.load() < 18.0f) {
            temperature_alert = true;
            alert_count++;
        } else {
            temperature_alert = false;
        }
        
        // Humidity alerts  
        if (humidity_percent.load() > 70.0f || humidity_percent.load() < 30.0f) {
            humidity_alert = true;
            alert_count++;
        } else {
            humidity_alert = false;
        }
        
        // Air quality alerts
        if (air_quality_index.load() > 100.0f) {
            air_quality_alert = true;
            alert_count++;
        } else {
            air_quality_alert = false;
        }
        
        // HVAC control logic
        if (temperature_celsius.load() > 25.0f || humidity_percent.load() > 65.0f) {
            hvac_system_active = true;
        } else if (temperature_celsius.load() < 21.0f && humidity_percent.load() < 45.0f) {
            hvac_system_active = false;
        }
        
        active_sensors = 8 - (battery_voltage.load() < 3.3f ? 1 : 0);
    }
};

void printSensorReadings(int cycle) {
    std::cout << "\n=== Environmental Reading #" << std::setw(3) << cycle + 1 << " ===" << std::endl;
    std::cout << std::fixed << std::setprecision(1);
    
    std::cout << "🌡️  Temperature: " << temperature_celsius.load() << "°C";
    if (temperature_alert.load()) std::cout << " ⚠️ ";
    std::cout << " | 💧 Humidity: " << humidity_percent.load() << "%";
    if (humidity_alert.load()) std::cout << " ⚠️";
    std::cout << std::endl;
    
    std::cout << "🌪️  Pressure: " << pressure_hpa.load() << " hPa"
              << " | 🍃 CO₂: " << co2_ppm.load() << " ppm" << std::endl;
              
    std::cout << "💡 Light: " << light_lux.load() << " lux"
              << " | 🔊 Noise: " << noise_level_db.load() << " dB" << std::endl;
              
    std::cout << "📊 AQI: " << air_quality_index.load();
    if (air_quality_alert.load()) std::cout << " ⚠️";
    std::cout << " | 👤 Motion: " << (motion_detected.load() ? "YES" : "NO") << std::endl;
    
    std::cout << "⚡ Power: " << power_consumption_watts.load() << "W"
              << " | 🔋 Battery: " << std::setprecision(2) << battery_voltage.load() << "V" << std::endl;
              
    std::cout << "🌡️  HVAC: " << (hvac_system_active.load() ? "ON" : "OFF")
              << " | 📡 Packets: " << data_packets_sent.load()
              << " | ⚠️ Alerts: " << alert_count.load() << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🚀 Initializing IoT Environmental Monitoring System..." << std::endl;
    std::cout << "📡 Connecting " << active_sensors.load() << " sensors to network..." << std::endl;
    std::cout << "🔧 Setting up real-time monitoring and alerting..." << std::endl;
    std::cout << "📊 Monitoring variables: temperature_celsius, humidity_percent, pressure_hpa, co2_ppm, light_lux, motion_detected, noise_level_db, air_quality_index" << std::endl;
    
    // Wait for system initialization
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    std::cout << "\n✅ System Online - Starting 24-hour environmental monitoring simulation..." << std::endl;
    
    EnvironmentalSimulator simulator;
    
    for (int cycle = 0; cycle < 80; ++cycle) {
        // Update sensor readings
        simulator.simulateRealisticEnvironment(cycle);
        
        // Check for alerts and update system status
        simulator.checkAlerts();
        
        // Print readings every 4 cycles (to avoid spam)
        if (cycle % 4 == 0) {
            printSensorReadings(cycle);
        }
        
        // Realistic sensor update interval
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
    
    std::cout << "\n🏁 Environmental Monitoring Demo Complete!" << std::endl;
    std::cout << "📊 Total data packets transmitted: " << data_packets_sent.load() << std::endl;
    std::cout << "⚠️  Final alert status: " << alert_count.load() << " active alerts" << std::endl;
    std::cout << "🔋 Battery status: " << std::setprecision(2) << battery_voltage.load() << "V" << std::endl;
    
    return 0;
}
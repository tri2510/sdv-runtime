/*
 * Sample Basic Monitoring Application
 * Demonstrates atomic variable tracing with Kit Server integration
 */

#include <atomic>
#include <iostream>
#include <thread>
#include <chrono>
#include <random>
#include <cmath>
#include <iomanip>
#include <signal.h>
#include <unistd.h>

// Global atomic variables for monitoring
std::atomic<double> g_temperature{25.0};      // Celsius
std::atomic<double> g_pressure{101.3};        // kPa  
std::atomic<double> g_humidity{65.0};         // %
std::atomic<int> g_rpm{800};                  // RPM
std::atomic<bool> g_system_active{true};      // System status
std::atomic<int> g_error_count{0};            // Error counter
std::atomic<double> g_voltage{12.6};          // Battery voltage
std::atomic<double> g_current{5.2};           // Current draw (Amps)

// Control flags
std::atomic<bool> g_running{true};

void signal_handler(int signal) {
    std::cout << "\nShutdown signal received. Stopping..." << std::endl;
    g_running = false;
}

// Simulation thread - generates realistic sensor data
void sensor_simulation_thread() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> temp_noise(0.0, 0.5);
    std::normal_distribution<> pressure_noise(0.0, 0.2);
    std::normal_distribution<> humidity_noise(0.0, 2.0);
    
    int cycle = 0;
    
    while (g_running) {
        cycle++;
        
        // Temperature simulation with daily cycle
        double base_temp = 20.0 + 10.0 * std::sin(cycle * 0.001);
        g_temperature.store(base_temp + temp_noise(gen));
        
        // Pressure simulation with weather patterns
        double base_pressure = 101.3 + 2.0 * std::sin(cycle * 0.0005);
        g_pressure.store(base_pressure + pressure_noise(gen));
        
        // Humidity inverse correlation with temperature
        double base_humidity = 80.0 - (g_temperature.load() - 20.0) * 1.5;
        g_humidity.store(std::max(30.0, std::min(95.0, base_humidity + humidity_noise(gen))));
        
        // RPM simulation based on load cycles
        int target_rpm = 800 + (cycle % 100) * 20;
        if (cycle % 200 < 50) {
            target_rpm += 1500;  // High load period
        }
        g_rpm.store(target_rpm + static_cast<int>(temp_noise(gen) * 50));
        
        // System status and error simulation
        if (cycle % 500 == 0) {
            g_error_count.fetch_add(1);
        }
        
        if (g_temperature.load() > 35.0 || g_pressure.load() < 99.0) {
            g_system_active.store(false);
        } else {
            g_system_active.store(true);
        }
        
        // Electrical system simulation
        double load_factor = static_cast<double>(g_rpm.load()) / 2500.0;
        g_voltage.store(12.6 + 1.2 * load_factor + temp_noise(gen) * 0.1);
        g_current.store(3.0 + 5.0 * load_factor + std::abs(temp_noise(gen)));
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

// Monitoring thread - displays current values
void monitoring_thread() {
    while (g_running) {
        // Clear screen and display current values
        system("clear");
        
        std::cout << "=== Basic Monitoring System ===" << std::endl;
        std::cout << "Process ID: " << getpid() << std::endl;
        std::cout << std::endl;
        
        std::cout << "Environmental Sensors:" << std::endl;
        std::cout << "  Temperature:  " << std::fixed << std::setprecision(1) 
                  << g_temperature.load() << " °C" << std::endl;
        std::cout << "  Pressure:     " << std::fixed << std::setprecision(1)
                  << g_pressure.load() << " kPa" << std::endl;
        std::cout << "  Humidity:     " << std::fixed << std::setprecision(1)
                  << g_humidity.load() << " %" << std::endl;
        
        std::cout << std::endl;
        std::cout << "Engine Monitoring:" << std::endl;
        std::cout << "  RPM:          " << g_rpm.load() << " RPM" << std::endl;
        std::cout << "  System:       " << (g_system_active.load() ? "ACTIVE" : "FAULT") << std::endl;
        std::cout << "  Errors:       " << g_error_count.load() << std::endl;
        
        std::cout << std::endl;
        std::cout << "Electrical System:" << std::endl;
        std::cout << "  Voltage:      " << std::fixed << std::setprecision(2)
                  << g_voltage.load() << " V" << std::endl;
        std::cout << "  Current:      " << std::fixed << std::setprecision(1)
                  << g_current.load() << " A" << std::endl;
        std::cout << "  Power:        " << std::fixed << std::setprecision(1)
                  << (g_voltage.load() * g_current.load()) << " W" << std::endl;
        
        std::cout << std::endl;
        std::cout << "Kit Server Integration:" << std::endl;
        std::cout << "  Variables:    8 atomic variables monitored" << std::endl;
        std::cout << "  Update Rate:  10 Hz" << std::endl;
        std::cout << "  Status:       " << (g_running.load() ? "RUNNING" : "STOPPING") << std::endl;
        
        std::cout << std::endl;
        std::cout << "Press Ctrl+C to stop..." << std::endl;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}

// Alert system thread
void alert_system_thread() {
    while (g_running) {
        bool alert_triggered = false;
        
        // Check for alert conditions
        if (g_temperature.load() > 40.0) {
            std::cout << "\n🚨 ALERT: High temperature detected: " 
                      << g_temperature.load() << "°C" << std::endl;
            alert_triggered = true;
        }
        
        if (g_voltage.load() < 11.5) {
            std::cout << "\n🚨 ALERT: Low battery voltage: " 
                      << g_voltage.load() << "V" << std::endl;
            alert_triggered = true;
        }
        
        if (g_rpm.load() > 4000) {
            std::cout << "\n🚨 ALERT: High RPM detected: " 
                      << g_rpm.load() << " RPM" << std::endl;
            alert_triggered = true;
        }
        
        if (alert_triggered) {
            // Simulate sending alert to kit server
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}

int main(int argc, char* argv[]) {
    std::cout << "Starting Basic Monitoring Sample..." << std::endl;
    std::cout << "Process ID: " << getpid() << std::endl;
    std::cout << "Monitoring 8 atomic variables for Kit Server integration" << std::endl;
    
    // Set up signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Start threads
    std::thread sensor_thread(sensor_simulation_thread);
    std::thread monitor_thread(monitoring_thread);
    std::thread alert_thread(alert_system_thread);
    
    // Main loop - could handle kit server communication here
    while (g_running) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // Simulate kit server heartbeat
        static int heartbeat_counter = 0;
        if (++heartbeat_counter % 50 == 0) {
            // This is where kit server integration would update variables
            // For now, just continue simulation
        }
    }
    
    // Clean shutdown
    std::cout << "Shutting down threads..." << std::endl;
    
    sensor_thread.join();
    monitor_thread.join();  
    alert_thread.join();
    
    std::cout << "Basic Monitoring Sample stopped successfully." << std::endl;
    
    return 0;
}
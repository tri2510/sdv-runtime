#include <iostream>
#include <thread>
#include <chrono>
#include <cstdint>
#include <atomic>

// Basic automotive monitoring variables - fundamental types
class BasicTypesMonitor {
public:
    // Fundamental signed integers
    int8_t temperature_offset = 0;
    int16_t steering_angle = 0;
    int32_t odometer_reading = 0;
    int64_t total_engine_runtime = 0;
    
    // Fundamental unsigned integers  
    uint8_t battery_level = 100;
    uint16_t engine_rpm = 0;
    uint32_t distance_traveled = 0;
    uint64_t microsecond_timestamp = 0;
    
    // Floating point types
    float current_speed = 0.0f;
    double gps_latitude = 0.0;
    double gps_longitude = 0.0;
    
    // Boolean states
    bool engine_running = false;
    bool brake_applied = false;
    bool turn_signal_left = false;
    bool turn_signal_right = false;
    bool headlights_on = false;
    
    // Character types
    char gear_position = 'P';
    char drive_mode = 'D';
    
    // Standard int types
    int fuel_level = 50;
    long engine_cycles = 0;
    short tire_pressure_psi = 32;
    
    void updateValues() {
        static int cycle = 0;
        cycle++;
        
        // Simulate realistic automotive data updates
        temperature_offset = (cycle % 201) - 100; // -100 to +100
        steering_angle = (cycle * 17) % 7200 - 3600; // -360 to +360 degrees * 10
        odometer_reading = cycle * 100;
        total_engine_runtime += 1000; // microseconds
        
        battery_level = 100 - (cycle % 101);
        engine_rpm = 800 + (cycle % 6000);
        distance_traveled = cycle * 50;
        microsecond_timestamp = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch()).count();
        
        current_speed = (cycle % 120) + (cycle % 10) * 0.1f; // 0-120 km/h
        gps_latitude = 52.520008 + (cycle % 1000) * 0.0001; // Berlin area
        gps_longitude = 13.404954 + (cycle % 1000) * 0.0001;
        
        engine_running = (cycle % 30) > 5; // Running most of the time
        brake_applied = (cycle % 20) < 3;  // Occasional braking
        turn_signal_left = (cycle % 50) < 5;
        turn_signal_right = (cycle % 60) < 5;
        headlights_on = (cycle % 100) > 60; // On ~40% of time
        
        // Gear simulation: P, R, N, D
        char gears[] = {'P', 'R', 'N', 'D'};
        gear_position = gears[cycle % 4];
        
        // Drive modes: E(co), C(omfort), S(port)
        char modes[] = {'E', 'C', 'S'};
        drive_mode = modes[cycle % 3];
        
        fuel_level = std::max(0, 100 - (cycle / 10));
        engine_cycles += engine_rpm / 60; // Approximate cycles per second
        tire_pressure_psi = 30 + (cycle % 10);
        
        std::cout << "Cycle " << cycle << ": Speed=" << current_speed 
                  << "km/h, RPM=" << engine_rpm << ", Gear=" << gear_position 
                  << ", Battery=" << (int)battery_level << "%" << std::endl;
    }
};

int main() {
    BasicTypesMonitor monitor;
    
    std::cout << "Basic Types Monitor Started - Testing fundamental C++ types" << std::endl;
    std::cout << "Variables include: integers, floats, booleans, characters" << std::endl;
    std::cout << "Simulating automotive data updates every 500ms" << std::endl;
    
    for (int i = 0; i < 60; ++i) { // Run for ~30 seconds
        monitor.updateValues();
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    
    std::cout << "Basic types monitoring test completed." << std::endl;
    return 0;
}
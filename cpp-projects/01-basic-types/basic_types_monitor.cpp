#include <iostream>
#include <thread>
#include <chrono>
#include <cstdint>
#include <atomic>

// Global variables for basic automotive monitoring - fundamental types
// Using global variables to demonstrate ptrace memory monitoring capability

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
    total_engine_runtime = cycle * 1000000LL;
    
    battery_level = 100 - (cycle % 90);
    engine_rpm = 800 + (cycle * 73) % 6200;
    distance_traveled = cycle * 10;
    microsecond_timestamp = cycle * 1000000ULL;
    
    current_speed = 20.0f + (cycle % 100) * 0.5f;
    gps_latitude = 37.7749 + (cycle % 1000) * 0.00001;
    gps_longitude = -122.4194 + (cycle % 1000) * 0.00001;
    
    engine_running = (cycle > 10);
    brake_applied = (cycle % 10 < 3);
    turn_signal_left = (cycle % 20 < 5);
    turn_signal_right = (cycle % 20 >= 15);
    headlights_on = (cycle % 100 < 60);
    
    gear_position = "PRND"[cycle % 4];
    drive_mode = "DSME"[cycle % 4];
    
    fuel_level = 100 - (cycle % 95);
    engine_cycles = cycle * 100L;
    tire_pressure_psi = 28 + (cycle % 12);
}

void printStatus() {
    std::cout << "\n=== Basic Types Monitor Status ===" << std::endl;
    std::cout << "Temperature Offset: " << (int)temperature_offset << "°C" << std::endl;
    std::cout << "Steering Angle: " << steering_angle / 10.0 << "°" << std::endl;
    std::cout << "Current Speed: " << current_speed << " mph" << std::endl;
    std::cout << "Engine RPM: " << engine_rpm << std::endl;
    std::cout << "Battery Level: " << (int)battery_level << "%" << std::endl;
    std::cout << "Fuel Level: " << fuel_level << "%" << std::endl;
    std::cout << "Gear Position: " << gear_position << std::endl;
    std::cout << "Engine Running: " << (engine_running ? "Yes" : "No") << std::endl;
    std::cout << "GPS: " << gps_latitude << ", " << gps_longitude << std::endl;
}

int main() {
    std::cout << "Starting Basic Types Monitor (Global Variables Demo)" << std::endl;
    std::cout << "Monitoring " << 25 << " global variables..." << std::endl;
    
    while (true) {
        updateValues();
        
        static int print_counter = 0;
        if (++print_counter % 10 == 0) {
            printStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    
    return 0;
}
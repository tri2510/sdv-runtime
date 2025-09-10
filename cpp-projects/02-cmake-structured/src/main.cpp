#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <cstdint>

// Global variables for CMake-structured vehicle systems
// Demonstrating global variable monitoring with atomic types for thread safety

// Vehicle Control System Global Variables
std::atomic<float> target_speed{0.0f};
std::atomic<float> actual_speed{0.0f};
std::atomic<int16_t> throttle_position{0}; // 0-1000 (0-100.0%)
std::atomic<int16_t> brake_pressure{0};    // 0-1000 bar scaled
std::atomic<bool> cruise_control_active{false};
std::atomic<bool> abs_active{false};
std::atomic<bool> esp_active{false};

// Engine Control Global Variables
std::atomic<uint16_t> engine_rpm{0};
std::atomic<uint8_t> engine_load{0};  // 0-100%
std::atomic<int8_t> engine_temp{0};   // Celsius

// Transmission Global Variables
std::atomic<uint8_t> gear_number{0};  // 0=Park, 1-8=Forward gears
std::atomic<bool> transmission_locked{false};

// Sensor System Global Variables
std::atomic<float> gps_latitude{0.0f};
std::atomic<float> gps_longitude{0.0f};
std::atomic<int16_t> gps_altitude{0};
std::atomic<float> imu_accel_x{0.0f};
std::atomic<float> imu_accel_y{0.0f};
std::atomic<float> imu_accel_z{0.0f};
std::atomic<float> imu_gyro_x{0.0f};
std::atomic<float> imu_gyro_y{0.0f};
std::atomic<float> imu_gyro_z{0.0f};

// TPMS (Tire Pressure Monitoring System) Global Variables
std::atomic<uint16_t> tire_pressure_fl{0};  // Front-left in kPa
std::atomic<uint16_t> tire_pressure_fr{0};  // Front-right
std::atomic<uint16_t> tire_pressure_rl{0};  // Rear-left  
std::atomic<uint16_t> tire_pressure_rr{0};  // Rear-right
std::atomic<int8_t> tire_temp_fl{0};
std::atomic<int8_t> tire_temp_fr{0};
std::atomic<int8_t> tire_temp_rl{0};
std::atomic<int8_t> tire_temp_rr{0};

// Battery Management System Global Variables
std::atomic<float> battery_voltage{0.0f};
std::atomic<float> battery_current{0.0f};
std::atomic<uint8_t> battery_soc{0};  // State of charge %
std::atomic<int8_t> battery_temp{0};

void updateVehicleController() {
    static int cycle = 0;
    cycle++;
    
    // Update control systems
    target_speed.store(30.0f + (cycle % 100) * 0.5f);
    actual_speed.store(target_speed.load() - 2.0f + (cycle % 5) * 0.4f);
    throttle_position.store((cycle * 31) % 1001);
    brake_pressure.store((cycle % 20 < 5) ? 200 + cycle % 300 : 0);
    
    cruise_control_active.store(cycle % 200 > 100);
    abs_active.store(cycle % 30 < 3);
    esp_active.store(cycle % 40 < 2);
    
    // Engine parameters
    engine_rpm.store(800 + (cycle * 73) % 6200);
    engine_load.store(20 + (cycle * 17) % 81);
    engine_temp.store(60 + (cycle / 10) % 40);
    
    // Transmission
    gear_number.store(cycle / 100 % 8);
    transmission_locked.store(gear_number.load() == 0);
}

void updateSensorManager() {
    static int cycle = 0;
    cycle++;
    
    // GPS updates
    gps_latitude.store(37.7749f + (cycle % 1000) * 0.00001f);
    gps_longitude.store(-122.4194f + (cycle % 1000) * 0.00001f);
    gps_altitude.store(100 + (cycle % 500));
    
    // IMU sensor data
    imu_accel_x.store(-2.0f + (cycle % 400) * 0.01f);
    imu_accel_y.store(-1.0f + (cycle % 200) * 0.01f);
    imu_accel_z.store(9.8f + (cycle % 10) * 0.01f);
    imu_gyro_x.store(-5.0f + (cycle % 1000) * 0.01f);
    imu_gyro_y.store(-3.0f + (cycle % 600) * 0.01f);
    imu_gyro_z.store(-1.0f + (cycle % 200) * 0.01f);
    
    // TPMS updates
    tire_pressure_fl.store(220 + (cycle % 30));
    tire_pressure_fr.store(225 + (cycle % 25));
    tire_pressure_rl.store(215 + (cycle % 35));
    tire_pressure_rr.store(218 + (cycle % 32));
    
    tire_temp_fl.store(20 + (cycle / 10) % 60);
    tire_temp_fr.store(22 + (cycle / 10) % 58);
    tire_temp_rl.store(19 + (cycle / 10) % 61);
    tire_temp_rr.store(21 + (cycle / 10) % 59);
    
    // Battery management
    battery_voltage.store(12.0f + (cycle % 20) * 0.1f);
    battery_current.store(-50.0f + (cycle % 1000) * 0.1f);
    battery_soc.store(100 - (cycle / 100) % 60);
    battery_temp.store(15 + (cycle / 50) % 30);
}

void printStatus() {
    std::cout << "\n=== CMake Vehicle Systems Status (Global Variables) ===" << std::endl;
    std::cout << "Speed: " << actual_speed.load() << " mph (target: " << target_speed.load() << ")" << std::endl;
    std::cout << "Engine RPM: " << engine_rpm.load() << std::endl;
    std::cout << "Throttle: " << throttle_position.load()/10.0f << "%" << std::endl;
    std::cout << "Gear: " << (int)gear_number.load() << std::endl;
    std::cout << "GPS: " << gps_latitude.load() << ", " << gps_longitude.load() << std::endl;
    std::cout << "Battery: " << (int)battery_soc.load() << "% @ " << battery_voltage.load() << "V" << std::endl;
    std::cout << "Tire Pressures (kPa): FL=" << tire_pressure_fl.load() 
              << " FR=" << tire_pressure_fr.load()
              << " RL=" << tire_pressure_rl.load()
              << " RR=" << tire_pressure_rr.load() << std::endl;
}

int main() {
    std::cout << "CMake Vehicle Systems Monitor Starting (Global Variables Demo)" << std::endl;
    std::cout << "Monitoring " << 40 << " global atomic variables..." << std::endl;
    
    while (true) {
        updateVehicleController();
        updateSensorManager();
        
        static int print_counter = 0;
        if (++print_counter % 10 == 0) {
            printStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(750));
    }
    
    return 0;
}
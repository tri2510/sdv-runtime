#include <iostream>
#include <thread>
#include <chrono>
#include <cstdint>
#include <atomic>
#include <cstring>
#include <cmath>

// Embedded ECU-style programming with fixed-point arithmetic
// Global variables for demonstrating ptrace monitoring in embedded systems

// Fixed-point types (Q notation) - simplified to basic types
typedef int q15_t;  // Q15 fixed-point: simplified to int
typedef int q31_t;  // Q31 fixed-point: simplified to int

// Fixed-point conversion macros - simplified
#define FLOAT_TO_Q15(x) ((q15_t)((x) * 32768.0f))
#define Q15_TO_FLOAT(x) (((float)(x)) / 32768.0f)
#define FLOAT_TO_Q31(x) ((q31_t)((x) * 2147483648.0f))
#define Q31_TO_FLOAT(x) (((float)(x)) / 2147483648.0f)

// Global ECU variables - Fixed-point sensor values
std::atomic<q15_t> throttle_position_q15{0};      // 0.0-1.0 range
std::atomic<q15_t> brake_pedal_q15{0};            // 0.0-1.0 range
std::atomic<q15_t> accelerator_pedal_q15{0};      // 0.0-1.0 range
std::atomic<q31_t> vehicle_speed_q31{0};          // km/h in Q31

// Global ECU variables - Engine control (fixed-point)
std::atomic<q15_t> fuel_injection_time_q15{0};    // milliseconds
std::atomic<q15_t> ignition_advance_q15{0};       // degrees BTDC
std::atomic<q15_t> idle_air_control_q15{0};       // 0.0-1.0 duty cycle

// Global ECU variables - Packed status registers
std::atomic<int> status_reg1_raw{0};
std::atomic<char> status_reg2_raw{0};

// Global ECU variables - Communication counters (typical CAN/LIN)
std::atomic<int> can_tx_counter{0};
std::atomic<int> can_rx_counter{0};
std::atomic<int> can_error_counter{0};
std::atomic<char> lin_frame_counter{0};

// Global ECU variables - Diagnostic trouble codes (DTCs)
std::atomic<int> active_dtc_count{0};
std::atomic<int> dtc_p0xxx{0};  // Powertrain DTCs
std::atomic<int> dtc_b0xxx{0};  // Body DTCs
std::atomic<int> dtc_c0xxx{0};  // Chassis DTCs
std::atomic<int> dtc_u0xxx{0};  // Network DTCs

// Global ECU variables - Timing and scheduling (typical RTOS variables)
std::atomic<int> main_loop_counter{0};
std::atomic<int> task_execution_time_us{0};
std::atomic<char> cpu_load_percent{0};

// Global ECU variables - Memory management
std::atomic<int> stack_usage_bytes{0};
std::atomic<int> heap_usage_bytes{0};
std::atomic<char> memory_fragmentation_percent{0};

void updateECUState(int cycle) {
    // Update throttle position (sine wave)
    float throttle_float = 0.3f + 0.4f * sin(cycle * 0.1f);
    throttle_position_q15.store(FLOAT_TO_Q15(throttle_float));
    
    // Update brake pedal (periodic)
    float brake_float = (cycle % 50 < 10) ? 0.7f : 0.0f;
    brake_pedal_q15.store(FLOAT_TO_Q15(brake_float));
    
    // Update accelerator pedal
    float accel_float = 0.2f + 0.5f * sin(cycle * 0.15f);
    accelerator_pedal_q15.store(FLOAT_TO_Q15(accel_float));
    
    // Update vehicle speed
    float speed_kmh = 20.0f + 60.0f * Q15_TO_FLOAT(throttle_position_q15.load());
    vehicle_speed_q31.store(FLOAT_TO_Q31(speed_kmh / 200.0f)); // Scale to fit Q31
    
    // Engine control calculations
    float injection_time = 2.0f + 8.0f * Q15_TO_FLOAT(throttle_position_q15.load());
    fuel_injection_time_q15.store(FLOAT_TO_Q15(injection_time / 20.0f));
    
    float ignition = 10.0f + 20.0f * Q15_TO_FLOAT(throttle_position_q15.load());
    ignition_advance_q15.store(FLOAT_TO_Q15(ignition / 45.0f));
    
    float idle_control = 0.2f + 0.3f * cos(cycle * 0.05f);
    idle_air_control_q15.store(FLOAT_TO_Q15(idle_control));
    
    // Pack status registers (typical embedded bitfield packing)
    int status1 = 0;
    status1 |= (1 << 0);  // engine_running
    status1 |= (cycle % 10 < 8) ? (1 << 1) : 0;  // fuel_pump_on
    status1 |= (cycle % 100 < 5) ? (1 << 2) : 0;  // starter_engaged
    status1 |= (1 << 3);  // ignition_on
    status1 |= (cycle % 30 > 5) ? (1 << 4) : 0;  // oil_pressure_ok
    status1 |= (cycle % 40 > 10) ? (1 << 5) : 0;  // coolant_temp_ok
    status1 |= (1 << 6);  // battery_ok
    status1 |= (cycle % 20 > 2) ? (1 << 7) : 0;  // alternator_charging
    status_reg1_raw.store(status1);
    
    char status2 = 0;
    status2 |= ((cycle / 100) % 8) & 0x0F;  // gear_position
    status2 |= (cycle % 50 < 5) ? (1 << 4) : 0;  // abs_active
    status2 |= (cycle % 60 < 3) ? (1 << 5) : 0;  // traction_control
    status2 |= (cycle % 70 < 2) ? (1 << 6) : 0;  // esp_active
    status2 |= (cycle % 1000 < 100) ? (1 << 7) : 0;  // parking_brake
    status_reg2_raw.store(status2);
    
    // Update CAN/LIN counters
    can_tx_counter.fetch_add(17);
    can_rx_counter.fetch_add(23);
    if (cycle % 100 == 0) {
        can_error_counter.fetch_add(1);
    }
    lin_frame_counter.store((lin_frame_counter.load() + 1) % 256);
    
    // Simulate DTCs
    if (cycle % 500 == 0) {
        active_dtc_count.store(active_dtc_count.load() + 1);
        dtc_p0xxx.store(0x0301);  // P0301 - Cylinder 1 misfire
    }
    if (cycle % 1000 == 0) {
        dtc_c0xxx.store(0x0121);  // C0121 - ABS sensor
    }
    
    // RTOS-style timing
    main_loop_counter.fetch_add(1);
    task_execution_time_us.store(250 + (cycle % 100));
    cpu_load_percent.store(30 + (cycle % 40));
    
    // Memory simulation
    stack_usage_bytes.store(512 + (cycle % 256));
    heap_usage_bytes.store(1024 + (cycle % 512));
    memory_fragmentation_percent.store(5 + (cycle % 20));
}

void printECUStatus() {
    std::cout << "\n=== Embedded ECU Status (Global Variables) ===" << std::endl;
    
    // Display fixed-point values
    std::cout << "Throttle: " << Q15_TO_FLOAT(throttle_position_q15.load()) * 100 << "%" << std::endl;
    std::cout << "Vehicle Speed: " << Q31_TO_FLOAT(vehicle_speed_q31.load()) * 200 << " km/h" << std::endl;
    std::cout << "Fuel Injection: " << Q15_TO_FLOAT(fuel_injection_time_q15.load()) * 20 << " ms" << std::endl;
    
    // Display status registers
    int status1 = status_reg1_raw.load();
    std::cout << "Engine: " << ((status1 & 0x01) ? "Running" : "Stopped") << std::endl;
    std::cout << "Oil Pressure: " << ((status1 & 0x10) ? "OK" : "Low") << std::endl;
    
    // Display communication counters
    std::cout << "CAN TX: " << can_tx_counter.load() << " frames" << std::endl;
    std::cout << "CAN Errors: " << can_error_counter.load() << std::endl;
    
    // Display DTCs
    std::cout << "Active DTCs: " << active_dtc_count.load() << std::endl;
    
    // Display RTOS metrics
    std::cout << "CPU Load: " << (int)cpu_load_percent.load() << "%" << std::endl;
    std::cout << "Main Loop: " << main_loop_counter.load() << " cycles" << std::endl;
}

int main() {
    std::cout << "Embedded ECU System Starting (Global Variables Demo)" << std::endl;
    std::cout << "Monitoring " << 25 << " global embedded-style variables..." << std::endl;
    std::cout << "Fixed-point arithmetic, bit-packed registers, CAN/LIN counters" << std::endl;
    
    int cycle = 0;
    while (true) {
        updateECUState(cycle);
        
        if (cycle % 20 == 0) {  // 250ms * 20 = 5 seconds
            printECUStatus();
        }
        
        cycle++;
        std::this_thread::sleep_for(std::chrono::milliseconds(250));  // Typical ECU rate
    }
    
    return 0;
}
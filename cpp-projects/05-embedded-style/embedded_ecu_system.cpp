#include <iostream>
#include <thread>
#include <chrono>
#include <cstdint>
#include <atomic>
#include <cstring>

// Embedded ECU-style programming with fixed-point arithmetic
// Typical for automotive microcontrollers

// Fixed-point types (Q notation)
typedef int16_t q15_t;  // Q15 fixed-point: 1 sign + 15 fractional bits
typedef int32_t q31_t;  // Q31 fixed-point: 1 sign + 31 fractional bits

// Fixed-point conversion macros
#define FLOAT_TO_Q15(x) ((q15_t)((x) * 32768.0f))
#define Q15_TO_FLOAT(x) (((float)(x)) / 32768.0f)
#define FLOAT_TO_Q31(x) ((q31_t)((x) * 2147483648.0f))
#define Q31_TO_FLOAT(x) (((float)(x)) / 2147483648.0f)

// Bit-packed register structures (typical ECU register maps)
struct __attribute__((packed)) StatusRegister1 {
    uint16_t engine_running : 1;
    uint16_t fuel_pump_on : 1;
    uint16_t starter_engaged : 1;
    uint16_t ignition_on : 1;
    uint16_t oil_pressure_ok : 1;
    uint16_t coolant_temp_ok : 1;
    uint16_t battery_ok : 1;
    uint16_t alternator_charging : 1;
    uint16_t o2_sensor_ready : 1;
    uint16_t catalyst_ready : 1;
    uint16_t evap_ready : 1;
    uint16_t secondary_air_ready : 1;
    uint16_t ac_clutch_on : 1;
    uint16_t power_steering_ok : 1;
    uint16_t brake_booster_ok : 1;
    uint16_t reserved : 1;
};

struct __attribute__((packed)) StatusRegister2 {
    uint8_t gear_position : 4;    // 0-15 (P=0, R=1, N=2, D=3, etc.)
    uint8_t abs_active : 1;
    uint8_t traction_control : 1;
    uint8_t esp_active : 1;
    uint8_t parking_brake : 1;
};

// Global ECU variables (typical embedded style)
class EmbeddedECU {
public:
    // Fixed-point sensor values
    std::atomic<q15_t> throttle_position_q15{0};      // 0.0-1.0 range
    std::atomic<q15_t> brake_pedal_q15{0};            // 0.0-1.0 range
    std::atomic<q15_t> accelerator_pedal_q15{0};      // 0.0-1.0 range
    std::atomic<q31_t> vehicle_speed_q31{0};          // km/h in Q31
    
    // Engine control (fixed-point)
    std::atomic<q15_t> fuel_injection_time_q15{0};    // milliseconds
    std::atomic<q15_t> ignition_advance_q15{0};       // degrees BTDC
    std::atomic<q15_t> idle_air_control_q15{0};       // 0.0-1.0 duty cycle
    
    // Packed status registers
    std::atomic<uint16_t> status_reg1_raw{0};
    std::atomic<uint8_t> status_reg2_raw{0};
    
    // Communication counters (typical CAN/LIN)
    std::atomic<uint32_t> can_tx_counter{0};
    std::atomic<uint32_t> can_rx_counter{0};
    std::atomic<uint16_t> can_error_counter{0};
    std::atomic<uint8_t> lin_frame_counter{0};
    
    // Diagnostic trouble codes (DTCs)
    std::atomic<uint16_t> active_dtc_count{0};
    std::atomic<uint32_t> dtc_p0xxx{0};  // Powertrain DTCs
    std::atomic<uint32_t> dtc_b0xxx{0};  // Body DTCs
    std::atomic<uint32_t> dtc_c0xxx{0};  // Chassis DTCs
    std::atomic<uint32_t> dtc_u0xxx{0};  // Network DTCs
    
    // Timing and scheduling (typical RTOS variables)
    std::atomic<uint32_t> main_loop_counter{0};
    std::atomic<uint16_t> task_execution_time_us{0};
    std::atomic<uint8_t> cpu_load_percent{0};
    
    // Memory management
    std::atomic<uint16_t> stack_usage_bytes{0};
    std::atomic<uint16_t> heap_usage_bytes{0};
    std::atomic<bool> watchdog_triggered{false};
    
    void updateECUState(int cycle) {
        main_loop_counter.fetch_add(1);
        
        // Simulate throttle/brake pedal inputs (fixed-point)
        float throttle_float = 0.3f + 0.4f * sin(cycle * 0.1f);
        throttle_position_q15.store(FLOAT_TO_Q15(std::max(0.0f, std::min(1.0f, throttle_float))));
        
        float brake_float = (cycle % 100 < 20) ? 0.6f : 0.0f;
        brake_pedal_q15.store(FLOAT_TO_Q15(brake_float));
        
        float accel_float = Q15_TO_FLOAT(throttle_position_q15.load());
        accelerator_pedal_q15.store(FLOAT_TO_Q15(accel_float));
        
        // Vehicle speed calculation (Q31 fixed-point for high precision)
        float speed_kmh = 50.0f + 30.0f * sin(cycle * 0.08f);
        vehicle_speed_q31.store(FLOAT_TO_Q31(speed_kmh / 200.0f)); // Normalize to 0-1 range
        
        // Engine control calculations
        float fuel_time = 2.0f + Q15_TO_FLOAT(throttle_position_q15.load()) * 8.0f; // 2-10ms
        fuel_injection_time_q15.store(FLOAT_TO_Q15(fuel_time / 20.0f)); // Normalize
        
        float ignition_timing = 15.0f - Q15_TO_FLOAT(throttle_position_q15.load()) * 10.0f;
        ignition_advance_q15.store(FLOAT_TO_Q15(ignition_timing / 45.0f)); // Normalize
        
        float idle_control = 0.2f + 0.3f * cos(cycle * 0.05f);
        idle_air_control_q15.store(FLOAT_TO_Q15(idle_control));
        
        // Update bit-packed status registers
        StatusRegister1 sr1;
        sr1.engine_running = (cycle % 100) > 10;
        sr1.fuel_pump_on = sr1.engine_running || ((cycle % 150) < 30);
        sr1.starter_engaged = (cycle % 200) < 5;
        sr1.ignition_on = (cycle % 100) > 5;
        sr1.oil_pressure_ok = sr1.engine_running;
        sr1.coolant_temp_ok = (cycle > 50); // Warm-up simulation
        sr1.battery_ok = (cycle % 1000) > 50;
        sr1.alternator_charging = sr1.engine_running;
        sr1.o2_sensor_ready = (cycle > 100);
        sr1.catalyst_ready = (cycle > 200);
        sr1.evap_ready = (cycle > 150);
        sr1.secondary_air_ready = sr1.engine_running;
        sr1.ac_clutch_on = (cycle % 300) < 200;
        sr1.power_steering_ok = true;
        sr1.brake_booster_ok = true;
        sr1.reserved = 0;
        
        uint16_t sr1_value;
        memcpy(&sr1_value, &sr1, sizeof(sr1_value));
        status_reg1_raw.store(sr1_value);
        
        StatusRegister2 sr2;
        // Gear simulation: P(0) -> R(1) -> N(2) -> D(3) -> 2(4) -> 1(5)
        sr2.gear_position = (cycle / 50) % 6;
        sr2.abs_active = Q15_TO_FLOAT(brake_pedal_q15.load()) > 0.4f;
        sr2.traction_control = Q15_TO_FLOAT(throttle_position_q15.load()) > 0.8f;
        sr2.esp_active = sr2.abs_active || sr2.traction_control;
        sr2.parking_brake = sr2.gear_position == 0; // Engaged in Park
        
        status_reg2_raw.store(*reinterpret_cast<uint8_t*>(&sr2));
        
        // Communication counters
        can_tx_counter.fetch_add(5); // 5 frames per cycle
        can_rx_counter.fetch_add(8); // 8 frames received per cycle
        
        if (cycle % 100 == 0) {
            can_error_counter.fetch_add(1); // Occasional error
        }
        
        lin_frame_counter.store(static_cast<uint8_t>((cycle * 3) % 256));
        
        // DTC simulation
        active_dtc_count.store((cycle % 500 < 10) ? 2 : 0);
        
        if (active_dtc_count.load() > 0) {
            dtc_p0xxx.store(0x01010000 | (cycle % 256)); // P0101 + variation
            dtc_b0xxx.store(0x01020000 | ((cycle + 50) % 256)); // B0102 + variation
        } else {
            dtc_p0xxx.store(0);
            dtc_b0xxx.store(0);
        }
        
        // System performance monitoring
        task_execution_time_us.store(200 + (cycle % 100)); // 200-300 microseconds
        cpu_load_percent.store(30 + (cycle % 40)); // 30-70% CPU load
        
        stack_usage_bytes.store(512 + (cycle % 256)); // Stack usage variation
        heap_usage_bytes.store(1024 + sin(cycle * 0.1f) * 200);
        
        watchdog_triggered.store((cycle % 1000) == 999); // Rare watchdog trigger
    }
    
    void displayECUStatus() {
        std::cout << "=== Embedded ECU Status ===" << std::endl;
        
        // Display fixed-point values
        std::cout << "PEDALS: Throttle=" << Q15_TO_FLOAT(throttle_position_q15.load()) * 100.0f << "%, "
                  << "Brake=" << Q15_TO_FLOAT(brake_pedal_q15.load()) * 100.0f << "%" << std::endl;
                  
        std::cout << "ENGINE: FuelTime=" << Q15_TO_FLOAT(fuel_injection_time_q15.load()) * 20.0f << "ms, "
                  << "Timing=" << Q15_TO_FLOAT(ignition_advance_q15.load()) * 45.0f << "° BTDC" << std::endl;
                  
        std::cout << "SPEED: " << Q31_TO_FLOAT(vehicle_speed_q31.load()) * 200.0f << " km/h" << std::endl;
        
        // Decode bit-packed registers
        StatusRegister1 sr1;
        uint16_t sr1_raw = status_reg1_raw.load();
        memcpy(&sr1, &sr1_raw, sizeof(sr1));
        
        std::cout << "STATUS1: Engine=" << sr1.engine_running << ", FuelPump=" << sr1.fuel_pump_on
                  << ", Battery=" << sr1.battery_ok << ", O2Ready=" << sr1.o2_sensor_ready << std::endl;
        
        StatusRegister2 sr2;
        uint8_t sr2_raw = status_reg2_raw.load();
        memcpy(&sr2, &sr2_raw, sizeof(sr2));
        
        char gear_names[] = {'P', 'R', 'N', 'D', '2', '1'};
        std::cout << "STATUS2: Gear=" << gear_names[sr2.gear_position % 6] 
                  << ", ABS=" << sr2.abs_active << ", ESP=" << sr2.esp_active << std::endl;
        
        std::cout << "COMM: CAN TX=" << can_tx_counter.load() 
                  << ", RX=" << can_rx_counter.load() 
                  << ", Errors=" << can_error_counter.load() << std::endl;
                  
        std::cout << "SYSTEM: CPU=" << static_cast<int>(cpu_load_percent.load()) << "%, "
                  << "Stack=" << stack_usage_bytes.load() << "B, "
                  << "DTCs=" << active_dtc_count.load() << std::endl;
    }
};

int main() {
    std::cout << "Embedded ECU System Monitor" << std::endl;
    std::cout << "Features: Fixed-point arithmetic, bit-packed registers, CAN counters" << std::endl;
    std::cout << "Simulating typical automotive microcontroller operations" << std::endl;
    
    EmbeddedECU ecu;
    
    for (int cycle = 0; cycle < 80; ++cycle) {
        ecu.updateECUState(cycle);
        
        // Display status every 20 cycles
        if ((cycle + 1) % 20 == 0) {
            std::cout << "\n--- ECU Cycle " << cycle + 1 << " (Loop: " 
                      << ecu.main_loop_counter.load() << ") ---" << std::endl;
            ecu.displayECUStatus();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(250)); // 4Hz update rate (typical ECU)
    }
    
    std::cout << "\nEmbedded ECU monitoring completed." << std::endl;
    std::cout << "Total main loops: " << ecu.main_loop_counter.load() << std::endl;
    return 0;
}
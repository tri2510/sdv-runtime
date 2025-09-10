#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <vector>
#include <random>
#include <cmath>

// Performance stress testing for high-frequency variable monitoring
class HighFrequencyMonitor {
public:
    // High-frequency control loop variables (1kHz+ updates)
    std::atomic<float> pid_setpoint{50.0f};
    std::atomic<float> pid_process_value{48.5f};
    std::atomic<float> pid_error{0.0f};
    std::atomic<float> pid_integral{0.0f};
    std::atomic<float> pid_derivative{0.0f};
    std::atomic<float> pid_output{0.0f};
    
    // Multiple sensor arrays for stress testing
    std::atomic<float> sensor_array_1[32];   // 32 temperature sensors
    std::atomic<uint16_t> sensor_array_2[64]; // 64 pressure sensors
    std::atomic<int32_t> sensor_array_3[16];  // 16 position sensors
    
    // Rapid-changing counters
    std::atomic<uint64_t> high_freq_counter{0};
    std::atomic<uint32_t> interrupt_counter{0};
    std::atomic<uint16_t> timer_overflow_count{0};
    std::atomic<uint8_t> state_machine_state{0};
    
    // Performance metrics
    std::atomic<uint64_t> total_updates{0};
    std::atomic<uint32_t> updates_per_second{0};
    std::atomic<float> cpu_utilization{0.0f};
    std::atomic<uint16_t> max_loop_time_us{0};
    std::atomic<uint16_t> min_loop_time_us{65535};
    
    // Multi-threaded shared variables
    std::atomic<double> shared_accumulator{0.0};
    std::atomic<bool> thread_sync_flag{false};
    std::atomic<uint32_t> thread_barrier_counter{0};
    
    // Vehicle dynamics (high-rate updates)
    std::atomic<float> wheel_speed_fl{0.0f};  // Front-left
    std::atomic<float> wheel_speed_fr{0.0f};  // Front-right  
    std::atomic<float> wheel_speed_rl{0.0f};  // Rear-left
    std::atomic<float> wheel_speed_rr{0.0f};  // Rear-right
    std::atomic<float> lateral_acceleration{0.0f};
    std::atomic<float> longitudinal_acceleration{0.0f};
    std::atomic<float> yaw_rate{0.0f};
    std::atomic<float> steering_wheel_angle{0.0f};
    
    // Random number generator for realistic noise
    mutable std::mt19937 rng{std::random_device{}()};
    mutable std::uniform_real_distribution<float> noise_dist{-0.1f, 0.1f};
    
    HighFrequencyMonitor() {
        // Initialize sensor arrays
        for (int i = 0; i < 32; ++i) {
            sensor_array_1[i].store(20.0f + i * 2.0f); // Temperature range
        }
        for (int i = 0; i < 64; ++i) {
            sensor_array_2[i].store(1000 + i * 10); // Pressure range
        }
        for (int i = 0; i < 16; ++i) {
            sensor_array_3[i].store(i * 1000); // Position range
        }
    }
    
    void highFrequencyUpdate(uint64_t cycle) {
        total_updates.fetch_add(1);
        high_freq_counter.fetch_add(1);
        
        // PID control loop simulation (typical 1kHz control)
        float setpoint = pid_setpoint.load();
        float pv = pid_process_value.load();
        float error = setpoint - pv;
        pid_error.store(error);
        
        // Integral term (simplified)
        float integral = pid_integral.load() + error * 0.001f; // dt = 1ms
        pid_integral.store(integral);
        
        // Derivative term
        static float last_error = 0.0f;
        float derivative = (error - last_error) / 0.001f;
        pid_derivative.store(derivative);
        last_error = error;
        
        // PID output
        float output = 1.0f * error + 0.1f * integral + 0.01f * derivative;
        pid_output.store(output);
        
        // Update process value based on output
        pv += output * 0.01f + noise_dist(rng); // Add realistic noise
        pid_process_value.store(pv);
        
        // Update sensor arrays with realistic patterns
        for (int i = 0; i < 32; ++i) {
            float temp = 25.0f + 10.0f * sin(cycle * 0.001f + i * 0.2f) + noise_dist(rng);
            sensor_array_1[i].store(temp);
        }
        
        for (int i = 0; i < 64; ++i) {
            uint16_t pressure = static_cast<uint16_t>(1000 + 200 * cos(cycle * 0.0005f + i * 0.1f) + noise_dist(rng) * 10);
            sensor_array_2[i].store(pressure);
        }
        
        for (int i = 0; i < 16; ++i) {
            int32_t position = static_cast<int32_t>(i * 1000 + 500 * sin(cycle * 0.002f + i * 0.3f));
            sensor_array_3[i].store(position);
        }
        
        // Interrupt simulation
        if (cycle % 10 == 0) {
            interrupt_counter.fetch_add(1);
        }
        
        // Timer overflow simulation
        if (cycle % 65536 == 0) {
            timer_overflow_count.fetch_add(1);
        }
        
        // State machine
        state_machine_state.store(static_cast<uint8_t>(cycle % 8));
        
        // Vehicle dynamics updates
        float base_speed = 50.0f + 20.0f * sin(cycle * 0.0001f);
        wheel_speed_fl.store(base_speed + noise_dist(rng));
        wheel_speed_fr.store(base_speed + noise_dist(rng));
        wheel_speed_rl.store(base_speed + noise_dist(rng));
        wheel_speed_rr.store(base_speed + noise_dist(rng));
        
        lateral_acceleration.store(sin(cycle * 0.0003f) * 2.0f + noise_dist(rng));
        longitudinal_acceleration.store(cos(cycle * 0.0002f) * 1.5f + noise_dist(rng));
        yaw_rate.store(sin(cycle * 0.0004f) * 10.0f + noise_dist(rng));
        steering_wheel_angle.store(sin(cycle * 0.0001f) * 90.0f + noise_dist(rng));
        
        // Shared accumulator (simulates inter-thread communication)
        double current = shared_accumulator.load();
        while (!shared_accumulator.compare_exchange_weak(current, current + error * error)) {
            // Retry if CAS fails
        }
        
        // Thread synchronization
        if (cycle % 1000 == 0) {
            thread_sync_flag.store(!thread_sync_flag.load());
            thread_barrier_counter.fetch_add(1);
        }
    }
    
    void updatePerformanceMetrics(std::chrono::high_resolution_clock::time_point start_time,
                                 std::chrono::high_resolution_clock::time_point end_time) {
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
        uint16_t loop_time = static_cast<uint16_t>(duration.count());
        
        // Update min/max loop times
        uint16_t current_max = max_loop_time_us.load();
        while (loop_time > current_max && !max_loop_time_us.compare_exchange_weak(current_max, loop_time));
        
        uint16_t current_min = min_loop_time_us.load();
        while (loop_time < current_min && !min_loop_time_us.compare_exchange_weak(current_min, loop_time));
        
        // CPU utilization (simplified calculation)
        float utilization = std::min(100.0f, loop_time / 10.0f); // Assume 1ms target
        cpu_utilization.store(utilization);
    }
    
    void displayStressTestStatus() {
        std::cout << "=== Performance Stress Test Status ===" << std::endl;
        
        std::cout << "PID: SP=" << pid_setpoint.load() << ", PV=" << pid_process_value.load() 
                  << ", Error=" << pid_error.load() << ", Output=" << pid_output.load() << std::endl;
                  
        std::cout << "COUNTERS: HighFreq=" << high_freq_counter.load() 
                  << ", Interrupts=" << interrupt_counter.load() 
                  << ", Overflows=" << timer_overflow_count.load() << std::endl;
                  
        std::cout << "PERFORMANCE: TotalUpdates=" << total_updates.load() 
                  << ", UPS=" << updates_per_second.load() 
                  << ", CPU=" << cpu_utilization.load() << "%" << std::endl;
                  
        std::cout << "TIMING: MinLoop=" << min_loop_time_us.load() << "µs, "
                  << "MaxLoop=" << max_loop_time_us.load() << "µs" << std::endl;
                  
        std::cout << "SENSORS: T1[0]=" << sensor_array_1[0].load() 
                  << ", P2[0]=" << sensor_array_2[0].load() 
                  << ", Pos3[0]=" << sensor_array_3[0].load() << std::endl;
                  
        std::cout << "VEHICLE: WheelFL=" << wheel_speed_fl.load() << "km/h, "
                  << "LatAccel=" << lateral_acceleration.load() << "g, "
                  << "YawRate=" << yaw_rate.load() << "°/s" << std::endl;
                  
        std::cout << "SYNC: Accumulator=" << shared_accumulator.load() 
                  << ", SyncFlag=" << thread_sync_flag.load() 
                  << ", Barrier=" << thread_barrier_counter.load() << std::endl;
    }
};

void workerThread(HighFrequencyMonitor& monitor, int thread_id) {
    std::cout << "Worker thread " << thread_id << " started" << std::endl;
    
    for (int i = 0; i < 1000; ++i) {
        // Simulate additional load on shared variables
        double current = monitor.shared_accumulator.load();
        while (!monitor.shared_accumulator.compare_exchange_weak(current, current + thread_id * 0.1)) {
            // Retry if CAS fails
        }
        monitor.thread_barrier_counter.fetch_add(1);
        
        // Add some computation to stress the system
        volatile float dummy = 0.0f;
        for (int j = 0; j < 100; ++j) {
            dummy += sin(i * j * 0.001f);
        }
        
        std::this_thread::sleep_for(std::chrono::microseconds(500));
    }
}

int main() {
    std::cout << "Performance Stress Test - High-Frequency Variable Monitoring" << std::endl;
    std::cout << "Simulating 1kHz+ control loops with multiple concurrent threads" << std::endl;
    std::cout << "Testing rapid variable changes and monitoring system performance" << std::endl;
    
    HighFrequencyMonitor monitor;
    
    // Launch worker threads for additional stress
    std::vector<std::thread> worker_threads;
    for (int i = 0; i < 4; ++i) {
        worker_threads.emplace_back(workerThread, std::ref(monitor), i);
    }
    
    auto start_time = std::chrono::high_resolution_clock::now();
    uint64_t updates_this_second = 0;
    auto last_second = start_time;
    
    // Main high-frequency loop
    for (uint64_t cycle = 0; cycle < 10000; ++cycle) { // 10,000 iterations
        auto loop_start = std::chrono::high_resolution_clock::now();
        
        monitor.highFrequencyUpdate(cycle);
        updates_this_second++;
        
        auto loop_end = std::chrono::high_resolution_clock::now();
        monitor.updatePerformanceMetrics(loop_start, loop_end);
        
        // Calculate updates per second
        auto now = std::chrono::high_resolution_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_second).count() >= 1) {
            monitor.updates_per_second.store(static_cast<uint32_t>(updates_this_second));
            updates_this_second = 0;
            last_second = now;
        }
        
        // Display status every 2000 cycles
        if ((cycle + 1) % 2000 == 0) {
            std::cout << "\n--- High-Frequency Cycle " << cycle + 1 << " ---" << std::endl;
            monitor.displayStressTestStatus();
        }
        
        // Target frequency: ~1kHz (1ms per iteration)
        std::this_thread::sleep_for(std::chrono::microseconds(100)); // 10kHz for stress testing
    }
    
    // Wait for worker threads to complete
    for (auto& thread : worker_threads) {
        thread.join();
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto total_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::cout << "\n=== Performance Stress Test Complete ===" << std::endl;
    std::cout << "Total runtime: " << total_duration.count() << " ms" << std::endl;
    std::cout << "Total updates: " << monitor.total_updates.load() << std::endl;
    std::cout << "Average UPS: " << (monitor.total_updates.load() * 1000) / total_duration.count() << std::endl;
    std::cout << "Final accumulator: " << monitor.shared_accumulator.load() << std::endl;
    
    return 0;
}
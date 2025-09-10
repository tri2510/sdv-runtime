#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <cmath>
#include <random>

// Performance stress test with global variables
// High-frequency updates demonstrating ptrace monitoring under load

// Global PID control variables (1kHz+ updates)
std::atomic<float> pid_setpoint{50.0f};
std::atomic<float> pid_process_value{48.5f};
std::atomic<float> pid_error{0.0f};
std::atomic<float> pid_integral{0.0f};
std::atomic<float> pid_derivative{0.0f};
std::atomic<float> pid_output{0.0f};

// Global sensor variables (simulating sensor arrays)
std::atomic<float> sensor_temp_1{25.0f};
std::atomic<float> sensor_temp_2{26.5f};
std::atomic<float> sensor_temp_3{24.8f};
std::atomic<float> sensor_temp_4{27.2f};
std::atomic<uint32_t> sensor_pressure_1{101325};
std::atomic<uint32_t> sensor_pressure_2{101400};
std::atomic<uint32_t> sensor_pressure_3{101280};
std::atomic<uint32_t> sensor_pressure_4{101350};
std::atomic<int32_t> sensor_position_1{0};
std::atomic<int32_t> sensor_position_2{1000};
std::atomic<int32_t> sensor_position_3{-500};
std::atomic<int32_t> sensor_position_4{750};

// Global rapid-changing counters
std::atomic<uint64_t> high_freq_counter{0};
std::atomic<uint32_t> interrupt_counter{0};
std::atomic<uint16_t> timer_overflow_count{0};
std::atomic<uint8_t> state_machine_state{0};

// Global performance metrics
std::atomic<uint64_t> total_updates{0};
std::atomic<uint32_t> updates_per_second{0};
std::atomic<float> cpu_utilization{0.0f};
std::atomic<uint16_t> max_loop_time_us{0};
std::atomic<uint16_t> min_loop_time_us{65535};

// Global multi-threaded shared variables
std::atomic<double> shared_accumulator{0.0};
std::atomic<bool> thread_sync_flag{false};
std::atomic<uint32_t> thread_barrier_counter{0};

// Global vehicle dynamics variables (high-rate updates)
std::atomic<float> wheel_speed_fl{0.0f};  // Front-left
std::atomic<float> wheel_speed_fr{0.0f};  // Front-right  
std::atomic<float> wheel_speed_rl{0.0f};  // Rear-left
std::atomic<float> wheel_speed_rr{0.0f};  // Rear-right
std::atomic<float> lateral_acceleration{0.0f};
std::atomic<float> longitudinal_acceleration{0.0f};
std::atomic<float> yaw_rate{0.0f};
std::atomic<float> steering_wheel_angle{0.0f};

// Global timing and performance variables
std::atomic<uint64_t> microsecond_timer{0};
std::atomic<uint32_t> performance_score{1000};
std::atomic<float> jitter_measurement{0.0f};
std::atomic<uint16_t> cache_miss_count{0};
std::atomic<uint32_t> context_switch_count{0};

// Random number generator
thread_local std::mt19937 rng{std::random_device{}()};
thread_local std::uniform_real_distribution<float> noise_dist{-0.1f, 0.1f};

void highFrequencyUpdate(uint64_t cycle) {
    // PID controller simulation
    float error = pid_setpoint.load() - pid_process_value.load();
    pid_error.store(error);
    
    float integral = pid_integral.load() + error * 0.001f; // 1ms timestep
    pid_integral.store(integral);
    
    static float previous_error = 0.0f;
    float derivative = (error - previous_error) / 0.001f;
    pid_derivative.store(derivative);
    previous_error = error;
    
    float output = 1.2f * error + 0.8f * integral + 0.1f * derivative;
    pid_output.store(output);
    
    // Update process value based on output
    float process_val = pid_process_value.load() + output * 0.01f + noise_dist(rng);
    pid_process_value.store(process_val);
    
    // High-frequency counters
    high_freq_counter.fetch_add(1);
    interrupt_counter.store((interrupt_counter.load() + 17) % 1000000);
    
    if (cycle % 1000 == 0) {
        timer_overflow_count.fetch_add(1);
    }
    
    state_machine_state.store((state_machine_state.load() + 1) % 16);
    
    // Sensor updates with noise
    sensor_temp_1.store(25.0f + 10.0f * sin(cycle * 0.001f) + noise_dist(rng));
    sensor_temp_2.store(26.5f + 8.0f * cos(cycle * 0.0015f) + noise_dist(rng));
    sensor_temp_3.store(24.8f + 12.0f * sin(cycle * 0.0008f) + noise_dist(rng));
    sensor_temp_4.store(27.2f + 6.0f * cos(cycle * 0.0012f) + noise_dist(rng));
    
    sensor_pressure_1.store(101325 + static_cast<uint32_t>(500 * sin(cycle * 0.002f)));
    sensor_pressure_2.store(101400 + static_cast<uint32_t>(300 * cos(cycle * 0.0025f)));
    sensor_pressure_3.store(101280 + static_cast<uint32_t>(400 * sin(cycle * 0.0018f)));
    sensor_pressure_4.store(101350 + static_cast<uint32_t>(350 * cos(cycle * 0.0022f)));
    
    sensor_position_1.store(static_cast<int32_t>(1000 * sin(cycle * 0.0005f)));
    sensor_position_2.store(1000 + static_cast<int32_t>(500 * cos(cycle * 0.0008f)));
    sensor_position_3.store(-500 + static_cast<int32_t>(800 * sin(cycle * 0.0006f)));
    sensor_position_4.store(750 + static_cast<int32_t>(600 * cos(cycle * 0.0007f)));
    
    // Vehicle dynamics
    wheel_speed_fl.store(50.0f + 20.0f * sin(cycle * 0.0003f) + noise_dist(rng));
    wheel_speed_fr.store(52.0f + 18.0f * cos(cycle * 0.0004f) + noise_dist(rng));
    wheel_speed_rl.store(49.0f + 22.0f * sin(cycle * 0.00035f) + noise_dist(rng));
    wheel_speed_rr.store(51.0f + 19.0f * cos(cycle * 0.00045f) + noise_dist(rng));
    
    lateral_acceleration.store(sin(cycle * 0.0002f) * 2.5f + noise_dist(rng));
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
                             uint64_t cycle) {
    total_updates.fetch_add(1);
    
    // Calculate timing metrics
    auto now = std::chrono::high_resolution_clock::now();
    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(now - start_time);
    microsecond_timer.store(elapsed.count());
    
    // Update performance metrics every 100 cycles
    if (cycle % 100 == 0) {
        uint16_t loop_time = static_cast<uint16_t>(elapsed.count() % 10000);
        
        if (loop_time > max_loop_time_us.load()) {
            max_loop_time_us.store(loop_time);
        }
        if (loop_time < min_loop_time_us.load()) {
            min_loop_time_us.store(loop_time);
        }
        
        // Simulate CPU utilization
        float utilization = 60.0f + 30.0f * sin(cycle * 0.01f);
        cpu_utilization.store(utilization);
        
        // Update performance score
        uint32_t score = 1000 - static_cast<uint32_t>(utilization * 5);
        performance_score.store(score);
        
        // Simulate cache misses and context switches
        cache_miss_count.store(cache_miss_count.load() + (cycle % 7));
        context_switch_count.fetch_add(cycle % 3);
        
        // Jitter measurement
        static uint64_t last_time = 0;
        uint64_t current_time = microsecond_timer.load();
        if (last_time > 0) {
            int64_t diff = current_time - last_time;
            float jitter = abs(diff - 100) / 100.0f; // Expecting 100μs intervals
            jitter_measurement.store(jitter);
        }
        last_time = current_time;
    }
}

// Worker thread function
void workerThread(int thread_id) {
    std::mt19937 local_rng{std::random_device{}()};
    std::uniform_real_distribution<double> local_dist{-1.0, 1.0};
    
    for (int i = 0; i < 1000; ++i) {
        // Simulate some work
        double current = shared_accumulator.load();
        while (!shared_accumulator.compare_exchange_weak(current, current + thread_id * 0.1)) {
            // Retry if CAS fails
        }
        
        std::this_thread::sleep_for(std::chrono::microseconds(50));
    }
}

void printPerformanceStatus() {
    std::cout << "\n=== Performance Stress Test Status (Global Variables) ===" << std::endl;
    
    std::cout << "PID Control:" << std::endl;
    std::cout << "  Setpoint: " << pid_setpoint.load() << std::endl;
    std::cout << "  Process Value: " << pid_process_value.load() << std::endl;
    std::cout << "  Error: " << pid_error.load() << std::endl;
    std::cout << "  Output: " << pid_output.load() << std::endl;
    
    std::cout << "Performance Metrics:" << std::endl;
    std::cout << "  High Freq Counter: " << high_freq_counter.load() << std::endl;
    std::cout << "  CPU Utilization: " << cpu_utilization.load() << "%" << std::endl;
    std::cout << "  Performance Score: " << performance_score.load() << "/1000" << std::endl;
    std::cout << "  Max Loop Time: " << max_loop_time_us.load() << " μs" << std::endl;
    
    std::cout << "Vehicle Dynamics:" << std::endl;
    std::cout << "  Wheel Speeds: FL=" << wheel_speed_fl.load()
              << " FR=" << wheel_speed_fr.load()
              << " RL=" << wheel_speed_rl.load()
              << " RR=" << wheel_speed_rr.load() << std::endl;
    std::cout << "  Acceleration: Lat=" << lateral_acceleration.load()
              << " Long=" << longitudinal_acceleration.load() << std::endl;
    
    std::cout << "Shared Data:" << std::endl;
    std::cout << "  Accumulator: " << shared_accumulator.load() << std::endl;
    std::cout << "  Thread Barrier: " << thread_barrier_counter.load() << std::endl;
}

int main() {
    std::cout << "Performance Stress Test Starting (Global Variables Demo)" << std::endl;
    std::cout << "Monitoring " << 50 << " global high-frequency variables..." << std::endl;
    std::cout << "PID controllers, sensor arrays, vehicle dynamics, multi-threading" << std::endl;
    
    // Start worker threads for additional stress
    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        workers.emplace_back(workerThread, i);
    }
    
    auto start_time = std::chrono::high_resolution_clock::now();
    uint64_t cycle = 0;
    
    while (true) {
        highFrequencyUpdate(cycle);
        updatePerformanceMetrics(start_time, cycle);
        
        if (cycle % 1000 == 0) {  // Every 100ms (at 100μs intervals)
            printPerformanceStatus();
        }
        
        cycle++;
        std::this_thread::sleep_for(std::chrono::microseconds(100));  // 10kHz rate
    }
    
    // Join worker threads (never reached in this infinite loop)
    for (auto& worker : workers) {
        worker.join();
    }
    
    return 0;
}
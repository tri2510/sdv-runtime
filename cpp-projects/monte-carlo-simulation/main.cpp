#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>
#include <random>
#include <iomanip>
#include <cmath>
#include <vector>

// Scientific Computing Variables (Global for memory monitoring)
std::atomic<double> pi_estimate{0.0};           // Current π estimation
std::atomic<int> total_samples{0};              // Total Monte Carlo samples processed
std::atomic<int> inside_circle{0};              // Points inside unit circle
std::atomic<double> convergence_rate{0.0};      // Rate of convergence to π
std::atomic<double> error_percentage{100.0};    // Error from true π value
std::atomic<double> computation_speed{0.0};     // Samples per second

// Multi-threaded computation variables
std::atomic<int> active_threads{1};             // Number of active worker threads
std::atomic<int> completed_batches{0};          // Completed computation batches
std::atomic<double> confidence_interval{0.0};   // Statistical confidence interval
std::atomic<bool> converged{false};             // Convergence achieved flag

// Performance metrics
std::atomic<double> cpu_utilization{0.0};       // Estimated CPU usage %
std::atomic<double> memory_usage_mb{0.0};       // Estimated memory usage
std::atomic<int> iterations_per_batch{10000};   // Samples per computation batch
std::atomic<double> elapsed_time{0.0};          // Total computation time

// Advanced statistics
std::atomic<double> standard_deviation{0.0};    // Standard deviation of estimates
std::atomic<double> variance{0.0};              // Variance of π estimates
std::atomic<double> chi_square_statistic{0.0};  // Goodness of fit test

void printBanner() {
    std::cout << R"(
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                   MONTE CARLO π COMPUTATION                      ║
    ║                Scientific Computing Simulation                    ║
    ║                                                                   ║
    ║  🔬 Statistical Analysis  📊 Convergence  🧮 Parallel Processing  ║
    ╚═══════════════════════════════════════════════════════════════════╝
    )" << std::endl;
}

class MonteCarloEngine {
private:
    std::vector<std::thread> worker_threads;
    std::random_device rd;
    std::atomic<bool> running{true};
    std::vector<double> pi_history;
    const double TRUE_PI = 3.141592653589793;
    
public:
    MonteCarloEngine(int num_threads = 4) {
        active_threads = num_threads;
    }
    
    void runSingleThreadedBatch(int batch_size) {
        std::mt19937 gen(rd());
        std::uniform_real_distribution<double> dis(-1.0, 1.0);
        
        int local_inside = 0;
        
        for (int i = 0; i < batch_size; ++i) {
            double x = dis(gen);
            double y = dis(gen);
            
            if (x*x + y*y <= 1.0) {
                local_inside++;
            }
        }
        
        // Update atomic counters
        inside_circle = inside_circle.load() + local_inside;
        total_samples = total_samples.load() + batch_size;
        
        // Calculate current π estimate
        double current_pi = 4.0 * inside_circle.load() / total_samples.load();
        pi_estimate = current_pi;
        
        // Calculate error
        error_percentage = std::abs((current_pi - TRUE_PI) / TRUE_PI) * 100.0;
        
        // Store for statistical analysis
        pi_history.push_back(current_pi);
        
        completed_batches = completed_batches.load() + 1;
    }
    
    void calculateStatistics() {
        if (pi_history.size() < 2) return;
        
        // Calculate variance and standard deviation
        double mean = pi_estimate.load();
        double sum_squared_diff = 0.0;
        
        for (double estimate : pi_history) {
            double diff = estimate - mean;
            sum_squared_diff += diff * diff;
        }
        
        variance = sum_squared_diff / (pi_history.size() - 1);
        standard_deviation = std::sqrt(variance.load());
        
        // Calculate confidence interval (95%)
        double std_error = standard_deviation.load() / std::sqrt(pi_history.size());
        confidence_interval = 1.96 * std_error; // 95% CI
        
        // Calculate convergence rate
        if (pi_history.size() > 10) {
            double recent_change = std::abs(pi_history.back() - pi_history[pi_history.size()-10]);
            convergence_rate = recent_change / 10.0; // Change per batch
        }
        
        // Check for convergence (error < 0.1%)
        converged = (error_percentage.load() < 0.1);
        
        // Calculate chi-square statistic (simplified)
        chi_square_statistic = variance.load() * pi_history.size();
    }
    
    void updatePerformanceMetrics(double batch_time) {
        // Calculate computation speed
        computation_speed = iterations_per_batch.load() / batch_time;
        
        // Estimate CPU utilization (simplified model)
        cpu_utilization = std::min(100.0, (computation_speed.load() / 100000.0) * 100.0);
        
        // Estimate memory usage (simplified)
        memory_usage_mb = (total_samples.load() * sizeof(double)) / (1024.0 * 1024.0) + 
                          pi_history.size() * sizeof(double) / (1024.0 * 1024.0) + 10.0; // Base usage
    }
    
    void runSimulation(int total_batches) {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        for (int batch = 0; batch < total_batches && running.load(); ++batch) {
            auto batch_start = std::chrono::high_resolution_clock::now();
            
            // Run Monte Carlo batch
            runSingleThreadedBatch(iterations_per_batch.load());
            
            auto batch_end = std::chrono::high_resolution_clock::now();
            double batch_time = std::chrono::duration<double>(batch_end - batch_start).count();
            
            // Update statistics and metrics
            calculateStatistics();
            updatePerformanceMetrics(batch_time);
            
            // Update elapsed time
            auto current_time = std::chrono::high_resolution_clock::now();
            elapsed_time = std::chrono::duration<double>(current_time - start_time).count();
            
            // Dynamic batch size adjustment for better performance
            if (batch > 10 && computation_speed > 50000) {
                iterations_per_batch = std::min(50000, iterations_per_batch.load() + 1000);
            }
            
            // Early termination if converged
            if (converged.load() && batch > 20) {
                std::cout << "🎯 CONVERGENCE ACHIEVED! Stopping early at batch " << batch + 1 << std::endl;
                break;
            }
            
            // Small delay for monitoring
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        
        running = false;
    }
};

void printComputationStatus(int batch) {
    std::cout << "\n=== Monte Carlo Batch #" << std::setw(3) << batch + 1 << " ===" << std::endl;
    std::cout << std::fixed << std::setprecision(6);
    
    std::cout << "🧮 π Estimate: " << pi_estimate.load() 
              << " | Error: " << std::setprecision(4) << error_percentage.load() << "%" << std::endl;
              
    std::cout << "📊 Samples: " << total_samples.load() 
              << " | Inside Circle: " << inside_circle.load()
              << " | Batches: " << completed_batches.load() << std::endl;
              
    std::cout << "📈 Speed: " << std::setprecision(0) << computation_speed.load() << " samples/s"
              << " | Conv Rate: " << std::setprecision(6) << convergence_rate.load() << std::endl;
              
    std::cout << "📊 Std Dev: " << std::setprecision(6) << standard_deviation.load()
              << " | Confidence ±: " << confidence_interval.load() << std::endl;
              
    std::cout << "💻 CPU: " << std::setprecision(1) << cpu_utilization.load() << "%"
              << " | Memory: " << memory_usage_mb.load() << " MB"
              << " | Time: " << std::setprecision(2) << elapsed_time.load() << "s" << std::endl;
              
    if (converged.load()) {
        std::cout << "🎯 CONVERGED ✓";
    } else {
        std::cout << "🔄 Computing...";
    }
    std::cout << " | χ²: " << std::setprecision(3) << chi_square_statistic.load() << std::endl;
}

void printFinalResults() {
    std::cout << "\n╔══════════════════════════════════════════════════════════════════╗" << std::endl;
    std::cout << "║                         FINAL RESULTS                           ║" << std::endl;
    std::cout << "╚══════════════════════════════════════════════════════════════════╝" << std::endl;
    
    std::cout << std::fixed << std::setprecision(10);
    std::cout << "🎯 Final π Estimate: " << pi_estimate.load() << std::endl;
    std::cout << "📏 True π Value:     " << 3.141592653589793 << std::endl;
    std::cout << "📊 Absolute Error:   " << std::abs(pi_estimate.load() - 3.141592653589793) << std::endl;
    std::cout << "📈 Relative Error:   " << std::setprecision(6) << error_percentage.load() << "%" << std::endl;
    
    std::cout << std::setprecision(0);
    std::cout << "🧮 Total Samples:    " << total_samples.load() << std::endl;
    std::cout << "📦 Completed Batches:" << completed_batches.load() << std::endl;
    std::cout << "⚡ Average Speed:    " << computation_speed.load() << " samples/second" << std::endl;
    std::cout << "⏱️  Total Time:      " << std::setprecision(2) << elapsed_time.load() << " seconds" << std::endl;
    
    std::cout << std::setprecision(6);
    std::cout << "📊 Standard Dev:     " << standard_deviation.load() << std::endl;
    std::cout << "📈 95% Confidence:   ±" << confidence_interval.load() << std::endl;
    std::cout << "🎯 Converged:        " << (converged.load() ? "YES ✓" : "NO") << std::endl;
}

int main() {
    printBanner();
    
    std::cout << "🚀 Initializing Monte Carlo π Computation..." << std::endl;
    std::cout << "🔬 Using statistical sampling to estimate π value" << std::endl;
    std::cout << "📊 Monitoring variables: pi_estimate, total_samples, inside_circle, convergence_rate, error_percentage, computation_speed" << std::endl;
    std::cout << "🧮 Target accuracy: π ± 0.001 (0.1% error)" << std::endl;
    
    // Initialize computation
    std::this_thread::sleep_for(std::chrono::seconds(1));
    
    std::cout << "\n🔬 Starting Monte Carlo simulation..." << std::endl;
    
    MonteCarloEngine engine(1); // Single-threaded for simplicity
    
    const int MAX_BATCHES = 80;
    
    // Start computation in separate thread
    std::thread computation_thread([&engine, MAX_BATCHES]() {
        engine.runSimulation(MAX_BATCHES);
    });
    
    // Monitor progress
    for (int batch = 0; batch < MAX_BATCHES; ++batch) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        
        // Print status every few batches
        if (batch % 4 == 0) {
            printComputationStatus(batch);
        }
        
        // Check if computation finished early
        if (converged.load() && completed_batches > 20) {
            break;
        }
        
        // Stop if computation thread finished
        if (completed_batches >= MAX_BATCHES) {
            break;
        }
    }
    
    // Wait for computation to complete
    computation_thread.join();
    
    printFinalResults();
    
    return 0;
}
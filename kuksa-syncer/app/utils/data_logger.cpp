#include "data_logger.h"
#include <iostream>
#include <iomanip>

namespace Utils {
    // Define atomic variables  
    std::atomic<int> log_entries{0};
    std::atomic<bool> logging_active{true};
    std::atomic<float> disk_usage{45.2f};
    
    void initialize() {
        std::cout << "🔧 Data Logger initialized" << std::endl;
        logging_active = true;
    }
    
    void update(int cycle) {
        // Simulate logging activity
        if (logging_active.load()) {
            log_entries = cycle * 3; // 3 entries per cycle
            disk_usage = 45.2f + (cycle * 0.1f); // Gradually increasing
        }
        
        // Toggle logging occasionally
        logging_active = (cycle % 50 != 0);
    }
    
    void printStatus() {
        std::cout << std::fixed << std::setprecision(1)
                  << "📝 Logs: " << log_entries.load() << " entries | "
                  << "Active: " << (logging_active.load() ? "YES" : "NO") << " | "
                  << "Disk: " << disk_usage.load() << "% used"
                  << std::endl;
    }
}
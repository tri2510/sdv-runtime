#include "logger.h"
#include <iostream>
#include <chrono>
#include <ctime>

Logger& Logger::getInstance() {
    static Logger instance;
    return instance;
}

void Logger::logInfo(const std::string& message) {
    total_logs = total_logs.load() + 1;
    info_count = info_count.load() + 1;
    
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::cout << "[INFO " << std::ctime(&time) << "] " << message << std::endl;
}

void Logger::logWarning(const std::string& message) {
    total_logs = total_logs.load() + 1;
    warning_count = warning_count.load() + 1;
    
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::cout << "[WARN " << std::ctime(&time) << "] " << message << std::endl;
}

void Logger::logError(const std::string& message) {
    total_logs = total_logs.load() + 1;
    error_count = error_count.load() + 1;
    
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    
    std::cerr << "[ERROR " << std::ctime(&time) << "] " << message << std::endl;
}
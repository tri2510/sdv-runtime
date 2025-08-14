#include "Logger.h"
#include <chrono>

Logger::Logger(const std::string& component) : component(component) {
}

void Logger::info(const std::string& message) {
    std::cout << "[INFO] [" << component << "] " << message << std::endl;
}

void Logger::warning(const std::string& message) {
    std::cout << "[WARN] [" << component << "] " << message << std::endl;
}

void Logger::error(const std::string& message) {
    std::cout << "[ERROR] [" << component << "] " << message << std::endl;
}

void Logger::debug(const std::string& message) {
    std::cout << "[DEBUG] [" << component << "] " << message << std::endl;
}
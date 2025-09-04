#pragma once
#include <atomic>
#include <string>
#include <fstream>

class Logger {
public:
    static Logger& getInstance();
    
    void logInfo(const std::string& message);
    void logWarning(const std::string& message);
    void logError(const std::string& message);
    
    int getLogCount() const { return total_logs.load(); }
    int getErrorCount() const { return error_count.load(); }
    int getWarningCount() const { return warning_count.load(); }

private:
    Logger() = default;
    ~Logger() = default;
    
    std::atomic<int> total_logs{0};
    std::atomic<int> error_count{0};
    std::atomic<int> warning_count{0};
    std::atomic<int> info_count{0};
};
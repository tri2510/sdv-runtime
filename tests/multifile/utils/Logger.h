#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <iostream>

class Logger {
private:
    std::string component;

public:
    Logger(const std::string& component);
    
    void info(const std::string& message);
    void warning(const std::string& message);
    void error(const std::string& message);
    void debug(const std::string& message);
};

#endif // LOGGER_H
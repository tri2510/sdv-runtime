#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <string>
#include <ctime>
#include <sstream>

#define COMM_VERSION "1.0.0-communication-test"
#define BUFFER_SIZE 1024

// Function to get current timestamp
inline std::string getCurrentTimestamp() {
    time_t rawtime;
    time(&rawtime);
    return std::to_string(rawtime);
}

// Function to format message with timestamp
inline std::string formatMessage(const std::string& level, const std::string& message) {
    std::stringstream ss;
    ss << "[" << level << "] " << getCurrentTimestamp() << ": " << message;
    return ss.str();
}

#endif // COMMUNICATION_H
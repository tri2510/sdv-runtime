#include "SystemConfig.h"

SystemConfig::SystemConfig() 
    : version("2.0.1-multifile"), maxSpeed(120.0), maxConnections(50) {
}

std::string SystemConfig::getVersion() const {
    return version;
}

double SystemConfig::getMaxSpeed() const {
    return maxSpeed;
}

int SystemConfig::getMaxConnections() const {
    return maxConnections;
}

void SystemConfig::setMaxSpeed(double speed) {
    if (speed > 0 && speed <= 200) {
        maxSpeed = speed;
    }
}

void SystemConfig::setMaxConnections(int connections) {
    if (connections > 0) {
        maxConnections = connections;
    }
}
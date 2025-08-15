#include "SpeedSensor.h"

SpeedSensor::SpeedSensor(int id, const std::string& name) 
    : sensorId(id), name(name), currentSpeed(0.0), active(true) {
}

int SpeedSensor::getSensorId() const {
    return sensorId;
}

std::string SpeedSensor::getName() const {
    return name;
}

double SpeedSensor::getSpeed() const {
    return currentSpeed;
}

bool SpeedSensor::isActive() const {
    return active;
}

void SpeedSensor::setSpeed(double speed) {
    if (active && speed >= 0) {
        currentSpeed = speed;
    }
}

void SpeedSensor::activate() {
    active = true;
}

void SpeedSensor::deactivate() {
    active = false;
    currentSpeed = 0.0;
}
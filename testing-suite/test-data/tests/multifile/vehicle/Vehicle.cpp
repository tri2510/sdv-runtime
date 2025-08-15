#include "Vehicle.h"

Vehicle::Vehicle(const std::string& id, const std::string& name) 
    : id(id), name(name), speed(0.0), moving(false) {
}

std::string Vehicle::getId() const {
    return id;
}

std::string Vehicle::getName() const {
    return name;
}

double Vehicle::getSpeed() const {
    return speed;
}

bool Vehicle::isMoving() const {
    return moving;
}

void Vehicle::setSpeed(double speed) {
    this->speed = speed;
}

void Vehicle::updateStatus() {
    moving = (speed > 0.1);
}
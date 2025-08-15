#ifndef VEHICLE_H
#define VEHICLE_H

#include <string>

class Vehicle {
private:
    std::string id;
    std::string name;
    double speed;
    bool moving;

public:
    Vehicle(const std::string& id, const std::string& name);
    
    std::string getId() const;
    std::string getName() const;
    double getSpeed() const;
    bool isMoving() const;
    
    void setSpeed(double speed);
    void updateStatus();
};

#endif // VEHICLE_H
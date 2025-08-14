#ifndef SPEEDSENSOR_H
#define SPEEDSENSOR_H

#include <string>

class SpeedSensor {
private:
    int sensorId;
    std::string name;
    double currentSpeed;
    bool active;

public:
    SpeedSensor(int id, const std::string& name);
    
    int getSensorId() const;
    std::string getName() const;
    double getSpeed() const;
    bool isActive() const;
    
    void setSpeed(double speed);
    void activate();
    void deactivate();
};

#endif // SPEEDSENSOR_H
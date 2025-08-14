#ifndef SYSTEMCONFIG_H
#define SYSTEMCONFIG_H

#include <string>

class SystemConfig {
private:
    std::string version;
    double maxSpeed;
    int maxConnections;
    
public:
    SystemConfig();
    
    std::string getVersion() const;
    double getMaxSpeed() const;
    int getMaxConnections() const;
    
    void setMaxSpeed(double speed);
    void setMaxConnections(int connections);
};

#endif // SYSTEMCONFIG_H
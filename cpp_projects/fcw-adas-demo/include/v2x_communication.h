#ifndef V2X_COMMUNICATION_H
#define V2X_COMMUNICATION_H

#include "types.h"
#include <vector>
#include <string>

struct V2XMessage {
    std::string sender_id;
    Position3D sender_position;
    Motion sender_motion;
    float timestamp;
    std::string message_type;
    std::string data;
};

class V2XCommunication {
private:
    std::vector<V2XMessage> received_messages;
    std::string vehicle_id;
    float last_broadcast_time;
    
public:
    V2XCommunication();
    
    void initialize(const std::string& id);
    void update(const Vehicle& ego_vehicle, float current_time);
    
    void broadcast_position(const Vehicle& ego_vehicle, float current_time);
    void broadcast_emergency_warning(const std::string& warning_type, float current_time);
    
    std::vector<Vehicle> get_nearby_vehicles() const;
    std::vector<std::string> get_received_warnings() const;
    
    void simulate_incoming_v2x_data();
    
private:
    void process_received_messages();
    void cleanup_old_messages(float current_time);
};

#endif // V2X_COMMUNICATION_H
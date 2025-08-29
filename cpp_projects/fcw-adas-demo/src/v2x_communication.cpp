#include "v2x_communication.h"
#include <random>
#include <iostream>
#include <algorithm>
#include <iomanip>

V2XCommunication::V2XCommunication() : last_broadcast_time(0.0f) {
    vehicle_id = "EGO_VEHICLE_001";
}

void V2XCommunication::initialize(const std::string& id) {
    vehicle_id = id;
    std::cout << "V2X Communication: Initialized for vehicle " << vehicle_id << std::endl;
}

void V2XCommunication::update(const Vehicle& ego_vehicle, float current_time) {
    // Broadcast position every 100ms
    if (current_time - last_broadcast_time >= 0.1f) {
        broadcast_position(ego_vehicle, current_time);
        last_broadcast_time = current_time;
    }
    
    // Simulate receiving V2X messages
    simulate_incoming_v2x_data();
    
    // Clean up old messages
    cleanup_old_messages(current_time);
    
    // Process any received messages
    process_received_messages();
}

void V2XCommunication::broadcast_position(const Vehicle& ego_vehicle, float current_time) {
    // In a real system, this would transmit over V2X radio
    // For simulation, we just log the broadcast
    static int broadcast_count = 0;
    if (++broadcast_count % 50 == 0) { // Log every 5 seconds
        std::cout << "📡 V2X Broadcast: Position (" 
                  << std::fixed << std::setprecision(1)
                  << ego_vehicle.position.x << ", " 
                  << ego_vehicle.position.y << "), Speed: "
                  << ego_vehicle.motion.velocity.x * 3.6f << " km/h" << std::endl;
    }
}

void V2XCommunication::broadcast_emergency_warning(const std::string& warning_type, float current_time) {
    std::cout << "🚨 V2X Emergency Broadcast: " << warning_type << " at time " 
              << current_time << std::endl;
    
    // Create emergency message
    V2XMessage emergency_msg;
    emergency_msg.sender_id = vehicle_id;
    emergency_msg.timestamp = current_time;
    emergency_msg.message_type = "EMERGENCY";
    emergency_msg.data = warning_type;
    
    // In real system, this would be transmitted to nearby vehicles
}

std::vector<Vehicle> V2XCommunication::get_nearby_vehicles() const {
    std::vector<Vehicle> nearby_vehicles;
    
    // Extract vehicle information from recent V2X messages
    for (const auto& msg : received_messages) {
        if (msg.message_type == "POSITION" && msg.sender_id != vehicle_id) {
            Vehicle vehicle;
            vehicle.position = msg.sender_position;
            vehicle.motion = msg.sender_motion;
            vehicle.is_ego = false;
            vehicle.mass = 1500.0f; // Default mass
            
            nearby_vehicles.push_back(vehicle);
        }
    }
    
    return nearby_vehicles;
}

std::vector<std::string> V2XCommunication::get_received_warnings() const {
    std::vector<std::string> warnings;
    
    for (const auto& msg : received_messages) {
        if (msg.message_type == "WARNING" || msg.message_type == "EMERGENCY") {
            warnings.push_back(msg.sender_id + ": " + msg.data);
        }
    }
    
    return warnings;
}

void V2XCommunication::simulate_incoming_v2x_data() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<> prob(0.0, 1.0);
    static std::uniform_real_distribution<> pos_x(-100.0, 200.0);
    static std::uniform_real_distribution<> pos_y(0.0, 10.5);
    static std::uniform_real_distribution<> speed(10.0, 25.0);
    
    // Randomly receive V2X messages from other vehicles
    if (prob(gen) < 0.1) { // 10% chance per update cycle
        V2XMessage msg;
        msg.sender_id = "VEHICLE_" + std::to_string(static_cast<int>(prob(gen) * 1000));
        msg.sender_position = {static_cast<float>(pos_x(gen)), 
                              static_cast<float>(pos_y(gen)), 0.0f};
        msg.sender_motion.velocity = {static_cast<float>(speed(gen)), 0.0f, 0.0f};
        msg.timestamp = last_broadcast_time;
        msg.message_type = "POSITION";
        msg.data = "Normal driving";
        
        received_messages.push_back(msg);
    }
    
    // Occasionally simulate emergency warnings
    if (prob(gen) < 0.01) { // 1% chance
        V2XMessage warning_msg;
        warning_msg.sender_id = "TRAFFIC_CONTROL_001";
        warning_msg.timestamp = last_broadcast_time;
        warning_msg.message_type = "WARNING";
        warning_msg.data = "Construction ahead - reduce speed";
        
        received_messages.push_back(warning_msg);
        
        std::cout << "📨 V2X Warning received: " << warning_msg.data << std::endl;
    }
}

void V2XCommunication::process_received_messages() {
    // Process any special messages that require action
    for (const auto& msg : received_messages) {
        if (msg.message_type == "EMERGENCY" && msg.sender_id != vehicle_id) {
            // Handle emergency messages from other vehicles
            static float last_emergency_log = 0.0f;
            if (msg.timestamp - last_emergency_log > 5.0f) {
                std::cout << "🚨 Emergency alert from " << msg.sender_id 
                          << ": " << msg.data << std::endl;
                last_emergency_log = msg.timestamp;
            }
        }
    }
}

void V2XCommunication::cleanup_old_messages(float current_time) {
    // Remove messages older than 5 seconds
    const float max_age = 5.0f;
    
    received_messages.erase(
        std::remove_if(received_messages.begin(), received_messages.end(),
            [current_time, max_age](const V2XMessage& msg) {
                return (current_time - msg.timestamp) > max_age;
            }),
        received_messages.end()
    );
}
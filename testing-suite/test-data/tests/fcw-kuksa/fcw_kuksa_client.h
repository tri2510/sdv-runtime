#ifndef FCW_KUKSA_CLIENT_H
#define FCW_KUKSA_CLIENT_H

#include <string>
#include <map>
#include <vector>
#include <chrono>
#include <cmath>
#include <sstream>
#include <iomanip>
#include "vehicle_signals.h"

namespace fcw_kuksa {
    
    // KUKSA Databroker Client (Simplified C++ implementation)
    class KuksaClient {
    private:
        bool connected;
        std::string server_address;
        int server_port;
        
    public:
        KuksaClient() : connected(false), server_port(55555) {}
        
        // Connect to KUKSA Databroker
        bool connect(const std::string& address, int port) {
            server_address = address;
            server_port = port;
            
            // In a real implementation, this would establish gRPC connection
            // For this demo, we simulate the connection attempt
            if (address == "127.0.0.1" && port == 55555) {
                // Simulate connection success/failure based on environment
                // In container with KUKSA running, this would succeed
                connected = false; // Set to false for compilation testing
                return connected;
            }
            return false;
        }
        
        // Read vehicle signal from KUKSA Databroker
        double readSignal(const std::string& signal_path) {
            if (!connected) {
                return 0.0; // Return default value if not connected
            }
            
            // Simulate reading from KUKSA Databroker
            // Real implementation would use gRPC calls to databroker
            if (signal_path == "Vehicle.Speed") {
                return 75.0; // km/h
            } else if (signal_path == "Vehicle.CurrentLocation.Latitude") {
                return 37.7749; // Example latitude
            } else if (signal_path == "Vehicle.CurrentLocation.Longitude") {
                return -122.4194; // Example longitude
            }
            
            return 0.0;
        }
        
        // Write vehicle signal to KUKSA Databroker
        bool writeSignal(const std::string& signal_path, double value) {
            if (!connected) {
                return false; // Cannot write if not connected
            }
            
            // Simulate writing to KUKSA Databroker
            // Real implementation would use gRPC calls to set datapoint values
            return true; // Simulate successful write
        }
        
        // Write string signal to KUKSA Databroker
        bool writeSignal(const std::string& signal_path, const std::string& value) {
            if (!connected) {
                return false;
            }
            
            // Simulate writing string value
            return true;
        }
        
        // Check if connected to databroker
        bool isConnected() const {
            return connected;
        }
        
        // Get connection info
        std::string getConnectionInfo() const {
            std::stringstream ss;
            ss << server_address << ":" << server_port 
               << " (Status: " << (connected ? "Connected" : "Disconnected") << ")";
            return ss.str();
        }
    };
    
    // FCW Analysis Result Structure
    struct FCWAnalysis {
        double distance_meters;
        double relative_speed_kmh;
        double ttc_seconds;
        std::string risk_level;
        double risk_score; // 0.0 = safe, 1.0 = maximum risk
        
        FCWAnalysis() : distance_meters(0), relative_speed_kmh(0), 
                       ttc_seconds(999.0), risk_level("NONE"), risk_score(0.0) {}
    };
    
    // FCW Response Structure
    struct FCWResponse {
        bool warning_active;
        bool critical_warning;
        std::string warning_level;
        std::string audio_alert;
        std::string visual_alert;
        bool emergency_brake;
        bool request_lane_change;
        int target_lane;
        
        FCWResponse() : warning_active(false), critical_warning(false), 
                       warning_level("NONE"), audio_alert("Silent"), 
                       visual_alert("Normal"), emergency_brake(false),
                       request_lane_change(false), target_lane(0) {}
    };
    
    // FCW System with KUKSA Integration
    class FCWSystemWithKuksa {
    private:
        bool kuksa_available;
        
        // Calculate Time-to-Collision
        double calculateTTC(double distance, double relative_speed_kmh) {
            if (relative_speed_kmh <= 0) {
                return 999.0; // No collision risk
            }
            
            double relative_speed_ms = relative_speed_kmh / 3.6; // Convert km/h to m/s
            return distance / relative_speed_ms;
        }
        
        // Assess risk level from TTC
        std::string assessRiskLevel(double ttc_seconds, double& risk_score) {
            if (ttc_seconds < 1.5) {
                risk_score = 1.0;
                return "CRITICAL";
            } else if (ttc_seconds < 3.0) {
                risk_score = 0.7;
                return "WARNING";
            } else if (ttc_seconds < 5.0) {
                risk_score = 0.3;
                return "LOW";
            } else {
                risk_score = 0.0;
                return "NONE";
            }
        }
        
    public:
        FCWSystemWithKuksa(bool kuksa_connected) : kuksa_available(kuksa_connected) {}
        
        // Read vehicle data from KUKSA Databroker
        VehicleData readVehicleDataFromKuksa(KuksaClient& client) {
            VehicleData vehicle;
            
            if (kuksa_available && client.isConnected()) {
                // Read actual signals from KUKSA
                vehicle.speed = client.readSignal("Vehicle.Speed");
                vehicle.position = client.readSignal("Vehicle.CurrentLocation.Latitude");
                vehicle.lane_id = 2; // Would be derived from other signals
            } else {
                // Use default simulation data
                vehicle.speed = 75.0;
                vehicle.position = 150.0;
                vehicle.lane_id = 2;
            }
            
            return vehicle;
        }
        
        // Perform FCW collision analysis
        FCWAnalysis performFCWAnalysis(const VehicleData& ego, const VehicleData& front) {
            FCWAnalysis analysis;
            
            analysis.distance_meters = front.position - ego.position;
            analysis.relative_speed_kmh = ego.speed - front.speed;
            analysis.ttc_seconds = calculateTTC(analysis.distance_meters, analysis.relative_speed_kmh);
            analysis.risk_level = assessRiskLevel(analysis.ttc_seconds, analysis.risk_score);
            
            return analysis;
        }
        
        // Generate FCW response based on analysis
        FCWResponse generateFCWResponse(const FCWAnalysis& analysis) {
            FCWResponse response;
            
            if (analysis.risk_level == "CRITICAL") {
                response.critical_warning = true;
                response.warning_active = true;
                response.warning_level = "CRITICAL";
                response.audio_alert = "High-frequency beeping";
                response.visual_alert = "Red flashing display";
                response.emergency_brake = true;
                response.request_lane_change = true;
                response.target_lane = 3; // Example lane change
                
            } else if (analysis.risk_level == "WARNING") {
                response.warning_active = true;
                response.warning_level = "WARNING";
                response.audio_alert = "Medium-frequency beeping";
                response.visual_alert = "Yellow steady display";
                response.emergency_brake = false;
                response.request_lane_change = false;
                
            } else if (analysis.risk_level == "LOW") {
                response.warning_active = true;
                response.warning_level = "LOW";
                response.audio_alert = "Single beep";
                response.visual_alert = "Blue indicator";
                response.emergency_brake = false;
                response.request_lane_change = false;
                
            } else {
                response.warning_level = "NONE";
                response.audio_alert = "Silent";
                response.visual_alert = "Normal";
            }
            
            return response;
        }
        
        // Write FCW data to KUKSA Databroker
        bool writeFCWDataToKuksa(KuksaClient& client, const FCWAnalysis& analysis, 
                                 const FCWResponse& response) {
            if (!kuksa_available || !client.isConnected()) {
                return false;
            }
            
            // Write FCW status signals to VSS paths
            bool success = true;
            
            success &= client.writeSignal("Vehicle.ADAS.FCW.Status", 
                                         response.warning_active ? "ACTIVE" : "INACTIVE");
            success &= client.writeSignal("Vehicle.ADAS.FCW.WarningLevel", response.warning_level);
            success &= client.writeSignal("Vehicle.ADAS.FCW.TimeToCollision", analysis.ttc_seconds);
            success &= client.writeSignal("Vehicle.ADAS.FCW.RiskScore", analysis.risk_score);
            success &= client.writeSignal("Vehicle.ADAS.EmergencyBrake", 
                                         response.emergency_brake ? "ACTIVE" : "INACTIVE");
            
            return success;
        }
    };
}

#endif // FCW_KUKSA_CLIENT_H
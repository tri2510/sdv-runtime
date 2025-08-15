#ifndef VEHICLE_SIGNALS_H
#define VEHICLE_SIGNALS_H

#include <string>

// Vehicle Signal Specification (VSS 4.0) Path Definitions
struct VehicleSignalPaths {
    // Basic vehicle signals
    std::string vehicle_speed = "Vehicle.Speed";
    std::string position_x = "Vehicle.CurrentLocation.Latitude";
    std::string position_y = "Vehicle.CurrentLocation.Longitude";
    std::string heading = "Vehicle.CurrentLocation.Heading";
    
    // ADAS FCW specific signals
    std::string fcw_status = "Vehicle.ADAS.FCW.Status";
    std::string warning_level = "Vehicle.ADAS.FCW.WarningLevel";
    std::string ttc_seconds = "Vehicle.ADAS.FCW.TimeToCollision";
    std::string risk_score = "Vehicle.ADAS.FCW.RiskScore";
    
    // Emergency systems
    std::string emergency_brake = "Vehicle.ADAS.EmergencyBrake";
    std::string lane_change_request = "Vehicle.ADAS.LaneChangeAssist.Status";
    
    // Warning systems
    std::string audio_alert = "Vehicle.Cabin.AudioSystem.Alert";
    std::string visual_alert = "Vehicle.Cabin.HMI.FCWWarning";
    
    // Vehicle state signals
    std::string gear_position = "Vehicle.Drivetrain.Transmission.Gear";
    std::string brake_pedal = "Vehicle.Chassis.Brake.PedalPosition";
    std::string acceleration = "Vehicle.Acceleration.Longitudinal";
    
    // Environment sensing (would come from sensors/cameras)
    std::string front_distance = "Vehicle.ADAS.ObstacleDetection.FrontDistance";
    std::string relative_speed = "Vehicle.ADAS.ObstacleDetection.RelativeSpeed";
    
    VehicleSignalPaths() {
        // Constructor - paths are initialized above
    }
    
    // Print all VSS paths for debugging
    void printAllPaths() const {
        std::cout << "=== Vehicle Signal Specification (VSS 4.0) Paths ===" << std::endl;
        std::cout << "Basic Vehicle:" << std::endl;
        std::cout << "  Speed: " << vehicle_speed << std::endl;
        std::cout << "  Position: " << position_x << ", " << position_y << std::endl;
        std::cout << "  Heading: " << heading << std::endl;
        std::cout << "" << std::endl;
        
        std::cout << "ADAS FCW System:" << std::endl;
        std::cout << "  Status: " << fcw_status << std::endl;
        std::cout << "  Warning Level: " << warning_level << std::endl;
        std::cout << "  Time-to-Collision: " << ttc_seconds << std::endl;
        std::cout << "  Risk Score: " << risk_score << std::endl;
        std::cout << "" << std::endl;
        
        std::cout << "Emergency Systems:" << std::endl;
        std::cout << "  Emergency Brake: " << emergency_brake << std::endl;
        std::cout << "  Lane Change: " << lane_change_request << std::endl;
        std::cout << "" << std::endl;
        
        std::cout << "Warning Systems:" << std::endl;
        std::cout << "  Audio Alert: " << audio_alert << std::endl;
        std::cout << "  Visual Alert: " << visual_alert << std::endl;
    }
};

// Vehicle Data Structure
struct VehicleData {
    double speed;        // km/h
    double position;     // meters (or latitude for GPS)
    int lane_id;         // lane number
    double heading;      // degrees
    double acceleration; // m/s²
    
    VehicleData() : speed(0.0), position(0.0), lane_id(1), 
                   heading(0.0), acceleration(0.0) {}
    
    VehicleData(double s, double p, int l) : speed(s), position(p), lane_id(l),
                                           heading(0.0), acceleration(0.0) {}
};

// KUKSA Signal Value Types
enum class SignalType {
    DOUBLE,
    STRING,
    BOOLEAN,
    INTEGER
};

// KUKSA Signal Definition
struct KuksaSignal {
    std::string path;
    SignalType type;
    std::string description;
    std::string unit;
    
    KuksaSignal(const std::string& p, SignalType t, const std::string& desc, 
               const std::string& u = "") 
        : path(p), type(t), description(desc), unit(u) {}
};

// Pre-defined KUKSA signals for FCW system
class FCWKuksaSignals {
public:
    static std::vector<KuksaSignal> getFCWSignals() {
        return {
            KuksaSignal("Vehicle.Speed", SignalType::DOUBLE, "Vehicle speed", "km/h"),
            KuksaSignal("Vehicle.ADAS.FCW.Status", SignalType::STRING, "FCW system status"),
            KuksaSignal("Vehicle.ADAS.FCW.WarningLevel", SignalType::STRING, "FCW warning level"),
            KuksaSignal("Vehicle.ADAS.FCW.TimeToCollision", SignalType::DOUBLE, "Time to collision", "s"),
            KuksaSignal("Vehicle.ADAS.FCW.RiskScore", SignalType::DOUBLE, "Collision risk score", "ratio"),
            KuksaSignal("Vehicle.ADAS.EmergencyBrake", SignalType::STRING, "Emergency brake status"),
            KuksaSignal("Vehicle.CurrentLocation.Latitude", SignalType::DOUBLE, "GPS Latitude", "degrees"),
            KuksaSignal("Vehicle.CurrentLocation.Longitude", SignalType::DOUBLE, "GPS Longitude", "degrees"),
            KuksaSignal("Vehicle.Acceleration.Longitudinal", SignalType::DOUBLE, "Longitudinal acceleration", "m/s²")
        };
    }
    
    static void printSignalDefinitions() {
        std::cout << "=== FCW KUKSA Signal Definitions ===" << std::endl;
        auto signals = getFCWSignals();
        
        for (const auto& signal : signals) {
            std::cout << "📡 " << signal.path << std::endl;
            std::cout << "   Type: " << getSignalTypeString(signal.type) << std::endl;
            std::cout << "   Description: " << signal.description << std::endl;
            if (!signal.unit.empty()) {
                std::cout << "   Unit: " << signal.unit << std::endl;
            }
            std::cout << std::endl;
        }
    }
    
private:
    static std::string getSignalTypeString(SignalType type) {
        switch (type) {
            case SignalType::DOUBLE: return "Double";
            case SignalType::STRING: return "String";
            case SignalType::BOOLEAN: return "Boolean";
            case SignalType::INTEGER: return "Integer";
            default: return "Unknown";
        }
    }
};

#endif // VEHICLE_SIGNALS_H
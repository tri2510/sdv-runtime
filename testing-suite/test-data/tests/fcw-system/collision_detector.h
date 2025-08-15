#ifndef COLLISION_DETECTOR_H
#define COLLISION_DETECTOR_H

#include "fcw_types.h"
#include <vector>
#include <cmath>

// Advanced Collision Detection Features
namespace CollisionDetector {
    
    // Physics-based TTC calculation with acceleration
    struct AdvancedTTC {
        double basic_ttc;           // Basic TTC without acceleration
        double acceleration_adjusted; // TTC considering deceleration
        bool emergency_braking;     // Whether emergency braking is needed
        
        AdvancedTTC() : basic_ttc(999.0), acceleration_adjusted(999.0), emergency_braking(false) {}
    };
    
    // Calculate advanced TTC with physics
    AdvancedTTC calculateAdvancedTTC(const VehicleState& ego, const VehicleState& front, 
                                   double ego_accel = -3.5) { // Default emergency braking deceleration
        AdvancedTTC result;
        
        double distance = front.position - ego.position;
        double relative_speed = ego.speed - front.speed; // km/h
        
        // Basic TTC calculation
        if (relative_speed > 0) {
            double relative_speed_ms = relative_speed / 3.6; // Convert to m/s
            result.basic_ttc = distance / relative_speed_ms;
        }
        
        // Advanced TTC with acceleration (quadratic equation)
        // d = v*t + 0.5*a*t^2, solve for t when d = 0 (collision)
        if (relative_speed > 0 && ego_accel != 0) {
            double v = relative_speed / 3.6; // m/s
            double a = ego_accel;             // m/s^2
            double d = distance;              // m
            
            // Quadratic formula: 0.5*a*t^2 + v*t - d = 0
            double discriminant = v*v + 2*a*d;
            
            if (discriminant >= 0 && a < 0) { // Only for deceleration
                double t1 = (-v + sqrt(discriminant)) / a;
                double t2 = (-v - sqrt(discriminant)) / a;
                
                // Take the positive, smaller time
                if (t1 > 0 && t2 > 0) {
                    result.acceleration_adjusted = std::min(t1, t2);
                } else if (t1 > 0) {
                    result.acceleration_adjusted = t1;
                } else if (t2 > 0) {
                    result.acceleration_adjusted = t2;
                }
            }
        }
        
        // Determine if emergency braking is needed
        result.emergency_braking = (result.acceleration_adjusted < CRITICAL_TTC_THRESHOLD);
        
        return result;
    }
    
    // Multi-lane collision risk assessment
    struct LaneRisk {
        int lane_id;
        double risk_score;        // 0.0 = safe, 1.0 = maximum risk
        bool recommended_lane;    // Whether this lane is recommended for lane change
        
        LaneRisk(int id = 1, double score = 0.0, bool rec = false) 
            : lane_id(id), risk_score(score), recommended_lane(rec) {}
    };
    
    // Assess lane change options
    std::vector<LaneRisk> assessLaneChangeOptions(const VehicleState& ego_vehicle, 
                                                 const std::vector<VehicleState>& surrounding_vehicles) {
        std::vector<LaneRisk> lane_risks;
        
        // Assess lanes 1, 2, 3, 4 (typical highway)
        for (int lane = 1; lane <= 4; lane++) {
            LaneRisk risk(lane);
            
            // Calculate risk based on vehicles in this lane
            for (const auto& vehicle : surrounding_vehicles) {
                if (vehicle.lane_id == lane) {
                    double distance = std::abs(vehicle.position - ego_vehicle.position);
                    double speed_diff = std::abs(vehicle.speed - ego_vehicle.speed);
                    
                    // Risk increases with closer distance and speed differences
                    double lane_risk = std::max(0.0, 1.0 - (distance / MAX_DETECTION_RANGE)) + 
                                      (speed_diff / 100.0); // Normalize speed difference
                    
                    risk.risk_score = std::max(risk.risk_score, lane_risk);
                }
            }
            
            // Current lane gets penalty if there's collision risk
            if (lane == ego_vehicle.lane_id) {
                risk.risk_score += 0.3; // Penalty for staying in risky lane
            }
            
            // Recommend lane with lowest risk (not current lane)
            risk.recommended_lane = (risk.risk_score < 0.2 && lane != ego_vehicle.lane_id);
            
            lane_risks.push_back(risk);
        }
        
        return lane_risks;
    }
    
    // Emergency action recommendation
    struct EmergencyAction {
        bool emergency_brake;
        bool request_lane_change;
        int target_lane;
        double recommended_deceleration; // m/s^2
        std::string action_reason;
        
        EmergencyAction() : emergency_brake(false), request_lane_change(false), 
                           target_lane(0), recommended_deceleration(0.0) {}
    };
    
    // Generate emergency action plan
    EmergencyAction generateEmergencyAction(const AdvancedTTC& ttc_analysis,
                                          const std::vector<LaneRisk>& lane_options) {
        EmergencyAction action;
        
        if (ttc_analysis.acceleration_adjusted < CRITICAL_TTC_THRESHOLD) {
            action.emergency_brake = true;
            action.recommended_deceleration = -5.0; // Strong emergency braking
            action.action_reason = "Critical collision risk detected - emergency braking required";
            
            // Find safest lane for emergency lane change
            double lowest_risk = 1.0;
            for (const auto& lane : lane_options) {
                if (lane.recommended_lane && lane.risk_score < lowest_risk) {
                    action.request_lane_change = true;
                    action.target_lane = lane.lane_id;
                    lowest_risk = lane.risk_score;
                }
            }
            
            if (action.request_lane_change) {
                action.action_reason += " + emergency lane change to Lane " + std::to_string(action.target_lane);
            }
            
        } else if (ttc_analysis.basic_ttc < WARNING_TTC_THRESHOLD) {
            action.recommended_deceleration = -2.0; // Moderate braking
            action.action_reason = "Warning level - precautionary deceleration";
        }
        
        return action;
    }
}

#endif // COLLISION_DETECTOR_H
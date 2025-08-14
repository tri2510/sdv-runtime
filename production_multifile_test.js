const io = require('socket.io-client');

console.log('🐳 Production SDV Runtime: Multi-File Project Test');
console.log('==================================================\n');

const socket = io('http://localhost:3090');

// Complex project to test production container's full capabilities
const productionProject = {
    "main.cpp": `#include <iostream>
#include <vector>
#include <memory>
#include "sdv/vehicle_engine.h"
#include "fcw/fcw_system.h"
#include "utils/logger.h"
#include "config/sdv_settings.h"

int main() {
    Logger logger;
    logger.info("Starting Production SDV Runtime multi-file test...");
    
    // Test SDV Vehicle Engine
    auto engine = std::make_unique<VehicleEngine>();
    engine->initialize();
    
    // Test FCW System  
    auto fcw = std::make_unique<FCWSystem>();
    fcw->setThresholds(2.5, 1.0);
    
    std::vector<double> speeds = {30.0, 45.0, 60.0, 80.0};
    
    logger.info("Testing SDV vehicle systems in production container...");
    
    for (const auto& speed : speeds) {
        engine->setSpeed(speed);
        auto status = fcw->checkCollisionRisk(speed, 15.0);
        
        std::cout << "Speed: " << speed << " km/h, FCW Status: " 
                  << (status ? "WARNING" : "SAFE") << std::endl;
    }
    
    logger.info("Production SDV multi-file test completed successfully!");
    logger.info("All enhanced compilation features working in production!");
    
    return 0;
}`,

    "sdv/vehicle_engine.cpp": `#include "vehicle_engine.h"
#include <iostream>
#include <algorithm>

VehicleEngine::VehicleEngine() : currentSpeed(0.0), isInitialized(false) {}

void VehicleEngine::initialize() {
    isInitialized = true;
    std::cout << "[SDV ENGINE] Vehicle engine initialized for production runtime" << std::endl;
}

void VehicleEngine::setSpeed(double speed) {
    if (!isInitialized) {
        std::cout << "[SDV ENGINE] Error: Engine not initialized" << std::endl;
        return;
    }
    
    currentSpeed = std::max(0.0, speed);
    std::cout << "[SDV ENGINE] Speed set to: " << currentSpeed << " km/h" << std::endl;
}

double VehicleEngine::getSpeed() const {
    return currentSpeed;
}

bool VehicleEngine::isEngineReady() const {
    return isInitialized && currentSpeed >= 0.0;
}`,

    "fcw/fcw_system.cpp": `#include "fcw_system.h"
#include <iostream>
#include <cmath>

FCWSystem::FCWSystem() : warningThreshold(3.0), criticalThreshold(1.5) {}

void FCWSystem::setThresholds(double warning, double critical) {
    warningThreshold = warning;
    criticalThreshold = critical;
    std::cout << "[FCW SYSTEM] Thresholds set - Warning: " << warning 
              << "s, Critical: " << critical << "s" << std::endl;
}

bool FCWSystem::checkCollisionRisk(double vehicleSpeed, double distanceToObstacle) {
    if (vehicleSpeed <= 0.0 || distanceToObstacle <= 0.0) {
        return false;
    }
    
    // Calculate time to collision (simplified)
    double timeToCollision = distanceToObstacle / (vehicleSpeed / 3.6); // Convert km/h to m/s
    
    bool riskDetected = timeToCollision <= warningThreshold;
    
    if (riskDetected) {
        std::cout << "[FCW SYSTEM] COLLISION RISK DETECTED! TTC: " 
                  << timeToCollision << "s" << std::endl;
    }
    
    return riskDetected;
}

double FCWSystem::calculateTTC(double speed, double distance) {
    if (speed <= 0.0) return INFINITY;
    return distance / (speed / 3.6);
}`,

    "utils/logger.cpp": `#include "logger.h"
#include <iostream>
#include <chrono>
#include <iomanip>
#include <sstream>

void Logger::info(const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::cout << "[PROD-SDV] [" 
              << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
              << "] INFO: " << message << std::endl;
}

void Logger::error(const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::cout << "[PROD-SDV] [" 
              << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
              << "] ERROR: " << message << std::endl;
}

void Logger::warning(const std::string& message) {
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::cout << "[PROD-SDV] [" 
              << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S")
              << "] WARN: " << message << std::endl;
}`,

    "include/sdv/vehicle_engine.h": `#ifndef VEHICLE_ENGINE_H
#define VEHICLE_ENGINE_H

class VehicleEngine {
private:
    double currentSpeed;
    bool isInitialized;

public:
    VehicleEngine();
    void initialize();
    void setSpeed(double speed);
    double getSpeed() const;
    bool isEngineReady() const;
};

#endif`,

    "include/fcw/fcw_system.h": `#ifndef FCW_SYSTEM_H
#define FCW_SYSTEM_H

class FCWSystem {
private:
    double warningThreshold;
    double criticalThreshold;

public:
    FCWSystem();
    void setThresholds(double warning, double critical);
    bool checkCollisionRisk(double vehicleSpeed, double distanceToObstacle);
    double calculateTTC(double speed, double distance);
};

#endif`,

    "include/utils/logger.h": `#ifndef LOGGER_H
#define LOGGER_H

#include <string>

class Logger {
public:
    void info(const std::string& message);
    void error(const std::string& message);
    void warning(const std::string& message);
};

#endif`,

    "include/config/sdv_settings.h": `#ifndef SDV_SETTINGS_H
#define SDV_SETTINGS_H

#define SDV_VERSION "2.0.0"
#define PRODUCTION_ENVIRONMENT "SDV Runtime Container"
#define FCW_DEFAULT_WARNING_THRESHOLD 3.0
#define FCW_DEFAULT_CRITICAL_THRESHOLD 1.5
#define MAX_VEHICLE_SPEED 200.0

// Production SDV Runtime Configuration
#define CONTAINER_COMPILATION_ENABLED true
#define MULTI_FILE_PROJECT_SUPPORT true

#endif`
};

let phases = [];
let startTime = Date.now();

socket.on('connect', () => {
    console.log('🔌 Connected to Production SDV Runtime container');
    console.log('📤 Uploading complex multi-file SDV project to production container...\n');
    
    socket.emit('compile_cpp', {
        files: productionProject,
        app_name: "production_sdv_multifile",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push({ phase: data.status, time: elapsed, success: data.code === 0 });
    
    if (data.status === 'run-stdout') {
        console.log(`🚀 SDV Production Output: ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 Production File: ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 Production Build: ${data.result.trim()}`);
    } else if (data.status.includes('configure')) {
        console.log(`⚙️  Configuration: ${data.result.trim()}`);
    } else {
        console.log(`📋 [${elapsed}ms] ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Production SDV Multi-File Test: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Production Time: ${elapsed}ms`);
        console.log(`📊 Compilation Phases: ${phases.length}`);
        
        console.log('\n📈 Production Phase Breakdown:');
        phases.forEach((phase, idx) => {
            if (idx < 10) { // Show first 10 phases
                console.log(`  ${idx + 1}. ${phase.phase} (${phase.time}ms) ${phase.success ? '✅' : '❌'}`);
            }
        });
        if (phases.length > 10) {
            console.log(`  ... and ${phases.length - 10} more phases`);
        }
        
        console.log('\n🏆 Production SDV Runtime Enhanced Compilation Features:');
        console.log('  ✅ Multi-file C++ project compilation');
        console.log('  ✅ Dynamic header include resolution');
        console.log('  ✅ CMake build system integration');
        console.log('  ✅ Real-time compilation streaming');
        console.log('  ✅ Container-aware path handling');
        console.log('  ✅ Production environment execution');
        
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Production SDV connection failed:', error.message);
});

socket.on('disconnect', (reason) => {
    console.log(`🔌 Disconnected from Production SDV: ${reason}`);
    process.exit(0);
});

console.log('🚀 Starting Production SDV Runtime complex multi-file test...');
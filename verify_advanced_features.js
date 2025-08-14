const io = require('socket.io-client');

console.log('🔬 VERIFICATION: Advanced Features Test');
console.log('=====================================\n');

const socket = io('http://localhost:3090');

// Advanced project with deep nested structure and complex dependencies
const advancedProject = {
    "main.cpp": `#include <iostream>
#include <vector>
#include <memory>
#include "deep/nested/component.h"
#include "modules/data_processor.h" 
#include "utils/math/calculations.h"
#include "config/system_config.h"

int main() {
    std::cout << "=== ADVANCED FEATURE VERIFICATION ===" << std::endl;
    
    // Test deep nested includes
    auto component = std::make_unique<DeepNestedComponent>();
    component->initialize();
    
    // Test cross-module dependencies
    DataProcessor processor;
    std::vector<double> data = {1.5, 2.7, 3.9, 4.2, 5.8};
    
    auto result = processor.processVector(data);
    std::cout << "Processed " << data.size() << " elements" << std::endl;
    
    // Test mathematical utilities
    double sum = MathUtils::calculateSum(data);
    double avg = MathUtils::calculateAverage(data);
    
    std::cout << "Sum: " << sum << ", Average: " << avg << std::endl;
    
    // Test configuration system
    std::cout << "System Version: " << SYSTEM_VERSION << std::endl;
    std::cout << "Max Processing Elements: " << MAX_ELEMENTS << std::endl;
    
    std::cout << "✅ All advanced features verified successfully!" << std::endl;
    
    return 0;
}`,

    "deep/nested/component.cpp": `#include "component.h"
#include <iostream>

void DeepNestedComponent::initialize() {
    initialized = true;
    std::cout << "[DEEP] Deep nested component initialized" << std::endl;
}

bool DeepNestedComponent::isReady() const {
    return initialized;
}`,

    "modules/data_processor.cpp": `#include "data_processor.h"
#include "../utils/math/calculations.h"
#include <algorithm>

std::vector<double> DataProcessor::processVector(const std::vector<double>& input) {
    std::vector<double> result = input;
    
    // Apply processing using math utilities
    std::transform(result.begin(), result.end(), result.begin(),
                   [](double x) { return x * 1.5; });
    
    return result;
}

double DataProcessor::getProcessingFactor() const {
    return 1.5;
}`,

    "utils/math/calculations.cpp": `#include "calculations.h"
#include <numeric>

double MathUtils::calculateSum(const std::vector<double>& data) {
    return std::accumulate(data.begin(), data.end(), 0.0);
}

double MathUtils::calculateAverage(const std::vector<double>& data) {
    if (data.empty()) return 0.0;
    return calculateSum(data) / data.size();
}

double MathUtils::calculateStandardDeviation(const std::vector<double>& data) {
    if (data.size() <= 1) return 0.0;
    
    double mean = calculateAverage(data);
    double sum = 0.0;
    
    for (double value : data) {
        sum += (value - mean) * (value - mean);
    }
    
    return std::sqrt(sum / (data.size() - 1));
}`,

    "include/deep/nested/component.h": `#ifndef DEEP_NESTED_COMPONENT_H
#define DEEP_NESTED_COMPONENT_H

class DeepNestedComponent {
private:
    bool initialized = false;

public:
    void initialize();
    bool isReady() const;
};

#endif`,

    "include/modules/data_processor.h": `#ifndef DATA_PROCESSOR_H
#define DATA_PROCESSOR_H

#include <vector>

class DataProcessor {
public:
    std::vector<double> processVector(const std::vector<double>& input);
    double getProcessingFactor() const;
};

#endif`,

    "include/utils/math/calculations.h": `#ifndef CALCULATIONS_H
#define CALCULATIONS_H

#include <vector>
#include <cmath>

class MathUtils {
public:
    static double calculateSum(const std::vector<double>& data);
    static double calculateAverage(const std::vector<double>& data);
    static double calculateStandardDeviation(const std::vector<double>& data);
};

#endif`,

    "include/config/system_config.h": `#ifndef SYSTEM_CONFIG_H
#define SYSTEM_CONFIG_H

#define SYSTEM_VERSION "3.0.0-advanced"
#define MAX_ELEMENTS 10000
#define PROCESSING_ENABLED true
#define DEEP_NESTING_SUPPORT true
#define CROSS_MODULE_DEPENDENCIES true

// Advanced feature flags
#define FEATURE_MATH_UTILS true
#define FEATURE_DATA_PROCESSING true
#define FEATURE_NESTED_COMPONENTS true

#endif`
};

let phases = [];
let fileCount = 0;
let startTime = Date.now();

socket.on('connect', () => {
    console.log('🔌 Connected for advanced feature testing');
    console.log('📁 Project structure:');
    console.log('  - 8 files across 6 different directories');
    console.log('  - Deep nested includes (3+ levels)');
    console.log('  - Cross-module dependencies');
    console.log('  - Complex header resolution');
    console.log('📤 Uploading advanced project...\n');
    
    socket.emit('compile_cpp', {
        files: advancedProject,
        app_name: "advanced_features_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push({ status: data.status, time: elapsed, code: data.code });
    
    if (data.status === 'file-written') {
        fileCount++;
        console.log(`📝 [${elapsed}ms] File ${fileCount}/8: ${data.result.trim()}`);
    } else if (data.status.includes('configure')) {
        console.log(`⚙️  [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🔬 ADVANCED FEATURES VERIFICATION RESULTS:`);
        console.log(`==========================================`);
        console.log(`🎯 Overall Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        console.log(`📊 Total Phases: ${phases.length}`);
        console.log(`📁 Files Processed: ${fileCount}/8`);
        
        console.log(`\n🔍 Feature Verification Details:`);
        
        // Verify file processing
        if (fileCount === 8) {
            console.log(`  ✅ Multi-file processing: All 8 files processed correctly`);
        } else {
            console.log(`  ❌ Multi-file processing: Only ${fileCount}/8 files processed`);
        }
        
        // Verify deep directory structure
        const configurePhases = phases.filter(p => p.status.includes('configure'));
        if (configurePhases.length > 0) {
            console.log(`  ✅ CMake configuration: ${configurePhases.length} configuration steps`);
        } else {
            console.log(`  ❌ CMake configuration: No configuration detected`);
        }
        
        // Verify build process
        const buildPhases = phases.filter(p => p.status.includes('build'));
        if (buildPhases.length > 0) {
            console.log(`  ✅ Build process: ${buildPhases.length} build steps completed`);
        } else {
            console.log(`  ❌ Build process: No build steps detected`);
        }
        
        // Verify execution
        const runPhases = phases.filter(p => p.status.includes('run'));
        if (runPhases.length > 0 && data.code === 0) {
            console.log(`  ✅ Program execution: Successful with exit code 0`);
        } else {
            console.log(`  ❌ Program execution: Failed or no execution detected`);
        }
        
        // Performance analysis
        console.log(`\n📈 Performance Analysis:`);
        console.log(`  ⚡ Files/second: ${(fileCount / (elapsed/1000)).toFixed(1)}`);
        console.log(`  🕐 Average phase time: ${(elapsed/phases.length).toFixed(1)}ms`);
        
        const success = data.code === 0 && fileCount === 8 && buildPhases.length > 0;
        console.log(`\n🏆 ADVANCED VERIFICATION: ${success ? '✅ PASSED' : '❌ FAILED'}`);
        
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ FAIL: Connection error:', error.message);
    console.log('🏆 ADVANCED VERIFICATION: ❌ FAILED');
    process.exit(1);
});

console.log('🔄 Starting advanced features verification...');
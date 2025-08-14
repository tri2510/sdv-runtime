const io = require('socket.io-client');
const fs = require('fs').promises;
const { spawn } = require('child_process');

console.log('🔧 VERIFICATION: Executable Communication Test');
console.log('=============================================\n');

const socket = io('http://localhost:3090');

// Test project that creates an executable with communication capabilities
const communicationProject = {
    "main.cpp": `#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <fstream>
#include "config.h"

int main() {
    std::cout << "=== EXECUTABLE COMMUNICATION TEST ===" << std::endl;
    
    // Test 1: Standard output communication
    std::cout << "MESSAGE:Hello from compiled executable!" << std::endl;
    std::cout << "STATUS:Executable started successfully" << std::endl;
    
    // Test 2: File-based communication
    std::ofstream outputFile("/tmp/executable_output.txt");
    if (outputFile.is_open()) {
        outputFile << "File communication test successful\\n";
        outputFile << "Timestamp: " << std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count() << "\\n";
        outputFile << "Version: " << VERSION << "\\n";
        outputFile.close();
        std::cout << "FILE:Output file created at /tmp/executable_output.txt" << std::endl;
    } else {
        std::cout << "ERROR:Failed to create output file" << std::endl;
    }
    
    // Test 3: Return code communication
    std::cout << "RETURN_CODE:About to return success code 42" << std::endl;
    
    // Test 4: Timing communication
    auto start = std::chrono::high_resolution_clock::now();
    
    // Simulate some work
    volatile long sum = 0;
    for(int i = 0; i < 1000000; ++i) {
        sum += i;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "PERFORMANCE:Work completed in " << duration.count() << "ms" << std::endl;
    std::cout << "RESULT:Sum calculated as " << sum << std::endl;
    
    // Test 5: Multi-line output
    std::cout << "MULTILINE_START" << std::endl;
    std::cout << "Line 1 of multiline output" << std::endl;
    std::cout << "Line 2 with special chars: @#$%^&*()" << std::endl;
    std::cout << "Line 3 with numbers: 12345" << std::endl;
    std::cout << "MULTILINE_END" << std::endl;
    
    std::cout << "FINAL:All communication tests completed successfully!" << std::endl;
    
    return 42; // Custom return code for testing
}`,
    
    "config.h": `#ifndef CONFIG_H
#define CONFIG_H
#define VERSION "1.0.0-communication-test"
#define BUILD_TYPE "Communication Verification"
#endif`
};

let compilationPhases = [];
let executionOutput = [];
let startTime = Date.now();
let executablePath = '';

socket.on('connect', () => {
    console.log('🔌 Connected for executable communication testing');
    console.log('📤 Uploading communication test project...\n');
    
    socket.emit('compile_cpp', {
        files: communicationProject,
        app_name: "communication_test",
        run: true  // This will test execution
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    
    if (data.status === 'compile-start') {
        console.log(`📋 [${elapsed}ms] Compilation started`);
        compilationPhases.push({phase: 'start', time: elapsed});
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
        compilationPhases.push({phase: 'build', time: elapsed});
    } else if (data.status === 'build-done') {
        console.log(`✅ [${elapsed}ms] Build completed with code ${data.code}`);
        if (data.code === 0) {
            console.log(`🎯 Executable should be ready for communication testing`);
        }
    } else if (data.status === 'run-stdout') {
        // This is the key part - testing executable communication
        const output = data.result.trim();
        executionOutput.push(output);
        console.log(`🚀 [${elapsed}ms] EXEC: ${output}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  [${elapsed}ms] EXEC ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 [${elapsed}ms] Execution completed with exit code: ${data.code}`);
        analyzeExecutableCommunication(data.code, elapsed);
    }
    
    if (data.isDone) {
        socket.disconnect();
    }
});

function analyzeExecutableCommunication(exitCode, totalTime) {
    console.log(`\n🔍 EXECUTABLE COMMUNICATION ANALYSIS:`);
    console.log(`=====================================`);
    
    // Test 1: Standard Output Communication
    const hasStandardOutput = executionOutput.some(line => line.includes('MESSAGE:'));
    console.log(`📤 Standard Output: ${hasStandardOutput ? '✅ WORKING' : '❌ FAILED'}`);
    
    if (hasStandardOutput) {
        const messageLines = executionOutput.filter(line => line.includes('MESSAGE:'));
        messageLines.forEach(line => {
            console.log(`   📨 ${line}`);
        });
    }
    
    // Test 2: Status Communication
    const hasStatusUpdates = executionOutput.some(line => line.includes('STATUS:'));
    console.log(`📊 Status Updates: ${hasStatusUpdates ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 3: File Communication
    const hasFileOutput = executionOutput.some(line => line.includes('FILE:'));
    console.log(`📁 File Communication: ${hasFileOutput ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 4: Return Code Communication
    const expectedReturnCode = 42;
    const returnCodeCorrect = exitCode === expectedReturnCode;
    console.log(`🔢 Return Code: ${returnCodeCorrect ? '✅ WORKING' : '❌ FAILED'} (expected: ${expectedReturnCode}, got: ${exitCode})`);
    
    // Test 5: Performance Communication
    const hasPerformanceData = executionOutput.some(line => line.includes('PERFORMANCE:'));
    console.log(`⚡ Performance Data: ${hasPerformanceData ? '✅ WORKING' : '❌ FAILED'}`);
    
    if (hasPerformanceData) {
        const perfLines = executionOutput.filter(line => line.includes('PERFORMANCE:'));
        perfLines.forEach(line => {
            console.log(`   ⏱️  ${line}`);
        });
    }
    
    // Test 6: Multi-line Communication
    const hasMultilineStart = executionOutput.some(line => line.includes('MULTILINE_START'));
    const hasMultilineEnd = executionOutput.some(line => line.includes('MULTILINE_END'));
    const multilineWorking = hasMultilineStart && hasMultilineEnd;
    console.log(`📄 Multi-line Output: ${multilineWorking ? '✅ WORKING' : '❌ FAILED'}`);
    
    // Test 7: Output Completeness
    const totalOutputLines = executionOutput.length;
    const expectedMinimumLines = 8; // Based on our test program
    const outputComplete = totalOutputLines >= expectedMinimumLines;
    console.log(`📋 Output Completeness: ${outputComplete ? '✅ WORKING' : '❌ FAILED'} (${totalOutputLines} lines)`);
    
    // Overall Assessment
    const testsResults = [
        hasStandardOutput,
        hasStatusUpdates, 
        hasFileOutput,
        returnCodeCorrect,
        hasPerformanceData,
        multilineWorking,
        outputComplete
    ];
    
    const passedTests = testsResults.filter(Boolean).length;
    const totalTests = testsResults.length;
    const successRate = (passedTests / totalTests * 100).toFixed(1);
    
    console.log(`\n📊 COMMUNICATION TEST SUMMARY:`);
    console.log(`=============================`);
    console.log(`✅ Passed Tests: ${passedTests}/${totalTests}`);
    console.log(`📈 Success Rate: ${successRate}%`);
    console.log(`⏱️  Total Time: ${totalTime}ms`);
    console.log(`📤 Output Lines: ${totalOutputLines}`);
    
    if (passedTests === totalTests) {
        console.log(`\n🎉 EXECUTABLE COMMUNICATION: ✅ FULLY WORKING`);
        console.log(`🚀 All communication channels verified successfully!`);
    } else {
        console.log(`\n⚠️  EXECUTABLE COMMUNICATION: ❌ PARTIAL ISSUES`);
        console.log(`🔧 Some communication channels need attention`);
    }
    
    // Display captured output for verification
    console.log(`\n📜 COMPLETE EXECUTABLE OUTPUT:`);
    console.log(`=============================`);
    executionOutput.forEach((line, index) => {
        console.log(`${(index + 1).toString().padStart(2, ' ')}. ${line}`);
    });
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection failed:', error.message);
    process.exit(1);
});

console.log('🔄 Starting executable communication verification...');
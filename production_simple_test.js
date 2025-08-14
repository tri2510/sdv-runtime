const io = require('socket.io-client');

console.log('🐳 Production SDV Runtime: Simple C++ Compilation Test');
console.log('====================================================\n');

const socket = io('http://localhost:3090');

const simpleProject = {
    "main.cpp": `#include <iostream>
#include <string>

int main() {
    std::string containerMsg = "Hello from Production SDV Runtime!";
    std::cout << containerMsg << std::endl;
    std::cout << "C++ compilation successful in SDV production container!" << std::endl;
    
    // Test container environment
    std::cout << "Testing production SDV environment..." << std::endl;
    std::cout << "Enhanced compilation features working!" << std::endl;
    
    return 0;
}`,
    
    "production_info.h": `#ifndef PRODUCTION_INFO_H
#define PRODUCTION_INFO_H

#define PRODUCTION_VERSION "1.0.0"
#define BUILD_ENVIRONMENT "Production SDV Runtime"
#define COMPILATION_SERVICE "Kit-Manager Enhanced"

#endif`
};

let totalMessages = 0;
let startTime = Date.now();

socket.on('connect', () => {
    console.log('🔌 Connected to Production SDV Runtime container');
    console.log('📤 Sending C++ project to production container...\n');
    
    socket.emit('compile_cpp', {
        files: simpleProject,
        app_name: "production_simple_test",
        run: true  // Execute in container
    });
});

socket.on('compile_cpp_reply', (data) => {
    totalMessages++;
    const elapsed = Date.now() - startTime;
    
    // Highlight container-specific messages
    if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] Production Output: ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] Written: ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] Build: ${data.result.trim()}`);
    } else {
        console.log(`📋 [${elapsed}ms] ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Production SDV Test Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        console.log(`📊 Messages: ${totalMessages}`);
        console.log(`🐳 Production SDV Runtime: Execution completed`);
        
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Production SDV container connection failed:', error.message);
});

socket.on('disconnect', (reason) => {
    console.log(`🔌 Disconnected from Production SDV container: ${reason}`);
    process.exit(0);
});

console.log('🚀 Starting Production SDV Runtime compilation test...');
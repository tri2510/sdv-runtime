const io = require('socket.io-client');
const net = require('net');

console.log('🌐 VERIFICATION: Network Communication Test');
console.log('==========================================\n');

const socket = io('http://localhost:3090');

// Create a simple TCP server for testing network communication
let testServer;

function createTestServer() {
    return new Promise((resolve) => {
        testServer = net.createServer((connection) => {
            console.log('📡 Test server: Client connected');
            
            connection.on('data', (data) => {
                const message = data.toString().trim();
                console.log(`📨 Test server received: ${message}`);
                
                // Echo back with confirmation
                connection.write(`SERVER_RESPONSE: ${message}`);
            });
            
            connection.on('end', () => {
                console.log('📡 Test server: Client disconnected');
            });
        });
        
        testServer.listen(8899, 'localhost', () => {
            console.log('📡 Test server listening on localhost:8899');
            resolve();
        });
    });
}

// Test project that can communicate over network
const networkProject = {
    "main.cpp": `#include <iostream>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

int main() {
    std::cout << "=== NETWORK COMMUNICATION TEST ===" << std::endl;
    
    // Test 1: Create socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        std::cout << "ERROR: Failed to create socket" << std::endl;
        return 1;
    }
    std::cout << "✅ Socket created successfully" << std::endl;
    
    // Test 2: Setup server address
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8899);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    std::cout << "📍 Connecting to localhost:8899..." << std::endl;
    
    // Test 3: Connect to test server
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cout << "ERROR: Connection failed" << std::endl;
        close(sock);
        return 2;
    }
    std::cout << "✅ Connected to test server" << std::endl;
    
    // Test 4: Send data
    const char* message = "Hello from compiled executable!";
    if (send(sock, message, strlen(message), 0) < 0) {
        std::cout << "ERROR: Failed to send data" << std::endl;
        close(sock);
        return 3;
    }
    std::cout << "📤 Sent message: " << message << std::endl;
    
    // Test 5: Receive response
    char buffer[1024] = {0};
    int bytes_received = recv(sock, buffer, sizeof(buffer), 0);
    if (bytes_received < 0) {
        std::cout << "ERROR: Failed to receive data" << std::endl;
        close(sock);
        return 4;
    }
    std::cout << "📨 Received response: " << buffer << std::endl;
    
    // Test 6: Cleanup
    close(sock);
    std::cout << "🔌 Connection closed" << std::endl;
    std::cout << "✅ Network communication test completed successfully!" << std::endl;
    
    return 0;
}`
};

let networkTestStarted = false;

socket.on('connect', async () => {
    console.log('🔌 Connected to SDV Runtime for network communication test');
    
    // Start test server first
    console.log('🚀 Setting up test server...');
    await createTestServer();
    
    console.log('📤 Uploading network communication project...\n');
    
    socket.emit('compile_cpp', {
        files: networkProject,
        app_name: "network_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    if (data.status === 'compile-start') {
        console.log('📋 Network test compilation started');
    } else if (data.status === 'file-written') {
        console.log(`📝 ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`🌐 NETWORK EXEC: ${data.result.trim()}`);
    } else if (data.status === 'run-stderr') {
        console.log(`⚠️  NETWORK ERROR: ${data.result.trim()}`);
    } else if (data.status === 'run-done') {
        console.log(`🏁 Network test execution completed with code: ${data.code}`);
        analyzeNetworkTest(data.code);
    }
    
    if (data.isDone) {
        setTimeout(() => {
            if (testServer) {
                testServer.close(() => {
                    console.log('📡 Test server shut down');
                    socket.disconnect();
                });
            } else {
                socket.disconnect();
            }
        }, 1000);
    }
});

function analyzeNetworkTest(exitCode) {
    console.log(`\n🌐 NETWORK COMMUNICATION ANALYSIS:`);
    console.log(`=================================`);
    
    const success = exitCode === 0;
    console.log(`🎯 Overall Result: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`🔢 Exit Code: ${exitCode}`);
    
    if (success) {
        console.log(`✅ Socket creation: Working`);
        console.log(`✅ Network connection: Working`);
        console.log(`✅ Data transmission: Working`);
        console.log(`✅ Data reception: Working`);
        console.log(`✅ Connection cleanup: Working`);
        
        console.log(`\n🎉 NETWORK COMMUNICATION: ✅ FULLY FUNCTIONAL`);
        console.log(`🚀 Compiled executables can communicate over network!`);
    } else {
        console.log(`❌ Network communication failed`);
        console.log(`🔧 Check network connectivity and firewall settings`);
        
        console.log(`\n⚠️  NETWORK COMMUNICATION: ❌ FAILED`);
    }
}

socket.on('connect_error', (error) => {
    console.error('❌ Connection to SDV Runtime failed:', error.message);
    if (testServer) {
        testServer.close();
    }
    process.exit(1);
});

console.log('🔄 Starting network communication verification...');
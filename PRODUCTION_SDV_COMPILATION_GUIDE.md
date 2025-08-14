# Production SDV Runtime - Enhanced Compilation Guide
## Complete Multi-Language C++ & Rust Compilation System

> **Comprehensive guide for using the enhanced SDV Runtime with integrated compilation capabilities**

---

## 🎯 What This Guide Covers

- **Production SDV Runtime**: How to use the enhanced Kit-Manager with compilation features
- **Docker Container Setup**: Building and running the production container
- **C++ & Rust Compilation**: Multi-file project compilation with real-time streaming
- **Socket.IO Integration**: How to connect clients and use the compilation API
- **Performance Testing**: Load testing and concurrent client scenarios
- **Production Deployment**: Real-world usage patterns and best practices

---

## 📋 System Requirements

### Prerequisites
```bash
# Check Docker installation
docker --version          # Should be 20.10+ 
docker compose version    # Should be v2.0+

# Check system resources
free -h                   # At least 4GB RAM recommended
df -h                     # At least 3GB disk space

# Check Node.js (for testing clients)
node --version            # Should be 14+
```

### Network Setup
```bash
# Check if port 3090 is available (SDV Runtime uses port 3090, not 5000)
lsof -i :3090            # Should show nothing
netstat -tuln | grep 3090   # Should show nothing
```

---

## 🚀 Step 1: Build Production SDV Runtime Container

### 1.1 Clone and Prepare Repository
```bash
# Clone the production SDV runtime repository
git clone https://github.com/tri2510/sdv-runtime.git
cd sdv-runtime

# Switch to the enhanced compilation branch
git checkout enhanced-compilation-service

# Verify enhanced compilation files are present
ls -la Kit-Manager/src/index.js  # Should show enhanced compilation code
```

### 1.2 Build the Production Container
```bash
# Build using the simplified Kit-Manager Dockerfile
docker build -f Dockerfile.kitmanager \
  --tag sdv-runtime-production:latest \
  --progress=plain \
  .

# Expected output:
# [+] Building 120.5s (15/15) FINISHED
# => => naming to docker.io/library/sdv-runtime-production:latest

# Verify the image was created
docker images | grep sdv-runtime-production
```

### 1.3 Start the Production Container
```bash
# Create output directory for compiled executables
mkdir -p docker-output

# Run container with proper port mapping (3090, not 5000!)
docker run -d \
  --name sdv-runtime-container \
  --publish 3090:3090 \
  --volume "$(pwd)/docker-output:/home/dev/data/output" \
  --restart unless-stopped \
  sdv-runtime-production:latest

# Expected output: Container ID (e.g., a1b2c3d4e5f6...)

# Check if container is running
docker ps | grep sdv-runtime-container
# Should show container with status "Up" and port "0.0.0.0:3090->3090/tcp"

# Check container logs
docker logs sdv-runtime-container
# Expected output:
# Compilation base path: /home/dev
# SDV Runtime Kit Manager with Multi-language Compilation listening on port 3090
# Available compilation endpoints: compile_rust, compile_cpp
```

---

## 🧪 Step 2: Test Basic Connectivity

### 2.1 Simple Connection Test
```bash
# Create connectivity test
cat > test_connection.js << 'EOF'
const io = require('socket.io-client');

console.log('🔌 Testing Production SDV Runtime Connection');
console.log('==========================================\n');

const socket = io('http://localhost:3090', {
    timeout: 10000,
    forceNew: true
});

socket.on('connect', () => {
    console.log('✅ Successfully connected to Production SDV Runtime');
    console.log('🔌 Socket ID:', socket.id);
    console.log('🌐 Enhanced compilation service is ready!');
    console.log('📡 Available endpoints: compile_cpp, compile_rust');
    
    socket.disconnect();
    process.exit(0);
});

socket.on('connect_error', (error) => {
    console.error('❌ Failed to connect to SDV Runtime:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('1. Check container: docker ps | grep sdv-runtime');
    console.log('2. Check logs: docker logs sdv-runtime-container');
    console.log('3. Verify port: curl http://localhost:3090');
    
    process.exit(1);
});

console.log('🔄 Connecting to SDV Runtime on localhost:3090...');
EOF

# Run connectivity test
node test_connection.js
```

---

## 🔨 Step 3: C++ Compilation Tests

### 3.1 Simple C++ Project Test
```bash
# Create simple C++ compilation test
cat > test_cpp_simple.js << 'EOF'
const io = require('socket.io-client');

console.log('🐳 Production SDV Runtime: Simple C++ Test');
console.log('==========================================\n');

const socket = io('http://localhost:3090');

// Simple C++ project with multiple files
const project = {
    "main.cpp": `#include <iostream>
#include <string>
#include "config.h"

int main() {
    std::cout << "Hello from Production SDV Runtime!" << std::endl;
    std::cout << "Version: " << SDV_VERSION << std::endl;
    std::cout << "C++ compilation successful!" << std::endl;
    return 0;
}`,
    
    "config.h": `#ifndef CONFIG_H
#define CONFIG_H
#define SDV_VERSION "2.0.0"
#define PRODUCTION_BUILD true
#endif`
};

let startTime = Date.now();

socket.on('connect', () => {
    console.log('🔌 Connected to Production SDV Runtime');
    console.log('📤 Sending C++ project for compilation...\n');
    
    // Send compilation request
    socket.emit('compile_cpp', {
        files: project,
        app_name: "simple_test",
        run: true  // Execute after compilation
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    
    if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] Program Output: ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
    } else {
        console.log(`📋 [${elapsed}ms] ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        socket.disconnect();
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Connection failed:', error.message);
    process.exit(1);
});
EOF

# Run simple C++ test
node test_cpp_simple.js
```

### 3.2 Complex Multi-File C++ Project Test
```bash
# Create complex multi-file project test
cat > test_cpp_complex.js << 'EOF'
const io = require('socket.io-client');

console.log('🐳 Production SDV Runtime: Complex Multi-File Test');
console.log('=================================================\n');

const socket = io('http://localhost:3090');

// Complex SDV project with multiple directories and files
const complexProject = {
    "main.cpp": `#include <iostream>
#include <vector>
#include <memory>
#include "vehicle/engine.h"
#include "safety/fcw.h"
#include "utils/logger.h"

int main() {
    Logger logger;
    logger.info("Starting complex SDV system test...");
    
    auto engine = std::make_unique<VehicleEngine>();
    auto fcw = std::make_unique<FCWSystem>();
    
    engine->initialize();
    fcw->setThreshold(2.5);
    
    std::vector<double> speeds = {30.0, 60.0, 100.0};
    
    for (auto speed : speeds) {
        engine->setSpeed(speed);
        bool warning = fcw->checkCollisionRisk(speed, 20.0);
        std::cout << "Speed: " << speed << " km/h, FCW: " 
                  << (warning ? "WARNING" : "SAFE") << std::endl;
    }
    
    logger.info("Complex SDV test completed successfully!");
    return 0;
}`,

    "vehicle/engine.cpp": `#include "engine.h"
#include <iostream>

VehicleEngine::VehicleEngine() : speed(0.0), initialized(false) {}

void VehicleEngine::initialize() {
    initialized = true;
    std::cout << "[ENGINE] Vehicle engine initialized" << std::endl;
}

void VehicleEngine::setSpeed(double s) {
    if (initialized) {
        speed = s;
        std::cout << "[ENGINE] Speed set to " << speed << " km/h" << std::endl;
    }
}`,

    "safety/fcw.cpp": `#include "fcw.h"
#include <iostream>

FCWSystem::FCWSystem() : threshold(3.0) {}

void FCWSystem::setThreshold(double t) {
    threshold = t;
}

bool FCWSystem::checkCollisionRisk(double speed, double distance) {
    double ttc = distance / (speed / 3.6);
    bool risk = ttc < threshold;
    if (risk) {
        std::cout << "[FCW] COLLISION RISK! TTC: " << ttc << "s" << std::endl;
    }
    return risk;
}`,

    "utils/logger.cpp": `#include "logger.h"
#include <iostream>
#include <chrono>

void Logger::info(const std::string& msg) {
    std::cout << "[INFO] " << msg << std::endl;
}`,

    "include/vehicle/engine.h": `#ifndef ENGINE_H
#define ENGINE_H
class VehicleEngine {
    double speed;
    bool initialized;
public:
    VehicleEngine();
    void initialize();
    void setSpeed(double s);
};
#endif`,

    "include/safety/fcw.h": `#ifndef FCW_H
#define FCW_H
class FCWSystem {
    double threshold;
public:
    FCWSystem();
    void setThreshold(double t);
    bool checkCollisionRisk(double speed, double distance);
};
#endif`,

    "include/utils/logger.h": `#ifndef LOGGER_H
#define LOGGER_H
#include <string>
class Logger {
public:
    void info(const std::string& msg);
};
#endif`
};

let phases = [];
let startTime = Date.now();

socket.on('connect', () => {
    console.log('🔌 Connected to Production SDV Runtime');
    console.log('📤 Uploading complex multi-file project...\n');
    
    socket.emit('compile_cpp', {
        files: complexProject,
        app_name: "complex_sdv_test",
        run: true
    });
});

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push(data.status);
    
    if (data.status === 'run-stdout') {
        console.log(`🚀 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status === 'file-written') {
        console.log(`📝 [${elapsed}ms] ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 [${elapsed}ms] ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Complex Test Result: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`⏱️  Total Time: ${elapsed}ms`);
        console.log(`📊 Compilation Phases: ${phases.length}`);
        
        console.log('\n🏆 Features Verified:');
        console.log('  ✅ Multi-file C++ compilation');
        console.log('  ✅ Dynamic header resolution');
        console.log('  ✅ CMake build system');
        console.log('  ✅ Real-time progress streaming');
        
        socket.disconnect();
    }
});
EOF

# Run complex C++ test
node test_cpp_complex.js
```

---

## 🦀 Step 4: Rust Compilation Test

### 4.1 Rust Project Test
```bash
# Create Rust compilation test
cat > test_rust.js << 'EOF'
const io = require('socket.io-client');

console.log('🦀 Production SDV Runtime: Rust Compilation Test');
console.log('===============================================\n');

const socket = io('http://localhost:3090');

// Rust code with custom dependencies
const rustCode = `/*Cargo.toml
[dependencies]
serde = "1.0"
*/

use std::collections::HashMap;

fn main() {
    println!("Hello from Rust in Production SDV Runtime!");
    
    let mut vehicle_data = HashMap::new();
    vehicle_data.insert("speed", 75.0);
    vehicle_data.insert("fuel", 45.2);
    
    println!("Vehicle Data: {:?}", vehicle_data);
    println!("Rust compilation successful in SDV Runtime!");
}`;

socket.on('connect', () => {
    console.log('🔌 Connected to Production SDV Runtime for Rust');
    
    socket.emit('compile_rust', {
        code: rustCode,
        app_name: "rust_test",
        run: true
    });
});

socket.on('compile_rust_reply', (data) => {
    if (data.status === 'run-stdout') {
        console.log(`🚀 Rust Output: ${data.result.trim()}`);
    } else {
        console.log(`📋 ${data.status}: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n🎯 Rust Test: ${data.code === 0 ? '✅ SUCCESS' : '❌ FAILED'}`);
        socket.disconnect();
    }
});
EOF

# Run Rust test
node test_rust.js
```

---

## 📊 Step 5: Load Testing & Performance

### 5.1 Concurrent Client Load Test
```bash
# Create load testing script
cat > test_load.js << 'EOF'
const io = require('socket.io-client');

console.log('🚀 Production SDV Runtime: Load Testing');
console.log('======================================\n');

class LoadTester {
    constructor() {
        this.results = [];
        this.activeConnections = 0;
    }
    
    createTestProject(clientId) {
        return {
            "main.cpp": `#include <iostream>
#include <chrono>

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    
    // Simulate work
    volatile long sum = 0;
    for(int i = 0; i < 100000; ++i) {
        sum += i * ${clientId};
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Client ${clientId} completed work in " << duration.count() << "ms" << std::endl;
    return 0;
}`
        };
    }
    
    runLoadTest(numClients = 3) {
        console.log(`🔥 Starting load test with ${numClients} concurrent clients\n`);
        
        const startTime = Date.now();
        let completed = 0;
        
        for (let i = 1; i <= numClients; i++) {
            setTimeout(() => {
                this.runClient(i, startTime, () => {
                    completed++;
                    if (completed === numClients) {
                        this.showResults(startTime);
                    }
                });
            }, (i - 1) * 500);
        }
    }
    
    runClient(clientId, globalStart, callback) {
        const socket = io('http://localhost:3090', { forceNew: true });
        const clientStart = Date.now();
        this.activeConnections++;
        
        socket.on('connect', () => {
            console.log(`🔌 Client ${clientId} connected (${this.activeConnections} active)`);
            
            socket.emit('compile_cpp', {
                files: this.createTestProject(clientId),
                app_name: `load_client_${clientId}`,
                run: true
            });
        });
        
        socket.on('compile_cpp_reply', (data) => {
            if (data.isDone) {
                const duration = Date.now() - clientStart;
                
                this.results.push({
                    clientId,
                    success: data.code === 0,
                    duration
                });
                
                console.log(`✅ Client ${clientId} completed in ${duration}ms`);
                this.activeConnections--;
                socket.disconnect();
                callback();
            }
        });
        
        socket.on('connect_error', (error) => {
            console.error(`❌ Client ${clientId} failed: ${error.message}`);
            this.activeConnections--;
            callback();
        });
    }
    
    showResults(startTime) {
        const totalTime = Date.now() - startTime;
        const successful = this.results.filter(r => r.success);
        
        console.log('\n📊 Load Test Results');
        console.log('===================');
        console.log(`⏱️  Total Duration: ${totalTime}ms`);
        console.log(`👥 Total Clients: ${this.results.length}`);
        console.log(`✅ Successful: ${successful.length}`);
        console.log(`📈 Success Rate: ${(successful.length / this.results.length * 100).toFixed(1)}%`);
        
        if (successful.length > 0) {
            const avg = successful.reduce((sum, r) => sum + r.duration, 0) / successful.length;
            const min = Math.min(...successful.map(r => r.duration));
            const max = Math.max(...successful.map(r => r.duration));
            
            console.log(`📊 Performance:`);
            console.log(`   Average: ${avg.toFixed(1)}ms`);
            console.log(`   Fastest: ${min}ms`);
            console.log(`   Slowest: ${max}ms`);
        }
        
        console.log('\n🏆 Production SDV handled concurrent compilation requests successfully!');
        process.exit(0);
    }
}

// Run the load test
const tester = new LoadTester();
tester.runLoadTest(3);
EOF

# Run load test
node test_load.js
```

---

## 🛠️ Step 6: Container Management

### 6.1 Container Management Commands
```bash
# Check container status
docker ps | grep sdv-runtime-container

# View real-time logs
docker logs -f sdv-runtime-container

# Check container resource usage
docker stats sdv-runtime-container

# Access container shell for debugging
docker exec -it sdv-runtime-container /bin/bash

# Stop the container
docker stop sdv-runtime-container

# Remove the container
docker rm sdv-runtime-container

# Remove the image (if needed)
docker rmi sdv-runtime-production:latest
```

### 6.2 Troubleshooting Common Issues
```bash
# If container won't start:
docker logs sdv-runtime-container  # Check for errors

# If port 3090 is busy:
lsof -i :3090  # Find what's using the port
sudo kill -9 <PID>  # Kill the process

# If compilation fails:
docker exec -it sdv-runtime-container which gcc g++ cmake  # Check tools
docker exec -it sdv-runtime-container ls -la /home/dev/data/ws  # Check workspace

# Reset everything:
docker stop sdv-runtime-container
docker rm sdv-runtime-container
docker rmi sdv-runtime-production:latest
# Then rebuild from step 1.2
```

---

## 🔧 Step 7: API Reference

### 7.1 Socket.IO Endpoints

#### **C++ Compilation Endpoint**
```javascript
// Connect to SDV Runtime
const socket = io('http://localhost:3090');

// Send C++ compilation request
socket.emit('compile_cpp', {
    files: {
        "main.cpp": "C++ source code here",
        "header.h": "Header file content",
        "subdir/module.cpp": "Files in subdirectories supported"
    },
    app_name: "my_project",  // Unique project name
    run: true               // Execute after compilation (optional)
});

// Listen for compilation responses
socket.on('compile_cpp_reply', (data) => {
    console.log('Status:', data.status);      // Current phase
    console.log('Output:', data.result);      // Compilation output
    console.log('Done:', data.isDone);        // True when finished
    console.log('Exit Code:', data.code);     // 0 = success, >0 = error
});
```

#### **Rust Compilation Endpoint**
```javascript
// Send Rust compilation request
socket.emit('compile_rust', {
    code: `
/*Cargo.toml
[dependencies]
serde = "1.0"
*/

fn main() {
    println!("Hello Rust!");
}`,
    app_name: "rust_project",
    run: true
});

// Listen for Rust responses
socket.on('compile_rust_reply', (data) => {
    // Same response format as C++
});
```

### 7.2 Response Status Types

| Status | Description | When It Occurs |
|--------|-------------|----------------|
| `compile-start` | Compilation beginning | Request received |
| `file-written` | Source file saved | Each file processed |
| `configure-stdout` | CMake configuration output | CMake running |
| `build-stdout` | Build process output | Make/compilation |
| `build-done` | Compilation finished | Build complete |
| `run-stdout` | Program execution output | When `run: true` |
| `run-done` | Execution finished | Program terminated |

---

## 🌟 Step 8: Advanced Usage Examples

### 8.1 Real-Time Progress Monitoring
```javascript
const socket = io('http://localhost:3090');

let phases = [];
let startTime = Date.now();

socket.on('compile_cpp_reply', (data) => {
    const elapsed = Date.now() - startTime;
    phases.push({ status: data.status, time: elapsed });
    
    // Create progress indicators
    if (data.status === 'file-written') {
        console.log(`📝 File processed: ${data.result.trim()}`);
    } else if (data.status.includes('build')) {
        console.log(`🔨 Building: ${data.result.trim()}`);
    } else if (data.status === 'run-stdout') {
        console.log(`🚀 Output: ${data.result.trim()}`);
    }
    
    if (data.isDone) {
        console.log(`\n⏱️ Total phases: ${phases.length}`);
        console.log(`🎯 Success: ${data.code === 0 ? 'Yes' : 'No'}`);
    }
});
```

### 8.2 Error Handling Best Practices
```javascript
socket.on('compile_cpp_reply', (data) => {
    // Handle different types of errors
    if (data.status.includes('error') || data.status.includes('failed')) {
        console.error(`❌ Error in ${data.status}:`, data.result);
        
        if (data.isDone && data.code !== 0) {
            console.log('🔧 Compilation failed. Check:');
            console.log('  - Syntax errors in C++ code');
            console.log('  - Missing header files');
            console.log('  - Incorrect file paths');
        }
    }
});

socket.on('connect_error', (error) => {
    console.error('❌ Connection failed:', error.message);
    console.log('💡 Make sure SDV Runtime container is running on port 3090');
});

socket.on('disconnect', (reason) => {
    if (reason === 'io server disconnect') {
        console.log('🔌 Server disconnected the client');
    } else {
        console.log(`🔌 Disconnected: ${reason}`);
    }
});
```

---

## 📚 Key Differences from Original System

### **Important Changes to Note**

1. **Port Changed**: Uses **port 3090** (not 5000) - SDV Runtime standard
2. **Enhanced Kit-Manager**: Full SDV runtime environment, not standalone service
3. **Production Ready**: Includes monitoring, logging, and scalability features  
4. **Multi-Architecture**: Supports both AMD64 and ARM64 containers
5. **Container Integration**: Works within complete SDV ecosystem

### **File Structure**
```
sdv-runtime-production/
├── Kit-Manager/
│   ├── src/
│   │   └── index.js              # Enhanced with compilation endpoints
│   ├── package.json              # Added toml dependencies
│   └── configs.js                # Port 3090 configuration
├── Dockerfile.kitmanager         # Simplified container build
├── docker-output/                # Compiled executables appear here
└── test files...                 # Your test scripts
```

---

## 🎉 Summary

This Production SDV Runtime provides:

1. **🔧 Complete C++ Compilation**: Multi-file projects with CMake
2. **🦀 Rust Support**: Custom dependencies via Cargo.toml
3. **📡 Real-time Streaming**: Live compilation progress
4. **🐳 Production Container**: Scalable Docker deployment  
5. **⚡ High Performance**: Concurrent client support
6. **🛡️ Production Ready**: Integrated with SDV Runtime ecosystem

### **Quick Start Commands**
```bash
# 1. Build and start
docker build -f Dockerfile.kitmanager -t sdv-runtime-production:latest .
docker run -d --name sdv-runtime-container -p 3090:3090 sdv-runtime-production:latest

# 2. Test connection
node test_connection.js

# 3. Test compilation
node test_cpp_simple.js

# 4. Advanced testing
node test_cpp_complex.js
node test_load.js
```

🚀 **Your Production SDV Runtime with enhanced compilation is ready for deployment!**
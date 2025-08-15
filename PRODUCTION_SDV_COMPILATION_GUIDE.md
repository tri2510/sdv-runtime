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

## 🧪 Step 2: Transparent File-Based Testing System

### 2.1 Overview of Test Structure

The SDV Runtime now uses a **transparent file-based testing system** where all C++ source code is stored in separate, inspectable files instead of inline strings.

```
tests/
├── simple/          # Basic 2-file C++ projects  
│   ├── main.cpp     # Simple SDV test program
│   └── config.h     # Configuration headers
├── multifile/       # Complex multi-directory projects
│   ├── main.cpp     # Vehicle system main program
│   ├── vehicle/     # Vehicle classes and management
│   ├── sensors/     # Sensor data processing
│   ├── utils/       # Logging and utility functions
│   └── config/      # System configuration
├── communication/   # Communication and I/O testing
│   ├── main.cpp     # File I/O, exit codes, performance tests
│   └── communication.h
└── network/         # Network programming tests
    └── main.cpp     # Socket programming examples
```

### 2.2 Install Dependencies and Inspect Test Files

```bash
# Install required dependencies
npm install socket.io-client

# View all available test files and structure
./inspect_test_files.sh

# Examine specific test categories
ls -la tests/simple/
ls -la tests/multifile/
ls -la tests/communication/

# Inspect individual test files  
cat tests/simple/main.cpp              # Basic SDV program
cat tests/multifile/vehicle/Vehicle.h  # Vehicle class definition
cat tests/communication/main.cpp       # Communication testing
```

### 3.1 Simple Connection Test

```bash
# Run the ready-to-use connection test
node test_connection.js

# Expected output:
# 🔌 Testing Production SDV Runtime Connection
# ✅ Successfully connected to Production SDV Runtime
# 🔌 Socket ID: abc123...
# 🌐 Enhanced compilation service is ready!
# 📡 Available endpoints: compile_cpp, compile_rust
```

---

## 🔨 Step 4: C++ Compilation Tests

### 4.1 Simple C++ Project Test

```bash
# Run the file-based simple C++ test
node test_cpp_simple.js

# This test automatically loads files from tests/simple/ and compiles:
# - main.cpp: Basic SDV program with configuration access
# - config.h: System configuration and version definitions

# Expected output:
# 🐳 Production SDV Runtime: Simple C++ Test
# 📄 Loaded: config.h (210 chars)
# 📄 Loaded: main.cpp (829 chars)
# 📤 Sending C++ project with 2 files for compilation...
# 🔨 [ 50%] Building CXX object...
# 🔨 [100%] Linking CXX executable app
# 🚀 Program Output: === SIMPLE SDV COMPILATION TEST ===
#    Hello from Production SDV Runtime!
#    Config Version: 1.0.0-production
# 🎯 Result: ✅ SUCCESS
```

**📁 Simple Test Files**: View the source files being compiled:
```bash
cat tests/simple/main.cpp    # Main program logic
cat tests/simple/config.h    # Configuration definitions
```

### 4.2 Complex Multi-File Project Test

```bash
# Run the file-based complex multi-file test
node test_cpp_complex.js

# This test automatically loads 9 files from tests/multifile/ including:
# - Vehicle system with classes and inheritance
# - Sensor management with real-time data processing  
# - Logging utilities with timestamp formatting
# - System configuration with advanced settings
# - Cross-module dependencies and header resolution

# Expected output:
# 🐳 Production SDV Runtime: Complex Multi-File Test
# 📄 Loaded: vehicle/Vehicle.cpp (497 chars)
# 📄 Loaded: sensors/SpeedSensor.h (466 chars)
# 📄 Loaded: utils/Logger.cpp (617 chars)
# ...(9 files total)
# 🔨 [ 16%] Building CXX object config/SystemConfig.cpp.o
# 🔨 [ 33%] Building CXX object main.cpp.o
# 🔨 [100%] Built target app
# 🚀 [INFO] [SDV_SYSTEM] Vehicle initialized: SDV-PROD-001
# 🎯 Result: ✅ SUCCESS
```

**📁 Complex Test Structure**: Examine the multi-file project:
```bash
# View the complex project structure
find tests/multifile -name "*.cpp" -o -name "*.h" | sort

# Examine key files
cat tests/multifile/main.cpp                    # Main program
cat tests/multifile/vehicle/Vehicle.h           # Vehicle class definition
cat tests/multifile/sensors/SpeedSensor.cpp     # Sensor implementation
```

### 4.3 Production Testing Scripts

The repository includes several production-ready test scripts that use transparent file-based input:

```bash
# Run simple production test (uses tests/simple/)
node production_simple_test.js

# Run complex multi-file production test (uses tests/multifile/)
node production_multifile_test.js

# Run executable communication verification (uses tests/communication/)
node verify_executable_communication.js

# Run advanced features verification (uses tests/multifile/)
node verify_advanced_features.js

# Run network communication test (uses tests/network/)
node verify_network_communication.js

# Run load testing (uses tests/simple/ with modifications)
node production_load_test.js

# Run comprehensive file-based test suite
node run_file_based_tests.js
```

**📊 Test Results Dashboard**: All tests show exactly which files are loaded:
```bash
# Each test displays file loading progress:
# 📄 Loaded: main.cpp (1660 chars)
# 📄 Loaded: vehicle/Vehicle.h (439 chars)
# 📄 Loaded: sensors/SpeedSensor.cpp (651 chars)
# ...
```

---

## ✅ Step 5: Executable Communication Verification

### 5.1 Test Executable Communication Channels

```bash
# Run communication verification test
node verify_executable_communication.js

# This test verifies that compiled executables can:
# - Communicate via standard output/input
# - Create and write to files
# - Return custom exit codes (like 42)
# - Handle multi-line output with special characters
# - Generate performance timing data

# Expected output shows comprehensive communication testing:
# 🔧 VERIFICATION: Executable Communication Test  
# 📄 Loaded: communication.h (622 chars)
# 📄 Loaded: main.cpp (2157 chars)
# 🚀 EXEC: === EXECUTABLE COMMUNICATION TEST ===
# 🚀 EXEC: MESSAGE:Hello from compiled executable!
# 🚀 EXEC: FILE_CREATED:/tmp/executable_output.txt
# 🏁 Execution completed with exit code: 42
# ✅ All communication channels verified successfully!
```

**📁 Communication Test Files**: Examine the communication test source:
```bash
cat tests/communication/main.cpp          # Communication test program
cat tests/communication/communication.h   # Communication utilities
```

### 5.2 Direct Executable Testing

```bash
# Test executables directly outside the container
node verify_direct_execution.js

# This verifies that generated executables:
# - Can be executed independently
# - Work on the host system
# - Maintain all functionality outside Docker
# - Are properly linked and portable
```

---

## 🌐 Step 6: Network and Advanced Features

### 6.1 Network Communication Testing

```bash
# Run network communication test
node verify_network_communication.js

# Note: Network tests are expected to fail due to container isolation
# This is correct security behavior - the test demonstrates:
# - Socket creation and configuration
# - Network programming concepts
# - Container security isolation
# - Expected connection failures in isolated environments
```

**📁 Network Test Files**: Examine network programming examples:
```bash
cat tests/network/main.cpp    # Socket programming and network communication
```

### 6.2 Advanced Features Verification

```bash
# Run advanced features test (uses complex multifile structure)
node verify_advanced_features.js

# This comprehensive test verifies:
# - Multi-directory project compilation
# - Complex header dependency resolution
# - Cross-module function calls
# - Advanced C++ features (classes, templates, STL)
# - Real-world SDV system simulation
```

---

## 📊 Step 7: Performance and Load Testing

### 7.1 Load Testing with Multiple Clients

```bash
# Run production load testing
node production_load_test.js

# This test simulates multiple concurrent clients:
# - Spawns multiple Socket.IO connections
# - Tests concurrent compilation requests
# - Measures performance under load
# - Verifies container stability
# - Reports success rates and timing metrics
```

### 7.2 Comprehensive Test Suite

```bash
# Run the complete file-based test suite
node run_file_based_tests.js

# This executes all major test categories:
# 1. Simple Test from Files
# 2. Multi-file Test from Files  
# 3. Communication Test from Files

# Expected final output:
# 📊 FILE-BASED TEST SUITE FINAL REPORT
# 🎯 OVERALL RESULT: ✅ ALL TESTS PASSED
# 📈 Success Rate: 3/3 (100.0%)
# 🎉 FILE-BASED TESTING APPROACH: ✅ FULLY VALIDATED
```

---

## 🔍 Step 8: Manual Verification Procedures

### 8.1 Container Health Check

```bash
# 1. Verify container is running and responsive
docker ps | grep sdv-runtime-container
docker logs --tail 20 sdv-runtime-container

# 2. Test direct port connectivity
curl -f http://localhost:3090 || echo "Connection failed"
nc -zv localhost 3090

# 3. Check container resource usage
docker stats sdv-runtime-container --no-stream
```

### 8.2 File System Verification

```bash
# 4. Verify test file structure is complete
ls -la tests/simple/
ls -la tests/multifile/
ls -la tests/communication/
ls -la tests/network/

# 5. Check compiled executables are generated
ls -la docker-output/
file docker-output/app_* | head -5  # Should show ELF executables
```

### 8.3 Compilation Verification

```bash
# 6. Test basic Socket.IO connectivity
timeout 10 node test_connection.js

# 7. Test simple compilation
timeout 30 node test_cpp_simple.js

# 8. Test complex multi-file compilation  
timeout 60 node test_cpp_complex.js

# 9. Verify executable communication
timeout 30 node verify_executable_communication.js

# 10. Run comprehensive test suite
timeout 120 node run_file_based_tests.js
```

---

## 📚 Key Features of the File-Based Testing System

### **Important Improvements**

1. **🔍 Complete Transparency**: All C++ source code visible in separate files
2. **📁 Organized Structure**: Logical categorization by test complexity
3. **🔧 Easy Debugging**: Modify individual files for experimentation  
4. **📚 Educational Value**: Clear project structure examples
5. **🔄 Reusable Components**: Modular test files for different scenarios
6. **🛠️ Maintainability**: No hidden inline code - everything is inspectable

### **File Structure Overview**

```
sdv-runtime-production/
├── Kit-Manager/
│   ├── src/
│   │   └── index.js              # Enhanced with compilation endpoints
│   ├── package.json              # Added dependencies
│   └── configs.js                # Port 3090 configuration
├── Dockerfile.kitmanager         # Simplified container build
├── docker-output/                # Compiled executables appear here
├── tests/                        # 🆕 Transparent test file structure
│   ├── simple/                   # Basic C++ projects
│   ├── multifile/                # Complex multi-directory projects
│   ├── communication/            # Communication testing files
│   └── network/                  # Network programming tests
├── test_*.js                     # File-based test scripts
├── production_*.js               # Production test scripts
├── verify_*.js                   # Verification scripts
├── run_file_based_tests.js       # Comprehensive test suite
└── inspect_test_files.sh         # File inspection utility
```

### **Inspection and Debugging Tools**

```bash
# 1. Complete file inspection
./inspect_test_files.sh

# 2. Examine specific test categories
cat tests/simple/main.cpp
cat tests/multifile/vehicle/Vehicle.h
cat tests/communication/main.cpp

# 3. Find all C++ files
find tests -name "*.cpp" -o -name "*.h" | sort

# 4. Search for specific patterns
grep -r "include" tests/
grep -r "std::" tests/
```

---

## 🎉 Summary

This Production SDV Runtime provides:

1. **🔨 Complete C++ Compilation**: Multi-file projects with CMake
2. **🦀 Rust Support**: Custom dependencies via Cargo.toml
3. **📡 Real-time Streaming**: Live compilation progress
4. **🐳 Production Container**: Scalable Docker deployment  
5. **⚡ High Performance**: Concurrent client support
6. **🛡️ Production Ready**: Integrated with SDV Runtime ecosystem
7. **🔍 Transparent Testing**: File-based input system for complete visibility

### **🔍 Getting Started with File-Based Tests**

```bash
# 1. Explore test file structure
./inspect_test_files.sh

# 2. Run individual tests  
node test_cpp_simple.js         # Basic compilation
node test_cpp_complex.js        # Multi-file projects
node verify_executable_communication.js  # Communication tests

# 3. Run comprehensive test suite
node run_file_based_tests.js

# 4. Examine specific test inputs
cat tests/simple/main.cpp
cat tests/multifile/vehicle/Vehicle.h
cat tests/communication/main.cpp
```

**🎯 All tests now use transparent, file-based input - no hidden inline code!**

The SDV Runtime is production-ready with comprehensive testing, transparent file structure, and full C++ compilation capabilities. The file-based testing system ensures complete visibility into what gets compiled while maintaining professional-grade functionality.

---

*Last updated: December 2024 - Enhanced with transparent file-based testing system*
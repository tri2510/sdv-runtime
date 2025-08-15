# End-to-End Testing Guide for SDV Runtime Production System

## Complete Testing Documentation for Transparent File-Based SDV Runtime

> **This document provides the exact steps to perform comprehensive end-to-end testing of the SDV Runtime production system using the transparent file-based testing approach.**

---

## 🎯 Testing Overview

This guide demonstrates how to perform complete end-to-end testing of the SDV Runtime production system, validating:

- **Container Build & Startup**: Docker containerization and service initialization
- **File-Based Compilation**: Transparent C++ multi-file project compilation
- **Communication Channels**: Executable output, file I/O, and exit codes
- **Performance Testing**: Load testing with concurrent clients
- **Advanced Features**: Complex multi-directory project compilation

---

## 📋 Prerequisites

### System Requirements
```bash
# Verify Docker installation
docker --version          # Should be 20.10+
docker compose version    # Should be v2.0+

# Check system resources
free -h                   # At least 4GB RAM recommended
df -h                     # At least 3GB disk space

# Check Node.js for test clients
node --version            # Should be 14+
npm --version             # For dependencies
```

### Network Setup
```bash
# Ensure port 3090 is available
lsof -i :3090            # Should show nothing
netstat -tuln | grep 3090   # Should show nothing
```

---

## 🐳 Step 1: Container Build and Startup

### 1.1 Clone and Prepare Production Repository
```bash
# Navigate to production directory
cd /path/to/sdv-runtime-production

# Verify enhanced compilation files are present
ls -la Kit-Manager/src/index.js     # Should show enhanced compilation code
ls -la testing-suite/               # Should show organized testing structure
```

### 1.2 Quick Start with Automated Setup
```bash
# Use the convenient automated setup
./run-tests.sh

# When prompted "Would you like to build and start the container now? (y/n):"
# Choose 'y' to automatically:
# - Build container using Dockerfile.kitmanager
# - Create docker-output directory
# - Stop/remove any existing containers
# - Start new container with proper configuration
# - Verify container is ready for testing

# Expected output:
# 🔨 Building SDV Runtime container...
# 🚀 Starting SDV Runtime container...
# ✅ Container started successfully
# 🎯 Container is ready for testing!
```

### 1.3 Manual Container Build and Start
```bash
# Option A: Build the production container
docker build -f Dockerfile.kitmanager \
  --tag sdv-runtime-production:latest \
  --progress=plain \
  .

# Expected output:
# [+] Building 120.5s (15/15) FINISHED
# => => naming to docker.io/library/sdv-runtime-production:latest

# Verify image creation
docker images | grep sdv-runtime-production

# Option B: Create output directory and manage existing containers
mkdir -p docker-output

# Stop and remove any existing container
docker stop sdv-runtime-container 2>/dev/null || true
docker rm sdv-runtime-container 2>/dev/null || true

# Option C: Start container with proper port mapping (3090)
docker run -d \
  --name sdv-runtime-container \
  --publish 3090:3090 \
  --volume "$(pwd)/docker-output:/home/dev/data/output" \
  --restart unless-stopped \
  sdv-runtime-production:latest

# Expected output: Container ID (e.g., a1b2c3d4e5f6...)

# Verify container is running
docker ps | grep sdv-runtime-container
# Should show: status "Up" and port "0.0.0.0:3090->3090/tcp"
```

### 1.4 Container Health Verification
```bash
# Check container logs
docker logs sdv-runtime-e2e-test

# Expected output:
# Compilation base path: /home/dev
# SDV Runtime Kit Manager with Multi-language Compilation listening on port 3090
# Available compilation endpoints: compile_rust, compile_cpp

# Test direct connectivity
curl -f http://localhost:3090 || echo "HTTP endpoint not available (expected)"
nc -zv localhost 3090  # Should show connection success
```

**✅ Step 1 Result**: Container should be running with port 3090 accessible and logs showing successful startup.

---

## 🔌 Step 2: Basic Connectivity Testing

### 2.1 Install Dependencies
```bash
# Install required Node.js dependencies
npm install socket.io-client

# Verify installation
node -e "console.log(require('socket.io-client'))" > /dev/null && echo "✅ Socket.IO client installed"
```

### 2.2 Test Socket.IO Connection
```bash
# Run basic connection test
node test_connection.js

# Expected output:
# 🔌 Testing Production SDV Runtime Connection
# ✅ Successfully connected to Production SDV Runtime
# 🔌 Socket ID: abc123...
# 🌐 Enhanced compilation service is ready!
# 📡 Available endpoints: compile_cpp, compile_rust
```

**✅ Step 2 Result**: Socket.IO connection established successfully with compilation endpoints available.

---

## 📁 Step 3: Transparent File-Based System Verification

### 3.1 Inspect Test File Structure
```bash
# View the transparent file-based test structure
./testing-suite/utilities/inspect_test_files.sh

# Expected structure:
# tests/
# ├── simple/          # Basic 2-file C++ projects
# ├── multifile/       # Complex multi-directory projects  
# ├── communication/   # Communication and I/O testing
# └── network/         # Network programming tests

# Examine specific test categories
ls -la tests/simple/
ls -la tests/multifile/
ls -la tests/communication/
```

### 3.2 Examine Test File Contents
```bash
# View simple test files
cat tests/simple/main.cpp      # Basic SDV program
cat tests/simple/config.h      # Configuration headers

# View complex multi-file structure
find tests/multifile -name "*.cpp" -o -name "*.h" | sort
cat tests/multifile/main.cpp                    # Main program
cat tests/multifile/vehicle/Vehicle.h           # Vehicle class definition

# View communication test files
cat tests/communication/main.cpp                # Communication test program
cat tests/communication/communication.h         # Communication utilities
```

**✅ Step 3 Result**: All test files should be visible and inspectable, demonstrating complete transparency.

---

## 🔨 Step 4: Basic Compilation Testing

### 4.1 Simple C++ Project Test
```bash
# Run file-based simple compilation test
node test_cpp_simple.js

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

# Verify timing is reasonable (< 3 seconds)
```

### 4.2 Complex Multi-File Project Test
```bash
# Run file-based complex compilation test
node test_cpp_complex.js

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

# Verify all 9 files are processed correctly
```

**✅ Step 4 Result**: Both simple and complex compilation tests should succeed with all files processed correctly.

---

## 📞 Step 5: Communication Testing

### 5.1 Executable Communication Verification
```bash
# Test executable communication channels
node verify_executable_communication.js

# Expected output:
# 🔧 VERIFICATION: Executable Communication Test
# 📄 Loaded: communication.h (622 chars)
# 📄 Loaded: main.cpp (2157 chars)
# 🚀 EXEC: === EXECUTABLE COMMUNICATION TEST ===
# 🚀 EXEC: MESSAGE:Hello from compiled executable!
# 🚀 EXEC: FILE_CREATED:/tmp/executable_output.txt
# 🏁 Execution completed with exit code: 42
# ✅ All communication channels verified successfully!

# Verify custom exit code (42) is working
```

### 5.2 Check Generated Executables
```bash
# Verify executables are generated in output directory
ls -la docker-output/

# Expected: Multiple executable files with ELF format
file docker-output/app_* | head -5
# Should show: ELF 64-bit LSB shared object, x86-64

# Count total generated executables
ls -1 docker-output/app_* | wc -l
# Should show increasing number with each test
```

**✅ Step 5 Result**: Executables should be generated and communication channels (stdout, files, exit codes) working properly.

---

## 🏗️ Step 6: Advanced Features Testing

### 6.1 Advanced Multi-File Compilation
```bash
# Test advanced features with complex structure
node verify_advanced_features.js

# Expected output:
# 🔬 VERIFICATION: Advanced Features Test
# 📄 Loaded: config/SystemConfig.cpp (592 chars)
# ...(9 files total)
# 🔨 [ 16%] Building CXX object config/SystemConfig.cpp.o
# 🔨 [100%] Built target app
# 🚀 [INFO] [SDV_SYSTEM] Vehicle initialized: SDV-PROD-001
# 🏆 ADVANCED VERIFICATION: ✅ PASSED (or minor count discrepancy)

# Verify CMake configuration and build steps complete successfully
```

### 6.2 Network Communication Test
```bash
# Test network programming capabilities
node verify_network_communication.js

# Expected behavior:
# - Test should compile successfully
# - Network connection will fail due to container isolation
# - This is correct security behavior and should be documented as expected
```

**✅ Step 6 Result**: Advanced compilation features working, network isolation properly enforced.

---

## 🚀 Step 7: Performance and Load Testing

### 7.1 Production Load Testing
```bash
# Run production load test with multiple concurrent clients
node production_load_test.js

# Expected output:
# 🚀 Production SDV Runtime Load Testing
# 
# 🚀 Running Light Production Load Test (2 clients, 1000ms delay)
# 🔌 Production Client 1 connected (1 active)
# ✅ Production Client 1 completed in 762ms (code: 0)
# ✅ Production Client 2 completed in 784ms (code: 0)
# 
# 📊 Production Performance Metrics:
#    Average Compilation Time: 773.0ms
#    Success Rate: 100.0%
# 🎯 Production environment stability: EXCELLENT

# Verify 100% success rate and reasonable timing (< 1500ms average)
```

### 7.2 Comprehensive Test Suite
```bash
# Run complete file-based test suite
node run_file_based_tests.js

# Expected final output:
# 📊 FILE-BASED TEST SUITE FINAL REPORT
# 🎯 OVERALL RESULT: ✅ ALL TESTS PASSED
# 📈 Success Rate: 3/3 (100.0%)
# 🎉 FILE-BASED TESTING APPROACH: ✅ FULLY VALIDATED

# Verify all three major test categories pass:
# 1. Simple Test from Files
# 2. Multi-file Test from Files  
# 3. Communication Test from Files
```

**✅ Step 7 Result**: Load testing should show 100% success rate with reasonable performance metrics.

---

## 🔍 Step 8: Manual Verification Procedures

### 8.1 Container Health Check
```bash
# 1. Verify container is running and responsive
docker ps | grep sdv-runtime-e2e-test
docker logs --tail 20 sdv-runtime-e2e-test

# 2. Check container resource usage
docker stats sdv-runtime-e2e-test --no-stream

# 3. Verify network connectivity
nc -zv localhost 3090
```

### 8.2 File System Verification
```bash
# 4. Verify test file structure is complete
ls -la tests/simple/      # Should show: main.cpp, config.h
ls -la tests/multifile/   # Should show: multiple subdirectories
ls -la tests/communication/  # Should show: communication files

# 5. Check compiled executables are generated
ls -la docker-output/
file docker-output/app_* | head -5  # Should show ELF executables
```

### 8.3 Performance Verification
```bash
# 6. Test basic Socket.IO connectivity with timeout
timeout 10 node test_connection.js

# 7. Test simple compilation with timeout
timeout 30 node test_cpp_simple.js

# 8. Test complex multi-file compilation with timeout
timeout 60 node test_cpp_complex.js

# 9. Verify executable communication with timeout
timeout 30 node verify_executable_communication.js

# 10. Run comprehensive test suite with timeout
timeout 120 node run_file_based_tests.js
```

**✅ Step 8 Result**: All manual verification steps should complete within specified timeouts.

---

## 📊 Expected Test Results Summary

### ✅ Successful End-to-End Test Indicators

1. **Container Status**: `docker ps` shows container running with port 3090 mapped
2. **Connection Test**: Socket.IO connection established within 2 seconds
3. **Simple Compilation**: 2-file project compiles in under 3 seconds
4. **Complex Compilation**: 9-file project compiles in under 5 seconds
5. **Communication**: Custom exit code 42 and file I/O working
6. **Load Testing**: 100% success rate with multiple concurrent clients
7. **File Generation**: Multiple executable files in `docker-output/` directory
8. **Performance**: Average compilation time under 1.5 seconds per project

### 📈 Performance Benchmarks

- **Simple Project**: < 3 seconds compilation time
- **Complex Project**: < 5 seconds compilation time  
- **Load Testing**: 100% success rate with 2-3 concurrent clients
- **Memory Usage**: Container should use < 1GB RAM
- **Executable Size**: Generated executables 15-60KB depending on complexity

### 🎯 Quality Indicators

- **Transparency**: All test files visible and editable in `tests/` directory
- **Reliability**: All tests should pass consistently on repeated runs
- **Scalability**: Load testing demonstrates concurrent client support
- **Maintainability**: Test files can be modified for different scenarios

---

## 🛠️ Troubleshooting Common Issues

### Container Issues
```bash
# If container fails to start
docker logs sdv-runtime-e2e-test
docker build --no-cache -f Dockerfile.kitmanager -t sdv-runtime-production:latest .

# If port 3090 is in use
sudo lsof -i :3090
sudo kill -9 <PID>
```

### Connection Issues
```bash
# If Socket.IO connection fails
nc -zv localhost 3090  # Test basic connectivity
docker logs sdv-runtime-e2e-test | grep "listening"  # Verify service started
```

### Compilation Issues
```bash
# If compilation fails
docker exec -it sdv-runtime-e2e-test ls -la /home/dev/data/ws/  # Check workspace
docker exec -it sdv-runtime-e2e-test gcc --version  # Verify compiler
```

---

## 🧹 Cleanup After Testing

### Stop and Remove Test Container
```bash
# Stop the test container
docker stop sdv-runtime-e2e-test

# Remove the container
docker rm sdv-runtime-e2e-test

# Optional: Remove generated executables
rm -rf docker-output/app_*

# Optional: Remove Docker image
docker rmi sdv-runtime-production:latest
```

---

## 🎉 End-to-End Testing Completion

Upon successful completion of all steps, you will have:

1. **✅ Verified Container Deployment**: Production SDV Runtime running in Docker
2. **✅ Validated File-Based System**: Transparent test file structure working
3. **✅ Confirmed C++ Compilation**: Multi-file projects compiling successfully
4. **✅ Tested Communication**: Executables communicating through all channels
5. **✅ Validated Performance**: Load testing showing production readiness
6. **✅ Generated Executables**: Multiple working C++ programs in output directory

### 📋 Success Criteria Checklist

- [ ] Container builds and starts successfully
- [ ] Socket.IO connection establishes within 10 seconds
- [ ] Simple compilation completes in under 3 seconds
- [ ] Complex compilation (9 files) completes in under 5 seconds
- [ ] Communication test shows exit code 42
- [ ] Load test achieves 100% success rate
- [ ] At least 10 executable files generated in `docker-output/`
- [ ] All test files visible and inspectable in `tests/` directory

**🏆 If all criteria are met, the SDV Runtime production system is fully validated and ready for production deployment!**

---

*End-to-End Testing Guide - Generated for SDV Runtime Production System*
*Last Updated: August 2024 - Enhanced File-Based Testing Edition*
# SDV Runtime Production - Setup Commands Summary

## 🚀 Quick Reference Guide

### **Automated Setup (Recommended)**

```bash
# Complete setup from scratch
./setup-sdv-runtime.sh

# Run tests with container auto-setup
./run-tests.sh
```

### **Manual Setup Commands**

#### 1. Install Dependencies
```bash
npm install socket.io-client
```

#### 2. Build Container
```bash
docker build -f Dockerfile.kitmanager \
  --tag sdv-runtime-production:latest \
  --progress=plain \
  .
```

#### 3. Start Container
```bash
# Create output directory
mkdir -p docker-output

# Stop existing container (if any)
docker stop sdv-runtime-container 2>/dev/null || true
docker rm sdv-runtime-container 2>/dev/null || true

# Start new container
docker run -d \
  --name sdv-runtime-container \
  --publish 3090:3090 \
  --volume "$(pwd)/docker-output:/home/dev/data/output" \
  --restart unless-stopped \
  sdv-runtime-production:latest
```

#### 4. Verify Setup
```bash
# Check container status
docker ps | grep sdv-runtime-container

# Check container logs
docker logs sdv-runtime-container

# Test connection
cd testing-suite/scripts
node test_connection.js
```

---

## 🧪 Testing Commands

### **Test Launcher (Interactive)**
```bash
./run-tests.sh
```

### **Individual Tests**
```bash
cd testing-suite/scripts

# Basic tests
node test_connection.js                    # Connection test
node test_cpp_simple.js                   # Simple compilation
node test_cpp_complex.js                  # Multi-file compilation

# Verification tests
node verify_executable_communication.js   # Communication testing
node verify_advanced_features.js          # Advanced features
node verify_network_communication.js      # Network programming

# Production tests
node production_simple_test.js             # Production simple test
node production_multifile_test.js          # Production multi-file test
node production_load_test.js               # Load testing

# Complete test suite
node run_file_based_tests.js              # All tests
```

### **File Inspection**
```bash
# View all test files
./testing-suite/utilities/inspect_test_files.sh

# Individual file inspection
cat testing-suite/test-data/tests/simple/main.cpp
cat testing-suite/test-data/tests/multifile/vehicle/Vehicle.h
```

---

## 🔧 Container Management

### **Container Commands**
```bash
# Check status
docker ps | grep sdv-runtime

# View logs
docker logs sdv-runtime-container

# Stop container
docker stop sdv-runtime-container

# Remove container
docker rm sdv-runtime-container

# Restart container
docker restart sdv-runtime-container
```

### **Container Information**
- **Name**: `sdv-runtime-container`
- **Port**: `3090` (mapped to host port 3090)
- **Output Directory**: `./docker-output`
- **Base Image**: `sdv-runtime-production:latest`

---

## 📁 File Structure

```
sdv-runtime-production/
├── setup-sdv-runtime.sh           # Complete automated setup
├── run-tests.sh                   # Interactive test launcher
├── docker-output/                 # Generated executables
├── testing-suite/
│   ├── test-data/tests/           # C++ source files
│   ├── scripts/                   # Test execution scripts
│   ├── documentation/             # Guides and reports
│   └── utilities/                 # Helper scripts
├── Kit-Manager/                   # Enhanced compilation service
├── Dockerfile.kitmanager          # Container build file
└── PRODUCTION_SDV_COMPILATION_GUIDE.md
```

---

## 🎯 Common Workflows

### **First Time Setup**
```bash
# 1. Clone repository
git clone <repository-url>
cd sdv-runtime-production

# 2. Run complete setup
./setup-sdv-runtime.sh

# 3. Run tests
./run-tests.sh
```

### **Development Workflow**
```bash
# 1. Start container (if not running)
./run-tests.sh  # Choose 'y' if container setup is needed

# 2. Run specific tests
cd testing-suite/scripts
node test_cpp_simple.js

# 3. Check generated executables
ls -la ../../docker-output/
```

### **Container Rebuild**
```bash
# 1. Stop existing container
docker stop sdv-runtime-container
docker rm sdv-runtime-container

# 2. Rebuild container
docker build -f Dockerfile.kitmanager --tag sdv-runtime-production:latest .

# 3. Start new container
./run-tests.sh  # Choose 'y' when prompted
```

---

## 🚨 Troubleshooting

### **Container Issues**
```bash
# Container won't start
docker logs sdv-runtime-container

# Port already in use
sudo lsof -i :3090
sudo kill -9 <PID>

# Permission issues
sudo chown -R $USER:$USER docker-output/
```

### **Connection Issues**
```bash
# Test basic connectivity
nc -zv localhost 3090

# Check if container is running
docker ps | grep sdv-runtime

# Restart container
docker restart sdv-runtime-container
```

### **Test Failures**
```bash
# Check dependencies
npm list socket.io-client

# Reinstall dependencies
npm install socket.io-client

# Run connection test
cd testing-suite/scripts
node test_connection.js
```

---

## ✅ Success Indicators

### **Successful Setup**
- ✅ Container running on port 3090
- ✅ Connection test passes within 10 seconds
- ✅ Simple compilation completes < 3 seconds
- ✅ Executables generated in `docker-output/`

### **Performance Benchmarks**
- **Simple Projects**: < 1000ms compilation time
- **Complex Projects**: < 2000ms compilation time
- **Load Testing**: 100% success rate with 2-3 concurrent clients

---

*SDV Runtime Production Setup Commands - Quick Reference*
*Last Updated: August 2024*
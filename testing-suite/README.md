# SDV Runtime Testing Suite

## Organized Testing Framework for Production SDV Runtime

This testing suite provides a comprehensive, transparent, and well-organized testing framework for the SDV Runtime production system with enhanced C++ compilation capabilities.

---

## 📁 Directory Structure

```
testing-suite/
├── test-data/           # Test input files and data
│   └── tests/
│       ├── simple/      # Basic 2-file C++ projects
│       ├── multifile/   # Complex multi-directory projects
│       ├── communication/ # Communication and I/O testing
│       └── network/     # Network programming tests
├── scripts/             # Test execution scripts
│   ├── test_*.js        # Basic test scripts
│   ├── production_*.js  # Production test scripts
│   ├── verify_*.js      # Verification scripts
│   └── run_file_based_tests.js # Complete test suite
├── documentation/       # Test guides and reports
│   ├── END_TO_END_TESTING_GUIDE.md
│   ├── EXECUTABLE_COMMUNICATION_REPORT.md
│   └── VERIFICATION_REPORT.md
└── utilities/           # Helper scripts and tools
    └── inspect_test_files.sh
```

---

## 🚀 Quick Start

### Prerequisites
1. Docker installed and running
2. Node.js dependencies: `npm install socket.io-client` (optional - will be prompted)

### Easy Testing with Automated Setup
```bash
# From the sdv-runtime-production root directory
./run-tests.sh

# When prompted "Would you like to build and start the container now? (y/n):"
# Choose 'y' for automated:
# - Container build using Dockerfile.kitmanager
# - Container startup with proper port mapping (3090)
# - Output directory creation
# - Container readiness verification
```

### Manual Test Execution
```bash
# Navigate to scripts directory
cd testing-suite/scripts

# Run individual tests
node test_connection.js                    # Test connection
node test_cpp_simple.js                   # Simple compilation
node test_cpp_complex.js                  # Multi-file compilation
node verify_executable_communication.js   # Communication testing
node production_load_test.js              # Load testing
node run_file_based_tests.js             # Complete test suite
```

---

## 🔍 Test Categories

### 1. **Connection Tests**
- **test_connection.js**: Basic Socket.IO connectivity
- **verify_connection.js**: Enhanced connection verification

### 2. **Compilation Tests**
- **test_cpp_simple.js**: Basic 2-file C++ project
- **test_cpp_complex.js**: Complex multi-directory project
- **test_simple_from_files.js**: Simple test with file analysis
- **test_multifile_from_files.js**: Multi-file test with structure analysis

### 3. **Production Tests**
- **production_simple_test.js**: Production-grade simple testing
- **production_multifile_test.js**: Production-grade complex testing
- **production_load_test.js**: Concurrent client load testing

### 4. **Verification Tests**
- **verify_executable_communication.js**: Executable I/O testing
- **verify_advanced_features.js**: Advanced compilation features
- **verify_network_communication.js**: Network programming (expected to fail due to container isolation)
- **verify_direct_execution.js**: Direct executable testing

### 5. **Automotive System Tests**
- **test_fcw_system.js**: Forward Collision Warning system compilation (inspired by FCW Showcase)

### 6. **Comprehensive Testing**
- **run_file_based_tests.js**: Complete test suite execution

---

## 📄 Test Data Organization

### Simple Tests (`test-data/tests/simple/`)
- `main.cpp`: Basic SDV program with configuration access
- `config.h`: System configuration and version definitions

### Multi-file Tests (`test-data/tests/multifile/`)
- `main.cpp`: Vehicle system main program
- `vehicle/`: Vehicle classes and management (`Vehicle.h`, `Vehicle.cpp`)
- `sensors/`: Sensor data processing (`SpeedSensor.h`, `SpeedSensor.cpp`)
- `utils/`: Logging and utility functions (`Logger.h`, `Logger.cpp`)
- `config/`: System configuration (`SystemConfig.h`, `SystemConfig.cpp`)

### Communication Tests (`test-data/tests/communication/`)
- `main.cpp`: File I/O, exit codes, performance tests
- `communication.h`: Communication utilities and definitions

### Network Tests (`test-data/tests/network/`)
- `main.cpp`: Socket programming examples (expected to fail in container)

### FCW System Tests (`test-data/tests/fcw-system/`)
- `main.cpp`: Forward Collision Warning system with TTC calculations
- `fcw_types.h`: Vehicle state management and FCW engine classes
- `collision_detector.h`: Advanced collision detection algorithms and physics

---

## 🛠️ Utilities

### File Inspection
```bash
# Inspect all test files
cd testing-suite/utilities
./inspect_test_files.sh

# Examine specific files
cat ../test-data/tests/simple/main.cpp
cat ../test-data/tests/multifile/vehicle/Vehicle.h
```

### File Structure Analysis
```bash
# Find all C++ files
find testing-suite/test-data/tests -name "*.cpp" -o -name "*.h" | sort

# Check test categories
ls -la testing-suite/test-data/tests/
```

---

## 📊 Expected Results

### ✅ Success Indicators
- **Connection Test**: Socket.IO connection established < 2 seconds
- **Simple Compilation**: 2-file project compiles < 3 seconds  
- **Complex Compilation**: 9-file project compiles < 5 seconds
- **Communication**: Custom exit codes and file I/O working
- **Load Testing**: 100% success rate with concurrent clients
- **File Generation**: Executables created in `docker-output/`

### 📈 Performance Benchmarks
- **Simple Projects**: < 1000ms compilation time
- **Complex Projects**: < 2000ms compilation time
- **Load Testing**: 100% success rate with 2-3 concurrent clients
- **Memory Usage**: Container < 1GB RAM usage

---

## 📚 Documentation

### Available Guides
- **END_TO_END_TESTING_GUIDE.md**: Complete step-by-step testing guide
- **EXECUTABLE_COMMUNICATION_REPORT.md**: Communication channel analysis
- **VERIFICATION_REPORT.md**: System verification details

### Key Features
- **Complete Transparency**: All test code visible and editable
- **Organized Structure**: Logical categorization by complexity
- **Easy Debugging**: Individual file modification for experimentation
- **Educational Value**: Clear project structure examples
- **Maintainability**: No hidden inline code

---

## 🔧 Troubleshooting

### Common Issues

1. **Container Not Running**
   ```bash
   docker ps | grep sdv-runtime
   # If not running, start with:
   docker run -d --name sdv-runtime-container -p 3090:3090 -v "$(pwd)/docker-output:/home/dev/data/output" sdv-runtime-production:latest
   ```

2. **Path Issues**
   ```bash
   # Make sure you're in the right directory
   ls testing-suite/  # Should show: documentation/ scripts/ test-data/ utilities/
   ```

3. **Permission Issues**
   ```bash
   chmod +x testing-suite/utilities/inspect_test_files.sh
   chmod +x run-tests.sh
   ```

4. **Dependencies Missing**
   ```bash
   npm install socket.io-client
   ```

---

## 🎯 Benefits of This Organization

1. **🔍 Clear Separation**: Tests, data, scripts, and documentation are clearly separated
2. **📁 Easy Navigation**: Logical folder structure for different types of content
3. **🔄 Maintainability**: Individual components can be modified independently
4. **📚 Documentation**: All guides and reports in dedicated location
5. **🛠️ Utilities**: Helper scripts organized in dedicated utilities folder
6. **🚀 Easy Access**: Simple launcher script for common operations

---

*SDV Runtime Testing Suite - Organized for Production Use*
*Last Updated: August 2024*
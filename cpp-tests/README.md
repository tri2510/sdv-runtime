# C++ Variable Monitoring Test Suite

## 🎯 Overview

This unified test suite validates the C++ global variable monitoring functionality that works **independently of KUKSA databroker**. The tests are organized into three categories based on their scope and purpose.

## 📁 Test Structure

```
cpp-tests/
├── unit/                    # Unit tests for individual components
├── integration/             # Integration tests for full workflows
├── verification/           # Final validation and verification tests
├── run_all_tests.py        # Master test runner
└── README.md              # This file
```

## 🧪 Test Categories

### Unit Tests (`unit/`)
Tests individual components and functions in isolation:

- **`test_auto_detection.py`** - Tests automatic C++ variable detection from source code and binaries
- **`quick_cpp_test.py`** - Quick validation that C++ tracing components work correctly

**Goal**: Validate that individual components (variable detection, symbol mapping) work correctly.

### Integration Tests (`integration/`)
Tests complete workflows and system integration:

- **`test_smart_adaptive.py`** - Tests smart adaptive syncer that filters non-existent variables
- **`test_end_to_end_integration.py`** - Complete end-to-end pipeline testing
- **`test_syncer_pipeline.py`** - Tests the full syncer pipeline integration

**Goal**: Validate that components work together to provide complete C++ monitoring functionality.

### Verification Tests (`verification/`)
Final validation that the entire system meets requirements:

- **`final_verification_test.py`** - Final verification that C++ tracing works without KUKSA databroker
- **`final_ego_speed_test.py`** - Specific validation of automotive variable monitoring

**Goal**: Confirm that the complete system validates the original requirements and goals.

## 🚀 Running Tests

### Run All Tests
```bash
cd /home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-tests
python3 run_all_tests.py
```

### Run Specific Test Category
```bash
# Unit tests only
python3 -m pytest unit/ -v

# Integration tests only
python3 -m pytest integration/ -v

# Verification tests only
python3 -m pytest verification/ -v
```

### Run Individual Tests
```bash
# Test auto-detection
python3 unit/test_auto_detection.py

# Test smart adaptive syncer
python3 integration/test_smart_adaptive.py

# Final verification
python3 verification/final_verification_test.py
```

## ✅ Success Criteria

### Unit Tests
- ✅ Auto variable detection finds C++ global variables
- ✅ Symbol mapping correlates source variables with binary addresses
- ✅ Type detection correctly identifies variable types (int, float, atomic, etc.)

### Integration Tests
- ✅ Smart adaptive syncer filters non-existent variables
- ✅ End-to-end pipeline processes C++ projects successfully
- ✅ Syncer integrates with sample projects without errors

### Verification Tests
- ✅ C++ tracing works completely independent of KUKSA databroker
- ✅ Automotive variables are detected and monitored successfully
- ✅ System handles multiple project types (g++, CMake, Makefile)

## 🔗 Related Components

- **`../cpp-projects/`** - Sample C++ projects used by tests
- **`../kuksa-syncer/auto_variable_detector.py`** - Core auto-detection logic
- **`../kuksa-syncer/cpp_memory_debugger.py`** - Memory monitoring functionality
- **`../kuksa-syncer/ptrace_memory_reader.py`** - Low-level memory reading

## 🎯 Validation Goals

This test suite validates that:

1. **Global Variable Detection**: Automatically finds C++ global variables in source code
2. **Symbol Mapping**: Correlates source variables with binary memory addresses
3. **Memory Monitoring**: Reads variable values from running C++ processes using ptrace
4. **Smart Filtering**: Handles non-existent variables gracefully
5. **Project Compatibility**: Works with different build systems (g++, CMake, Makefile)
6. **Automotive Focus**: Successfully monitors automotive-relevant variables
7. **Independence**: Functions completely without KUKSA databroker dependency

## 📊 Test Coverage

- ✅ **Variable Types**: int, float, double, bool, char, atomic types
- ✅ **Build Systems**: Direct g++, CMake, traditional Makefile
- ✅ **Project Structures**: Single file, multi-directory, complex namespaces
- ✅ **Automotive Scenarios**: Vehicle systems, ADAS, sensor data, engine control
- ✅ **Error Handling**: Non-existent variables, compilation failures, runtime errors

Perfect for validating the universal C++ variable monitoring system! 🚗💻
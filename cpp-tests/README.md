# Complete C++ Variable Monitoring Test Suite

## 🎯 Overview

This is the **single, unified test suite** for all C++ global variable monitoring functionality that works **independently of KUKSA databroker**. All tests have been consolidated from previously scattered directories (`test/`, `integration-tests/`, `kuksa-syncer/`) into this organized structure.

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

- **`test_auto_detection.py`** - Automatic C++ variable detection from source code and binaries
- **`quick_cpp_test.py`** - Quick validation that C++ tracing components work correctly
- **`final_memory_test.py`** - Memory reading and variable address validation
- **`check_variable_addresses.py`** - Variable address mapping verification
- **`debug_memory_reading.py`** - Memory reading debugging utilities
- **`test_simple_memory_read.py`** - Simple memory reading validation

**Goal**: Validate that individual components (variable detection, symbol mapping, memory reading) work correctly.

### Integration Tests (`integration/`)
Tests complete workflows and system integration:

- **`test_smart_adaptive.py`** - Smart adaptive syncer that filters non-existent variables
- **`test_end_to_end_integration.py`** - Complete end-to-end pipeline testing
- **`test_syncer_pipeline.py`** - Full syncer pipeline integration
- **`test_ptrace_monitoring.py`** - Ptrace-based memory monitoring integration
- **`test_cpp_commands.py`** - C++ command handling and execution
- **`test_direct_cpp_build.py`** - Direct C++ compilation and monitoring
- **`test_kitserver_cpp_build.py`** - Kit-server C++ integration
- **`test_command_handling.py`** - Command processing and handling
- **`test_syncer_import.py`** - Syncer module import and initialization
- **`test_with_variable_detector.py`** - Variable detector integration
- **`simulate_kitserver_request.py`** - Kit-server request simulation

**Goal**: Validate that components work together to provide complete C++ monitoring functionality.

### Verification Tests (`verification/`)
Final validation that the entire system meets requirements:

- **`final_verification_test.py`** - Final verification that C++ tracing works without KUKSA databroker
- **`final_ego_speed_test.py`** - Specific validation of automotive variable monitoring
- **`test_automotive_variables.py`** - Comprehensive automotive variable testing
- **`validate_complete_integration.py`** - Complete system integration validation

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
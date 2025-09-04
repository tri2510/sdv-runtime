# C++ Compilation Tests

This directory contains tests for the C++ compilation pipeline and kit server integration.

## Files

- **`test_direct_cpp_build.py`** - Direct test of C++ compilation pipeline using ProjectUtils
- **`test_kitserver_cpp_build.py`** - Simulates kit server C++ compilation requests
- **`test_cpp_commands.py`** - Tests C++ command handling from kit server
- **`simulate_kitserver_request.py`** - Complete kit server → syncer → compilation flow simulation

## Purpose

These tests validate the entire C++ compilation workflow:
1. Kit server sends WebSocket message with C++ code
2. Syncer processes the message and creates project files
3. C++ code gets compiled with debug symbols
4. Binary is ready for execution and monitoring

## Key Features Tested

- ✅ **Automatic variable detection** from C++ source
- ✅ **Tree structure project format** parsing
- ✅ **ProjectUtils** file creation and compilation
- ✅ **WebSocket message handling** simulation
- ✅ **Binary creation** with proper debug symbols

## Usage

```bash
# Test direct compilation pipeline
python3 test_direct_cpp_build.py

# Test kit server simulation
python3 simulate_kitserver_request.py

# Test command handling
python3 test_cpp_commands.py
```

## Results

All compilation tests **pass successfully** - the C++ compilation pipeline is 100% functional.
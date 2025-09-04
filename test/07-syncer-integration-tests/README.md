# Syncer Integration Tests

This directory contains tests for syncer.py integration and core functionality.

## Files

- **`test_syncer_import.py`** - Tests syncer module imports and dependencies
- **`test_command_handling.py`** - Tests WebSocket command handling in syncer
- **`test_ptrace_monitoring.py`** - Tests ptrace memory monitoring integration

## Purpose

These tests validate the syncer.py integration with:
- C++ memory monitoring modules
- WebSocket message handling
- Command processing pipeline
- Import dependencies

## Key Features Tested

- ✅ **Module imports** - All required modules load correctly
- ✅ **C++ memory monitoring** - Integration with auto detection system
- ✅ **WebSocket handlers** - Command routing and processing
- ✅ **Error handling** - Graceful fallbacks when dependencies unavailable

## Usage

```bash
# Test syncer imports
python3 test_syncer_import.py

# Test command handling
python3 test_command_handling.py

# Test memory monitoring integration
python3 test_ptrace_monitoring.py
```

## Results

All syncer integration tests **pass successfully** - the syncer is ready for production use.
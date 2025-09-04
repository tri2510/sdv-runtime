# Kit Server Simulation Test

This directory contains a focused test that simulates the exact kit server → syncer → C++ compilation pipeline without KUKSA dependencies.

## Files

- **`test_kitserver_simulation.py`** - Complete kit server simulation bypassing KUKSA connection issues

## Purpose

This test demonstrates the complete autowrx → syncer workflow:
1. Kit server (autowrx) sends WebSocket message with C++ code and variable list
2. Syncer receives message and auto-detects variables
3. C++ project gets created using tree structure format
4. Binary compiles with debug symbols
5. Memory monitoring starts for requested automotive variables
6. Real-time variable monitoring displays automotive data

## Key Features Tested

- ✅ **Kit server message format** - Exact WebSocket message structure
- ✅ **Automotive variables** - ego_speed, current_lane, steering_angle, collision_risk
- ✅ **Tree structure parsing** - Project creation from kit server format
- ✅ **Auto variable detection** - No hardcoded variables
- ✅ **Memory monitoring** - Real-time automotive data tracking
- ✅ **KUKSA-free operation** - Works without KUKSA server connection

## Usage

```bash
# Run from sdv-runtime root directory
python3 test/09-kitserver-simulation/test_kitserver_simulation.py
```

## Expected Output

The test will show:
- Kit server message simulation
- Variable auto-detection (5 variables found)
- C++ project creation and compilation
- Real-time automotive variable monitoring
- Memory reading with actual values

## Benefits

- **No KUKSA dependency** - Bypasses connection refused errors
- **Complete pipeline test** - Tests autowrx → syncer integration
- **Real automotive data** - Monitors actual vehicle variables
- **Production-ready** - Shows system working end-to-end
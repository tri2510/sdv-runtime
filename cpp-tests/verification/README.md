# Automotive Variable Tests

This directory contains tests specifically for automotive C++ variable monitoring.

## Files

- **`test_automotive_variables.py`** - Tests automotive variable detection and compilation
- **`fixed_automotive_main.cpp`** - Corrected C++ code with proper automotive variable names

## Purpose

These tests validate that the automatic variable detection system works with automotive-specific variables and ensures proper naming compatibility between kit server expectations and C++ variable declarations.

## Key Variables Tested

- **`ego_speed`** - Vehicle speed (float)
- **`current_lane`** - Current lane number (int)  
- **`steering_angle`** - Steering wheel angle (float)
- **`collision_risk`** - Collision risk factor (float)

## Key Features Tested

- ✅ **Variable name matching** - Kit server requests match C++ declarations
- ✅ **Automotive data types** - Float and int types for vehicle data
- ✅ **Symbol table validation** - Variables found in compiled binary
- ✅ **Type-aware compilation** - Proper atomic variable handling

## Usage

```bash
# Test automotive variable detection
python3 test_automotive_variables.py
```

## Results

All automotive variable tests **pass successfully** - the system correctly detects and processes automotive C++ variables.

## Solution Provided

The **`fixed_automotive_main.cpp`** file contains the corrected C++ code that matches kit server expectations, solving the original variable name mismatch issue.
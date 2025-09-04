# Memory Monitoring Debug Tests

This directory contains debugging and testing scripts for the C++ memory monitoring system.

## Files

- **`debug_memory_reading.py`** - Comprehensive debug script to test memory reading pipeline
- **`check_variable_addresses.py`** - Analyzes memory layout and variable addresses using nm, objdump, readelf
- **`final_memory_test.py`** - Step-by-step process state debugging for ptrace issues
- **`test_simple_memory_read.py`** - Basic ptrace memory reading test with error analysis

## Purpose

These tests were created to debug the ptrace-based memory monitoring system and identify why processes were exiting with code -19 during memory reads.

## Key Findings

1. ✅ **Variable detection** works perfectly
2. ✅ **Symbol address calculation** works correctly  
3. ✅ **Data section mapping** is accurate
4. ❌ **Ptrace memory reading** causes process death (SIGSTOP/exit -19)

## Usage

Run individual tests to debug specific aspects:

```bash
# Test comprehensive memory reading pipeline
python3 debug_memory_reading.py

# Analyze variable addresses in binary
python3 check_variable_addresses.py

# Debug process state during ptrace
python3 final_memory_test.py
```

## Next Steps

The memory monitoring system needs an alternative to ptrace, such as:
- `/proc/PID/mem` reading
- Shared memory communication
- File-based variable sharing
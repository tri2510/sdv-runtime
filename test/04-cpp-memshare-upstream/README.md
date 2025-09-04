# Feature 1: C++ Memory Share with Upstream Implementation

## Overview
This test validates the complete C++ variable monitoring pipeline using upstream cpp-share-mem implementation.

## Test Scenario
1. **Frontend sends C++ code** in JSON project structure format
2. **Backend compiles and runs** C++ code with shared memory integration
3. **Variables are monitored** via atomic shared memory operations
4. **Frontend receives updates** through trace_vars WebSocket messages

## Test Files

### test_app.cpp
```cpp
#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Shared memory variables for monitoring
std::atomic<int> counter{0};
std::atomic<double> sensor_value{25.5};

int main() {
    std::cout << "Starting C++ app with memory monitoring..." << std::endl;
    
    for(int i = 0; i < 10; i++) {
        counter.store(i);
        sensor_value.store(25.5 + i * 0.5);
        
        std::cout << "Iteration " << i << ": counter=" << counter.load() 
                  << ", sensor=" << sensor_value.load() << std::endl;
        
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
    
    std::cout << "C++ app finished." << std::endl;
    return 0;
}
```

## Expected Behavior

### Frontend (autowrx)
1. User runs C++ code with watch variables: `counter, sensor_value`
2. Frontend sends WebSocket message:
   ```json
   {
     "cmd": "run_cpp_app",
     "data": {
       "language": "cpp",
       "watch_vars": "counter, sensor_value", 
       "code": "[{\"type\":\"file\",\"name\":\"main.cpp\",\"content\":\"...\"}]",
       "name": "test_app"
     }
   }
   ```

### Backend (syncer.py)
1. Receives run_cpp_app command
2. Validates JSON project structure  
3. Compiles C++ code with g++ and shared memory flags
4. Runs binary with cpp_debugger_util monitoring
5. Sends periodic trace_vars messages with variable values

### Frontend Variable Monitor
1. Receives trace_vars messages via WebSocket
2. Updates UI with real-time variable values:
   - `counter`: 0, 1, 2, 3, ...
   - `sensor_value`: 25.5, 26.0, 26.5, ...

## Validation Steps

### 1. Backend Standalone Test
```bash
cd /home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork
python3 -c "
import sys
sys.path.append('kuksa-syncer')
from syncer import ProjectUtils, cpp_debugger_util
print('✓ All upstream dependencies available')
"
```

### 2. Frontend Message Format Test  
- Check DaRuntimeConnector.tsx sends correct JSON project structure
- Verify WebSocket message format matches backend expectations

### 3. End-to-End Integration Test
- Run test_app.cpp through complete pipeline
- Verify compilation, execution, and variable monitoring
- Confirm trace_vars messages received in frontend

## Known Issues
- None with upstream implementation

## Success Criteria
- [x] Backend imports work without modification
- [x] Frontend sends proper JSON format  
- [ ] C++ code compiles and runs successfully
- [ ] Variables are monitored via shared memory
- [ ] trace_vars messages received in frontend UI
# C++ Demo Projects for SDV Runtime

This directory contains demonstration projects that showcase the shared memory integration capabilities with the SDV Runtime environment.

## Available Projects

### 1. FCW ADAS Demo (`fcw-adas-demo/`)

A comprehensive Forward Collision Warning (FCW) system demonstration similar to customer requirements:

**Features:**
- Multi-lane environment simulation (4 lanes)
- Real-time vehicle position and motion tracking
- Collision detection and warning algorithms
- V2X communication simulation
- Traffic light and speed limit monitoring
- Comprehensive shared memory integration

**Monitored Variables:**
- `ego_speed` (float) - Vehicle speed in km/h
- `collision_risk` (int) - Risk percentage (0-100)
- `current_lane` (int) - Current lane number (1-4)  
- `warning_active` (bool) - Warning system status
- `brake_pressure` (float) - Brake system pressure (0-100%)

### 2. Simple Counter (`simple-counter/`)

A basic demonstration project perfect for testing shared memory functionality:

**Features:**
- Simple counter that increments every second
- Two monitored variables for testing
- Bidirectional communication support

**Monitored Variables:**
- `counter` (int) - Main counter value
- `test` (int) - Test variable for modifications

## Building Projects

Each project uses CMake for building:

```bash
cd <project-directory>
mkdir build && cd build
cmake .. && make
./<executable-name>
```

## Shared Memory Integration

All projects include the shared memory wrapper (`shm_wrapper.h`) which enables:

1. **Real-time monitoring** - View variable values through Kit Manager
2. **Bidirectional communication** - Modify variables from external interface
3. **Thread-safe operations** - Using atomic variables for concurrent access

## Usage in SDV Runtime

1. Copy project files to the Kit Manager's compilation environment
2. Build using the provided CMakeLists.txt
3. Run the executable
4. Monitor and modify variables through the Kit Manager's shared memory interface

## Customer Alignment

The FCW ADAS Demo specifically addresses customer requirements:
- ✅ 4-lane environment simulation
- ✅ Collision detection and warning system
- ✅ V2X communication capabilities
- ✅ Traffic infrastructure monitoring
- ✅ Real-time variable monitoring and control

## Testing

Both projects have been designed to work seamlessly with the cpp-share-mem branch capabilities and provide realistic demonstrations for customer presentations.
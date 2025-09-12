# Integration Tests - Sample Projects

This folder contains sample projects demonstrating variable tracing integration with Kit Server and real-world C++ applications.

## Sample Projects Overview

### 1. `sample-basic-monitoring/`
**Purpose**: Basic atomic variable monitoring with kit server integration
- Simple C++ app with traced variables
- Kit server configuration
- Real-time monitoring dashboard

### 2. `sample-automotive-controls/`
**Purpose**: Automotive control systems with PID controllers
- Engine control simulation
- Brake system monitoring
- Speed control with feedback
- Kit server telemetry

### 3. `sample-sensor-fusion/`
**Purpose**: Multi-sensor data fusion and filtering
- IMU data processing
- GPS integration
- Kalman filter implementation
- Real-time position tracking

### 4. `sample-realtime-dashboard/`
**Purpose**: Real-time data visualization
- WebSocket integration
- Live charts and graphs
- Kit server data streaming
- Performance monitoring

### 5. `kit-server-integration/`
**Purpose**: Kit server configuration and utilities
- Server configuration templates
- Integration scripts
- Validation tools
- API examples

## Quick Start

1. **Build all samples**:
   ```bash
   ./build_all.sh
   ```

2. **Run basic monitoring**:
   ```bash
   cd sample-basic-monitoring
   ./run_with_kit_server.sh
   ```

3. **Start dashboard**:
   ```bash
   cd sample-realtime-dashboard
   ./start_dashboard.sh
   ```

## Kit Server Integration

All sample projects are designed to work with the kit server for:
- Variable discovery and registration
- Real-time data streaming
- Remote monitoring and control
- Performance analysis
- Debug tracing

## Requirements

- C++17 compatible compiler
- Kit server running
- Python 3.8+ (for dashboard)
- Node.js (for web components)
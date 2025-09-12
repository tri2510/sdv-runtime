#!/bin/bash

# Run basic monitoring sample with kit server integration
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Basic Monitoring with Kit Server ==="
echo ""

# Check if kit server is running
check_kit_server() {
    echo "Checking for Kit Server..."
    if pgrep -f "kit.*server" > /dev/null; then
        echo "✅ Kit Server is running"
        return 0
    else
        echo "⚠️  Kit Server not detected"
        return 1
    fi
}

# Build if needed
build_sample() {
    echo "Building basic monitoring sample..."
    cd "$SCRIPT_DIR"
    
    if [ ! -d "build" ]; then
        mkdir build
    fi
    
    cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j$(nproc)
    
    echo "✅ Build completed"
}

# Start kit server if not running
start_kit_server() {
    echo "Starting Kit Server..."
    
    # Look for kit server executable
    KIT_SERVER_PATH=""
    
    # Check common locations
    if [ -f "$PROJECT_ROOT/../kit-server" ]; then
        KIT_SERVER_PATH="$PROJECT_ROOT/../kit-server"
    elif [ -f "$PROJECT_ROOT/../build/kit-server" ]; then
        KIT_SERVER_PATH="$PROJECT_ROOT/../build/kit-server"
    elif command -v kit-server &> /dev/null; then
        KIT_SERVER_PATH="kit-server"
    fi
    
    if [ -n "$KIT_SERVER_PATH" ]; then
        echo "Starting Kit Server from: $KIT_SERVER_PATH"
        nohup "$KIT_SERVER_PATH" > /tmp/kit-server.log 2>&1 &
        KIT_SERVER_PID=$!
        echo "Kit Server started with PID: $KIT_SERVER_PID"
        sleep 2
        
        if ps -p $KIT_SERVER_PID > /dev/null; then
            echo "✅ Kit Server started successfully"
            return 0
        else
            echo "❌ Kit Server failed to start"
            return 1
        fi
    else
        echo "❌ Kit Server executable not found"
        echo "Please ensure kit server is built and available"
        return 1
    fi
}

# Setup variable monitoring
setup_monitoring() {
    echo "Setting up variable monitoring..."
    
    # Create monitoring configuration
    cat > "$SCRIPT_DIR/monitor_config.json" << EOF
{
    "process_name": "basic_monitoring",
    "variables": [
        {
            "name": "g_temperature",
            "type": "double",
            "description": "Temperature sensor reading in Celsius"
        },
        {
            "name": "g_pressure", 
            "type": "double",
            "description": "Atmospheric pressure in kPa"
        },
        {
            "name": "g_humidity",
            "type": "double", 
            "description": "Relative humidity percentage"
        },
        {
            "name": "g_rpm",
            "type": "int",
            "description": "Engine RPM"
        },
        {
            "name": "g_system_active",
            "type": "bool",
            "description": "System active status"
        },
        {
            "name": "g_error_count",
            "type": "int",
            "description": "Cumulative error count"
        },
        {
            "name": "g_voltage",
            "type": "double",
            "description": "Battery voltage"
        },
        {
            "name": "g_current",
            "type": "double",
            "description": "Current draw in Amps"
        }
    ],
    "update_interval_ms": 100,
    "export_formats": ["json", "csv"]
}
EOF
    
    echo "✅ Monitoring configuration created"
}

# Run the sample
run_sample() {
    echo "Running basic monitoring sample..."
    echo "Monitor output will show real-time variable values"
    echo "Kit Server integration will trace variables automatically"
    echo ""
    echo "Variables being monitored:"
    echo "  - g_temperature (environmental)"
    echo "  - g_pressure (environmental)" 
    echo "  - g_humidity (environmental)"
    echo "  - g_rpm (engine)"
    echo "  - g_system_active (status)"
    echo "  - g_error_count (diagnostics)"
    echo "  - g_voltage (electrical)"
    echo "  - g_current (electrical)"
    echo ""
    echo "Press Ctrl+C to stop..."
    echo ""
    
    cd "$SCRIPT_DIR/build"
    ./basic_monitoring
}

# Cleanup
cleanup() {
    echo ""
    echo "Cleaning up..."
    
    # Kill kit server if we started it
    if [ -n "$KIT_SERVER_PID" ]; then
        if ps -p $KIT_SERVER_PID > /dev/null; then
            echo "Stopping Kit Server (PID: $KIT_SERVER_PID)..."
            kill $KIT_SERVER_PID
        fi
    fi
    
    echo "Cleanup completed"
}

# Set up signal handler
trap cleanup EXIT

# Main execution flow
build_sample

if ! check_kit_server; then
    echo "Kit Server not running. Attempting to start..."
    if ! start_kit_server; then
        echo "Warning: Continuing without Kit Server"
        echo "Variable tracing will work, but Kit Server integration will be limited"
    fi
fi

setup_monitoring
run_sample
#!/bin/bash

# SDV Runtime Testing Suite Launcher
# ==================================
echo "🧪 SDV Runtime Testing Suite"
echo "============================"
echo ""

# Check if we're in the right directory
if [ ! -d "testing-suite" ]; then
    echo "❌ Error: testing-suite directory not found"
    echo "   Please run this script from the sdv-runtime-production root directory"
    exit 1
fi

# Check if container is running
if ! docker ps | grep -q "sdv-runtime"; then
    echo "❌ SDV Runtime container not running"
    echo ""
    read -p "Would you like to build and start the container now? (y/n): " build_container
    
    if [[ $build_container =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔨 Building SDV Runtime container..."
        docker build -f Dockerfile.kitmanager \
          --tag sdv-runtime-production:latest \
          --progress=plain \
          .
        
        if [ $? -ne 0 ]; then
            echo "❌ Container build failed"
            exit 1
        fi
        
        echo ""
        echo "🚀 Starting SDV Runtime container..."
        
        # Create output directory if it doesn't exist
        mkdir -p docker-output
        
        # Stop and remove any existing container with the same name
        docker stop sdv-runtime-container 2>/dev/null || true
        docker rm sdv-runtime-container 2>/dev/null || true
        
        # Start new container
        docker run -d \
          --name sdv-runtime-container \
          --publish 3090:3090 \
          --volume "$(pwd)/docker-output:/home/dev/data/output" \
          --restart unless-stopped \
          sdv-runtime-production:latest
        
        if [ $? -ne 0 ]; then
            echo "❌ Container start failed"
            exit 1
        fi
        
        echo "✅ Container started successfully"
        echo "⏳ Waiting for container to be ready (5 seconds)..."
        sleep 5
        
        # Verify container is running
        if ! docker ps | grep -q "sdv-runtime-container"; then
            echo "❌ Container failed to start properly"
            docker logs sdv-runtime-container
            exit 1
        fi
        
        echo "🎯 Container is ready for testing!"
        echo ""
    else
        echo ""
        echo "Please build and start the container manually:"
        echo "  docker build -f Dockerfile.kitmanager --tag sdv-runtime-production:latest ."
        echo "  docker run -d --name sdv-runtime-container -p 3090:3090 -v \"\$(pwd)/docker-output:/home/dev/data/output\" sdv-runtime-production:latest"
        exit 1
    fi
fi

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Node.js dependencies not found"
    read -p "Would you like to install dependencies now? (y/n): " install_deps
    
    if [[ $install_deps =~ ^[Yy]$ ]]; then
        echo "📦 Installing socket.io-client..."
        npm install socket.io-client
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install dependencies"
            exit 1
        fi
        
        echo "✅ Dependencies installed successfully"
    else
        echo "⚠️  Warning: Some tests may fail without socket.io-client dependency"
    fi
    echo ""
fi

# Change to scripts directory
cd testing-suite/scripts

echo "🔍 Available test options:"
echo "========================="
echo "1. Basic connection test"
echo "2. Simple C++ compilation test"
echo "3. Complex multi-file compilation test"
echo "4. Communication verification test"
echo "5. Advanced features test"
echo "6. FCW System test (automotive)"
echo "7. FCW-KUKSA Integration test (automotive + databroker)"
echo "8. Load testing"
echo "9. Run complete test suite"
echo "10. Inspect test files"
echo ""

read -p "Enter your choice (1-10): " choice

case $choice in
    1)
        echo "🔌 Running connection test..."
        node test_connection.js
        ;;
    2)
        echo "🔨 Running simple C++ test..."
        node test_cpp_simple.js
        ;;
    3)
        echo "🏗️ Running complex multi-file test..."
        node test_cpp_complex.js
        ;;
    4)
        echo "📞 Running communication verification..."
        node verify_executable_communication.js
        ;;
    5)
        echo "🔬 Running advanced features test..."
        node verify_advanced_features.js
        ;;
    6)
        echo "🚗 Running FCW System test..."
        node test_fcw_system.js
        ;;
    7)
        echo "📡 Running FCW-KUKSA Integration test..."
        node test_fcw_kuksa.js
        ;;
    8)
        echo "🚀 Running load testing..."
        node production_load_test.js
        ;;
    9)
        echo "🎯 Running complete test suite..."
        node run_file_based_tests.js
        ;;
    10)
        echo "🔍 Inspecting test files..."
        cd ../utilities
        ./inspect_test_files.sh
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "✅ Test execution completed!"
echo "📁 Check docker-output/ directory for generated executables"
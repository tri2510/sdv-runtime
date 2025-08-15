#!/bin/bash

# SDV Runtime Production Setup Script
# ===================================
echo "🚀 SDV Runtime Production Setup"
echo "==============================="
echo ""

# Check if we're in the right directory
if [ ! -f "Dockerfile.kitmanager" ]; then
    echo "❌ Error: Dockerfile.kitmanager not found"
    echo "   Please run this script from the sdv-runtime-production root directory"
    exit 1
fi

echo "📋 This script will:"
echo "   1. Install Node.js dependencies"
echo "   2. Build the SDV Runtime container"
echo "   3. Start the container with proper configuration"
echo "   4. Verify the setup is working"
echo ""

read -p "Continue with setup? (y/n): " continue_setup

if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo "📦 Step 1: Installing Node.js dependencies..."
echo "============================================="

# Install Node.js dependencies
npm install socket.io-client

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

echo "✅ Node.js dependencies installed successfully"
echo ""

echo "🔨 Step 2: Building SDV Runtime container..."
echo "============================================"

# Build the container
docker build -f Dockerfile.kitmanager \
  --tag sdv-runtime-production:latest \
  --progress=plain \
  .

if [ $? -ne 0 ]; then
    echo "❌ Container build failed"
    exit 1
fi

echo "✅ Container built successfully"
echo ""

echo "🚀 Step 3: Starting SDV Runtime container..."
echo "============================================"

# Create output directory
mkdir -p docker-output

# Stop and remove any existing container
echo "🧹 Cleaning up existing containers..."
docker stop sdv-runtime-container 2>/dev/null || true
docker rm sdv-runtime-container 2>/dev/null || true

# Start new container
echo "🏁 Starting new container..."
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
echo "⏳ Waiting for container to be ready (10 seconds)..."
sleep 10

# Verify container is running
if ! docker ps | grep -q "sdv-runtime-container"; then
    echo "❌ Container failed to start properly"
    echo "📋 Container logs:"
    docker logs sdv-runtime-container
    exit 1
fi

echo ""
echo "🔍 Step 4: Verifying setup..."
echo "============================="

# Check container logs
echo "📋 Container logs (last 10 lines):"
docker logs --tail 10 sdv-runtime-container

echo ""
echo "🔌 Testing basic connectivity..."

# Test basic connectivity
cd testing-suite/scripts
timeout 15 node test_connection.js

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SETUP COMPLETED SUCCESSFULLY!"
    echo "==============================="
    echo "✅ Container is running and accessible"
    echo "✅ SDV Runtime is ready for C++ compilation"
    echo "✅ All dependencies are installed"
    echo ""
    echo "🚀 Next steps:"
    echo "   - Run tests: ./run-tests.sh"
    echo "   - View test files: ./testing-suite/utilities/inspect_test_files.sh"
    echo "   - Check container status: docker ps | grep sdv-runtime"
    echo "   - View container logs: docker logs sdv-runtime-container"
    echo ""
    echo "🎯 Your SDV Runtime production system is ready to use!"
else
    echo ""
    echo "⚠️  SETUP COMPLETED WITH WARNINGS"
    echo "================================"
    echo "✅ Container is running"
    echo "❌ Connection test failed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check container logs: docker logs sdv-runtime-container"
    echo "   - Verify port 3090 is not in use: lsof -i :3090"
    echo "   - Try manual connection test: cd testing-suite/scripts && node test_connection.js"
fi

echo ""
echo "📊 Container Status:"
docker ps | grep sdv-runtime-container || echo "Container not found"

echo ""
echo "📁 Setup Summary:"
echo "   Container Name: sdv-runtime-container"
echo "   Port: 3090"
echo "   Output Directory: $(pwd)/docker-output"
echo "   Testing Suite: $(pwd)/testing-suite"
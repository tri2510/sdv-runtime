#!/bin/bash

echo "Building CMake Vehicle Systems Monitor..."

# Create build directory if it doesn't exist
mkdir -p build
cd build

# Configure and build with CMake
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: build/vehicle_systems"
    echo "Run with: cd build && ./vehicle_systems"
else
    echo "Build failed!"
    exit 1
fi
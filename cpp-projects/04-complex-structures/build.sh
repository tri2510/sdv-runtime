#!/bin/bash

echo "Building Complex Vehicle System Monitor..."
g++ -g -O0 -std=c++17 -pthread -o complex_vehicle_system complex_vehicle_system.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: complex_vehicle_system"
    echo "Run with: ./complex_vehicle_system"
else
    echo "Build failed!"
    exit 1
fi
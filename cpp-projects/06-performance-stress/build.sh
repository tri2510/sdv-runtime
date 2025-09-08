#!/bin/bash

echo "Building Performance Stress Test Monitor..."
g++ -g -O0 -std=c++17 -pthread -o performance_stress_test performance_stress_test.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: performance_stress_test"
    echo "Run with: ./performance_stress_test"
else
    echo "Build failed!"
    exit 1
fi
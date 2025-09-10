#!/bin/bash

echo "Building Basic Types Monitor..."
g++ -g -O0 -std=c++17 -pthread -o basic_types_monitor basic_types_monitor.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: basic_types_monitor"
    echo "Run with: ./basic_types_monitor"
else
    echo "Build failed!"
    exit 1
fi
#!/bin/bash

echo "Building Embedded ECU System Monitor..."
g++ -g -O0 -std=c++17 -pthread -o embedded_ecu_system embedded_ecu_system.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: embedded_ecu_system"
    echo "Run with: ./embedded_ecu_system"
else
    echo "Build failed!"
    exit 1
fi
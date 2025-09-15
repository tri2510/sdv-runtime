#!/bin/bash

echo "Building Simulink Vehicle Model..."
g++ -g -O0 -std=c++11 -o simulink_vehicle_model simulink_vehicle_model.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: simulink_vehicle_model"
    echo "Run with: ./simulink_vehicle_model"
else
    echo "Build failed!"
    exit 1
fi
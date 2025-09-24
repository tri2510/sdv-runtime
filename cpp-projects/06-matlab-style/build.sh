#!/bin/bash

echo "Building MATLAB-Style Vehicle Controller..."
g++ -g -O0 -std=c++11 -pthread -fno-pie -no-pie -o matlab_generated_code matlab_generated_code.cpp

if [ $? -eq 0 ]; then
    echo "Build successful! Executable: matlab_generated_code"
    echo "Run with: ./matlab_generated_code"
else
    echo "Build failed!"
    exit 1
fi

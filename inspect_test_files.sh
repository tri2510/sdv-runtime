#!/bin/bash

echo "📁 FILE-BASED TEST INPUT INSPECTION"
echo "==================================="
echo ""

echo "🔍 Available Test Categories:"
echo "----------------------------"
ls -la tests/

echo ""
echo "📄 Simple Test Files:"
echo "--------------------"
echo "📂 tests/simple/"
ls -la tests/simple/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat tests/simple/main.cpp
echo ""
echo "📄 config.h:"
echo "-------------"
cat tests/simple/config.h

echo ""
echo "📄 Multi-file Test Files:"
echo "-------------------------"
echo "📂 tests/multifile/"
find tests/multifile/ -type f -name "*.cpp" -o -name "*.h" | sort
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat tests/multifile/main.cpp
echo ""
echo "📄 Vehicle.h:"
echo "-------------"
cat tests/multifile/vehicle/Vehicle.h
echo ""
echo "📄 SpeedSensor.cpp:"
echo "-------------------"
cat tests/multifile/sensors/SpeedSensor.cpp

echo ""
echo "📄 Communication Test Files:"
echo "----------------------------"
echo "📂 tests/communication/"
ls -la tests/communication/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat tests/communication/main.cpp
echo ""
echo "📄 communication.h:"
echo "-------------------"
cat tests/communication/communication.h

echo ""
echo "📄 Network Test Files:"
echo "---------------------"
echo "📂 tests/network/"
ls -la tests/network/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat tests/network/main.cpp

echo ""
echo "🎯 INSPECTION COMPLETED"
echo "======================="
echo "✅ All test files are now transparent and inspectable"
echo "📁 Users can examine any file using: cat tests/[category]/[filename]"
echo "🔍 File structure is clearly organized by test category"
echo "📝 Each test demonstrates specific C++ compilation features"
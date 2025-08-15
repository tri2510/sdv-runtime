#!/bin/bash

echo "📁 FILE-BASED TEST INPUT INSPECTION"
echo "==================================="
echo ""

echo "🔍 Available Test Categories:"
echo "----------------------------"
ls -la ../test-data/tests/

echo ""
echo "📄 Simple Test Files:"
echo "--------------------"
echo "📂 test-data/tests/simple/"
ls -la ../test-data/tests/simple/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat ../test-data/tests/simple/main.cpp
echo ""
echo "📄 config.h:"
echo "-------------"
cat ../test-data/tests/simple/config.h

echo ""
echo "📄 Multi-file Test Files:"
echo "-------------------------"
echo "📂 test-data/tests/multifile/"
find ../test-data/tests/multifile/ -type f -name "*.cpp" -o -name "*.h" | sort
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat ../test-data/tests/multifile/main.cpp
echo ""
echo "📄 Vehicle.h:"
echo "-------------"
cat ../test-data/tests/multifile/vehicle/Vehicle.h
echo ""
echo "📄 SpeedSensor.cpp:"
echo "-------------------"
cat ../test-data/tests/multifile/sensors/SpeedSensor.cpp

echo ""
echo "📄 Communication Test Files:"
echo "----------------------------"
echo "📂 test-data/tests/communication/"
ls -la ../test-data/tests/communication/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat ../test-data/tests/communication/main.cpp
echo ""
echo "📄 communication.h:"
echo "-------------------"
cat ../test-data/tests/communication/communication.h

echo ""
echo "📄 Network Test Files:"
echo "---------------------"
echo "📂 test-data/tests/network/"
ls -la ../test-data/tests/network/
echo ""
echo "📄 main.cpp:"
echo "-------------"
cat ../test-data/tests/network/main.cpp

echo ""
echo "🎯 INSPECTION COMPLETED"
echo "======================="
echo "✅ All test files are now transparent and inspectable"
echo "📁 Users can examine any file using: cat testing-suite/test-data/tests/[category]/[filename]"
echo "🔍 File structure is clearly organized by test category"
echo "📝 Each test demonstrates specific C++ compilation features"
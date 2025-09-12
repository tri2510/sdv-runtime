#!/bin/bash

# Build All Integration Test Samples
# Builds all sample projects for kit server integration testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo " Building All Integration Test Samples"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

build_sample() {
    local sample_name=$1
    local sample_dir="$SCRIPT_DIR/$sample_name"
    
    echo "Building $sample_name..."
    
    if [ ! -d "$sample_dir" ]; then
        echo -e "${RED}❌ Sample directory not found: $sample_dir${NC}"
        return 1
    fi
    
    # Create build directory
    mkdir -p "$sample_dir/build"
    cd "$sample_dir/build"
    
    # CMake configure
    if ! cmake .. -DCMAKE_BUILD_TYPE=Release > cmake.log 2>&1; then
        echo -e "${RED}❌ CMake failed for $sample_name${NC}"
        echo "Check $sample_dir/build/cmake.log for details"
        return 1
    fi
    
    # Build
    if ! make -j$(nproc) > make.log 2>&1; then
        echo -e "${RED}❌ Build failed for $sample_name${NC}"
        echo "Check $sample_dir/build/make.log for details"
        return 1
    fi
    
    print_status 0 "$sample_name built successfully"
    return 0
}

# List of samples to build
SAMPLES=(
    "sample-basic-monitoring"
    "sample-automotive-controls"
)

# Build each sample
echo "Building samples..."
echo ""

BUILD_RESULTS=()
TOTAL_SAMPLES=${#SAMPLES[@]}
SUCCESSFUL_BUILDS=0

for sample in "${SAMPLES[@]}"; do
    if build_sample "$sample"; then
        BUILD_RESULTS+=("$sample:SUCCESS")
        ((SUCCESSFUL_BUILDS++))
    else
        BUILD_RESULTS+=("$sample:FAILED")
    fi
    echo ""
done

# Summary
echo "=========================================="
echo " Build Summary"
echo "=========================================="

for result in "${BUILD_RESULTS[@]}"; do
    sample=$(echo "$result" | cut -d: -f1)
    status=$(echo "$result" | cut -d: -f2)
    
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $sample${NC}"
    else
        echo -e "${RED}❌ $sample${NC}"
    fi
done

echo ""
echo "Successfully built: $SUCCESSFUL_BUILDS/$TOTAL_SAMPLES samples"

if [ $SUCCESSFUL_BUILDS -eq $TOTAL_SAMPLES ]; then
    echo -e "${GREEN}🎉 All samples built successfully!${NC}"
    echo ""
    echo "You can now run:"
    echo "  - Basic monitoring: cd sample-basic-monitoring && ./run_with_kit_server.sh"
    echo "  - Integration tests: cd kit-server-integration && python3 test_with_variable_detector.py"
    exit 0
else
    echo -e "${RED}❌ Some builds failed${NC}"
    exit 1
fi
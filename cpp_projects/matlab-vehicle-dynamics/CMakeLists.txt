cmake_minimum_required(VERSION 3.12)
project(matlab_vehicle_dynamics VERSION 1.0.0)

# Set C++ standard (compatible with MATLAB Coder output)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set build type if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags (similar to MATLAB Coder optimization settings)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/include
)

# Find required libraries
find_package(Threads REQUIRED)

# Check for real-time library (needed for shared memory)
find_library(RT_LIB rt)
if(RT_LIB)
    message(STATUS "Found real-time library: ${RT_LIB}")
else()
    message(STATUS "Real-time library not found - using dummy implementation")
endif()

# Source files
set(MATLAB_GENERATED_SOURCES
    src/vehicle_dynamics.cpp
    src/pid_controller.cpp
)

set(APPLICATION_SOURCES  
    src/main.cpp
)

# Create main executable
add_executable(vehicle_dynamics_sim
    ${MATLAB_GENERATED_SOURCES}
    ${APPLICATION_SOURCES}
)

# Link libraries
target_link_libraries(vehicle_dynamics_sim 
    ${CMAKE_THREAD_LIBS_INIT}
)

# Link real-time library if available (for shared memory)
if(RT_LIB)
    target_link_libraries(vehicle_dynamics_sim ${RT_LIB})
endif()

# Add math library (needed for mathematical functions)
target_link_libraries(vehicle_dynamics_sim m)

# Compiler definitions (equivalent to MATLAB Coder defines)
target_compile_definitions(vehicle_dynamics_sim PRIVATE
    MATLAB_MEX_FILE=0
    MATLAB_GENERATED_CODE=1
)

# Optional: Create library for MATLAB-generated code (for reuse)
add_library(matlab_vehicle_models STATIC
    ${MATLAB_GENERATED_SOURCES}
)

target_link_libraries(matlab_vehicle_models m)

# Optional: Unit tests (if Google Test is available)
find_package(GTest QUIET)
if(GTEST_FOUND)
    message(STATUS "Google Test found - building unit tests")
    
    add_executable(vehicle_tests
        src/vehicle_dynamics.cpp
        src/pid_controller.cpp
        test/test_vehicle_dynamics.cpp
        test/test_pid_controller.cpp
    )
    
    target_link_libraries(vehicle_tests 
        ${GTEST_LIBRARIES}
        ${CMAKE_THREAD_LIBS_INIT}
        m
    )
    
    # Add test to CTest
    enable_testing()
    add_test(NAME VehicleUnitTests COMMAND vehicle_tests)
else()
    message(STATUS "Google Test not found - skipping unit tests")
endif()

# Installation rules (for packaging)
install(TARGETS vehicle_dynamics_sim
    RUNTIME DESTINATION bin
)

install(FILES 
    README.md
    matlab_params.json
    DESTINATION share/matlab-vehicle-dynamics
)

# Custom targets for development workflow

# MATLAB-style clean and build
add_custom_target(matlab_clean
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target clean
    COMMENT "Cleaning build directory (MATLAB equivalent: clear all)"
)

add_custom_target(matlab_build
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR}
    COMMENT "Building project (MATLAB equivalent: build model)"
)

# Run simulation (equivalent to MATLAB sim() command)
add_custom_target(matlab_sim
    COMMAND $<TARGET_FILE:vehicle_dynamics_sim>
    DEPENDS vehicle_dynamics_sim
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Running vehicle dynamics simulation (MATLAB equivalent: sim('model'))"
)

# Package for Kit Server deployment
add_custom_target(package_for_kitserver
    COMMAND ${CMAKE_COMMAND} -E tar czf matlab-vehicle-dynamics.tar.gz
            README.md
            CMakeLists.txt  
            matlab_params.json
            include/
            src/
            test_scenarios/
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Creating package for Kit Server deployment"
)

# Print build information
message(STATUS "")
message(STATUS "MATLAB Vehicle Dynamics Project Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "  Real-time library: ${RT_LIB}")
message(STATUS "")
message(STATUS "Available targets:")
message(STATUS "  vehicle_dynamics_sim  - Main simulation executable")
message(STATUS "  matlab_clean         - Clean build directory")  
message(STATUS "  matlab_build         - Build project")
message(STATUS "  matlab_sim           - Run simulation")
message(STATUS "  package_for_kitserver - Create Kit Server package")
message(STATUS "")

# Development notes
message(STATUS "Development Workflow:")
message(STATUS "  1. Build:    cmake --build . --target matlab_build")
message(STATUS "  2. Run:      cmake --build . --target matlab_sim")
message(STATUS "  3. Package:  cmake --build . --target package_for_kitserver")
message(STATUS "  4. Deploy:   Upload matlab-vehicle-dynamics.tar.gz to Kit Server")
message(STATUS "")
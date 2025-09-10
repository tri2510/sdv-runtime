cmake_minimum_required(VERSION 3.16)
project(VehicleSystemsMonitor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Debug flags for variable monitoring
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
set(CMAKE_BUILD_TYPE Debug)

# Include directories
include_directories(include)

# Source files - Only main.cpp with global variables
set(SOURCES
    src/main.cpp
)

# Create executable
add_executable(vehicle_systems ${SOURCES})

# Link pthread
find_package(Threads REQUIRED)
target_link_libraries(vehicle_systems Threads::Threads)
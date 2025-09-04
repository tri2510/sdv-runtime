cmake_minimum_required(VERSION 3.16)
project(fcw-advanced VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Debug build for monitoring
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DDEBUG")
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

# Find required packages
find_package(Threads REQUIRED)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
)

# Source files
set(SOURCES
    src/main.cpp
)

# Create executable
add_executable(fcw_system ${SOURCES})

# Link libraries
target_link_libraries(fcw_system 
    Threads::Threads
)

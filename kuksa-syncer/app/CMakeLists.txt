cmake_minimum_required(VERSION 3.16)
project(cmake_multidir_test VERSION 1.0.0)

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
    ${CMAKE_SOURCE_DIR}/engine
    ${CMAKE_SOURCE_DIR}/control
    ${CMAKE_SOURCE_DIR}/utils
)

# Source files from multiple directories
set(SOURCES
    main.cpp
    engine/engine_controller.cpp
    control/vehicle_control.cpp
    utils/data_logger.cpp
)

# Create executable
add_executable(multidir_system ${SOURCES})

# Link libraries
target_link_libraries(multidir_system 
    Threads::Threads
)
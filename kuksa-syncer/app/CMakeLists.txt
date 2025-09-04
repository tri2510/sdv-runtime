cmake_minimum_required(VERSION 3.10)
project(AutonomousVehicleSystem)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add debug symbols for monitoring
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DDEBUG")
set(CMAKE_BUILD_TYPE Debug)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/sensors
    ${CMAKE_CURRENT_SOURCE_DIR}/control
    ${CMAKE_CURRENT_SOURCE_DIR}/perception
    ${CMAKE_CURRENT_SOURCE_DIR}/planning
    ${CMAKE_CURRENT_SOURCE_DIR}/utils
)

# Source files
set(SOURCES
    main.cpp
    sensors/sensor_manager.cpp
    control/vehicle_controller.cpp
    perception/environment_analyzer.cpp
    planning/path_planner.cpp
    utils/logger.cpp
)

# Headers
set(HEADERS
    sensors/sensor_manager.h
    control/vehicle_controller.h
    perception/environment_analyzer.h
    planning/path_planner.h
    utils/logger.h
)

# Create executable
add_executable(autonomous_vehicle_system ${SOURCES} ${HEADERS})

# Link pthread for std::thread
find_package(Threads REQUIRED)
target_link_libraries(autonomous_vehicle_system Threads::Threads)

# Compiler-specific options
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(autonomous_vehicle_system PRIVATE -Wall -Wextra -pthread)
endif()
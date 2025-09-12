cmake_minimum_required(VERSION 3.10)
project(AutomotiveControlsSample VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "-Wall -Wextra -pthread")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Create executable
add_executable(automotive_controls main.cpp)

# Link pthread
target_link_libraries(automotive_controls pthread)

# Install
install(TARGETS automotive_controls
    RUNTIME DESTINATION bin
)
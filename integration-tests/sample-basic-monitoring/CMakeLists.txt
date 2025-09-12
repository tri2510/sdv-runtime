cmake_minimum_required(VERSION 3.10)
project(BasicMonitoringSample VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "-Wall -Wextra -pthread")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Create executable
add_executable(basic_monitoring main.cpp)

# Link pthread
target_link_libraries(basic_monitoring pthread)

# Install
install(TARGETS basic_monitoring
    RUNTIME DESTINATION bin
)
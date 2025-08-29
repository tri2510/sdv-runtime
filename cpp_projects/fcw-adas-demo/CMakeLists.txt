cmake_minimum_required(VERSION 3.16)
project(fcw_adas_demo)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(fcw_demo 
    src/main.cpp 
    src/vehicle_system.cpp
    src/environment.cpp
    src/fcw_controller.cpp
    src/v2x_communication.cpp
)

# Include directories
target_include_directories(fcw_demo PRIVATE include)

# Set compiler flags
if(MSVC)
    target_compile_options(fcw_demo PRIVATE /W4)
else()
    target_compile_options(fcw_demo PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Link pthread for threading support
target_link_libraries(fcw_demo pthread)
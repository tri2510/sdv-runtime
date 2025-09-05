cmake_minimum_required(VERSION 3.10)
project(ECUMultithreaded)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-g -O0 -pthread")

add_executable(ecu_system src/main.cpp)
target_link_libraries(ecu_system pthread)
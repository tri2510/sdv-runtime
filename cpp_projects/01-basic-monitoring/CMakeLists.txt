cmake_minimum_required(VERSION 3.10)
project(BasicMonitor)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-g -O0")

add_executable(basic_monitor src/main.cpp)
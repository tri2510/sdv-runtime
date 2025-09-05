cmake_minimum_required(VERSION 3.10)
project(ErrorHandling)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "-g -O0 -Wall")

add_executable(error_system src/main.cpp)
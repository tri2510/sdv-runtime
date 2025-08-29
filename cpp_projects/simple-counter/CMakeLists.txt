cmake_minimum_required(VERSION 3.16)
project(simple_counter)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(counter src/main.cpp)
target_include_directories(counter PRIVATE include)

if(MSVC)
    target_compile_options(counter PRIVATE /W4)
else()
    target_compile_options(counter PRIVATE -Wall -Wextra -Wpedantic)
endif()

target_link_libraries(counter pthread)
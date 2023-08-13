cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(log4cxx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} log4cxx)
target_compile_definitions(${PROJECT_NAME} PUBLIC _GNU_SOURCE)

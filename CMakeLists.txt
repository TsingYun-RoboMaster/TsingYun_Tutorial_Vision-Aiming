cmake_minimum_required(VERSION 3.16)
project(tsingyun_vision_aiming_homework LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(HW_BUILD_TESTS "Build homework C++ tests" ON)

if(HW_BUILD_TESTS)
  enable_testing()
endif()

add_subdirectory(tasks/task3-tracker)

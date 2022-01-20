cmake_minimum_required(VERSION 3.5)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test main.cpp)

target_link_libraries(test ${CONAN_LIBS})
cmake_minimum_required(VERSION 2.8.12)
project(PackageTest C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

if(APPLE)
    set(CMAKE_INSTALL_RPATH "@executable_path")
else()
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
endif()
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

add_executable(example simple_xy_wr.cpp)
target_link_libraries(example ${CONAN_LIBS} )

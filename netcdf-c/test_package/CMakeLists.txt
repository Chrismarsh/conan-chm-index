cmake_minimum_required(VERSION 3.10)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(SKIP_RPATHS TARGETS)

if(APPLE)
    set(CMAKE_INSTALL_RPATH "@executable_path")
else()
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
endif()
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

add_executable(example simple_xy_wr.c)
target_link_libraries(example ${CONAN_TARGETS})

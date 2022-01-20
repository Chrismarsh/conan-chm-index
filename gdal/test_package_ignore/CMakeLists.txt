project(helloworld)
cmake_minimum_required(VERSION 3.15)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# find_package(Iconv REQUIRED)
# find_package(gdal REQUIRED)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_executable(helloworld main.cpp)

message(STATUS "libs=${CONAN_LIBS}")
target_link_libraries(helloworld ${CONAN_LIBS}) # gdal::gdal ${CMAKE_DL_LIBS}) #https://bl.ocks.org/kwk/3595733
    
set_target_properties(helloworld
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    )
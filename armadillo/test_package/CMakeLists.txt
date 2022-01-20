project(PackageTest CXX)
cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)



if(APPLE)
    ## NOTE: On macOS, replace -lblas -llapack with -framework Accelerate
    set(CONAN_LIBS ${CONAN_LIBS} "-framework Accelerate")  # or "-framework accelerate" ?
    message(STATUS "Detected macOS. Added '-framework Accelerate' to compiler flags")
endif()

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)

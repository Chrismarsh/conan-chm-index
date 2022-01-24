project(TestFunc)
cmake_minimum_required(VERSION 3.18) #ensure we get the conan target functionality
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

#ensure we're embedding the rpath to the conan folder as this will be an "install" build which normally strips this
conan_basic_setup(KEEP_RPATHS)
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

add_executable(generate_tables_at_tol generate_tables_at_tol.cpp)
conan_target_link_libraries(generate_tables_at_tol)


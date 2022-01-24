project(TestFunc)
cmake_minimum_required(VERSION 2.8.12)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup(KEEP_RPATHS)

find_package(func REQUIRED)
message(STATUS ${func_INCLUDE_DIRS})
### Examples demonstrating the usage of FunC

## Computing maximum errors of all of the implementation types for varying step size
# add_executable(compute_max_err_of_tables compute_max_err_of_tables.cpp)
# target_link_libraries(compute_max_err_of_tables func::func)

# # add_executable(experiment experiment.cpp)
# # target_link_libraries(experiment func::func)

add_executable(generate_tables_at_tol generate_tables_at_tol.cpp)
target_link_libraries(generate_tables_at_tol func::func)

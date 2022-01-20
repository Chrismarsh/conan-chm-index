project(MyEigen3)
cmake_minimum_required(VERSION 2.8.12)

find_package(Eigen3 REQUIRED)

message(STATUS ${CONAN_INCLUDE_DIRS_EIGEN3})

add_executable(test main.cpp)
target_link_libraries(test Eigen3::Eigen3)

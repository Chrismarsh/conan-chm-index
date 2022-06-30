cmake_minimum_required(VERSION 2.8.12)
project(PackageTest C Fortran)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)


ADD_SUBDIRECTORY(F90)


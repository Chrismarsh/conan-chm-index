cmake_minimum_required(VERSION 2.8.12)
project(PackageTest)


# need 
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup(KEEP_RPATHS)

LIST(APPEND CMAKE_MODULE_PATH "${CONAN_ESMF_ROOT}/cmake")


message(STATUS ${CONAN_LIB_DIRS_ESMF})
file(GLOB outpath "${CONAN_LIB_DIRS_ESMF}/libO/*")

message(STATUS ${outpath} )

set( ESMFMKFILE "${outpath}/esmf.mk")


find_package(ESMF REQUIRED)



add_executable(example main.c)
target_link_libraries(example ESMF)

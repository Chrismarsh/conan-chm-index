from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os 

class NetcdfcConan(ConanFile):
    name = "netcdf-cxx"
    license = "MIT"
    url = "https://github.com/Chmarshris/conan-netcdf-cxx"
    description = "Unidata network Common Data Form cxx"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
                "fPIC": [True, False]}
    default_options = { "shared":True, 
                        "fPIC":True}

    generators = "cmake"

    source_subfolder = "netcdf-cxx4"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename("netcdf-cxx4-{0}".format(self.version), self.source_subfolder)

        if tools.os_info.is_macos:
            tools.replace_in_file("netcdf-cxx4/CMakeLists.txt", "PROJECT(NCXX C CXX)",
                                  '''PROJECT(NCXX C CXX)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup(KEEP_RPATHS)''')
        else:
            tools.replace_in_file("netcdf-cxx4/CMakeLists.txt", "PROJECT(NCXX C CXX)",
                                  '''PROJECT(NCXX C CXX)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup()''')

    def requirements(self):
        self.requires("netcdf-c/[>=4.6]@CHM/stable")


    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NCXX_ENABLE_TESTS"] = False
        cmake.definitions["ENABLE_CONVERSION_WARNINGS"] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"
        cmake.configure(source_folder="netcdf-cxx4")
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

        # if tools.os_info.is_linux:
        #     with tools.chdir(self.package_folder):
        #         cmd = "patchelf --remove-rpath lib/libnetcdf-cxx4.so"
        #         os.system(cmd)

    def package_info(self):
        self.cpp_info.libs = ["netcdf-cxx4"]

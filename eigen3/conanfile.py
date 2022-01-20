import os
from conans import ConanFile, CMake, tools
from conans.tools import download, unzip
from glob import glob
class EigenConan(ConanFile):
    name = "eigen3"
    description = "Eigen is a C++ template library for linear algebra"
    generators = "cmake"
    settings = None
    url="http://github.com/bilke/conan-eigen3"
    license="http://eigen.tuxfamily.org/index.php?title=Main_Page#License"


    def source(self):

        tools.get(**self.conan_data["sources"][self.version])
        os.rename("eigen-{}".format(self.version), 'eigen')


    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder="eigen")
        return cmake

    def build(self):

        cmake = self.configure_cmake()
        cmake.build()


    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.name = "Eigen3"
        self.cpp_info.includedirs = ['include/eigen3', 'include/unsupported']

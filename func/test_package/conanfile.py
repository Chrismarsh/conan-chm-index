import os
from conans import ConanFile, CMake


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    settings = "os", "compiler", "build_type", "arch"
    
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(".%sgenerate_tables_at_tol" %os.sep)

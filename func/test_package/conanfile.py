import os
from conans import ConanFile, CMake


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    settings = "os", "compiler", "build_type", "arch"
    
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("./bin/generate_tables_at_tol")

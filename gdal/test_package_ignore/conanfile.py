
import os
from conans import ConanFile, CMake

class GdalTestConan(ConanFile):
    """ GDAL Conan package test """

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def requirements(self):
        self.requires("zlib/[>=1.2]")
        self.requires("proj/[>=4 <5]@CHM/stable")
        self.requires("libiconv/1.15")


        self.requires("libcurl/[>=7.70.0]")
      
        self.requires("netcdf-c/4.6.2@CHM/stable")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(' ls -l')
        self.run(' ldd bin/helloworld')

        self.run("%s %s" % (os.sep.join([".", "bin", "helloworld"]), "conan"))

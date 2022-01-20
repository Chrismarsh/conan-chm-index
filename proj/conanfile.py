import os
from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, patch

class ProjConan(ConanFile):
    name = "proj"
    description = """proj is a library which converts geographic longitude and
                     latitude coordinates into cartesian coordinates."""

    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
    }
    default_options = {
        "shared":True,
        "fPIC": True
        }

    url="http://github.com/bilke/conan-proj"
    license="https://github.com/OSGeo/proj.4"

    def config(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == 'Visual Studio':
            self.options.remove("fPIC")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename('proj-{0}'.format(self.version), 'proj')

    
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_CCT"] = "OFF"
        cmake.definitions["BUILD_CS2CS"] = "OFF"
        cmake.definitions["BUILD_GEOD"] = "OFF"
        cmake.definitions["BUILD_GIE"] = "OFF"
        cmake.definitions["BUILD_PROJ"] = "OFF"
        cmake.definitions["BUILD_PROJSYNC"] = "OFF"
        cmake.definitions["BUILD_PROJINFO"] = "OFF"

        cmake.definitions["BUILD_TESTING"] = "OFF"

        cmake.definitions["CMAKE_BUILD_TYPE"] = "Release"

        if self.options.shared == False:
            cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"

        cmake.configure(source_folder='proj', build_folder="build")

        return cmake

    def build(self):

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()


    def package_info(self):
     
        self.cpp_info.libs = ["proj"]
        
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')

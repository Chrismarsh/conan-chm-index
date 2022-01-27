from __future__ import print_function
import os
from fnmatch import fnmatch
from conans.model.version import Version
from conans import ConanFile, AutoToolsBuildEnvironment, tools, RunEnvironment
from conans.tools import download, unzip
from six import StringIO

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class GdalConan(ConanFile):
    """ Conan package for GDAL """

    name = "gdal"
    description = "GDAL - Geospatial Data Abstraction Library"
    url = "http://www.gdal.org/"
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    
    options = {"shared": [True, False], 
               "libcurl": [True, False],
               "netcdf": [True, False] }
    
    default_options = {"shared": True,
                         "libcurl": True, 
                         "netcdf": True}

    
    exports_sources = ['patches/*']
    exports = ["LICENSE.md"]

    _folder = "gdal"
    _env_build = None


    def requirements(self):
        self.requires("zlib/[>=1.2]")

        v = Version(self.version)

        if v < "3":
            self.requires("proj/[>=4 <5]@CHM/stable")
        else:
            self.requires("proj/[>=7]@CHM/stable")

        self.requires("libiconv/[>=1.15]")

        if self.options.netcdf:
            self.requires("netcdf-c/[>=4.6]@CHM/stable")

        # if not self.options.shared:
        #     self.requires("sqlite3/3.27.1@bincrafters/stable", private=False, override=False)


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("gdal-{}".format(self.version), self._folder )
  
 
    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["CMAKE_BUILD_TYPE"] = "Release"

        cmake.definitions["GDAL_USE_CURL"] = self.options.libcurl
        if self.options.libcurl:
            curl_config = StringIO()
            self.run('which curl-config', output = curl_config)
            curl_config=curl_config.getvalue().rstrip()

            cmake.definitions["CURL_INCLUDE_DIR"] = curl_config

        cmake.definitions["GDAL_USE_LIBGEOTIFF_INTERNAL"]=True
        cmake.definitions["GDAL_USE_LIBJSONC_INTERNAL"]=True
        cmake.definitions["GDAL_USE_LIBTIFF_INTERNAL"]=True
        cmake.definitions["GDAL_USE_ZLIB_INTERNAL"]=True
        cmake.definitions["GDAL_USE_LIBJPEG_INTERNAL"]=True
        cmake.definitions["GDAL_USE_LIBPNG_INTERNAL"]=True

        cmake.definitions["PROJ_INCLUDE_DIR"]=self.deps_cpp_info["proj"].rootpath+"/include/"

        cmake.definitions["BUILD_PYTHON_BINDINGS"]=False

        cmake.definitions["GDAL_USE_NETCDF"]=elf.options.netcdf
        if self.options.netcdf:
            cmake.definitions["NETCDF_INCLUDE_DIR"] = self.deps_cpp_info["netcdf-c"].rootpath+"/include/"


        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = '@rpath' #self.package_folder+'/lib'



        cmake.configure(source_folder=self._folder)
        return cmake


    def build(self):

       
        cmake = self.configure_cmake()
        cmake.build()



    def package(self):
        cmake = self.configure_cmake()
        cmake.install()        
        # strip any hard coded install_name from the dylibs to simplify downstream use
        # if tools.os_info.is_macos:
        #     for path, subdirs, names in os.walk(os.path.join(self.package_folder, 'lib')):
        #         for name in names:

        #             if fnmatch(name, '*.dylib*'):
        #                 so_file = os.path.join(path, name)

        #                 cmd = "install_name_tool -id @rpath/{0} {1}".format(name, so_file)
        #                 os.system(cmd)


    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["gdal"]

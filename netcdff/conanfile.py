from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os 
from fnmatch import fnmatch

class Netcdff(ConanFile):
    name = "netcdff"
    license = "MIT"
    url = "https://github.com/Unidata/netcdf-fortran"
    description = "Unidata network Common Data Form fortran"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
                "fPIC": [True, False]}
    default_options = { "shared":True, 
                        "fPIC":True,
                        "*:shared":True}

    generators = "cmake"

    source_subfolder = "netcdf-fortran"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename("netcdf-fortran-{0}".format(self.version), self.source_subfolder)

        if tools.os_info.is_macos:
            tools.replace_in_file("netcdf-fortran/CMakeLists.txt", "PROJECT (NC4F Fortran C)",
                                  '''PROJECT (NC4F Fortran C)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup(KEEP_RPATHS)''')
        else:
            tools.replace_in_file("netcdf-fortran/CMakeLists.txt", "PROJECT (NC4F Fortran C)",
                                  '''PROJECT (NC4F Fortran C)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup()''')


    def requirements(self):
        self.requires("netcdf/4.7.4")


    def configure_cmake(self):
        cmake = CMake(self)
        # cmake.definitions["NCXX_ENABLE_TESTS"] = False
        # cmake.definitions["ENABLE_CONVERSION_WARNINGS"] = False
        # cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_RPATH"] = "@executable_path"
        else:
            #this seems to be ignored??
            cmake.definitions["CMAKE_INSTALL_RPATH"] = "\$ORIGIN"

        cmake.definitions["CMAKE_BUILD_WITH_INSTALL_RPATH"] = True

        # ensure we don't set the install_name to be the fully qualified path otherwise
        # it won't be relocatable
        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = '@rpath' 

        cmake.configure(source_folder=self.source_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

        for path, subdirs, names in os.walk(os.path.join(self.package_folder, 'lib')):
            for name in names:

                if fnmatch(name, '*.dylib*'):
                    so_file = os.path.join(path, name)

                    cmd = "install_name_tool -add_rpath @executable_path {0}".format(so_file)
                    os.system(cmd)

                if fnmatch(name, '*.so*'):
                    so_file = os.path.join(path, name)

                    cmd = "patchelf --set-rpath \$ORIGIN {0}".format(so_file)
                    os.system(cmd)


    def package_info(self):
        self.cpp_info.libs = ["netcdff"]

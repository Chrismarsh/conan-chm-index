from conans import ConanFile, CMake, tools
import os
import glob

class WindNinjaConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
   

    name = "windninja"
    license = "https://github.com/firelab/windninja/blob/master/LICENSE"
    author = "firelab"
    url = "https://github.com/firelab/windninja"
    description = "WindNinja is a diagnostic wind model developed for use in wildland fire modeling."
    generators = "cmake_find_package"

    options = {
            "openmp":[True, False]
            }

    default_options = {
            "openmp":True, 
            "*:shared": True,
            "netcdf:dap": False,
            "gdal:with_curl": True,
            "gdal:with_netcdf": True,
            "proj:with_curl": False
            }

    # build_policy = 'always' #as we track master, always build

    _source_folder = 'windninja'

    def source(self):

        tools.get(**self.conan_data["sources"][self.version])
        os.rename("windninja-{}".format(self.version), self._source_folder)


        # git = tools.Git()
        # git.clone("https://github.com/firelab/windninja.git") 
        # git.checkout("3.5.3")

        # Needed for Find OMP on MacOS
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "cmake_minimum_required(VERSION 2.6)",  "cmake_minimum_required(VERSION 3.16)")

        #ensure we use a C++11 compiler
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "project(WindNinja)", ''' project(WindNinja) 
                                                                          set(CMAKE_CXX_STANDARD 14)
                                                                          set(CMAKE_CXX_STANDARD_REQUIRED ON)
                                                                          set(CMAKE_CXX_EXTENSIONS OFF)
                                                                          add_compile_options(-w -Wno-narrowing)''')
        if tools.os_info.is_macos and self.options.openmp:
            print('!!! Macos and OMP not supported, setting openmp=false')
            self.options.openmp = False

        #Absolutely ensure we find it
        if(self.options.openmp):
            tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "FIND_PACKAGE(OpenMP)", "find_package(OpenMP REQUIRED)")

        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "include(FindBoost)", " ")
        
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "find_package(GDAL REQUIRED)", " ")
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "include(FindGDAL)", "find_package(GDAL REQUIRED)")

        #changes to support the conan finds
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "find_package(NetCDF REQUIRED)", ' ')
        tools.replace_in_file(os.path.join(self._source_folder,"CMakeLists.txt"), "include(FindNetCDF)", '''find_package(netcdf REQUIRED)''')

        target_string = ' GDAL::GDAL '
        if(self.options.openmp):
            target_string += ' OpenMP::OpenMP_CXX '

        
        tools.replace_in_file(os.path.join(self._source_folder,"autotest/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/solar_grid/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/cli/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/stl_converter/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/fetch_station/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/ninja/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/fetch_dem/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/gui/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        tools.replace_in_file(os.path.join(self._source_folder,"src/output_converter/CMakeLists.txt"),
            "set(LINK_LIBS",
            f"set(LINK_LIBS {target_string}")
        


    def requirements(self):
        self.requires("boost/[>=1.75.0]@CHM/stable" )
        self.requires("proj/[>=7.0]" )

        self.requires("libdeflate/1.12",override=True)
        self.requires("gdal/[>=3]" )
        self.requires("netcdf/4.7.4", override=True)
        

    def _configure_cmake(self):
        cmake = CMake(self)

      
        cmake.definitions["NINJA_QTGUI"] = False
        cmake.definitions["CMAKE_MODULE_PATH"] = self.build_folder # for the conan finds
        cmake.definitions["NINJAFOAM"] = False
        # cmake.definitions["NINJA_SCM_REVISION"] = self.version

        cmake.definitions["OPENMP_SUPPORT"]=self.options.openmp

        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_RPATH"] = "@executable_path/../lib"
        else:
            cmake.definitions["CMAKE_INSTALL_RPATH"] = "\$ORIGIN/../lib"

        cmake.definitions["CMAKE_BUILD_WITH_INSTALL_RPATH"] = True

        # ensure we don't set the libninja.dylib's install_name to be the fully qualified path otherwise
        # it won't be relocatable
        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = '@rpath' 

        cmake.verbose = True

        cmake.configure(source_folder=self._source_folder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def deploy(self):
        self.copy("*")  # copy from current package
        self.copy_deps("*.so*") # copy from dependencies
        self.copy_deps("*.dylib*") # copy from dependencies

    def imports(self):
        self.copy("*.so*", "lib", "lib")  # From bin to bin
        self.copy("*.dylib*", "lib", "lib")  # From lib to bin

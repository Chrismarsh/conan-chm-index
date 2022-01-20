import os
import re

from fnmatch import fnmatch
from conans import ConanFile, CMake, tools

class VTKConan(ConanFile):
    name = "vtk"
    description = "Visualization Toolkit by Kitware"
    url = "http://github.com/bilke/conan-vtk"
    license = "MIT"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    exports = ["LICENSE.md"]
    source_subfolder = "source_subfolder"
    options = {"shared": [True, False],
               "VTK_Group_Imaging": [True, False], #Request building Imaging modules
               "VTK_Group_MPI": [True, False], #Request building MPI modules
               "VTK_Group_Qt": [True, False],#Request building Qt modules
               "VTK_Group_Rendering": [True, False], #Request building Rendering modules
               "VTK_Group_StandAlone": [True, False], #Request building of all stand alone modules (no external dependencies required)
               "VTK_Group_Tk": [True, False], #Request building Tk modules
               "VTK_Group_Views": [True, False], #Request building Views modules
               "VTK_Group_Web": [True, False], #Request building Web modules
               "fPIC": [True, False]
               }
    default_options = ("shared=True", "fPIC=True",
                       "VTK_Group_Imaging=False",
                       "VTK_Group_MPI=False",
                       "VTK_Group_Qt=False",
                       "VTK_Group_Rendering=False",
                       "VTK_Group_StandAlone=True",
                       "VTK_Group_Tk=False",
                       "VTK_Group_Views=False",
                       "VTK_Group_Web=False"
       )

    short_paths = True



    def source(self):
       tools.get(**self.conan_data["sources"][self.version])
       os.rename("VTK-{}".format(self.version), self.source_subfolder)

    def requirements(self):
        if self.options.VTK_Group_Qt:
            self.requires("qt/5.12.4@bincrafters/stable")
            self.options["qt"]=True
            self.options["qt"].shared = True
            if tools.os_info.is_linux:
                self.options["qt"].qtx11extras = True

    def _system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ':i386'
            elif self.settings.arch == "x86_64":
                return ':amd64'

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return '.i686'
            elif self.settings.arch == 'x86_64':
                return '.x86_64'
        return ""

    def build_requirements(self):
        pack_names = None
        if not self.options.VTK_Group_Rendering and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                pack_names = [
                    "freeglut3-dev",
                    "mesa-common-dev",
                    "mesa-utils-extra",
                    "libgl1-mesa-dev",
                    "libglapi-mesa",
                    "libsm-dev",
                    "libx11-dev",
                    "libxext-dev",
                    "libxt-dev",
                    "libglu1-mesa-dev"]

        if pack_names:
            installer = tools.SystemPackageTool()
            for item in pack_names:
                installer.install(item + self._system_package_architecture())

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        if self.settings.os == 'Macos':
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = "@rpath"


        cmake.definitions["VTK_Group_Imaging"]=self.options.VTK_Group_Imaging
        cmake.definitions["VTK_Group_MPI"]=self.options.VTK_Group_MPI
        cmake.definitions["VTK_Group_Qt"]=self.options.VTK_Group_Qt
        cmake.definitions["VTK_Group_Rendering"]=self.options.VTK_Group_Rendering
        cmake.definitions["VTK_Group_StandAlone"]=self.options.VTK_Group_StandAlone  # This is required
        cmake.definitions["VTK_Group_Tk"]=self.options.VTK_Group_Tk
        cmake.definitions["VTK_Group_Views"]=self.options.VTK_Group_Views
        cmake.definitions["VTK_Group_Web"]=self.options.VTK_Group_Web


        if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
            cmake.definitions["CMAKE_DEBUG_POSTFIX"] = "_d"

        if self.settings.os == 'Macos':
            self.env['DYLD_LIBRARY_PATH'] = os.path.join(self.build_folder, 'lib')
            self.output.info("cmake build: %s" % self.build_folder)

            if self.settings.compiler == 'apple-clang' and tools.Version(self.settings.compiler.version).major >= '12':
                self.output.info("apple-clang v12 detected")
                cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wno-implicit-function-declaration"
                cmake.definitions["CMAKE_C_FLAGS"] = "-Wno-implicit-function-declaration"

        cmake.configure(source_folder=self.source_folder+'/'+self.source_subfolder,build_folder='build')

        if self.settings.os == 'Macos':
            # run_environment does not work here because it appends path just from
            # requirements, not from this package itself
            # https://docs.conan.io/en/latest/reference/build_helpers/run_environment.html#runenvironment
            lib_path = os.path.join(self.build_folder, 'lib')
            self.run('DYLD_LIBRARY_PATH={0} cmake --build build {1} -j'.format(lib_path, cmake.build_config))
        else:
            cmake.build()
        cmake.install()

    # From https://git.ircad.fr/conan/conan-vtk/blob/stable/8.2.0-r1/conanfile.py
    def cmake_fix_path(self, file_path, package_name):
        try:
            tools.replace_in_file(
                file_path,
                self.deps_cpp_info[package_name].rootpath.replace('\\', '/'),
                "${CONAN_" + package_name.upper() + "_ROOT}",
                strict=False
            )
        except:
            self.output.info("Ignoring {0}...".format(package_name))

    def cmake_fix_macos_sdk_path(self, file_path):
        # Read in the file
        with open(file_path, 'r') as file:
            file_data = file.read()

        if file_data:
            # Replace the target string
            file_data = re.sub(
                # Match sdk path
                r';/Applications/Xcode\.app/Contents/Developer/Platforms/MacOSX\.platform/Developer/SDKs/MacOSX\d\d\.\d\d\.sdk/usr/include',
                '',
                file_data,
                re.M
            )

            # Write the file out again
            with open(file_path, 'w') as file:
                file.write(file_data)

    def package(self):
        for path, subdirs, names in os.walk(os.path.join(self.package_folder, 'lib', 'cmake')):
            for name in names:
                if fnmatch(name, '*.cmake'):
                    cmake_file = os.path.join(path, name)

                    # if self.options.external_tiff:
                        # self.cmake_fix_path(cmake_file, "libtiff")
                    # if self.options.external_zlib:
                        # self.cmake_fix_path(cmake_file, "zlib")

                    if tools.os_info.is_macos:
                        self.cmake_fix_macos_sdk_path(cmake_file)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        version_split = self.version.split('.')
        short_version = "%s.%s" % (version_split[0], version_split[1])

        self.cpp_info.includedirs = [
            "include/vtk-%s" % short_version,
            "include/vtk-%s/vtknetcdf/include" % short_version,
            "include/vtk-%s/vtknetcdfcpp" % short_version
        ]

        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')

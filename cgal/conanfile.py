from conans import ConanFile, CMake, tools
import os

class CgalConan(ConanFile):
    name = "cgal"
    license = "GPL/LGPL"
    url = "https://github.com/Chrismarsh/conan-cgal/"
    description = "Computational Geometry Algorithms Library"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"
    options = {
                "with_gmp": [True, False],
                }                
    default_options = {
     "with_gmp": True, 
     }

    generators = "cmake_find_package"
  
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cgal-{}".format(self.version), 'cgal')

    def requirements(self):
        self.requires("boost/[>=1.70]@CHM/stable")
        self.requires("mpfr/[>=4.1.0]")
        # if self.options.with_gmp:
            # self.requires("gmp/[>=5.0]@CHM/stable")
            # self.requires("mpfr/[>=3.0]@CHM/stable")

    def configure_cmake(self):
        with tools.environment_append(self.cmake_env_vars):
            cmake = CMake(self)
            cmake.definitions["BOOST_ROOT"] = self.deps_cpp_info["boost"].rootpath
            cmake.definitions["BOOST_LIBRARYDIR"] = self.deps_cpp_info["boost"].rootpath
            cmake.definitions["CGAL_DISABLE_GMP"] = "OFF" if self.options.with_gmp else "ON"

            cmake.configure(source_folder="cgal")
            return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.info.header_only()

    @property
    def cmake_env_vars(self):
        env = {}
        if self.options.with_gmp:
            env["GMP_DIR"] = self.deps_cpp_info["gmp"].rootpath
            env["MPFR_DIR"] = self.deps_cpp_info["mpfr"].rootpath
        return env



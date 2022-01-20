# from conans.errors import ConanException
import os
import shutil

from conans import CMake, ConanFile, tools


class ArmadilloConan(ConanFile):
    name = "armadillo"
    license = "Apache License 2.0"
    url = "https://github.com/Chrismarsh/conan-armadillo"
    description = "C++ library for linear algebra & scientific computing"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # If true the recipe will use blas and lapack from system
        "use_system_blas": [True, False],
        "link_with_mkl": [True, False],
        "with_lapack":[True,False],
        "with_blas":[True,False],
        "use_wrapper":[True,False],
        "shared":[True,False]}
    default_options = ("use_system_blas=True",
                       "link_with_mkl=False",
                       # "use_extern_cxx11_rng=False",
                       "with_lapack=False",
                       "with_blas=False",
                       "use_wrapper=False",
                       "shared=True")
    generators = "cmake_find_package"

    def requirements(self):
        if self.options.with_blas and not self.options.use_system_blas:
            self.requires("openblas/[>=0.3.5]@conan/stable")
            self.requires("lapack/3.7.1@conan/stable")

    def configure_cmake(self):
        cmake = CMake(self)

        if self.options.link_with_mkl and not self.options.use_system_blas:
             raise Exception("Link with MKL options can only be True when use_system_blas is also True")

        cmake.definitions["ARMA_USE_WRAPPER"] = self.options.use_wrapper
        cmake.definitions["ARMA_NO_DEBUG"] = True
        cmake.definitions["DETECT_HDF5"] = False
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.configure(source_folder="armadillo")
        return cmake


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        os.rename("armadillo-{}".format(self.version), 'armadillo')

        arma_config_file = os.path.join("armadillo", "include", "armadillo_bits", "config.hpp")
        CMakeLists_path = os.path.join("armadillo", "CMakeLists.txt")

        if not self.options.with_lapack:
            tools.replace_in_file(file_path=arma_config_file,
                               search="#define ARMA_USE_LAPACK",
                               replace="//#define ARMA_USE_LAPACK")

        if not self.options.with_blas:
            tools.replace_in_file(file_path=arma_config_file,
                               search="#define ARMA_USE_BLAS",
                               replace="//#define ARMA_USE_BLAS")

        if not self.options.link_with_mkl:
            tools.replace_in_file(file_path=CMakeLists_path,
                               search="include(ARMA_FindMKL)",
                               replace="""#include(ARMA_FindMKL)
                                        set(MKL_FOUND "NO")""")


    def build(self):

        cmake = self.configure_cmake()
        cmake.build()


    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["armadillo"]
        return

from conans import ConanFile, CMake, tools
import os

class TrilinosConan(ConanFile):
    name = "trilinos"
    description = "The Trilinos scientific computing software stack"
    topics = ("conan", "trilinos", "scientific computing")
    url = "https://github.com/kevinrichardgreen/conan-trilinos"
    homepage = "https://trilinos.github.io/"
    license = "BSD/multi" # TODO: appropriate license tag... packages in Trilinos are variable

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_all_packages": [True, False],
        "with_belos": [True, False],
        "with_ifpack2": [True, False],
        "with_openmp": [True, False],
        "with_mpi": [True, False],
        "with_mkl": [True, False],
        "with_openblas": [True,False],
        "debug":[True,False],

        "mkl_root": "ANY",
        "blas_root":"ANY"
    }
    default_options = {
        "shared": True,
        "with_all_packages": False,
        "with_belos": True,         # iterative solvers
        "with_ifpack2": True,       # preconditioners
        "with_openmp": True,
        "with_mpi": False,
        "with_mkl": False,
        "with_openblas":False,
        "debug":False,
        "mkl_root": None,
        "blas_root": None
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    _use_conan_openblas = False

    def requirements(self):
        self.requires("zlib/[>=1.2]")

        # we have not specified anything, use conan openblas
        if not self.options.blas_root and not self.options.mkl_root:
            self.requires("openblas/[>=0.3.17]")
            self._use_conan_openblas = True





    def config_options(self):
        if self.settings.os not in ["Macos", "Linux"]:
            raise Exception("Unsupported System. This package currently only support Linux/Macos")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])


        if str(self.version) == 'chm':
            extracted_dir = "Trilinos-cherrypick_kokkos_for_chm"
        elif str(self.version) == 'master':
            extracted_dir = "Trilinos-master"
        elif str(self.version) == 'develop':
            extracted_dir = "Trilinos-develop"
        else:
            extracted_dir = "Trilinos-trilinos-release-%s" % self.version.replace(".","-")

        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self._use_conan_openblas:
            self.options['openblas'].build_lapack = True
            self.options['openblas'].shared = True

    def _configure_cmake(self):
        cmake = CMake(self)

        if tools.os_info.is_macos and self.options.with_openmp and str(self.version) is not "chm": 
            print('!!! Macos and OMP not supported, setting with_openmp=false')
            self.options.with_openmp = False

        if self._use_conan_openblas:
            self.options.with_openblas = True
            self.options.blas_root = self.deps_cpp_info["openblas"].rootpath + '/lib/'


        if self.options.with_mkl:

            if self.options.mkl_root is None:
                self.output.error('If building against mkl, ensure -o mkl_root is set. For example, -o trilinos:mkl_root=/opt/imkl/2019.3.199/mkl/lib/intel64" ')
                raise Exception('mkl_root not set')

            # as per https://github.com/trilinos/Trilinos/blob/master/cmake/TPLs/FindTPLMKL.cmake#L116
            cmake.definitions["BLAS_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root 
            cmake.definitions["BLAS_LIBRARY_NAMES:STRING"] ="mkl_rt" 

            cmake.definitions["LAPACK_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root
            cmake.definitions["LAPACK_LIBRARY_NAMES:STRING"] ="mkl_rt" 
            
            cmake.definitions["TPL_ENABLE_MKL:BOOL"] ="ON" 
            cmake.definitions["MKL_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root
            cmake.definitions["MKL_LIBRARY_NAMES:STRING"] ="mkl_rt" 
            cmake.definitions["MKL_INCLUDE_DIRS:FILEPATH"] =self.options.mkl_root+"/../../include" 

        if self.options.with_openblas:
            cmake.definitions["BLAS_LIBRARY_NAMES:STRING"] ="openblas" 
            cmake.definitions["LAPACK_LIBRARY_NAMES:STRING"] ="openblas" 

        
        if self.options.blas_root:
            cmake.definitions["BLAS_LIBRARY_DIRS:FILEPATH"] = self.options.blas_root
            cmake.definitions["LAPACK_LIBRARY_DIRS:FILEPATH"] = self.options.blas_root

        if self.settings.compiler == 'apple-clang' and tools.Version(self.settings.compiler.version).major >= '12':
            self.output.info("apple-clang v12 detected")
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wno-implicit-function-declaration"
            cmake.definitions["CMAKE_C_FLAGS"] = "-Wno-implicit-function-declaration"


        cmake.definitions["Trilinos_ENABLE_Fortran"] = False
        cmake.definitions["Trilinos_ENABLE_TESTS"] = False

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["Trilinos_ENABLE_ALL_PACKAGES"] = self.options.with_all_packages

        cmake.definitions["Trilinos_ENABLE_Belos"] = self.options.with_belos
        cmake.definitions["Trilinos_ENABLE_Ifpack2"] = self.options.with_ifpack2

        if self.options['debug']:
            self.options.with_openmp = False
            self.output.warn("Debug mode enable, disabling OMP for thread safety")

        cmake.definitions["Trilinos_ENABLE_OpenMP"] = self.options.with_openmp
        cmake.definitions["Trilinos_ENABLE_THREAD_SAFE"] = self.options.with_openmp

        # setting the ordinal only works 
        if not tools.os_info.is_macos:
            cmake.definitions["Tpetra_INST_INT_INT"] = True


        if tools.os_info.is_macos and str(self.version) is "master":
            cmake.definitions["Tpetra_INST_INT_INT"] = True
        else:
            self.output.warn("On macos, setting global ordinal requires master. Defaulting to GO=long long")
            
        CMAKE_CXX_FLAGS = '' 
        if self.options['debug']:
            cmake.definitions["Teuchos_ENABLE_DEBUG"]=True
            cmake.definitions["Teuchos_ENABLE_ABC"]=True
            cmake.definitions["Tpetra_ENABLE_DEBUG"]=True
            cmake.definitions['CMAKE_BUILD_TYPE']='DEBUG'
            CMAKE_CXX_FLAGS += " -g3 -ggdb "

        cmake.definitions["TPL_ENABLE_MPI"] = self.options.with_mpi

        CMAKE_CXX_FLAGS+=" -Wno-unused-result -Wno-deprecated-declarations "

        cmake.definitions["CMAKE_CXX_FLAGS"] = CMAKE_CXX_FLAGS

        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

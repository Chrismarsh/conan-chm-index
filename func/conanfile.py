from conans import ConanFile, CMake, tools


class FuncConan(ConanFile):
    name = "func"
    license = "GPL/LGPL"
    url = "https://github.com/uofs-simlab/func"
    description = "(Function Comparator) is a C++ tool for quickly profiling the performance of various different abstracted implementations of mathematical function evaluations"
    # no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    generators = "cmake_find_package"

    _source_folder='func'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("func-master", self._folder )

        tools.replace_in_file("src/CMakeLists.txt", "target_link_libraries(func PUBLIC ","target_link_libraries(func PUBLIC Boost::Boost")


    def requirements(self):
        self.requires("boost/[>=1.75.0]@CHM/stable")


    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_QUADMATH"] = False

        cmake.configure()
        
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)




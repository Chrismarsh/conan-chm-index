from conans import ConanFile, CMake
import os

class SnappyTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    # def configure(self):
        # self.options["gperftools"].heapprof = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.dylib", "bin", "lib")

    def test(self):
        os.chdir("bin")
        self.run(".%stest" % os.sep)

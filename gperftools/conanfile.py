from conans import ConanFile,AutoToolsBuildEnvironment,tools
from conans.tools import download, unzip
import os

class GperfToolsConan(ConanFile):
    name = "gperftools"
    description = "The fastest malloc we have seen."

    options = { 
                "shared":[True, False], 
                "cpuprof":[True, False], 
                "heapprof":[True, False], 
                "heapchecker":[True, False]
                }
    default_options = {
                 "shared":True,
                 "cpuprof":False,
                 "heapprof":False,
                 "heapchecker":False
                 }
    url = "https://github.com/gperftools/gperftools"
    license = "https://github.com/gperftools/gperftools/blob/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"

    _source_folder = 'gperftools'

    def requirements(self):

        if self.settings.os == 'Macos':
            self.options.cpuprof = self.options.heapprof = self.options.heapchecker = False
            print("!!!!!    libunwind is not supported on MacOS, disabling all associated functionality.    !!!!!")

        if self.options.cpuprof or self.options.heapprof or self.options.heapchecker:
            self.requires("libunwind/[>=1.3]@bincrafters/stable")

    def source(self):
         tools.get(**self.conan_data["sources"][self.version])
         os.rename("gperftools-{}".format(self.version), 'gperftools')

         tools.replace_in_file("%s/configure" % (self._source_folder), r"-install_name \$rpath/", "-install_name @rpath/" )
         self.run("chmod +x ./%s/configure" % (self._source_folder))
         self.run("chmod +x ./%s/install-sh" % (self._source_folder))

    def build(self):
        with tools.chdir(self._source_folder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure( 
                                 args = [ "" if self.options.cpuprof or self.options.heapprof or self.options.heapchecker else "--enable-minimal",
                                         "--enable-shared" if self.options.shared else "--disable-shared",
                                         "--enable-static" if not self.options.shared else "--disable-static",
                                         "--enable-cpu-profiler" if self.options.cpuprof else "--disable-cpu-profiler",
                                         "--enable-heap-profiler" if self.options.heapprof else "--disable-heap-profiler",
                                         "--enable-heap-checker" if self.options.heapchecker else "--disable-heap-checker" ])
            env_build.make()
    

    def package_info(self):
        if self.options.cpuprof or self.options.heapprof or self.options.heapchecker:
            self.cpp_info.libs = ["tcmalloc"]
        else:
            self.cpp_info.libs = ["tcmalloc_minimal"]


    def package(self):
        with tools.chdir(self._source_folder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.install()





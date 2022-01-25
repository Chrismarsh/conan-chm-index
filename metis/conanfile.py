from conans import ConanFile, AutoToolsBuildEnvironment, RunEnvironment, tools
import os
from conans.tools import download, unzip

class MetisConan(ConanFile):
    name = "metis"
    description = "METIS is a set of serial programs for partitioning graphs, partitioning finite element meshes, and producing fill reducing orderings for sparse matrices. The algorithms implemented in METIS are based on the multilevel recursive-bisection, multilevel k-way, and multi-constraint partitioning schemes developed in our lab.  "
    generators = "cmake"
    license = "http://glaros.dtc.umn.edu/gkhome/metis/metis/download"
    url="http://glaros.dtc.umn.edu/gkhome/metis/metis/download"
    settings = "os", "arch", "compiler", "build_type"

    options = { 
        "shared" :[True, False]
    }

    default_options = { 
        "shared": True
        }

    _source_subfolder = 'metis'


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("metis-{}".format(self.version), self._source_subfolder)

    def build(self):

        # uses 0/1 instead of true false
        shared = 1
        if not self.options.shared:
            shared = 0

        config_args = ["shared=" + str(shared) ]

        with tools.chdir(self._source_subfolder):
            self.env_build = AutoToolsBuildEnvironment(self)
            with tools.environment_append(self.env_build.vars):

                make_config = 'make config ' + ' '.join(config_args) + ' prefix=' + self.package_folder + ' assert=1'
                self.run(make_config, run_environment=True)
                self.run('make -j2', run_environment=True)

    def package(self):
        with tools.chdir(self._source_subfolder):
            with tools.environment_append(self.env_build.vars):
                self.run('make install', run_environment=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

from conans import ConanFile, AutoToolsBuildEnvironment, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
from conans.tools import os_info
import os, glob
from six import StringIO
import re

class ESMFConan(ConanFile):
    name = "esmf"
    license = "MIT"
    author = ""
    url = "https://esmf-org.github.io/"
    description = "Earth System Modeling Framework "
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    _source_folder = 'esmf'
    
    _autotools = None

    def source(self):
        # git = tools.Git(folder="")
        # git.clone("https://github.com/esmf-org/esmf.git", branch='ESMF_'+self.version.replace('.','_'), shallow=True)
        tools.get(**self.conan_data["sources"][self.version])

        for f in glob.glob("esmf-*"):
            os.rename(f, self._source_folder)

        tools.replace_in_file(file_path=self._source_folder+'/src/Infrastructure/Mesh/src/Moab/moab/Util.hpp',
                               search="define moab_isfinite(f) (!isinf(f) && !isnan(f))",
                               replace="define moab_isfinite(f) (!std::isinf(f) && !std::isnan(f))")

        try:
            # on macos under the github workflow env, gfortran is not symlinked and rather gfortran-<version> needs to be called
            # so patch the gfortran build rules to account for this name
            if os.environ["CI"]: # and os_info.is_macos:
                gfortran = os.environ["GFORTRAN_NAME"]
                tools.replace_in_file(file_path=self._source_folder+'/build_config/Darwin.gfortran.default/build_rules.mk',
                    search= "ESMF_F90DEFAULT         = gfortran",
                    replace=f"ESMF_F90DEFAULT         = {gfortran}")
        except KeyError as e:
            pass # we aren't running in a CI environemnt
        

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def _get_envars(self):

        esmf_envars = {}

        # gcc 10 requires a special set of compiler flags.                                    
        is_gfortran_10 = False

        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version.value) >= "10.0":
            is_gfortran_10 = True
        
        # if we use macos with default apple-clang but use a gcc10 gfortran from homebrew, conan doesn't know about this
        # so manually grab the $PATH gfortran version 
        if tools.os_info.is_macos and not is_gfortran_10:
            mybuf = StringIO()

            gfortran = "gfortran"
            try:
                if os.environ["CI"]:
                    gfortran = os.environ["GFORTRAN_NAME"]
            except KeyError as e:
                pass #not in CI

            self.run(f'{gfortran} --version',mybuf)

            ver = mybuf.getvalue()
            ver = re.findall("([0-9]+)\.[0-9]+\.[0-9]+",ver)
            if len(ver) ==0:
                self.output.error('Gfortran not found')
            if int(ver[0]) >= 10:
                is_gfortran_10 = True

        esmf_envars["ESMF_INSTALL_PREFIX"] =self.package_folder
        esmf_envars["ESMF_DIR"] = os.path.join(self.build_folder,self._source_folder)
        esmf_envars["ESMF_COMM"] = "mpiuni"

        # if is_gfortran_10:
            # esmf_envars["ESMF_F90COMPILEOPTS"] = "-fallow-argument-mismatch -fallow-invalid-boz"

        return esmf_envars

    def build(self):

        esmf_envars = self._get_envars()

        with tools.chdir(self._source_folder):
            env_build = self._configure_autotools()
            env_build.make(vars=esmf_envars)


    def package(self):
        esmf_envars = self._get_envars()

        with tools.chdir(self._source_folder):
            env_build = self._configure_autotools()
            env_build.install(vars=esmf_envars)
        
        self.copy('*.cmake','cmake','cmake')

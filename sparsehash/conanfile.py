from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os


class SparsehashConan(ConanFile):
    name = "sparsehash"
    description = "The C++ associative containers"
    homepage = "https://github.com/sparsehash/sparsehash"
    license = "BSD-3-Clause"
    topics = ("conan", "libsparsehash",
              "dense_hash_map", "sparse_hash_map",
              "dense_hash_set", "sparse_hash_set")
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/Chrismarsh/conan-sparsehash"
    exports = ["LICENSE"]
    _autotools = None

    _source_subfolder = 'sparsehash'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("sparsehash-sparsehash-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

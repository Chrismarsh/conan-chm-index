from __future__ import print_function
import os
from fnmatch import fnmatch
from conans.model.version import Version
from conans import ConanFile, AutoToolsBuildEnvironment, tools, RunEnvironment
from conans.tools import download, unzip
from six import StringIO

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class GdalConan(ConanFile):
    """ Conan package for GDAL """

    name = "gdal"
    description = "GDAL - Geospatial Data Abstraction Library"
    url = "http://www.gdal.org/"
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    
    options = {"shared": [True, False], 
               "libcurl": [True, False],
               "netcdf": [True, False] }
    
    default_options = {"shared": True,
                         "libcurl": True, 
                         "netcdf": True}

    
    exports_sources = ['patches/*']
    exports = ["LICENSE.md"]

    _folder = "gdal"
    _env_build = None


    def requirements(self):
        self.requires("zlib/[>=1.2]")

        v = Version(self.version)

        if v < "3":
            self.requires("proj/[>=4 <5]@CHM/stable")
        else:
            self.requires("proj/[>=7]@CHM/stable")

        self.requires("libiconv/[>=1.15]")

        if self.options.netcdf:
            self.requires("netcdf-c/[>=4.6]@CHM/stable")

        # if not self.options.shared:
        #     self.requires("sqlite3/3.27.1@bincrafters/stable", private=False, override=False)


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("gdal-{}".format(self.version), self._folder )
  
        if tools.os_info.is_macos:
            tools.replace_in_file("%s/configure" % self._folder, r"-install_name \$rpath/", "-install_name @rpath/")
            tools.replace_in_file("%s/m4/libtool.m4" % self._folder, r"-install_name \$rpath/", "-install_name @rpath/")

        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self._folder)


        # Work around this sillyness on macos. Tldr of the problem is that unless the install_name of the dylib is the full conan path
        # any child process run from configure won't be able to find it as DYLIB paths aren't passed in as per
        # https://stackoverflow.com/questions/35568122/why-isnt-dyld-library-path-being-propagated-here
        # and the conan RunEnv is not enough on macos
        # https://docs.conan.io/en/latest/reference/build_helpers/run_environment.html
        # so the work around is to embed all the conan library paths into the rpath of the test executables configure makes 
        if tools.os_info.is_macos:
            env_build = RunEnvironment(self)
            with tools.environment_append(env_build.vars):   
       
                rpath='-Wl,-rpath '
                try:
                    envar = os.environ['DYLD_LIBRARY_PATH']
                    rpath += envar 
                except:
                    pass
                rpath = rpath.replace(':',' -Wl,-rpath ')

              
                tools.replace_in_file("%s/configure" % (self._folder), 
                        """ac_link='$CC -o conftest$ac_exeext $CFLAGS $CPPFLAGS $LDFLAGS conftest.$ac_ext $LIBS >&5'""",
                        """ac_link='$CC  -o conftest$ac_exeext $CFLAGS $CPPFLAGS %s $LDFLAGS conftest.$ac_ext $LIBS >&5'"""% (rpath))


    def build(self):
        config_args = ["--with-geos=yes"]
        if self.options.shared:
            config_args += ["--disable-static", "--enable-shared"]
        else:
            config_args += [
                "--without-ld-shared", "--disable-shared", "--enable-static",
            ]

        config_args += ['--disable-rpath']

        if self.options.libcurl:
            curl_config = StringIO()
            self.run('which curl-config', output = curl_config)
            curl_config=curl_config.getvalue().rstrip()

            config_args += ["--with-curl="+curl_config]
        else:
            config_args += ["--without-curl"]

        config_args += ["--with-proj="+self.deps_cpp_info["proj"].rootpath]
        config_args += ["--without-geos"]
        config_args += ["--with-geotiff=internal"]
        config_args += ["--with-hide-internal-symbols"]
        config_args += ["--with-libtiff=internal"]
        config_args += ["--with-libz=internal"]
        config_args += ["--with-libjson-c=internal"]
        config_args += ["--with-threads"]
        config_args += ["--without-bsb"]
        config_args += ["--without-cfitsio"]
        config_args += ["--without-cryptopp"]
        config_args += ["--without-ecw"]
        config_args += ["--without-expat"]
        config_args += ["--without-fme"]
        config_args += ["--without-freexl"]
        config_args += ["--without-gif"]
        config_args += ["--without-gif"]
        config_args += ["--without-gnm"]
        config_args += ["--without-grass"]
        config_args += ["--without-grib"]
        config_args += ["--without-hdf4"]
        config_args += ["--without-hdf5"]
        config_args += ["--without-idb"]
        config_args += ["--without-ingres"]
        config_args += ["--without-jasper"]
        config_args += ["--without-jp2mrsid"]
        config_args += ["--with-jpeg=internal"]
        config_args += ["--without-jpeg12"]
        config_args += ["--without-kakadu"]
        config_args += ["--without-libgrass"]
        config_args += ["--without-libkml"]
        config_args += ["--without-libtool"]
        config_args += ["--without-mrf"]
        config_args += ["--without-mrsid"]
        config_args += ["--without-mysql"]

        if self.options.netcdf:
            config_args += ["--with-netcdf=" + self.deps_cpp_info["netcdf-c"].rootpath ]
        else:
            config_args += ["--without-netcdf"]
        
        config_args += ["--without-odbc"]
        config_args += ["--without-ogdi"]
        config_args += ["--without-openjpeg"]
        config_args += ["--without-pcidsk"]
        config_args += ["--without-pcraster"]
        config_args += ["--without-pcre"]
        config_args += ["--without-perl"]
        config_args += ["--without-pg"]
        config_args += ["--with-png=internal"]
        config_args += ["--without-python"]
        config_args += ["--without-qhull"]
        config_args += ["--without-sfcgal"]
        config_args += ["--without-sde"]
        config_args += ["--without-sqlite3"]
        config_args += ["--without-webp"]
        config_args += ["--without-xerces"]
        config_args += ["--without-xml2"]
        config_args += ["--without-crypto"]
        config_args += ["--without-kea"]
        config_args += ["--without-zstd"]

        run_str = './configure ' + ' '.join(config_args)
        run_str += ' --prefix ' + self.package_folder



        with tools.chdir(self._folder):
            self.env_build = AutoToolsBuildEnvironment(self)
            with tools.environment_append(self.env_build.vars):

                # use these such that on linux we correctly pass through the LD_LIBRARY_PATH to the child test exes
                self.run(run_str, run_environment=True)
                self.run('make -j2', run_environment=True)
                




    def package(self):
        with tools.chdir(self._folder):
            with tools.environment_append(self.env_build.vars):
                self.run('make install', run_environment=True)
        
        # strip any hard coded install_name from the dylibs to simplify downstream use
        if tools.os_info.is_macos:
            for path, subdirs, names in os.walk(os.path.join(self.package_folder, 'lib')):
                for name in names:

                    if fnmatch(name, '*.dylib*'):
                        so_file = os.path.join(path, name)

                        cmd = "install_name_tool -id @rpath/{0} {1}".format(name, so_file)
                        os.system(cmd)


    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["gdal"]

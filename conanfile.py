import os
from conans import ConanFile
from conans import tools
from conans import AutoToolsBuildEnvironment


class FreeImageConan(ConanFile):
    name = "freeimage"
    version = "3.18.0"
    description = "FreeImage for Windows, pre-built binaries are supplied"
    license = "FIPL"
    settings = "os_build", "compiler", "build_type", "arch_build"
    url = "https://github.com/bldrvnlw/conan-freeimage"
    _source_subfolder = "FreeImage"
    _build_subfolder = "build_subfolder"
    _destdir = None
    _incdir = None
    _installdir = None
    
    def configure(self):
        pass

    def source(self): 
        if self.settings.os_build != "Windows":
            tools.get("http://downloads.sourceforge.net/freeimage/FreeImage3180.zip")
            
            
    def build(self):
        if self.settings.os_build == "Windows":
            tools.get("http://downloads.sourceforge.net/freeimage/FreeImage3180Win32Win64.zip")
        else:
            autotools = AutoToolsBuildEnvironment(self)
            env_build_vars = autotools.vars
            # General configuration variables for FreeImage 
            env_build_vars['DESTDIR'] = self._build_subfolder
            self._destdir = env_build_vars['DESTDIR']
            env_build_vars["INCDIR"] = os.path.join(self._build_subfolder, "include")
            self._incdir = env_build_vars["INCDIR"]
            env_build_vars["INSTALLDIR"] = os.path.join(self._build_subfolder, "lib")
            self._installdir = env_build_vars["INSTALLDIR"]
            with tools.chdir(self._source_subfolder): 
                # FIP : Makefile.fip is for FreeImagePlus, the C++ FreeImage wrapper
                # make && make install
                autotools.make(target="-f Makefile.fip", vars=env_build_vars)
                autotools.make(target="-f Makefile.fip install", vars=env_build_vars)
        
    def package(self):
        if self.settings.os_build == "Windows":
            if self.settings.arch_build == "x86_64":
                src = os.path.join(self.build_folder, "FreeImage/Dist/x64")
            elif self.settings.arch_build == "x86":
                src = os.path.join(self.build_folder, "FreeImage/Dist/x32")
                
            self.copy("*.lib", dst="lib", src=src, keep_path=False)
            self.copy("*.dll", dst="bin", src=src, keep_path=False)
            self.copy("*.h", dst="include", src=src, keep_path=False)
        else:
            self.copy("*.a", dst="lib", src=self._installdir, keep_path=False)
            self.copy("*.so", dst="bin", src=self._installdir, keep_path=False)
            self.copy("*.h", dst="include", src=self._incdir, keep_path=False)
        

    def package_info(self):
        self.cpp_info.libs = ["freeimage"]
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
            env_build_vars['DESTDIR'] = self.package_folder
            env_build_vars["INCDIR"] = os.path.join(self.package_folder, "include")
            env_build_vars["INSTALLDIR"] = os.path.join(self.package_folder, "lib")
            with tools.chdir("FreeImage"): 
                autotools.make(target="-f Makefile.fip", vars=env_build_vars)
        
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
            with tools.chdir("FreeImage"): 
                src = ("./Dist")
                self.copy("*.a", dst="lib", src=src, keep_path=False)
                self.copy("*.so", dst="bin", src=src, keep_path=False)
                self.copy("*.h", dst="include", src=src, keep_path=False)
        

    def package_info(self):
        self.cpp_info.libs = ["freeimage"]
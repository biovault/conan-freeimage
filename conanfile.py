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
    _dist_subfolder = None
    
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
            # In order to set environment vars - unused in this recipe
            env_build_vars = autotools.vars
            with tools.chdir(self._source_subfolder): 
                # FIP : Makefile.fip is for FreeImagePlus, the C++ FreeImage wrapper
                # make 
                if self.settings.os_build == "Macos":
                    autotools.make(target="-f Makefile.osx", vars=env_build_vars)
                else:
                    autotools.make(target="-f Makefile.gnu", vars=env_build_vars)
                print("Cur dir: ", os.getcwd(), " Dist subdir: ", os.listdir("./Dist"))
                self._dist_subfolder = os.path.join(os.getcwd(), "Dist");
                # make install - not possible because chown fails
                #autotools.make(target="-f Makefile.gnu install", vars=env_build_vars)
        
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
            with tools.chdir(self._source_subfolder):
                self.copy("*.a", dst=os.path.join(self.package_folder, "lib"), src=self._dist_subfolder, keep_path=False)
                self.copy("*.so", dst=os.path.join(self.package_folder, "bin"), src=self._dist_subfolder, keep_path=False)
                self.copy("*.dylib", dst=os.path.join(self.package_folder, "bin"), src=self._dist_subfolder, keep_path=False)                
                self.copy("*.h", dst=os.path.join(self.package_folder, "include"), src=self._dist_subfolder, keep_path=False)
        

    def package_info(self):
        self.cpp_info.libs = ["freeimage"]
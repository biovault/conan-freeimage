import os
import shutil
from conans import ConanFile
from conans import tools
from conans import AutoToolsBuildEnvironment
from pathlib import Path

required_conan_version = ">=1.61.0"

class FreeImageConan(ConanFile):
    name = "freeimage"
    version = "3.18.0"
    description = "FreeImage for Windows, pre-built binaries are supplied"
    license = "FIPL"
    settings = "os_build", "compiler", "build_type", "arch_build"
    url = "https://github.com/biovault/conan-freeimage"
    _source_subfolder = "FreeImage"
    _build_subfolder = "build_subfolder"
    _dist_subfolder = None
    exports = "diff.patch"
    
    def configure(self):
        pass

    def source(self): 
        #pass
        if self.settings.os_build != "Windows":
            tools.get("http://downloads.sourceforge.net/freeimage/FreeImage3180.zip")

    def build(self):
        if self.settings.os_build == "Windows":
            tools.get("http://downloads.sourceforge.net/freeimage/FreeImage3180Win32Win64.zip")
        else:
            if self.settings.os_build == "Macos":
                tools.patch(patch_file="diff.patch", strip=1)  # Although the issues are seen at 12 patching on earlier is OK

            autotools = AutoToolsBuildEnvironment(self)
            # In order to set environment vars - unused in this recipe
            env_build_vars = autotools.vars
            with tools.chdir(self._source_subfolder): 
                # FIP : Makefile.fip is for FreeImagePlus, the C++ FreeImage wrapper
                # make 
                if self.settings.os_build == "Macos":
                    tools.replace_in_file('Makefile.osx', '-DNO_LCMS', '-DNO_LCMS -DDISABLE_PERF_MEASUREMENT') 
                    autotools.make(target="-f Makefile.osx", vars=env_build_vars)
                else:
                    print(f"Original env vars are {env_build_vars}", flush=True)
                    env_build_vars["CC"] = f"gcc-{ self.settings.compiler.version }"
                    env_build_vars["CXX"] = f"g++-{ self.settings.compiler.version }"
                    # 3.18 free image is not compatible with c++17
                    env_build_vars["CXXFLAGS"] = " ".join([os.getenv('CXXFLAGS', ''), '-std=c++14'])  
                    print(f"Single core env vars are {env_build_vars}", flush=True)
                    autotools.make(target="-f Makefile.gnu", vars=env_build_vars, args=["-j1"])
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
                self.copy("*.h", dst=os.path.join(self.package_folder, "include"), src=self._dist_subfolder, keep_path=False)
                if self.settings.os_build == "Macos":
                    # dylib should be symlinked to the .a file (perhaps at conan install time)
                    # Quick solution just copy & rename
                    self.copy("*.a", dst=os.path.join(self.package_folder, "bin"), src=self._dist_subfolder, keep_path=False)
                    os.rename(os.path.join(self.package_folder, "bin/libfreeimage.a"), os.path.join(self.package_folder, "bin/libfreeimage.dylib"))

    def package_info(self):
        self.cpp_info.libs = ["freeimage"]
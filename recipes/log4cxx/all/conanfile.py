from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps
from conan.tools.files import copy, get, patch, rmdir, save, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.gnu import PkgConfigDeps
import os
import textwrap

required_conan_version = ">=1.53.0"


class Log4cxxConan(ConanFile):
    name = "log4cxx"
    description = "Logging framework for C++ patterned after Apache log4j"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    homepage = "https://logging.apache.org/log4cxx"
    topics = ("logging", "log")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "prefer_boost": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "prefer_boost": False
    }

    generators = "CMakeDeps", "CMakeToolchain", "PkgConfigDeps"
    _cmake = None

    def layout(self):
        cmake_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("apr/1.7.0")
        self.requires("apr-util/1.6.1")
        self.requires("expat/2.5.0")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.9")

    def validate(self):
        # TODO: if compiler doesn't support C++17, boost can be used instead
        check_min_cppstd(self, 17)

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.build_requires("pkgconf/1.7.4")

    def source(self):
        #OSError: [WinError 123] The filename, directory name, or volume label syntax is incorrect:
        #'source_subfolder\\src\\test\\resources\\output\\xyz\\:'
        pattern = "*[!:]"
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, pattern=pattern)

    def _configure_cmake(self):
        if not self._cmake:
            definitions = {
                "BUILD_TESTING": False,
                "PREFER_BOOST": self.options.prefer_boost,
            }
            self._cmake = CMake(self)
            if self.settings.os == "Windows":
                definitions["LOG4CXX_INSTALL_PDB"] = False
            self._cmake.configure(variables=definitions)
        return self._cmake

    def build(self):
        apply_conandata_patches(self)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst="licenses")
        copy(self, "NOTICE", src=self.source_folder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "log4cxx")
        self.cpp_info.set_property("cmake_target_name", "log4cxx")
        self.cpp_info.set_property("pkg_config_name", "liblog4cxx")
        if not self.options.shared:
            self.cpp_info.defines = ["LOG4CXX_STATIC"]
        self.cpp_info.libs = ["log4cxx"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("odbc32")

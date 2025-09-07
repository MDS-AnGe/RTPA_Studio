"""
Configuration pour compiler le module C++ RTPA Studio
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from distutils.core import setup, Extension

# Extension C++ pour RTPA Studio
rtpa_core_module = Extension(
    'rtpa_core',
    sources=['rtpa_core.cpp'],
    include_dirs=[
        # Path to pybind11 headers
        pybind11.get_include(),
    ],
    language='c++',
    extra_compile_args=['-std=c++17', '-O3', '-march=native'],
)

setup(
    name='rtpa_core',
    version='1.0',
    description='Module C++ optimisé pour RTPA Studio',
    ext_modules=[rtpa_core_module],
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
)
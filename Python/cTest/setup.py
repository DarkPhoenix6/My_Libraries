from distutils.core import setup, Extension
import CythonConfig
from Cython.Build import cythonize

# ext_modules = cythonize(Extension(
#            "rect",                                 # the extension name
#            sources=["Python\\CythonConfig\\rect.pyx", "Python\\CythonConfig\\Rectangle.cpp"],  # the Cython source and
#                                                    # additional C++ source files
#            language="c++",                         # generate and compile C++ code
#       ))

ext_modules = cythonize(
           "test.pyx",                 # our Cython source

      )

setup(
    name="testapp",
    ext_modules=ext_modules,
)


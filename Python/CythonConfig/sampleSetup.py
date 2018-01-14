from distutils.core import setup, Extension
from Cython.Build import cythonize

# ext_modules = cythonize(Extension(
#            "rect",                                 # the extension name
#            sources=["Python\\CythonConfig\\rect.pyx", "Python\\CythonConfig\\Rectangle.cpp"],  # the Cython source and
#                                                    # additional C++ source files
#            language="c++",                         # generate and compile C++ code
#       ))

ext_modules = cythonize(
           "rect.pyx",                 # our Cython source
           language="c++",             # generate C++ code
      )

setup(
    name="rectangleapp",
    ext_modules=ext_modules,
)

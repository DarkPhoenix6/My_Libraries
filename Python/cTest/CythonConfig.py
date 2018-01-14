import os
import numpy
import pyximport

if os.name == 'nt':
    if 'CPATH' in os.environ.keys():
        os.environ['CPATH'] = os.environ['CPATH'] + numpy.get_include()
    else:
        os.environ['CPATH'] = numpy.get_include()

    # XXX: we're assuming that MinGW is installed in C:\MinGW (default)
    if 'PATH' in os.environ.keys():
        os.environ['PATH'] = os.environ['PATH'] + ';C:\\MinGW\\bin'
    else:
        os.environ['PATH'] = 'C:\\MinGW\\bin'

    mingw_setup_args = {'options': {'build_ext': {'compiler': 'mingw32'}}}
    pyximport.install(setup_args=mingw_setup_args)

elif os.name == 'posix':
    if 'CFLAGS' in os.environ.keys():
        os.environ['CFLAGS'] = os.environ['CFLAGS'] + ' -I' + numpy.get_include()
    else:
        os.environ['CFLAGS'] = ' -I' + numpy.get_include()

    pyximport.install()




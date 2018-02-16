from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library

standard_library.install_aliases()

import pip
from subprocess import call
import sys


if __name__ == '__main__':
    packages = [dist.project_name for dist in pip.get_installed_distributions()]
    #packages.remove('peewee')  # any packages causing update issues
    call(sys.executable + " -m " + "pip install --upgrade " + ' '.join(packages), shell=True)


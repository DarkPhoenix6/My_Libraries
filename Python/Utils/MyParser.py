from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import open
from builtins import str
from builtins import range
from builtins import object
from builtins import int
from builtins import bytes
from builtins import chr
from builtins import dict
from builtins import map
from builtins import input
# etc., as needed
from future import standard_library

standard_library.install_aliases()


class MyParser(object):
    def __init__(self):
        self.input_parser = self.parser()

    def parser(self):
        while 1:
            data = list(input().split(' '))
            for number in data:
                if len(number) > 0:
                    yield (number)

    def get_word(self):
        return next(self.input_parser)

    def get_number(self):
        data = self.get_word()
        try:
            return int(data)
        except ValueError:
            return float(data)

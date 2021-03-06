from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library
standard_library.install_aliases()
import os
import copy
from Utils import utils
from AES.gen_key_schedule import get_round_keys, set_key, gee
from AES.StateArray import StateArray, Matrix, MISSING
from AES import SubBytesAndMixColumns as SBMC


class MyAES(object):
    MIX_COLUMNS_ARRAY = SBMC.MIX_COLUMNS_ARRAY
    INV_MIX_COLUMNS_ARRAY = SBMC.INV_MIX_COLUMNS_ARRAY
    BYTES_SUB_TABLE = SBMC.BYTES_SUB_TABLE
    BYTES_SUB_TABLE_INV = SBMC.BYTES_SUB_TABLE_INV

    def __init__(self, matrix_list=[0] * 16, rounds=14, key=MISSING):

        self.matrix_list = copy.deepcopy(matrix_list)
        self.state_array = []
        while (len(self.matrix_list) % 16) != 0:
            self.matrix_list.append(0)
        self.rounds = rounds
        if key == MISSING:
            if self.rounds == 14:
                k = 32
            elif self.rounds == 12:
                k = 24
            elif self.rounds == 10:
                k = 16
            else:
                k = 32
            self.key = os.urandom(k)
        else:
            self.key = key
        self.round_keys = get_round_keys(self.key)


if __name__ == '__main__':
    pass

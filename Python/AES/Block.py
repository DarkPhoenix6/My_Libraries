from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library

standard_library.install_aliases()
import os
import copy
from AES.matrix import Matrix, MISSING
from AES.gen_key_schedule import get_round_keys, set_key
from AES import SubBytesAndMixColumns as SBMC
from Utils import utils

MIX_COLUMNS_ARRAY = SBMC.MIX_COLUMNS_ARRAY
INV_MIX_COLUMNS_ARRAY = SBMC.INV_MIX_COLUMNS_ARRAY
BYTES_SUB_TABLE = SBMC.BYTES_SUB_TABLE
BYTES_SUB_TABLE_INV = SBMC.BYTES_SUB_TABLE_INV


class Block(Matrix):

    def __init__(self, matrix_list=[0] * 16):
        if len(matrix_list) != 16:
            Matrix.__init__(self, [0] * 16, 4, 4)
        else:
            Matrix.__init__(self, list(matrix_list), 4, 4)

        self.transpose()

    def generate_empty_state(self):
        s = [[0 for x in range(self.columns)] for y in range(self.rows)]
        return s

    def add_round_key(self, round_key, transpose=False):
        for i in range(self.rows):
            for j in range(self.columns):
                if transpose:
                    self.state[i][j] = Block.gf_add(self.state[i][j], round_key[j][i])
                else:
                    self.state[i][j] = Block.gf_add(self.state[i][j], round_key[i][j])

    def add_iv(self, iv):

        self.add_round_key(iv, False)

    def subbytes(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.state[i][j] = BYTES_SUB_TABLE[self.state[i][j]]

    def mix_columns(self):

        s = self.generate_empty_state()
        for j in range(4):
            for i in range(4):
                s[i][j] = Block.mul_column(self.state, i, j)
        self.state = s

    def shift_rows(self):
        for i in range(4):
            self.state[i][0 - i], self.state[i][1 - i], self.state[i][2 - i], self.state[i][3 - i] = self.state[i][0], \
                                                                                                     self.state[i][1], \
                                                                                                     self.state[i][2], \
                                                                                                     self.state[i][3]

    def inv_mix_columns(self):
        s = self.generate_empty_state()
        for j in range(4):
            for i in range(4):
                s[i][j] = Block.mul_column(self.state, i, j, INV_MIX_COLUMNS_ARRAY)
        self.state = s

    @staticmethod
    def mul_column(state, row, column, mix_columns_array=MIX_COLUMNS_ARRAY):
        s0 = Block.gf_mul(state[0][column], mix_columns_array.state[row][0])
        s1 = Block.gf_mul(state[1][column], mix_columns_array.state[row][1])
        s2 = Block.gf_mul(state[2][column], mix_columns_array.state[row][2])
        s3 = Block.gf_mul(state[3][column], mix_columns_array.state[row][3])
        s5 = Block.gf_add(s0, s1)
        s6 = Block.gf_add(s5, s2)
        return Block.gf_add(s6, s3)

    def shift_column_one_down(self):
        self.state[0][1], self.state[1][1], self.state[2][1], self.state[3][1] = self.state[3][1], self.state[0][1], \
                                                                                 self.state[1][1], self.state[2][1],

    def state_as_one_dimensional_list(self):
        q = []
        for i in range(self.columns):
            for j in range(self.rows):
                q.append(copy.deepcopy(self.state[j][i]))
        return q




if __name__ == '__main__':
    pass

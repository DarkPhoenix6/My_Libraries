from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library

standard_library.install_aliases()
import os
from AES.matrix import Matrix, MISSING
from AES.gen_key_schedule import get_round_keys, set_key
from AES import SubBytesAndMixColumns as SBMC
from Utils import utils


class StateArray(Matrix):
    MIX_COLUMNS_ARRAY = SBMC.MIX_COLUMNS_ARRAY
    INV_MIX_COLUMNS_ARRAY = SBMC.INV_MIX_COLUMNS_ARRAY
    BYTES_SUB_TABLE = SBMC.BYTES_SUB_TABLE
    BYTES_SUB_TABLE_INV = SBMC.BYTES_SUB_TABLE_INV

    def __init__(self, matrix_list=[0] * 16, rounds=14, key=MISSING):
        if len(matrix_list) != 16:
            Matrix.__init__(self, [0] * 16, 4, 4)
        else:
            Matrix.__init__(self, list(matrix_list), 4, 4)
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

    def add_round_key(self, round_key, transpose=False):
        for i in range(self.rows):
            for j in range(self.columns):
                if transpose:
                    self.state[i][j] = Matrix.gf_add(self.state[i][j], round_key[j][i])
                else:
                    self.state[i][j] = Matrix.gf_add(self.state[i][j], round_key[i][j])

    def add_iv(self, iv):

        self.add_round_key(iv, False)

    def AES_encrypt(self, transpose_round_key=False):
        for i in range(0, (self.rounds + 1)):
            t = []
            for j in self.round_keys[i * 4:i * 4 + 4]:
                t += j
            round_key = Matrix.generate_matrix(t, 4, 4)
            if i == 0:
                self.add_round_key(round_key, transpose_round_key)
                # self.print_state()
            elif i == self.rounds:
                self.subbytes()
                # self.print_state()
                self.shift_rows()
                # self.print_state()
                self.add_round_key(round_key, transpose_round_key)
                # self.print_state()
            else:
                self.subbytes()
                # self.print_state()
                self.shift_rows()
                # self.print_state()
                self.mix_columns()
                # self.print_state()
                self.add_round_key(round_key, transpose_round_key)
                # self.print_state()

    def subbytes(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.state[i][j] = StateArray.BYTES_SUB_TABLE[self.state[i][j]]

    def mix_columns(self):

        s = self.generate_empty_state_array()
        for j in range(4):
            for i in range(4):
                s[i][j] = StateArray.mul_column(self.state, i, j)
        self.state = s

    def generate_empty_state_array(self):
        s = [[0 for x in range(self.columns)] for y in range(self.rows)]
        return s

    def shift_rows(self):
        for i in range(4):
            self.state[i][0 - i], self.state[i][1 - i], self.state[i][2 - i], self.state[i][3 - i] = self.state[i][0], \
                                                                                                     self.state[i][1], \
                                                                                                     self.state[i][2], \
                                                                                                     self.state[i][3]

    def inv_mix_columns(self):
        s = self.generate_empty_state_array()
        for j in range(4):
            for i in range(4):
                s[i][j] = StateArray.mul_column(self.state, i, j, StateArray.INV_MIX_COLUMNS_ARRAY)
        self.state = s

    @staticmethod
    def mul_column(state, row, column, mix_columns_array=MIX_COLUMNS_ARRAY):
        s0 = StateArray.gf_mul(state[0][column], mix_columns_array.state[row][0])
        s1 = StateArray.gf_mul(state[1][column], mix_columns_array.state[row][1])
        s2 = StateArray.gf_mul(state[2][column], mix_columns_array.state[row][2])
        s3 = StateArray.gf_mul(state[3][column], mix_columns_array.state[row][3])
        s5 = StateArray.gf_add(s0, s1)
        s6 = StateArray.gf_add(s5, s2)
        return StateArray.gf_add(s6, s3)

    def shift_column_one_down(self):
        self.state[0][1], self.state[1][1], self.state[2][1], self.state[3][1] = self.state[3][1], self.state[0][1], \
                                                                                 self.state[1][1], self.state[2][1],

    def __dict__(self):

        a = {
            'rows': self.rows,
            'columns': self.columns,
            'state': self.state,
            'rounds': self.rounds,
            'key': self.key,
            'round_keys': self.round_keys
        }
        return a

    def CF_hash(self, transpose_round_key=False, iv=[[222 for x in range(4)] for y in range(4)]):
        for i in range(0, (self.rounds + 1)):
            t = []
            for j in self.round_keys[i * 4:i * 4 + 4]:
                t += j
            round_key = Matrix.generate_matrix(t, 4, 4)
            if i == 0:
                self.add_iv(iv)
                self.subbytes()
                self.mix_columns()
                self.add_round_key(round_key, transpose_round_key)
            elif i == self.rounds:
                self.subbytes()
                self.CF_hash_block_stages()
                self.add_round_key(round_key, transpose_round_key)
            else:
                self.subbytes()
                self.CF_hash_block_stages()
                self.mix_columns()
                self.subbytes()
                self.add_round_key(round_key, transpose_round_key)

    def CF_hash_block_stages(self):
        self.CF_hash_stage_1()
        self.CF_hash_stage_2()
        self.CF_hash_stage_3()

    def CF_hash_stage_3(self):
        self.shift_rows()
        self.rotate_matrix_counterclockwise()
        self.rows_down()
        self.transpose()
        self.shift_column_one_down()

    def CF_hash_stage_2(self):
        self.shift_rows()
        self.rows_down()

    def CF_hash_stage_1(self):
        self.CF_hash_stage_2()
        self.transpose()


def time_it():
    global key3, b, t1, t2
    from time import clock as now
    key2 = 'hello'
    key2 = set_key(key2, 256)
    key3 = bytes(key2, 'ascii')
    b = StateArray([0x01, 0x02, 0x03, 0x04,
                    0x05, 0x06, 0x07, 0x08,
                    0x09, 0x0A, 0x0B, 0x0C,
                    0x0D, 0x0E, 0x0F, 0x10], rounds=14, key=key3)
    print(str(b.__dict__()))
    b.print_state()
    # b.AES_encrypt()
    t1 = now()
    for i in range(100000):
        if i % 1000 == 0:
            t3 = now()
            print(i, t3-t1)
        # print('\n' + str(i))
        # b.CF_hash_block_stages()
        b.CF_hash()
        # b.AES_encrypt()
    # b.shift_column_one_down()
    #     b.print_state()
    # # print(b.round_keys[0:4])
    # print('\n')
    t2 = now()
    print(str(t2 - t1))


if __name__ == '__main__':
    time_it()
    b.print_state()
    # b.rows_down()
    # b.print_state()
    #
    # b.AES_encrypt()
    #
    # print('\n')
    # b.print_state()
    #
    c = StateArray([0x01] * 16, rounds=10, key=key3)
    print('\n')

    # c.print_state()
    #
    # for j in range(10):
    #     c.AES_encrypt()
    #
    #     print('\n')
    #     c.print_state()
    print(utils.memory_address(b.BYTES_SUB_TABLE))
    print(utils.memory_address(c.BYTES_SUB_TABLE))
    print(utils.memory_address(b.BYTES_SUB_TABLE_INV))
    print(utils.memory_address(c.BYTES_SUB_TABLE_INV))
    print(utils.memory_address(b.MIX_COLUMNS_ARRAY))
    print(utils.memory_address(c.MIX_COLUMNS_ARRAY))
    print(utils.memory_address(b.INV_MIX_COLUMNS_ARRAY))
    print(utils.memory_address(c.INV_MIX_COLUMNS_ARRAY))

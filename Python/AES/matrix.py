import sys
import hashlib
import binascii
import os
import struct
import copy
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Utils import methoddispatch, singledispatch, gen_subbytes_table, gen_subbytes_inv_table
from bitstring import BitArray
from base64 import b16encode
from pylibscrypt import scrypt
from ctypes import string_at
import unittest
import ctypes
import math
from AES.gen_key_schedule import get_round_keys, set_key
from BitVector import *

# AES_modulus = bytes(hex(0b100011011))
MISSING = object()


class Matrix(object):

    def __init__(self, matrix_list: list, rows=MISSING, columns=MISSING):
        if rows == MISSING and columns == MISSING:
            self.rows = int(math.sqrt(len(matrix_list)))
            self.columns = self.rows
        elif rows == MISSING:
            self.columns = int(columns)
            self.rows = int(len(matrix_list) / self.columns)
        elif columns == MISSING:
            self.rows = int(rows)
            self.rows = int(len(matrix_list) / self.columns)
        else:
            self.rows = int(rows)
            self.columns = int(columns)

        self.state = Matrix.generate_matrix(matrix_list, self.rows, self.columns)  # self.state[row][column]

    @staticmethod
    def generate_matrix(matrix_list, rows, columns):
        m = [[0 for x in range(columns)] for y in range(rows)]

        count = 0
        for i in range(rows):
            for j in range(columns):
                m[i][j] = matrix_list[count]
                count += 1
        return m

    # def reverse_column(self, column):

    @staticmethod
    def transpose(matrix):
        matrix_list = []
        for i in range(matrix.rows):
            for j in range(matrix.columns):
                matrix_list.append(matrix.state[i][j])
        matrix_b = Matrix(matrix_list, matrix.columns, matrix.rows)
        return matrix_b

    @staticmethod
    def gf_add(a, b):
        return a ^ b

    @staticmethod
    def gf_mul(a, b, mod=0x11B):
        """
        Galois Field (256) Multiplication of two Bytes
        :param a:
        :param b:
        :param mod: x^8 + x^4 + x^3 + x + 1 for AES
        :return:
        """
        p = 0
        for i in range(8):
            if (b & 1) != 0:
                p ^= a
            high_bit_set = a & 0x80
            a <<= 1
            if high_bit_set != 0:
                a ^= mod
            b >>= 1
        return p

    def rotate_matrix_clockwise(self):
        s = Matrix([0] * (self.rows * self.columns), self.columns, self.rows)
        count = 0
        for i in range(self.rows):
            count -= 1
            for j in range(self.columns):
                # k = i - self.rows
                s.state[j][i] = self.state[count][j]
        self.state = s.state
        self.rows = s.rows
        self.columns = s.columns

    def print_state(self):
        for i in range(self.rows):
            print(self.state[i])

    def rotate_matrix_counterclockwise(self):
        s = Matrix([0] * (self.rows * self.columns), self.columns, self.rows)
        count = 0
        for j in range(self.columns):
            # k = i - self.rows
            count -= 1
            for i in range(self.rows):
                s.state[j][i] = self.state[i][count]
        self.state = s.state
        self.rows = s.rows
        self.columns = s.columns

    def __getitem__(self, item):
        return self.state[item]

    def __setitem__(self, key, value):
        self.state[key] = value


class StateArray(Matrix):
    MIX_COLUMNS_ARRAY = Matrix([0x02, 0x01, 0x01, 0x03,
                                0x03, 0x02, 0x01, 0x01,
                                0x01, 0x03, 0x02, 0x01,
                                0x01, 0x01, 0x03, 0x02])

    INV_MIX_COLUMNS_ARRAY = Matrix([0x0E, 0x0B, 0x0D, 0x09,
                                    0x09, 0x0E, 0x0B, 0x0D,
                                    0x0D, 0x09, 0x0E, 0x0B,
                                    0x0B, 0x0D, 0x09, 0x0E])

    BYTES_SUB_TABLE = gen_subbytes_table()
    BYTES_SUB_TABLE_INV = gen_subbytes_inv_table()

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
            elif i == self.rounds:
                self.subbytes()
                self.shift_rows()
                self.add_round_key(round_key, transpose_round_key)
            else:
                self.subbytes()
                self.shift_rows()
                self.mix_columns()
                self.add_round_key(round_key, transpose_round_key)

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


if __name__ == '__main__':
    a = Matrix([0x01, 0x02, 0x03, 0x04,
                0x05, 0x06, 0x07, 0x08,
                0x09, 0x0A, 0x0B, 0x0C,
                0x0D, 0x0E, 0x0F, 0x10,
                0x11, 0x12, 0x13, 0x14], 5, 4)
    a.print_state()
    a.rotate_matrix_clockwise()
    a.print_state()
    print('\n')
    a.rotate_matrix_counterclockwise()
    a.print_state()

    key2 = 'hello'
    key2 = set_key(key2, 128)
    key3 = bytes(key2, 'ascii')
    b = StateArray([0x01, 0x02, 0x03, 0x04,
                    0x05, 0x06, 0x07, 0x08,
                    0x09, 0x0A, 0x0B, 0x0C,
                    0x0D, 0x0E, 0x0F, 0x10], rounds=10, key=key3)

    # print(b.round_keys[0:4])
    print('\n')
    b.print_state()

    b.AES_encrypt()

    print('\n')
    b.print_state()

    c = StateArray([0x01] * 16, rounds=10, key=key3)
    print('\n')
    for i in range(c.rows):
        c.print_state()

    for j in range(10):
        c.AES_encrypt()

        print('\n')
        c.print_state()

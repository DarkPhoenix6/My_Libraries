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
import json
from AES.gen_key_schedule import get_round_keys, set_key
from ModGen import mod_gen, corrected_mod_gen
from AES.Error import IncompatibleMatrixError

MISSING = object()


class Matrix(object):

    def __init__(self, matrix_list: list, rows=MISSING, columns=MISSING):
        """

        :param matrix_list:
        :param rows: an int
        :param columns: an int
        """
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

    def transpose(self):
        matrix_list = []
        for i in range(self.rows):
            for j in range(self.columns):
                matrix_list.append(self.state[i][j])
        self.state = Matrix.generate_matrix(matrix_list, self.columns, self.rows)
        self.rows, self.columns = self.columns, self.rows

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

    def __to_dict__(self):
        return {
            'rows': self.rows,
            'columns': self.columns,
            'state': self.state
        }

    def __str__(self):
        q = self.__repr__().split(':')
        q[0] = type(self).__name__
        return ''.join(q)

    def __repr__(self):
        return self.matrix_repr()

    def matrix_repr(self):
        d = self.__to_dict__()
        q = self.state_as_one_dimensional_list()
        # return "%s(%r)" % (type(self).__name__, (str(q) + ', ' + str(d['rows']) + ', ' + str(d['columns'])))
        return "%s: (%s)" % (self.__class__, (str(q) + ', ' + str(d['rows']) + ', ' + str(d['columns'])))

    def state_as_one_dimensional_list(self):
        q = []
        for i in self.state:
            q += i
        return q

    def state_as_one_dimensional_tuple(self):
        return tuple(self.state_as_one_dimensional_list())

    def rows_down(self):
        a = self.state.pop(self.rows - 1)
        self.state.insert(0, a)

    def __add__(self, other):
        if self.rows == other.rows and self.columns == other.columns:
            m = [0 for x in range(self.columns * self.rows)]

            count = 0
            for i in range(self.rows):
                for j in range(self.columns):
                    m[count] = self.state[i][j] + other.state[i][j]
                    count += 1
            return Matrix(m, self.rows, self.columns)
        else:
            raise IncompatibleMatrixError('The matrices have different row and/or column sizes')

    def __radd__(self, other):
        return self.__add__(other)



if __name__ == '__main__':

    a = Matrix([0x01, 0x02, 0x03, 0x04,
                0x05, 0x06, 0x07, 0x08,
                0x09, 0x0A, 0x0B, 0x0C,
                0x0D, 0x0E, 0x0F, 0x10,
                0x11, 0x12, 0x13, 0x14], 5, 4)
    print(a.__dict__)
    print(a)
    print(repr(a))
    b = repr(a)
    print()
    # a.print_state()
    # a.rows_down()
    # a.print_state()
    # a.rotate_matrix_clockwise()
    # a.print_state()
    # print('\n')
    # a.rotate_matrix_counterclockwise()
    # a.print_state()
    #

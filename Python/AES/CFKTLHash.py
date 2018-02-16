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
from AES.Block import Block


class CFKTLHash(object):
    MIX_COLUMNS_ARRAY = SBMC.MIX_COLUMNS_ARRAY
    INV_MIX_COLUMNS_ARRAY = SBMC.INV_MIX_COLUMNS_ARRAY
    BYTES_SUB_TABLE = SBMC.BYTES_SUB_TABLE
    BYTES_SUB_TABLE_INV = SBMC.BYTES_SUB_TABLE_INV

    def __init__(self, matrix_list=[0] * 16, hash_length=256, circular_rounds=210, rounds=14, key=MISSING,
                 block_size=16):
        """

        :param matrix_list:
        :param hash_length:
        :param circular_rounds:
        :param rounds:
        :param key:
        :param block_size:
        """
        self.matrix_list = copy.deepcopy(matrix_list)
        self.block_size = block_size
        self.block_array = []
        self.key_array = []
        self.circular_rounds = circular_rounds
        self.hash_length = hash_length
        self.work_space = 128
        self.transpose_key = True
        rc = 0x10
        count = 1
        while len(self.matrix_list) < 4 or (len(self.matrix_list) % 4) != 0:
            self.matrix_list.append(0)
        while (len(self.matrix_list) % 16) != 0 or len(self.matrix_list) < (
                (self.hash_length + self.work_space) // 8) or len(self.matrix_list) < 48:
            word, rc = gee(self.matrix_list[-4:], rc)
            self.matrix_list += utils.xor_int_list(self.matrix_list[-4 * count:-4 * count + 4], word)
            count = (count + 3) % (len(self.matrix_list) // 4)

        self.num_blocks = len(self.matrix_list) // 16
        for i in CFKTLHash.block_generator(self.matrix_list, block_size=self.block_size):
            self.block_array.append(i)
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

        for i in range(-2, 1):
            self.key_array.append(self.block_array[i].state_as_one_dimensional_list())
        self.round_keys = get_round_keys(self.key)

    def cyclic_cipher_block_chaining(self):
        pass

    def cascading_cipher_block_chaining(self):
        pass

    def cascading_cyclic_cipher_block_chaining(self):
        """
        take two previous unencrypted blocks as key for current block
        :return:
        """
        count = -1
        first_go = True
        for i in range(self.circular_rounds):
            count += 1
            for j in self.block_array:
                k = self.key_array.pop(0)
                if first_go:
                    first_go = False
                else:
                    self.round_keys = get_round_keys(bytes(k + self.key_array[0]))
                self.key_array.append(j.state_as_one_dimensional_list())
                self.my_hash(j, transpose_round_key=True)

    def my_hash(self, current_block, transpose_round_key=False, iv=[[222 for x in range(4)] for y in range(4)]):
        for i in range(0, (self.rounds + 1)):
            t = []
            for j in self.round_keys[i * 4:i * 4 + 4]:
                t += j
            round_key = Matrix.generate_matrix(t, 4, 4)
            if i == 0:
                current_block.add_iv(iv)
                current_block.subbytes()
                current_block.mix_columns()
            elif i == self.rounds:
                current_block.subbytes()
                self.CF_hash_block_stages(current_block)
            else:
                current_block.subbytes()
                self.CF_hash_block_stages(current_block)
                current_block.mix_columns()
                current_block.subbytes()
            current_block.add_round_key(round_key, transpose_round_key)

    def CF_hash_block_stages(self, current_block):
        self.CF_hash_stage_1(current_block)
        self.CF_hash_stage_2(current_block)
        self.CF_hash_stage_3(current_block)

    def CF_hash_stage_3(self, current_block):
        current_block.shift_rows()
        current_block.rotate_matrix_counterclockwise()
        current_block.rows_down()
        current_block.transpose()
        current_block.shift_column_one_down()

    def CF_hash_stage_2(self, current_block):
        current_block.shift_rows()
        current_block.rows_down()

    def CF_hash_stage_1(self, current_block):
        self.CF_hash_stage_2(current_block)
        current_block.transpose()

    @staticmethod
    def block_generator(matrix_list, block_size):
        for j in range(len(matrix_list) // block_size):
            yield Block(matrix_list[j * block_size:j * block_size + block_size])


if __name__ == '__main__':
    key2 = 'hello'
    key2 = set_key(key2, 256)
    key3 = bytes(key2, 'ascii')
    a = 14
    o = 15
    b = CFKTLHash([0x01, 0x02, 0x03, 0x04,
                   0x05, 0x06, 0x07, 0x08,
                   0x09, 0x0A, 0x0B, 0x0C,
                   0x0D, 0x0E, 0x0F, 0x10], rounds=a, key=key3)
    c = CFKTLHash([i for i in range(22)], rounds=a, key=key3)
    d = CFKTLHash([i for i in range(52)], rounds=a, key=key3)

    b.cascading_cyclic_cipher_block_chaining()
    d.cascading_cyclic_cipher_block_chaining()

    print(b.__dict__)
    print(c.__dict__)
    print(d.__dict__)
    pass

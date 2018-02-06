from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from unittest import TestCase

from future import standard_library

standard_library.install_aliases()
from AES.gen_key_schedule import get_round_keys, set_key
from AES.StateArray import StateArray

class TestStateArray(TestCase):
    def test_add_round_key(self):
        self.fail()

    def test_add_iv(self):
        self.fail()

    def test_AES_encrypt(self):
        self.fail()

    def test_subbytes(self):
        self.fail()

    def test_mix_columns(self):
        self.fail()

    def test_generate_empty_state_array(self):
        self.fail()

    def test_shift_rows(self):
        key2 = 'hello'
        key2 = set_key(key2, 128)
        key3 = bytes(key2, 'ascii')
        b = StateArray([0x01, 0x02, 0x03, 0x04,
                        0x05, 0x06, 0x07, 0x08,
                        0x09, 0x0A, 0x0B, 0x0C,
                        0x0D, 0x0E, 0x0F, 0x10], rounds=10, key=key3)
        c = StateArray([0x0D, 0x0E, 0x0F, 0x10,
                        0x01, 0x02, 0x03, 0x04,
                        0x05, 0x06, 0x07, 0x08,
                        0x09, 0x0A, 0x0B, 0x0C], rounds=10, key=key3)

        b.rows_down()

    def test_inv_mix_columns(self):
        self.fail()

    def test_mul_column(self):
        self.fail()

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from future import standard_library

standard_library.install_aliases()
from Utils import gen_subbytes_table, gen_subbytes_inv_table
from AES.matrix import Matrix
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

if __name__ == '__main__':

    pass

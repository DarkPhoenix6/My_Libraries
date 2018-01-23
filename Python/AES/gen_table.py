from BitVector import *

AES_modulus = BitVector(bitstring = '100011011')

def gen_subbytes_table():
    subBytesTable = []
    c = BitVector(bitstring='01100011')
    for i in range(0, 256):
        a = BitVector(intVal=i, size=8).gf_MI(AES_modulus, 8) if i != 0 else BitVector(intVal=0)
        a1, a2, a3, a4 = [a.deep_copy() for x in range(4)]
        a ^= (a1 >> 4) ^ (a2 >> 5) ^ (a3 >> 6) ^ (a4 >> 7) ^ c
        subBytesTable.append(int(a))
    return tuple(subBytesTable)


def gen_inv_subbytes_table():
    inv_subBytesTable = []
    d = BitVector(bitstring='00000101')
    for i in range(0, 256):
        a = BitVector(intVal=i, size=8).gf_MI(AES_modulus, 8) if i != 0 else BitVector(intVal=0)
        a1, a2, a3 = [a.deep_copy() for x in range(3)]
        a ^= (a1 >> 2) ^ (a2 >> 5) ^ (a3 >> 7) ^ d
        inv_subBytesTable.append(int(a))
    return tuple(inv_subBytesTable)


if __name__ == '__main__':
    b

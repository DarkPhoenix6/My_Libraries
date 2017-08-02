from __future__ import division
from bitstring import BitArray
from MultiMethod.multimethod import multimethod
from functools import singledispatch
import struct
import ctypes
import sys
AES_modulus2 = 0b100011011


def int_to_bytes(data: int, len_bytes=1):
    return data.to_bytes(len, sys.byteorder)


def int_to_bytes_hex(data: int):
    return bytes(hex(data), 'utf-8')


def int_to_bytes_bin(data: int):
    return bytes(bin(data), 'utf-8')


def int32_to_uint32(i):
    return struct.unpack_from("I", struct.pack("i", i))[0]


def int32_to_uint322(i: int):
    return ctypes.c_uint32(i).value


def mod_gen(n, m, s=0):
    """
    Generator function that yields n tuples of m length containing consecutive indices within bounds n
    Such that the set of tuples generated from mod_gen(3, 3) would be ((2, 0, 1), (0, 1, 2), (1, 2, 0))
    :param n: The number of tuples to generate and the bounds of the indices in the tuple
    :param m: The number of indices per tuple
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(n):
        yield (tuple([(i + k + s) % n for k in range(int(m / 2) - m + 1, int(m / 2 + 1))]))


def mod_gen2(n, m, num, s=0):
    """
    Generator function that yields n tuples of m length containing consecutive indices within bounds n
    Such that the set of tuples generated from mod_gen(3, 3) would be ((2, 0, 1), (0, 1, 2), (1, 2, 0))
    :param n: The bounds of the indices in the tuple
    :param num: The number of tuples to generate
    :param m: The number of indices per tuple
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(num):
        yield (tuple([(i + k + s) % n for k in range(int(m / 2) - m + 1, int(m / 2 + 1))]))


def list_mod_gen(iterable, m, s=0, **num):
    """ Generator function that yields n tuples of m length containing consecutive list elements within bounds n
    Such that the set of tuples generated from list_mod_gen([a, b, c], 3) would be ((c, a, b), (a, b, c), (b, c, a))
    :param iterable: An iterable object with which we wish to iterate over consecutive elements
    :param m: The number of consecutive elements required
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(len(iterable)):
        yield (tuple(iterable[(i + k + s) % len(iterable)] for k in range(int(m / 2) - m + 1, int(m / 2) + 1)))


def center_sum(iterable):
    """ Sums up the contents of a list putting more weight on the center
    :param iterable: the list
    :return: the sum of the list with more weight on the center
    """
    center = int((len(iterable) + 1) / 2) - 1
    return sum([a * (float(center) / float(abs(center - i) + 1)) for i, a in enumerate(iterable)])


@singledispatch
def cut_the_deck(data):
    data2 = [data[len(data):] + data[:len(data)]]
    return data2


@cut_the_deck.register(bytes)
def _(data: bytes):
    data2 = b''.join([data[len(data):], data[:len(data)]])
    return data2


def reverse(data):
    data2 = data[::-1]
    return data2


@singledispatch
def flip_bits(data):
    for i in range(len(bin(data))):
        bin_data = flip_bit(data, i)
    return bin_data


@flip_bits.register(bytes)
def _(data: bytes):
    bin_data = BitArray(data)
    bin_data.invert()
    return bytes(bin_data.bytes)


def xor_(var: bytes, key: bytes):
    key = key[:len(var)]
    int_var = int.from_bytes(var, sys.byteorder)
    int_key = int.from_bytes(key, sys.byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(var), sys.byteorder)


def flip_bit(number, n):
    mask = (0b1 << n - 1)
    result = number ^ mask
    return bin(result)


def extended_gcd_rec(a, b):
    """
    Extended Euclidean algorithm
    :param a:
    :param b:
    :return:
    """
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd_rec(b % a, a)
        return g, x - (b // a) * y, y


def gcd_itr(num, mod):
    """
    Extended Euclidean algorithm
    :param num:
    :param mod:
    :return:
    """
    x_old, x, y_old, y1 = 1, 0, 0, 1
    while mod != 0:
        quotient, num, mod = num // mod, mod, num % mod
        x_old, x = x, x_old - quotient * x
        y_old, y1 = y1, y_old - quotient * y1
    return num, x_old, y_old


def mod_inv(a, m):
    """
    finds the modular multiplicative inverse using the Extended Euclidean algorithm
    :param a:
    :param m:
    :return:
    """
    g, x, y = gcd_itr(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def gf_add(a, b):
    return a ^ b


def gf_sub(a, b):
    return gf_add(a, b)


def gf_modular_mul(a, b, mod=0x1B):
    """
    Galois Field (256) Multiplication of two Bytes
    :param a:
    :param b:
    :param mod: x^8 + x^4 + x^3 + x + 1 for AES
    :return:
    """
    p = bytes(hex(0x00))
    for i in range(8):
        if (b & 1) != 0:
            p ^= a
        high_bit_set = bytes(a & 0x80)
        a <<= 1
        if high_bit_set != 0:
            a ^= mod
        b >>= 1
    return p


def gf_mod_div(a, b, mod=0x1B, field_size=8):
    """
    Galois Field (256) Multiplication of two Bytes
    :param a:
    :param b:
    :param mod: x^8 + x^4 + x^3 + x + 1 for AES
    :return:
    """
    a_ = a
    mod_ = mod
    b_ = b
    v = bytes(hex(0x00))
    while mod_ != 1 and a_ != 0:
        if (b_ & 1) != 0:
            if b_ >= mod_:
                b_ ^= mod_
                a_ ^= v
            else:
                b_ ^= mod_
                mod_ = b_
                a_ ^= v
                v = a
            b_ >>= 1
            a_ >>= 1
    return v


def gf_degree(a):
    res = 0
    a >>= 1
    while a != 0:
        a >>= 1
        res += 1
    return res


def gf_invert(a, mod=0x11B):
    v = mod
    g1 = 1
    g2 = 0
    j = gf_degree(a) - 8

    while a != 1:
        if j < 0:
            a, v = v, a
            g1, g2 = g2, g1
            j = -j

        a ^= v << j
        g1 ^= g2 << j

        a %= 256  # Emulating 8-bit overflow
        g1 %= 256 # Emulating 8-bit overflow

        j = gf_degree(a) - gf_degree(v)
    return g1


def extendedEuclideanGF2(a, b):
    # extended euclidean. a,b are values 10110011... in         integer form
    inita, initb = a, b   # if a and b are given as base-10 ints
    x, prevx = 0, 1
    y, prevy = 1, 0
    while b != 0:
        q = a//b
        a, b = b, a % b
        x, prevx = prevx - q*x, x
        y, prevy = prevy - q*y, y
    #print("Euclidean  %d * %d + %d * %d = %d" % (inita, prevx, initb, prevy, a))
    i2b = lambda n: int("{0:b}".format(n))  # convert decimal number to a binary value in a decimal number
    return i2b(a), i2b(prevx), i2b(prevy)


def modular_inverse(a, mod): # a,mod are integer values of 101010111... form
    bitsa = int("{0:b}".format(a), 2); bitsb = int("{0:b}".format(mod), 2)
    #return bitsa,bitsb,type(bitsa),type(bitsb),a,mod,type(a),type(mod)
    gcd, s, t = extendedEuclideanGF2(a, mod)
    s = int("{0:b}".format(s))
    initmi = s % mod
    mi = int("{0:b}".format(initmi))
    #print ("M Inverse %d * %d mod %d = 1"%(a,initmi,mod))
    if gcd != 1:
        return mi
    return mi

#def rotl8(x, shift)


def gen_subbytes_table2():
    subBytesTable = []
    c = 0b01100011
    for i in range(0, 256):
        a = gf_invert(i) if i != 0 else 0
        # For bit scrambling for the encryption SBox entries:
        a = affine_transformation(a, c)
        subBytesTable.append(int(a))
    return subBytesTable


def affine_transformation(a, c=0b01100011):
    a1, a2, a3, a4 = [a for x in range(4)]
    a ^= rot_r(a1, 4) ^ rot_r(a2, 5) ^ rot_r(a3, 6) ^ rot_r(a4, 7) ^ c
    return a


def rot_r(n, rotations=1, width=1):
    """Return a given number of bitwise right rotations of an integer n,
       for a given bit field width.
    """
    rotations %= width * 8  #  width bytes give 8*bytes bits
    if rotations < 1:
        return n
    mask = mask_gen(8 * width)   # store the mask
    n &= mask
    return (n >> rotations) | ((n << (8 * width - rotations)) & mask)  # apply the mask to result


def rot_l(n, rotations=1, width=1):
    """Return a given number of bitwise left rotations of an integer n,
       for a given bit field width.
    """
    rotations %= width * 8  #  width bytes give 8*bytes bits
    if rotations < 1:
        return n
    mask = mask_gen(8 * width)  # store the mask
    n &= mask
    return (n << rotations) | ((n >> (8 * width - rotations)) & mask)  # apply the mask to result


def mask_gen(n):
    return (2 ** n) - 1
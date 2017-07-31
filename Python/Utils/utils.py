from __future__ import division
from bitstring import BitArray
from MultiMethod.multimethod import multimethod
from functools import singledispatch
from typing import overload
import struct
import ctypes




def int_to_bytes(data: int):
    return bytes(bin(data), 'utf-8')


@overload
def int32_to_uint32(i):
    return struct.unpack_from("I", struct.pack("i", i))[0]


@int32_to_uint32.overload
def int32_to_uint32(i: int):
    return ctypes.c_uint32(i).value


@overload
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


@mod_gen.overload
def mod_gen(n, m, num, s=0):
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
        bin_data = Utils.flip_bit(data, i)
    return bin_data


@flip_bits.register(bytes)
def _(data: bytes):
    bin_data = BitArray(data)
    bin_data.invert()
    return bytes(bin_data.bytes)


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


def gcd_itr(b, n):
    """
    Extended Euclidean algorithm
    :param b:
    :param n:
    :return:
    """
    x0, x1, y0, y1 = 1, 0, 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return b, x0, y0


def mod_inv(a, m):
    """
    finds the modular inverse using the Extended Euclidean algorithm
    :param a:
    :param m:
    :return:
    """
    g, x, y = gcd_itr(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m



from __future__ import division, print_function
from bitstring import BitArray
from MultiMethod.multimethod import multimethod
from copy import deepcopy
from .memo import memoize
from functools import singledispatch, update_wrapper, reduce, recursive_repr
import struct
import ctypes
import sys
import collections
import math
from fractions import Fraction
from collections import Counter
AES_modulus2 = 0b100011011
pie = math.pi * math.e


def methoddispatch(func):
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, dispatcher)
    return wrapper


def int_to_bytes(data: int, len_bytes=1):
    return data.to_bytes(len_bytes, sys.byteorder)


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
        yield (tuple([(i + k + s) % n for k in range(int(m // 2) - m + 1, int(m // 2 + 1))]))


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


@memoize
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


@memoize
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


@memoize
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


@memoize
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


def deepcopy_with_sharing(obj, shared_attribute_names, memo=None):
    """

    :param obj:
    :param shared_attribute_names:
    :param memo:
    :return:
        Deepcopy an object, except for a given list of attributes, which should
    be shared between the original object and its copy.

    obj is some object
    shared_attribute_names: A list of strings identifying the attributes that
        should be shared between the original and its copy.
    memo is the dictionary passed into __deepcopy__.  Ignore this argument if
        not calling from within __deepcopy__.
    """
    assert isinstance(shared_attribute_names, (list, tuple))
    shared_attributes = {k: getattr(obj, k) for k in shared_attribute_names}

    if hasattr(obj, '__deepcopy__'):
        # Do hack to prevent infinite recursion in call to deepcopy
        deepcopy_method = obj.__deepcopy__
        obj.__deepcopy__ = None

    for attr in shared_attribute_names:
        del obj.__dict__[attr]

    clone = deepcopy(obj)

    for attr, val in shared_attributes.iteritems():
        setattr(obj, attr, val)
        setattr(clone, attr, val)

    if hasattr(obj, '__deepcopy__'):
        # Undo hack
        obj.__deepcopy__ = deepcopy_method
        del clone.__deepcopy__

    return clone


def generate_matrix(matrix_list, rows, columns):
    m = [[0 for x in range(columns)] for y in range(rows)]

    count = 0
    for i in range(columns):
        for j in range(rows):
            m[j][i] = matrix_list[count]
            count += 1
    return m


def transpose(matrix, rows, columns):
    matrix_list = []
    for i in range(rows):
        for j in range(columns):
            matrix_list.append(matrix[i][j])
    matrix_b = generate_matrix(matrix_list, columns, rows)
    return matrix_b


@memoize
def breadth_first_search(graph, root):
    visited, queue = set(), collections.deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)


@memoize
def bfs_paths(graph, start, goal):
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next_node in graph[vertex] - set(path):
            if next_node == goal:
                yield path + [next_node]
            else:
                queue.append((next_node, path + [next_node]))


@memoize
def bfs(graph, start):
    visited, queue = set(), [start]
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited:
            visited.add(vertex)
            queue.extend(graph[vertex] - visited)
    return visited


@memoize
def dfs_paths_itr(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        for next_node in graph[vertex] - set(path):
            if next_node == goal:
                yield path + [next_node]
            else:
                stack.append((next_node, path + [next_node]))


@memoize
def dfs_paths(graph, start, goal, path=None):
    if path is None:
        path = [start]
    if start == goal:
        yield path
    for next_node in graph[start] - set(path):
        yield from dfs_paths(graph, next_node, goal, path + [next_node])


@memoize
def dfs_itr(graph, start):
    visited, stack = set(), [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited


@memoize
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for next_node in graph[start] - visited:
        dfs(graph, next_node, visited)
    return visited


@memoize
def shortest_path(graph, start, goal):
    try:
        return next(bfs_paths(graph, start, goal))
    except StopIteration:
        return None


@memoize
def shortest_of_the_short(graph, start, gates):
    distances = []
    paths_ = []
    for i in gates:
        paths = shortest_path(graph, start, i)
        if paths is not None:
            distances.append(len(paths))
            paths_.append(paths)
    min_len = min(distances)
    path = paths_[distances.index(min_len)]
    return path


def q(cond, on_true, on_false):
    return {True: on_true, False: on_false}[cond is True]


@memoize
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def n_in_arithmetic_sequence(a, n, d):
    """

    :param a: is the first term
    :param n: is the term number
    :param d: is the difference between the terms (called the "common difference")
    :return: the nth number in an arithmetic sequence / Progression
    """
    return a + d * (n - 1)


def num_of_terms_in_arithmetic_sequence(a, d, number):
    return number


def sum_arithmetic_series(a, n, d):

    return (n / 2) * (2 * a + (n - 1) * d)


def sum_multiples_of_n_below_k(n, k):
    m = (k-1) // n
    return n * m * (m+1) // 2


def largest_prime_factor(num, div=2):
    while div < num:
        if num % div == 0 and num/div > 1:
            num = num / div
            div = 2
        else:
            div = div + 1
    return num


def lcm(a, b):
    if a > b:
        greater = a
    else:
        greater = b

    while True:
        if greater % a == 0 and greater % b == 0:
            lcm = greater
            break
        greater += 1

    return lcm


def get_lcm_for(your_list):
    return reduce(lambda x, y: lcm(x, y), your_list)


def findDivisor(num):
    # 2,3 are the most common divisor for many numbers hence I go by divisor of 2,3
    # if not then by the same number as divisor
    if num%2 == 0:
        return 2
    elif num%3==0:
        return 3
    return num


def findLCM(lcmArray):
    lcm = 1
    while len(lcmArray) > 0:
        minOfLCMArray = min(lcmArray)
        divisor = findDivisor(minOfLCMArray)

        for x in range(0, len(lcmArray)):
            quotient = lcmArray[x] / divisor
            remainder = lcmArray[x] % divisor
            if remainder == 0:
                lcmArray[x] = quotient

        lcm *= divisor
        minOfLCMArray = min(lcmArray)
        if minOfLCMArray == 1:
            lcmArray.remove(minOfLCMArray)
    return lcm


def round_to_tenths(a) -> float:
    return int(a * 10) / 10


def round_to_nearest_tenth(a) -> float:
    if (10 * a) >= (int((a * 10)) + 0.5):
        return int(1 + a * 10) / 10
    else:
        return int(a * 10) / 10


def mean(arr, n):
    res = 0
    for i in range(n):
        res += arr[i]
    return round_to_tenths(res / n)


def median(arr: list):
    i = len(arr)
    if i != 3:
        if (i % 2) == 0:
            return mean_of_2_median(arr, i)
        else:
            arr2 = deepcopy(arr)
            arr2.sort()
            return arr2[i // 2]
    else:
        arr2 = deepcopy(arr)
        if arr2[2] < arr2[0]:
            swap(arr2, 2, 0)
        if arr2[1] < arr2[0]:
            swap(arr2, 1, 0)
        if arr2[2] < arr2[1]:
            swap(arr2, 2, 1)
        return arr2[1]


def mean_of_2_median(arr, n):
    arr2 = deepcopy(arr)
    arr2.sort()
    a1 = n // 2
    a2 = a1 - 1
    res = (arr2[a1] + arr2[a2]) / 2
    return res


def mode(arr):
    counter = Counter(arr)
    max_count = max(counter.values())
    mode = [k for k, v in counter.items() if v == max_count]
    mode.sort()
    return mode


def array_sum(ar):
    k = 0
    for i in ar:
        k += i
    return k


def weighted_mean(arr: list, weights: list):
    denominator = numerator = 0
    for i in range(len(arr)):
        numerator += (arr[i] * weights[i])
        denominator += weights[i]
    if denominator != 0:
        return round_to_tenths((numerator / denominator))
    else:
        raise ZeroDivisionError


def reduce_fraction(numerator, denominator):
    greatest_factor = abs(math.gcd(numerator, denominator))
    if -1 < greatest_factor <= 1:
        return numerator, denominator
    else:
        return reduce_fraction(numerator // greatest_factor, denominator // greatest_factor)


def swap(arr, x, y):
    # Generic Swap for manipulating list data.
    temp = arr[x]
    arr[x] = arr[y]
    arr[y] = temp


def median_of_3(arr, left, last):
    mid = (left + last) / 2
    if arr[last] < arr[left]:
        left, last = last, left
    if arr[mid] < arr[left]:
        mid, left = left, mid
    if arr[last] < arr[mid]:
        mid, last = last, mid
    return mid


def median_of_3_of_m_o_3(arr, left, middle, last):
    if arr[last] < arr[left]:
        left, last = last, left
    if arr[middle] < arr[left]:
        middle, left = left, middle
    if arr[last] < arr[middle]:
        middle, last = last, middle
    return middle


def ninther_qsort(arr, left, last):
    l = last - left
    l_left = (l // 3 + 1) + left
    l_left2 = (2 * l // 3 + 1) + left
    return median_of_3_of_m_o_3(arr, median_of_3(arr, left, l_left), median_of_3(arr, l_left, l_left2), median_of_3(arr, l_left2, last))

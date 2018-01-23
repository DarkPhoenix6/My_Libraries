from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from copy import deepcopy
from Utils import methoddispatch
import Utils
import sys
IRREDUCIBLE_POLYNOMIAL_DEC = 0x11B,


class GaloisField(object):
    @methoddispatch
    def __init__(self, value, irreducible_polynomial=None, max_field_width=None, degree=None):
        """

        :param value: the value as an int, byte, or string of bits
        :param max_field_width: the maximum number of bits for the field
        :param irreducible_polynomial: an irreducible Polynomial AS A GaliosField object
        :param degree: the degree of the polynomial
        """
        if type(value) == type(bytes):
            self.__init__(self, int.from_bytes(value, sys.byteorder), irreducible_polynomial, max_field_width, degree)
        elif type(value) == type(str):
            self.bin = reversed(list(value[2:]))
            self.bin = [int(bit) for bit in self.bin]
            self.dec = None
            self.bytes = None
            self.hex = None
            self.irreducible_polynomial = irreducible_polynomial
            self.degree = degree
            self.__update_from_bin()
            if max_field_width is not None:
                self.field_width = max_field_width  # an least the degree of the polynomial + 1
            else:
                len(self.bytes) * 8
        else:
            self.dec = int(value)
            self.bytes = None
            self.update_byte_str()
            self.hex = hex(self.dec)[2:]
            bin_str = bin(self.dec)
            self.bin = reversed(list(bin_str[2:]))
            self.bin = [int(bit) for bit in self.bin]
            self.irreducible_polynomial = irreducible_polynomial
            if max_field_width is not None:
                self.field_width = max_field_width                  # an least the degree of the polynomial + 1
            else:
                len(self.bytes) * 8
            if degree is not None:
                self.degree = degree
            else:
                self.degree = len(self.bin) - 1

    @__init__.register(bytes)
    def _(self, value: bytes, irreducible_polynomial=None, degree=None):
        self.__init__(self, int.from_bytes(value, sys.byteorder), irreducible_polynomial, len(value) * 8, degree)

    def __str__(self) -> str:
        h = self.hex
        if self.dec < 16:
            h = '0' + h
        return h

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        if key < len(self.bin):
            return self.bin[key]
        else:
            return 0

    def __setitem__(self, key, value):
        if value in [0, 1]:
            while len(self.bin) <= key:
                self.bin.append(0)
            self.bin[key] = value
        self.__update_from_bin()

    def __lshift__(self, shift):
        return self.dec << shift

    def __rshift__(self, shift):
        return self.dec >> shift

    def __ilshift__(self, shift):
        self.dec = self.dec << shift
        self.__update_from_decimal()

    def __irshift__(self, shift):
        self.dec = self.dec >> shift
        self.__update_from_decimal()

    def __add__(self, x):
        if type(self) == type(x):
            r = GaloisField(self.dec, self.irreducible_polynomial)
            for i, a in enumerate(x.bin):
                r[i] = r[i] ^ a
            r.__update_from_bin()
        else:
            r = GaloisField.gf_add(self.dec, x)
        return r

    def __radd__(self, other):
        return GaloisField.__add__(self, other)

    def __iadd__(self, other):
        if type(other) == type(self):
            self.dec = GaloisField.__add__(self, other).dec
        else:
            self.dec = GaloisField.__add__(self, other)
        self.__update_from_decimal()

    def __sub__(self, other):
        return GaloisField.__add__(self, other)

    def __rsub__(self, other):
        return GaloisField.__sub__(self, other)

    def __isub__(self, other):
        GaloisField.__iadd__(self, other)

    def __mul__(self, x):
        if type(x) == type(self):
            r = GaloisField(0, self.irreducible_polynomial)
            for i, a in enumerate(self.bin):
                for j, b in enumerate(x.bin):
                    if a and b:
                        r[i + j] = r[i + j] ^ 1

            r.__update_from_bin()
            return r
        else:
            return GaloisField.__mul__(self, GaloisField(x)).dec

    def __rmul__(self, other):
        return GaloisField.__mul__(self, other)

    def __pow__(self, x):
        r = GaloisField(1, self.irreducible_polynomial)
        for i in range(1, x+1):
            r = r * GaloisField(self.dec)
            r.__update_from_bin()
            if r.irreducible_polynomial and r.degree >= r.irreducible_polynomial.grade:
                r = r + r.irreducible_polynomial
                r.__update_from_bin()
        return r

    def __rpow__(self, other):
        return GaloisField.__pow__(self, other)

    def __hex__(self) -> hex:
        return hex(self.dec)

    def __oct__(self) -> oct:
        return oct(self.dec)

    def __int__(self) -> int:
        return self.dec

    def __long__(self) -> int:
        return self.dec

    def __bytes__(self) -> bytes:
        return self.bytes

    def __xor__(self, other):
        return self.dec ^ other

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def circular_shift_left(self, shift):
        a = GaloisField.rot_l(self.dec, shift, self.field_width)
        return GaloisField(a, self.irreducible_polynomial, self.field_width, self.degree)

    def circular_shift_right(self, shift):
        a = GaloisField.rot_r(self.dec, shift, self.field_width)
        return GaloisField(a, self.irreducible_polynomial, self.field_width, self.degree)

    def shift_left(self, shift):
        return self.dec << shift

    def shift_right(self, shift):
        return self.dec >> shift

    def __update_from_decimal(self):
        self.update_byte_str()
        hex_str = hex(self.dec)
        self.hex = hex_str[2:]
        bin_str = bin(self.dec)
        self.bin = reversed(list(bin_str[2:]))
        self.bin = [int(bit) for bit in self.bin]
        self.degree = len(self.bin) - 1

    def __update_from_bin(self):
        self.__remove_most_significant_zeros()
        self.dec = 0
        for i, a in enumerate(self.bin):
            if a:
                self.dec += 2**i
        self.update_byte_str()
        self.bin_str = bin(self.dec)
        hex_str = hex(self.dec)
        self.hex = hex_str[2:]
        self.degree = len(self.bin)-1

    def update_byte_str(self):
        if self.dec.bit_length() % 8 == 0:
            bit_length = int(self.dec.bit_length() / 8)  # type: int
        else:
            bit_length = int(self.dec.bit_length() / 8) + 1
        self.bytes = Utils.int_to_bytes(self.dec, bit_length)

    def set_bin(self, bin_str):
        self.bin = reversed(list(bin_str[2:]))
        self.bin = [int(bit) for bit in self.bin]
        self.__update_from_bin()

    def __remove_most_significant_zeros(self):
        last = 0
        for i, a in enumerate(self.bin):
            if a:
                last = i
        del (self.bin[last + 1:])

    @staticmethod
    def gf_add(a, b):
        return a ^ b

    @staticmethod
    def gf_sub(a, b):
        return GaloisField.gf_add(a, b)

    @staticmethod
    def gf_mod_divide(a, b, mod=0x1B):
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

    @staticmethod
    def gf_degree(a):
        res = 0
        a_ = a
        a_ >>= 1
        while a_ != 0:
            a_ >>= 1
            res += 1
        return res

    @staticmethod
    def rot_r(n, rotations=1, width=1):
        """Return a given number of circular bitwise right rotations of an integer n,
           for a given byte field width.
        """
        n_ = n
        rotations %= width * 8  # width bytes give 8*bytes bits
        if rotations < 1:
            return n_
        mask = GaloisField.mask_gen(8 * width)  # store the mask
        n_ &= mask
        return (n_ >> rotations) | ((n_ << (8 * width - rotations)) & mask)  # apply the mask to result

    @staticmethod
    def rot_l(n, rotations=1, width=1):
        """Return a given number of  circular bitwise left rotations of an integer n,
           for a given byte field width.
        """
        n_ = n
        rotations %= width * 8  # width bytes give 8*bytes bits
        if rotations < 1:
            return n_
        mask = GaloisField.mask_gen(8 * width)  # store the mask
        n_ &= mask
        return (n_ << rotations) | ((n_ >> (8 * width - rotations)) & mask)  # apply the mask to result

    @staticmethod
    def mask_gen(bit_length):
        return (2 ** bit_length) - 1

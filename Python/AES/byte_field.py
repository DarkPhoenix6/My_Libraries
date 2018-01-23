from .galios_field import GaloisField, methoddispatch
from copy import deepcopy
import sys

_hexdict = {'0': '0000', '1': '0001', '2': '0010', '3': '0011',
            '4': '0100', '5': '0101', '6': '0110', '7': '0111',
            '8': '1000', '9': '1001', 'a': '1010', 'b': '1011',
            'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}


class ByteField(GaloisField):
    def __init__(self, value, irreducible_polynomial=None, degree=None):
        GaloisField.__init__(self, value, irreducible_polynomial, 8, degree)

    def __mod__(self, other):
        return self.dec % other

    def __rmod__(self, other):
        return other % self.dec

    def __lshift__(self, shift):
        return super().rot_l(self.dec, shift)

    def __rshift__(self, shift):
        return super().rot_r(self.dec, shift)

    def __ilshift__(self, shift):
        self.dec = self.__lshift__(shift)
        self.__update_from_decimal()

    def __irshift__(self, shift):
        self.dec = self.__rshift__(shift)
        self.__update_from_decimal()

    def __invert__(self):
        return self.gf_invert(self.dec)

    def __reversed__(self):
        a = deepcopy(self)
        bs = bin(self.dec)[2:]
        bs.zfill(8)
        bs = bs[::-1]
        bs = "0b" + bs
        a.set_bin(bs)
        return a

    @staticmethod
    def affine_transformation_int(a: int, c=0b01100011):
        a1, a2, a3, a4 = [a for x in range(4)]
        a ^= (ByteField.rot_r(a1, 4) ^ ByteField.rot_r(a2, 5) ^
              ByteField.rot_r(a3, 6) ^ ByteField.rot_r(a4, 7) ^ c)
        return a

    @staticmethod
    def gf_modular_multiply(a, b, mod=0x1B):
        """
        Galois Field (256) Multiplication of two Bytes
        :param a:
        :param b:
        :param mod: x^8 + x^4 + x^3 + x + 1 for AES
        :return:
        """
        a_ = a
        b_ = b
        p = bytes(hex(0x00))
        for i in range(8):
            if (b_ & 1) != 0:
                p ^= a_
            high_bit_set = bytes(a_ & 0x80)
            a_ <<= 1
            if high_bit_set != 0:
                a_ ^= mod
            b_ >>= 1
        return p

    @staticmethod
    def gf_invert(a, mod=0x11B):
        a_ = a
        v = mod
        g1 = 1
        g2 = 0
        j = ByteField.gf_degree(a_) - 8
        while a_ != 1:
            if j < 0:
                a_, v = v, a_
                g1, g2 = g2, g1
                j = -j
            a_ ^= v << j
            g1 ^= g2 << j
            a_ %= 256  # Emulating 8-bit overflow
            g1 %= 256  # Emulating 8-bit overflow
            j = ByteField.gf_degree(a_) - ByteField.gf_degree(v)
        return g1

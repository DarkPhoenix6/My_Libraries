from functools import singledispatch
import Utils
IRREDUCIBLE_POLYNOMIAL_DEC = 0x11B,


class GaloisField(object):
    @singledispatch
    def __init__(self, value: int, irreducible_polynomial=None, max_field_width=8, degree=None):
        """

        :param value: the value
        :param max_field_width: the maximum number of bits for the field
        :param irreducible_polynomial: an irreducible Polynomial AS A GaliosField object
        :param degree: the degree of the polynomial
        """
        self.dec = value
        self.bytes = None
        self.update_byte_str()
        self.hex = hex(self.dec)[2:]
        self.bin = reversed(list(self.bin_str[2:]))
        self.bin = [int(bit) for bit in self.bin]
        self.irreducible_polynomial = irreducible_polynomial
        self.field_width = max_field_width                  # an least the degree of the polynomial + 1
        if degree is not None:
            self.degree = degree
        else:
            self.degree = len(self.bin) - 1

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

    def __hex__(self):
        return hex(self.dec)

    def __oct__(self):
        return oct(self.dec)

    def __int__(self):
        return self.dec

    def __long__(self):
        return self.dec

    def __bytes__(self):
        return self.bytes

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
    def gf_invert(a, mod=0x11B):
        a_ = a
        v = mod
        g1 = 1
        g2 = 0
        j = GaloisField.gf_degree(a_) - 8
        while a_ != 1:
            if j < 0:
                a_, v = v, a_
                g1, g2 = g2, g1
                j = -j
            a_ ^= v << j
            g1 ^= g2 << j
            a_ %= 256  # Emulating 8-bit overflow
            g1 %= 256  # Emulating 8-bit overflow
            j = GaloisField.gf_degree(a_) - GaloisField.gf_degree(v)
        return g1

    @staticmethod
    def rot_r(n, rotations=1, width=1):
        """Return a given number of bitwise right rotations of an integer n,
           for a given bit field width.
        """
        rotations %= width * 8  # width bytes give 8*bytes bits
        if rotations < 1:
            return n
        mask = GaloisField.mask_gen(8 * width)  # store the mask
        n &= mask
        return (n >> rotations) | ((n << (8 * width - rotations)) & mask)  # apply the mask to result

    @staticmethod
    def rot_l(n, rotations=1, width=1):
        """Return a given number of bitwise left rotations of an integer n,
           for a given bit field width.
        """
        rotations %= width * 8  # width bytes give 8*bytes bits
        if rotations < 1:
            return n
        mask = GaloisField.mask_gen(8 * width)  # store the mask
        n &= mask
        return (n << rotations) | ((n >> (8 * width - rotations)) & mask)  # apply the mask to result

    @staticmethod
    def mask_gen(n):
        return (2 ** n) - 1

    @staticmethod
    def affine_transformation_int(a: int, c=0b01100011):
        a1, a2, a3, a4 = [a for x in range(4)]
        a ^= (GaloisField.rot_r(a1, 4) ^ GaloisField.rot_r(a2, 5) ^
              GaloisField.rot_r(a3, 6) ^ GaloisField.rot_r(a4, 7) ^ c)
        return a


@GaloisField.__init__.register()
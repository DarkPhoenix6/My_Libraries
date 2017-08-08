from .byte_field import ByteField
from .galios_field import GaloisField
import sys
DEFAULT_WORD = ByteField(0)


class Word(object):

    def __init__(self, byte_4, byte_3, byte_2, byte_1):
        self.word = []
        for i in [byte_4, byte_3, byte_2, byte_1]:
            if type(i) == type(ByteField):
                self.word.append(i)
            else:
                a = ByteField(i)
                self.word.append(a)

    def __bytes__(self) -> bytes:
        b = b''
        for i in self.word:
            b = b.join(bytes(i))
        return b

    def __str__(self) -> str:
        b = ''
        for i in self.word:
            b = b.join(str(i))
        return b

    def __repr__(self):
        return str(self)

    def __int__(self) -> int:
        return int.from_bytes(self.__bytes__(), sys.byteorder, signed=False)

    def __long__(self) -> int:
        return self.__int__()

    def circular_shift_left(self, shift):
        a = GaloisField(self.__bytes__())
        return a.circular_shift_left(shift)

    def circular_shift_right(self, shift):
        a = GaloisField.rot_r(self.dec, shift, self.field_width)
        return GaloisField(a, self.irreducible_polynomial, self.field_width, self.degree)

    def shift_left(self, shift):
        return self.dec << shift

    def shift_right(self, shift):
        return self.dec >> shift
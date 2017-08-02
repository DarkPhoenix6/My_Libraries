

class GaloisField(object):
    def __init__(self, value: int, field_width=8, irreducible_polynomial=0x11B, degree=None):
        """

        :param value: the value
        :param field_width: the degree of the polynomial + 1
        :param irreducible_polynomial: an irreducible
        :param
        """
        self.dec = value    # type: int
        self.hex_str = hex(value)
        self.hex = self.hex_str[2:]
        self.bin = reversed(list(bin(self.dec)[2:]))
        self.bin = [int(bit) for bit in self.bin]
        self.irreducible_polynomial = irreducible_polynomial
        self.field_width = field_width
        if degree is not None:
            self.degree = degree
        else:
            self.degree = self.field_width - 1

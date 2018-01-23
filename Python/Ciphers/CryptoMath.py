from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import open
from builtins import str
from builtins import range
from builtins import object
from builtins import int
from builtins import bytes
from builtins import chr
from builtins import dict
from builtins import map
from builtins import input
# etc., as needed
from Ciphers.CipherTools import *
from Ciphers.DetectEnglish import DetectEnglish
from Ciphers.FrequencyAnalysis import FrequencyAnalysis
from future import standard_library
standard_library.install_aliases()


class CryptoMath:

    @staticmethod
    def gcd(a, b) -> int:
        """
        using the Euclidean Algorithm
        :param a:
        :param b:
        :return:
        """
        while a != 0:
            a, b = b % a, a
        return b

    @staticmethod
    def find_mod_inverse(a, m):
        """
        finds the modular inverse of 'a'
        :param a:
        :param m: modulus
        :return:
        """

        g, x, y = CryptoMath.gcd_itr(a, m)
        if g != 1:
            # 'a' and 'm' are not relatively prime, therefore no inverse
            return None
        return x % m

    @staticmethod
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

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
from Ciphers.CryptoMath import CryptoMath
from future import standard_library

standard_library.install_aliases()
import sys
import random


class AffineCipher:
    symbols = """ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"""

    @staticmethod
    def get_key_parts(key):
        key_a = key // len(AffineCipher.symbols)
        key_b = key % len(AffineCipher.symbols)
        return key_a, key_b

    @staticmethod
    def check_keys(key_a, key_b, mode):
        if key_a == 1 and mode == 'encrypt':
            sys.exit('The affine cipher becomes incredibly weak when key A is set to 1. Choose a different key.')
        if key_b == 0 and mode == 'encrypt':
            sys.exit('The affine cipher becomes incredibly weak when key B is set to 0. Choose a different key.')
        if key_a < 0 or key_b < 0 or (key_b > len(AffineCipher.symbols) - 1):
            sys.exit(
                'Key A must be greater than 0 and Key B must be between 0 and %s.' % (len(AffineCipher.symbols) - 1))
        if CryptoMath.gcd(key_a, len(AffineCipher.symbols)) != 1:
            sys.exit('Key A (%s) and the symbol set size (%s) are not relatively prime. Choose a different key.' % (
                key_a, len(AffineCipher.symbols)))

    @staticmethod
    def encrypt(key, message):
        key_a, key_b = AffineCipher.get_key_parts(key)
        AffineCipher.check_keys(key_a, key_b, 'encrypt')
        ciphertext = ''
        for symbol in message:
            if symbol in AffineCipher.symbols:
                # encrypt this symbol
                symbol_index = AffineCipher.symbols.find(symbol)
                ciphertext += AffineCipher.symbols[(symbol_index * key_a + key_b) % len(AffineCipher.symbols)]
            else:
                ciphertext += symbol
        return ciphertext

    @staticmethod
    def decrypt(key, ciphertext):
        key_a, key_b = AffineCipher.get_key_parts(key)
        AffineCipher.check_keys(key_a, key_b, 'decrypt')
        plaintext = ''
        mod_inv_of_a = CryptoMath.find_mod_inverse(key_a, AffineCipher)

        for symbol in ciphertext:
            if symbol in AffineCipher.symbols:
                # decrypt this symbol
                symbol_index = AffineCipher.symbols.find(symbol)
                plaintext += AffineCipher.symbols[(symbol_index - key_b) * mod_inv_of_a % len(AffineCipher.symbols)]
            else:
                plaintext += symbol
        return plaintext

    @staticmethod
    def get_random_key():
        while True:
            key_a = random.randint(2, len(AffineCipher.symbols))
            key_b = random.randint(2, len(AffineCipher.symbols))
            if CryptoMath.gcd(key_a, len(AffineCipher.symbols)) == 1:
                return key_a * len(AffineCipher.symbols) + key_b

    @staticmethod
    def crack_affine(ciphertext):
        encryption_break_dict = {}
        for key in

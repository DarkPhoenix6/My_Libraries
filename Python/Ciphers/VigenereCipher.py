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
from future import standard_library

standard_library.install_aliases()


class VigenereCipher(object):
    @staticmethod
    def encrypt(message, key):
        return VigenereCipher.translate_message(message, key, 'encrypt')

    @staticmethod
    def decrypt(message, key):
        return VigenereCipher.translate_message(message, key, 'decrypt')

    @staticmethod
    def translate_message(message: str, key: str, mode: str):
        alphabet = get_alphabet_upper()
        translated = []
        i = 0   # key Index
        key = key.upper()
        len1 = len(alphabet)
        for j in message:  # loop through each character in the message
            num = VigenereCipher.find_symbol(alphabet, j)
            if num != -1:  # -1 means j.upper() was not found in alphabet
                if mode == 'encrypt':
                    num += alphabet.find(key[i])    # add if encrypting
                elif mode == 'decrypt':
                    num -= alphabet.find(key[i])    # subtract if decrypting

                num %= len1  # handle the potential wrap-around

                if j.isupper():
                    translated.append(alphabet[num])
                elif j.islower():
                    translated.append(alphabet[num].lower())
                i += 1
                if i == len1:
                    i = 0
            else:
                # The character was not in alphabet, so add it to translated as it is.
                translated.append(j)
        return ''.join(translated)

    @staticmethod
    def find_symbol(alphabet, j):
        return alphabet.find(j.upper())


class CrackVigenere(VigenereCipher):


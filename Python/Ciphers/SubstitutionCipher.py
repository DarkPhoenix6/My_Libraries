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
from builtins import list
# etc., as needed
from future import standard_library

standard_library.install_aliases()
import sys
import random
from Ciphers import CipherTools


def check_valid_key(key):
    key_list = list(key)
    letters_list = CipherTools.get_alphabet_upper_list()
    key_list.sort()
    if key_list != letters_list:
        sys.exit('There is an error in the key or symbol set.')


def encrypt(message, key):
    return translate_message(message, key, 'encrypt')


def decrypt(message, key):
    return translate_message(message, key, 'decrypt')


def translate_message(message, key, mode='encrypt'):
    translated = ''
    characters_a = CipherTools.get_alphabet_upper()
    characters_b = key
    if mode == 'decrypt':
        # swap
        characters_a, characters_b = characters_b, characters_a

    for symbol in message:
        if symbol.upper() in characters_a:
            symbol_index = characters_a.find(symbol.upper())
            if symbol.isupper():
                translated += characters_b[symbol_index].upper()
            else:
                translated += characters_b[symbol_index].lower()
        else:
            translated += symbol

    return translated


def get_random_key():
    key = CipherTools.get_alphabet_upper()
    random.shuffle(key)
    return ''.join(key)


def get_key_from_keyword(keyword):
    new_key = ''
    keyword = keyword.upper()
    key_alphabet = CipherTools.get_alphabet_upper_list()
    for i in range(len(keyword)):
        if keyword[i] not in new_key:
            new_key += keyword[i]
            key_alphabet.remove(keyword[i])
    return new_key + ''.join(key_alphabet)



if __name__ == '__main__':
    pass

import sys
from BitVector import *
from Python.ModGen.mod_gen import mod_gen
from AES.gen_table import gen_subbytes_table, gen_inv_subbytes_table
from Utils.utils import *


AES_modulus = BitVector(bitstring = '100011011')


@singledispatch
def get_round_keys(key: bytes):
    byte_sub_table = gen_subbytes_table()
    key_words = []
    len1 = len(key)
    if len1 == 16:
        key_words = gen_key_schedule_128(key, byte_sub_table)
    key_schedule = []
    print("\nEach 32-bit word of the key schedule is shown as a sequence of 4 one-byte integers:")
    for word_index, word in enumerate(key_words):
        keyword_in_ints = []
        for i in range(4):
            keyword_in_ints.append(word[i * 8:i * 8 + 8].intValue())
        if word_index % 4 == 0:
            print("\n")
        print("word %d: %s" % (word_index, str(keyword_in_ints)))
        key_schedule.append(keyword_in_ints)
    num_rounds = None
    if len1 == 16:
        num_rounds = 10
    if len1 == 24:
        num_rounds = 12
    if len1 == 32:
        num_rounds = 14
    round_keys = [None for i in range(num_rounds + 1)]
    for i in range(num_rounds + 1):
        round_keys[i] = (str(int_to_bytes(key_words[i * 4])) + str(int_to_bytes(key_words[i * 4 + 1])) +
                         str(int_to_bytes(key_words[i * 4 + 2])) + str(int_to_bytes(key_words[i * 4 + 3])))
    print("\n\nRound keys in hex (first key for input block):\n")
    for round_key in round_keys:
        print(round_key)


def gen_key_schedule_128(key, byte_sub_table):
    key_words = [None for i in range(44)]
    round_constant = 0x01
    for i in range(4):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(4, 44):
        if i % 4 == 0:
            kwd, round_constant = gee(key_words[i - 1], byte_sub_table, round_constant)
            key_words[i] = key_words[i - 4] ^ kwd
        else:
            key_words[i] = key_words[i - 4] ^ key_words[i - 1]
    return key_words


def gen_key_schedule_192(key, byte_sub_table):
    key_words = [None for i in range(52)]
    round_constant = 0x01
    for i in range(6):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(6, 52):
        if i % 6 == 0:
            kwd, round_constant = gee(key_words[i - 1], byte_sub_table, round_constant)
            key_words[i] = key_words[i - 6] ^ kwd
        else:
            key_words[i] = key_words[i - 6] ^ key_words[i - 1]
    return key_words


def gen_key_schedule_256(key, byte_sub_table):
    key_words = [None for i in range(60)]
    round_constant = 0x01
    for i in range(8):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(8, 60):
        if i % 8 == 0:
            kwd, round_constant = gee(key_words[i - 1], byte_sub_table, round_constant)
            key_words[i] = key_words[i - 8] ^ kwd
        elif (i - (i // 8) * 8) < 4:
            key_words[i] = key_words[i - 8] ^ key_words[i - 1]
        elif (i - (i // 8) * 8) == 4:
            key_words[i] = 0
            for j in range(4):
                key_words[i] += byte_sub_table[int(key_words[i - 1][8 * j:8 * j + 8])]
                key_words[i] ^= key_words[i - 8]
        elif (i - (i // 8) * 8) > 4 and ((i - (i // 8) * 8) < 8):
            key_words[i] = key_words[i - 8] ^ key_words[i - 1]
        else:
            sys.exit("error in key scheduling algo for i = %d" % i)
    return key_words


def gee(word, byte_sub_table, round_constant=0x01):
    rotated_word = rot_word(word)
    new_word = [0x00] * 4
    for i in range(4):
        new_word[i] = byte_sub_table[int(rotated_word[i])]
    new_word[0] = round_constant
    round_constant ^= gf_modular_mul(round_constant, 0x02)
    return new_word, round_constant


def rot_word(word: bytes):
    word2 = bytearray(word)
    w3 = word2.pop(3)
    word2.insert(0, w3)
    return word2


def r_con(word):
    """
    round Constant
    :param word:
    :return:
    """
import sys
# from BitVector import *
from Python.ModGen.mod_gen import mod_gen
# from AES.gen_table import gen_subbytes_table, gen_inv_subbytes_table
from Utils.utils import *


# AES_modulus = BitVector(bitstring = '100011011')

byte_sub_table = gen_subbytes_table()


def get_round_keys(key: bytes):
    key_words = []
    len1 = len(key)
    num_rounds = None
    if len1 == 16:
        key_words = gen_key_schedule_128(key)
    if len1 == 24:
        key_words = gen_key_schedule_192(key)
    if len1 == 32:
        key_words = gen_key_schedule_256(key)
    key_schedule = []
    for word_index, word in enumerate(key_words):
        keyword_in_ints = []
        for i in range(4):
            keyword_in_ints.append(word[i])
        key_schedule.append(keyword_in_ints)
    return key_schedule


def get_round_keys_verbose(key: bytes):
    key_words = []
    len1 = len(key)
    num_rounds = None
    if len1 == 16:
        key_words = gen_key_schedule_128(key)
        num_rounds = 10
    if len1 == 24:
        key_words = gen_key_schedule_192(key)
        num_rounds = 12
    if len1 == 32:
        key_words = gen_key_schedule_256(key)
        num_rounds = 14
    key_schedule = []
    print("\nEach 32-bit word of the key schedule is shown as a sequence of 4 one-byte integers:")
    for word_index, word in enumerate(key_words):
        keyword_in_ints = []
        for i in range(4):
            keyword_in_ints.append(word[i])
        if word_index % 4 == 0:
            print("\n")
        print("word %d: %s" % (word_index, str(keyword_in_ints)))
        key_schedule.append(keyword_in_ints)

    round_keys = [None for i in range(num_rounds + 1)]
    for i in range(num_rounds + 1):
        round_keys[i] = (show_hex_2(key_words[i * 4]) + show_hex_2(key_words[i * 4 + 1]) +
                         show_hex_2(key_words[i * 4 + 2]) + show_hex_2(key_words[i * 4 + 3]))
    print("\n\nRound keys in hex (first key for input block):\n")
    for round_key in round_keys:
        print(round_key)
    return key_schedule


def gen_key_schedule_128(key):
    key_words = [None for i in range(44)]
    round_constant = 0x01
    for i in range(4):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(4, 44):
        if i % 4 == 0:
            kwd, round_constant = gee(key_words[i - 1], round_constant)
            key_words[i] = xor_bytes(key_words[i - 4], bytes(kwd))
            # print(round_constant)
        else:
            key_words[i] = xor_bytes(key_words[i - 4], key_words[i - 1])
    return key_words


def gen_key_schedule_192(key):
    key_words = [None for i in range(52)]
    round_constant = 0x01
    for i in range(6):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(6, 52):
        if i % 6 == 0:
            kwd, round_constant = gee(key_words[i - 1], round_constant)
            key_words[i] = xor_bytes(key_words[i - 6], bytes(kwd))
        else:
            key_words[i] = xor_bytes(key_words[i - 6], key_words[i - 1])
    return key_words


def gen_key_schedule_256(key):
    key_words = [None for i in range(60)]
    round_constant = 0x01
    for i in range(8):
        key_words[i] = key[i * 4: i * 4 + 4]
    for i in range(8, 60):
        if i % 8 == 0:
            kwd, round_constant = gee(key_words[i - 1], round_constant)
            key_words[i] = xor_bytes(key_words[i - 8], bytes(kwd))
        elif (i - (i // 8) * 8) < 4:
            key_words[i] = xor_bytes(key_words[i - 8], key_words[i - 1])
        elif (i - (i // 8) * 8) == 4:
            key_words[i] = []
            for j in range(4):
                key_words[i].append(byte_sub_table[int(key_words[i - 1][j])])
            key_words[i] = xor_bytes(key_words[i - 8], key_words[i])
        elif (i - (i // 8) * 8) > 4 and ((i - (i // 8) * 8) < 8):
            key_words[i] = xor_bytes(key_words[i - 8], key_words[i - 1])
        else:
            sys.exit("error in key scheduling algo for i = %d" % i)
    return key_words


def gee(word, round_constant=0x01):
    rotated_word = rot_word(word)
    new_word = [0x00] * 4
    for i in range(4):
        new_word[i] = byte_sub_table[int(rotated_word[i])]
    new_word[0] ^= round_constant
    round_constant = gf_modular_mul(round_constant, 0x02)
    return new_word, round_constant


def rot_word(word: bytes):
    word2 = bytearray(word)
    w3 = word2.pop(0)
    word2.insert(3, w3)
    return word2


def show_hex_2(data):
    if type(data) == type(b'0'):
        return ''.join([format(data[i], '02x') for i in range(len(data))])
    return format(data, '02x')


def r_con(word):
    """
    round Constant
    :param word:
    :return:
    """


def set_key(key, keysize=128):
    return key + '0' * (keysize // 8 - len(key)) if len(key) < keysize // 8 else key[:keysize // 8]


if __name__ == '__main__':
    key = b'\x02L\x1e\x9e\xe7\x13\x0c\xac\xf8j\xd7\xbe`\x87\xe9\xd7'
    # get_round_keys(key)
    key2 = 'hello'
    key2 = set_key(key2, 128)
    key3 = bytes(key2, 'ascii')
    k = get_round_keys_verbose(key3)
    k2 = bytes([0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c])
    key4 = int_to_bytes(0x2b7e151628aed2a6abf7158809cf4f3c, 16)

    key5 = set_key(key2, 256)
    key6 = bytes(key5, 'ascii')
    k3 = get_round_keys_verbose(key6)
    # for i in range(16):
    #     print(key4[i])
    k4 = bytes([0x8e, 0x73, 0xb0, 0xf7, 0xda, 0x0e, 0x64, 0x52, 0xc8, 0x10, 0xf3, 0x2b, 0x80, 0x90, 0x79, 0xe5, 0x62, 0xf8, 0xea, 0xd2, 0x52, 0x2c, 0x6b, 0x7b])
    k6 = bytes([0x60, 0x3d, 0xeb, 0x10, 0x15, 0xca, 0x71, 0xbe, 0x2b, 0x73, 0xae, 0xf0, 0x85, 0x7d, 0x77, 0x81, 0x1f, 0x35, 0x2c, 0x07, 0x3b, 0x61, 0x08, 0xd7, 0x2d, 0x98, 0x10, 0xa3, 0x09, 0x14, 0xdf, 0xf4])
    get_round_keys_verbose(k2)
    get_round_keys_verbose(k4)
    get_round_keys_verbose(k6)



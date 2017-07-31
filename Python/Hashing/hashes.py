import hashlib
import binascii
import os
import struct
import sys
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Python.ModGen.mod_gen import mod_gen
from functools import singledispatch
from bitstring import BitArray
from base64 import b16encode
from pylibscrypt import scrypt
from ctypes import string_at
import unittest
import ctypes


MISSING = object()
backend = default_backend()
salt = os.urandom(16)


class Crypto(object):

    def __init__(self, iv=b'2222222222222222', key=MISSING):
        if key == MISSING:
            self.key = os.urandom(32)
        self.iv = bytes(binascii.a2b_qp(iv))
        self.aes_mode = modes.CBC(self.iv)
        self.cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()

    @staticmethod
    def aes_enc(plain_text, key, iv=b'2222222222222222'):
        pt = bytes(Crypto.padder(binascii.a2b_qp(plain_text)))
        mode = modes.CBC(bytes(iv))
        cipher = Cipher(algorithms.AES(key), mode, backend=backend)
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(pt) + encryptor.finalize()
        return cipher_text

    @staticmethod
    def aes_dec(cipher_text, key, iv=b'2222222222222222'):
        ct = bytes(binascii.a2b_qp(cipher_text))
        mode = modes.CBC(bytes(iv))
        cipher = Cipher(algorithms.AES(key), mode, backend=backend)
        decryptor = cipher.decryptor()
        pt = decryptor.update(ct) + decryptor.finalize()
        plain_text = Crypto.unpadder(pt)
        return plain_text

    @staticmethod
    def padder(data, padding_size=128):
        padder = padding.PKCS7(padding_size).padder()
        padded_data = padder.update(bytes(binascii.a2b_qp(data)))
        padded_data += padder.finalize()
        return padded_data

    @staticmethod
    def unpadder(padded_data, padding_size=128):
        unpadder = padding.PKCS7(padding_size).unpadder()
        data = unpadder.update(bytes(binascii.a2b_qp(padded_data)))
        data += unpadder.finalize()
        return data

    @staticmethod
    def dark_phoenix6_hash(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222', rounds=13):
        return Crypto.dp6_hash(plain_text, key, iv, rounds)

    @staticmethod
    def dp6_hash(plain_text, key, iv, rounds=1):
        blocks = Crypto.split_and_pad_blocks(plain_text)
        cipher_text_blocks = Crypto.dp6_algorithm(blocks, iv, key, rounds)
        hast_text = b''.join(cipher_text_blocks)
        return hast_text

    @staticmethod
    def dp6_algorithm(blocks, iv, key, rounds=1, count=0):
        if count == rounds:
            return blocks
        else:
            cipher_text_blocks = [b'0'] * len(blocks)
            for i in range(0, len(blocks)):
                l = [i for i in mod_gen(len(blocks), len(blocks), i + 1)][0]
                current_ptext = Crypto.join_blocks(blocks, l)
                cipher_text_blocks[i], iv = Crypto.aes_hasher(current_ptext, key, iv)
            return Crypto.dp6_algorithm(cipher_text_blocks, iv, key, rounds, 1 + count)

    @staticmethod
    def aes_hasher(data, key, iv):
        cipher_text = Crypto.aes_enc(data, key, iv)
        iv2 = Crypto.split_to_blocks(cipher_text, 128)
        return iv2[-1], iv2[-1]

    @staticmethod
    def aes_encryption(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222'):
        blocks = Crypto.split_and_pad_blocks(plain_text)
        padded_plain_text = b''.join(blocks)
        ciphertext = Crypto.aes_enc(padded_plain_text, key, iv)
        return ciphertext

    @staticmethod
    def aes_decryption(cipher_text, key, iv=b'2222222222222222'):
        ct = bytes(binascii.a2b_qp(cipher_text))
        padded_plain_text = Crypto.aes_dec(ct, key, iv)
        plain_text_array = bytearray(binascii.a2b_qp(padded_plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array)
        blocks[-1] = Crypto.unpadder(blocks[-1], 128)
        plain_text = b''.join(blocks)
        return plain_text

    @staticmethod
    def split_to_blocks(plain_text_array, blocksize=128):
        blocks = MISSING
        blocksize_bytes = int(blocksize / 8)
        array_blocksize_bytes = int(len(plain_text_array) / blocksize_bytes)
        count = 0
        for i in range(0, array_blocksize_bytes):
            if blocks == MISSING:
                blocks = [bytes(plain_text_array[i:blocksize_bytes])]
            else:
                k = i * blocksize_bytes
                blocks += [bytes(plain_text_array[k:k + blocksize_bytes])]
            count = i
        if len(plain_text_array) % blocksize_bytes != 0:
            if blocks == MISSING:
                blocks = [bytes(plain_text_array)]
            else:
                k = count * blocksize_bytes
                blocks += [bytes(plain_text_array[k + blocksize_bytes:])]
        return blocks

    @staticmethod
    def split_and_pad_blocks(plain_text, blocksize=128):
        plain_text_array = bytearray(binascii.a2b_qp(plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array, blocksize)
        blocks[-1] = Crypto.padder(blocks[-1], 128)
        return blocks

    @staticmethod
    def flip_bits(data: bytes):
        bin_data = BitArray(data)
        bin_data.invert()
        return bytes(bin_data.bytes)

    @staticmethod
    def reverse(data):
        data2 = data[::-1]
        return data2

    @staticmethod
    def cut_the_deck(data: bytes):
        data2 = b''.join([data[int(len(data)/2):], data[:int(len(data)/2)]])
        return data2

    @staticmethod
    def rotate_blocks(blocks, position=2):
        l = [i for i in mod_gen(len(blocks), len(blocks), position + 1)][0]
        rotated_blocks = Crypto.join_blocks(blocks, l)
        return rotated_blocks

    @staticmethod
    def join_blocks(blocks, iter_list=MISSING):
        if iter_list == MISSING:
            iter_list = [i for i in mod_gen(len(blocks), len(blocks), 1)][0]
        joined_blocks = b''.join(blocks[int(i)] for i in iter_list)
        return joined_blocks

    @staticmethod
    def sha2_512(data):
        digest = hashes.Hash(hashes.SHA512(), backend=backend)
        digest.update(data)
        return digest.finalize()

    @staticmethod
    @singledispatch
    def sha3_512(data):
        digest = hashlib.sha3_512()
        digest.update(bytes(data))
        return digest.digest()

    @staticmethod
    def whirlpool_512(data):
        digest = hashes.Hash(hashes.Whirlpool(), backend=backend)
        digest.update(data)
        return digest.finalize()

    @staticmethod
    def blake2b_512(data):
        digest = hashes.Hash(hashes.BLAKE2b(64), backend=backend)
        digest.update(data)
        return digest.finalize()

    @staticmethod
    def scrypt_512(data, salt_ = MISSING):
        if salt_ == MISSING:
            salt_ = Crypto.split_to_blocks(data)[0]
        digest = b16encode(scrypt(data, salt_))
        return digest

    @staticmethod
    def add_entropy(data, rounds=):
        return Crypto.add_entropy_sub(data, rounds)

    @staticmethod
    def add_entropy_sub(data, rounds):
        if rounds < 1:
            padded_blocks = Crypto.split_and_pad_blocks(data, 32)
            reversed_blocks = Crypto.reverse(padded_blocks)
            return Crypto.join_blocks(reversed_blocks)
        else:
            padded_blocks = Crypto.split_and_pad_blocks(data, 32)
            rotated_blocks = Crypto.rotate_blocks(padded_blocks, rounds + 2)
            entropy0 = Crypto.reverse(rotated_blocks)
            entropy1 = Crypto.cut_the_deck(entropy0)
            entropy2 = Crypto.flip_bits(entropy1)
            entropy3 = Crypto.xor_(Crypto.join_blocks(padded_blocks), entropy2)
            return Crypto.add_entropy_sub(entropy3.hex(), rounds - 1)

    @staticmethod
    def xor_(var: bytes, key: bytes):
        key = key[:len(var)]
        int_var = int.from_bytes(var, sys.byteorder)
        int_key = int.from_bytes(key, sys.byteorder)
        int_enc = int_var ^ int_key
        return int_enc.to_bytes(len(var), sys.byteorder)


@Crypto.sha3_512.register(bytes)
def _(data: bytes):
    digest = hashlib.sha3_512()
    digest.update(data)
    return digest.digest()


class Header(object):

    def __init__(self, version: ctypes.c_int32, merkle_root: str, previous_block_hash: str, time_: ctypes.c_uint64,
                 bits: ctypes.c_uint64, nonce: ctypes.c_uint32):
        """

        :param merkle_root:64 bytes
        :param version:
        :param previous_block_hash: 64 bytes
        :param time_: 8 bytes long
        :param bits: 4 bytes long is used to calculate difficulty
        :param nonce: 4 Bytes
        """
        self.version = version
        self.previous_block_hash = previous_block_hash
        self.merkle_root = merkle_root
        self.time_ = time_
        self.difficulty_bits = bits
        self.nonce = nonce
        self.h = (struct.pack("<L", version) + bytes.fromhex(previous_block_hash)[::-1] +
                  bytes.fromhex(merkle_root)[::-1] + struct.pack("<LLL", time_, bits, nonce))
        self.header = (string_at(ctypes.pointer(self.version)) + bytes.fromhex(previous_block_hash)[::-1] +
                       bytes.fromhex(merkle_root)[::-1] + string_at(ctypes.pointer(self.time_)) +
                       string_at(ctypes.pointer(self.difficulty_bits)) + string_at(ctypes.pointer(self.nonce)))

    def modify_nonce(self, nonce: ctypes.c_uint):
        self.nonce = nonce
        self.modify_header()

    def modify_header(self):
        self.h = (struct.pack("<L", self.version) + bytes.fromhex(self.previous_block_hash)[::-1] +
                  bytes.fromhex(self.merkle_root)[::-1] + struct.pack("<LLL", self.time_, self.difficulty_bits,
                                                                      self.nonce))
        self.header = (string_at(ctypes.pointer(self.version)) + bytes.fromhex(self.previous_block_hash)[::-1] +
                       bytes.fromhex(self.merkle_root)[::-1] + string_at(ctypes.pointer(self.time_)) +
                       string_at(ctypes.pointer(self.difficulty_bits)) + string_at(ctypes.pointer(self.nonce)))


class Hashes(Crypto):
    @staticmethod
    @singledispatch
    def x22_hash(data, rounds=22):
        hash0 = Hashes.x22(data, rounds)
        return hash0

    @staticmethod
    def x22(data, rounds=22):
        if rounds < 1:
            return data
        else:
            return Hashes.x22(Hashes.x22_hashes(data), rounds - 1)

    @staticmethod
    def x22_hashes(data):
        entropy0 = Hashes.add_entropy(data)
        hash0 = Hashes.blake2b_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.sha3_512(Hashes.blake2b_512(Hashes.whirlpool_512(entropy0))))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.sha3_512(Hashes.blake2b_512(Hashes.whirlpool_512(entropy0))))
        return hash0

    @staticmethod
    def x25(data):
        entropy0 = Hashes.add_entropy(data)
        hash0 = Hashes.scrypt_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.dark_phoenix6_hash(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.scrypt_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.sha3_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.scrypt_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.whirlpool_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.scrypt_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.blake2b_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.scrypt_512(Hashes.scrypt_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.blake2b_512(Hashes.scrypt_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.whirlpool_512(Hashes.scrypt_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.sha3_512(Hashes.scrypt_512(entropy0))
        entropy0 = Hashes.add_entropy(hash0)
        hash0 = Hashes.dark_phoenix6_hash(Hashes.scrypt_512(entropy0))
        return hash0


@Hashes.x22_hash.register(Header)
def _(data: Header):
    hash0 = Hashes.x22(data.header)
    return hash0


class TestCrypto(unittest.TestCase):
    """ Basic unit tests for Rectangle"""

    def test_aes_encryption(self):
        """ Tests the generation of a roof quadrilateral """
        key = b'u\x1eE\xd6\x9bn\x0b\x82\x13\r\xf5:\xc2Ii\xb7K\xa9_\xd3N\x10V\x17\xfb\x1e\xd9\xa7\xa9.\x0b\xe4'
        iv = b'\x02L\x1e\x9e\xe7\x13\x0c\xac\xf8j\xd7\xbe`\x87\xe9\xd7'
        pt = b'passwordqasswordsasswordmasswordbasswordtasswordcassworddasswordfasswordwasswordvassword'
        pt2 = b'passwordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpassword'
        ct = Crypto.aes_encryption(pt, key, iv)
        ct2 = Crypto.aes_encryption(pt2, key, iv)
        pt3 = Crypto.aes_decryption(ct, key, iv)
        pt4 = Crypto.aes_decryption(ct2, key, iv)
        self.assertEqual(pt3, pt)
        self.assertEqual(pt4, pt2)

    def test_block_split(self):
        blocks = Crypto.split_to_blocks(
            b'passwordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpassword')

    def test_aes_hash(self):
        key = b'u\x1eE\xd6\x9bn\x0b\x82\x13\r\xf5:\xc2Ii\xb7K\xa9_\xd3N\x10V\x17\xfb\x1e\xd9\xa7\xa9.\x0b\xe4'
        pt = b'passwordqasswordsasswordmasswordbasswordtasswordcassworddasswordfasswordwasswordvassword'
        iv = bytes(b'2222222222222222')
        ct = Crypto.dark_phoenix6_hash(pt, key, iv)
        ciphertext = binascii.hexlify(ct)
        self.assertEqual(ciphertext, b'e57cc212185f31a524b0d96758d7d0ea8130094733ff751dc8c3ae00d6c23b2472e655dbdb3d4637'
                                     b'987f75aba80a775a834c2abe5d30bf7da401c68230b44ab18206b652814dfc1f58d3f8ba6535953c'
                                     b'8135ab0c9c3d36e12d37181477254762')

    def test_bitflip(self):
        bits = 0b1101000011001010110110001101100011011110010000001110111011011110111001001101100011001
        bits2 = bytes(bin(bits), 'utf-8')
        bits3 = Crypto.flip_bits(bits2)
        new_bits = Crypto.flip_bits(b'2222222222222222')
        self.assertEqual(bits3,
                         b'\xcf\x9d\xce\xce\xcf\xce\xcf\xcf\xcf\xcf\xce\xce\xcf\xcf\xce\xcf\xce\xcf\xce\xce\xcf\xce\xce'
                         b'\xcf\xcf\xcf\xce\xce\xcf\xce\xce\xcf\xcf\xcf\xce\xce\xcf\xce\xce\xce\xce\xcf\xcf\xce\xcf\xcf'
                         b'\xcf\xcf\xcf\xcf\xce\xce\xce\xcf\xce\xce\xce\xcf\xce\xce\xcf\xce\xce\xce\xce\xcf\xce\xce\xce'
                         b'\xcf\xcf\xce\xcf\xcf\xce\xce\xcf\xce\xce\xcf\xcf\xcf\xce\xce\xcf\xcf\xce')
        self.assertEqual(new_bits, b'\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd\xcd')
        self.assertEqual(Crypto.flip_bits(new_bits), b'2222222222222222')
        self.assertEqual(Crypto.flip_bits(bits3), bits2)

    def test_x22(self):
        print(Hashes.x22_hash(b'1101000011001010110110001101100011011110010000001110111011011110111001001101100011001', 1))


# Won't run if imported
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCrypto)
    unittest.TextTestRunner(verbosity=2).run(suite)

import hashlib, binascii
import os
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Python.ModGen.mod_gen import mod_gen, list_mod_gen
from bitstring import BitArray
import unittest
MISSING = object()
backend = default_backend()


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
    def aes_enc(plain_text, key, iv=b'2222222222222222', keysize=256):
        pt = bytes(Crypto.padder(binascii.a2b_qp(plain_text)))
        if len(bytes(Crypto.padder(binascii.a2b_qp(key), keysize))) != keysize:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key), keysize))
        else:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key), keysize))
        mode = modes.CBC(bytes(binascii.a2b_qp(iv)))
        cipher = Cipher(algorithms.AES(byte_key), mode, backend=backend)
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(pt) + encryptor.finalize()
        return cipher_text

    @staticmethod
    def aes_decryption(cipher_text, key, iv=b'2222222222222222', keysize=MISSING):
        ct = bytes(binascii.a2b_qp(cipher_text))
        if keysize != MISSING:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key, keysize)))
        else:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key)))
        mode = modes.CBC(bytes(binascii.a2b_qp(iv)))
        cipher = Cipher(algorithms.AES(byte_key), mode, backend=backend)
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
    def aes_hash(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222', keysize=256):
        plain_text_array = bytearray(binascii.a2b_qp(plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array)
        blocks[-1] = Crypto.padder(blocks[-1], 128)
        cipher_text_blocks = [0] * len(blocks)
        for i in range(0, len(blocks)):
            l = [i for i in mod_gen(len(blocks), len(blocks), i)][0]
            current_ptext = b''.join(blocks[int(i)] for i in l)
            cipher_text_blocks[i], iv = Crypto.aes_hasher(current_ptext, key, iv, keysize)
        hast_text = b''.join(cipher_text_blocks)
        return hast_text

    @staticmethod
    def aes_hasher(data, key, iv, keysize):
        cipher_text = Crypto.aes_enc(data, key, iv, keysize)
        iv2 = Crypto.split_to_blocks(cipher_text, 128)
        return iv2, iv2

    @staticmethod
    def aes_encryption(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222', keysize=256):
        plain_text_array = bytearray(binascii.a2b_qp(plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array)
        blocks[-1] = Crypto.padder(blocks[-1], 128)
        padded_plain_text = b''.join(blocks)
        ciphertext = Crypto.aes_enc(padded_plain_text, key, iv, keysize)
        return ciphertext

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
    def flip_bits(data):
        bytes_data = bytes(data)
        bin_data = BitArray(bytes_data)
        for i in range(len(bin_data)):
            bin_data = Crypto.flip_bit(bin_data, i)
        return bytes(bin_data)

    @staticmethod
    def flip_bit(number, n):
        mask = (0b1 << n - 1)
        result = number ^ mask
        return bin(result)

    @staticmethod
    def reverse(data):
        data2 = data[len(data) - 1:-1:-1]
        return data2


class TestCrypto(unittest.TestCase):
    """ Basic unit tests for Rectangle"""

    def test_aes_encryption(self):
        """ Tests the generation of a roof quadrilateral """
        key = b'u\x1eE\xd6\x9bn\x0b\x82\x13\r\xf5:\xc2Ii\xb7K\xa9_\xd3N\x10V\x17\xfb\x1e\xd9\xa7\xa9.\x0b\xe4'

    def test_block_split(self):
        blocks = Crypto.split_to_blocks(
            b'passwordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpassword')

    def test_aes_hash(self):
        key = b'u\x1eE\xd6\x9bn\x0b\x82\x13\r\xf5:\xc2Ii\xb7K\xa9_\xd3N\x10V\x17\xfb\x1e\xd9\xa7\xa9.\x0b\xe4'
        pt = b'passwordqasswordsasswordmasswordbasswordtasswordcassworddasswordfasswordwasswordvassword'
        iv = b'2222222222222222'
        ct = Crypto.aes_hash(pt, key, iv, 256)
        print(ct)

# Won't run if imported
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCrypto)
    unittest.TextTestRunner(verbosity=2).run(suite)

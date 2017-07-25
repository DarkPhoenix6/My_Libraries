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
    def aes_enc(plain_text, key, iv=b'2222222222222222', keysize=MISSING):
        pt = bytes(Crypto.padder(binascii.a2b_qp(plain_text)))
        if keysize != MISSING:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key, keysize)))
        else:
            byte_key = bytes(Crypto.padder(binascii.a2b_qp(key)))
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
    def aes_hash(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222', keysize=MISSING):
        plain_text_array = bytearray(binascii.a2b_qp(plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array)
        blocks[-1] = Crypto.padder(blocks[-1], 128)
        cipher_text_blocks = [] * len(blocks)
        for i in range(len(blocks)):
            l = list_mod_gen(blocks, len(blocks), i)


    @staticmethod
    def aes_encryption(plain_text, key=b'22222222222222220123456789012345', iv=b'2222222222222222', keysize=MISSING):
        plain_text_array = bytearray(binascii.a2b_qp(plain_text))
        blocks = Crypto.split_to_blocks(plain_text_array)
        blocks[-1] = Crypto.padder(blocks[-1], 128)
        padded_plain_text = b''.join(blocks)

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


class TestCrypto(unittest.TestCase):
    """ Basic unit tests for Rectangle"""

    def test_aes_encryption(self):
        """ Tests the generation of a roof quadrilateral """
        key = b'u\x1eE\xd6\x9bn\x0b\x82\x13\r\xf5:\xc2Ii\xb7K\xa9_\xd3N\x10V\x17\xfb\x1e\xd9\xa7\xa9.\x0b\xe4'


    def test_block_split(self):
        blocks = Crypto.split_to_blocks(
            b'passwordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpassword')


# Won't run if imported
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCrypto)
    unittest.TextTestRunner(verbosity=2).run(suite)

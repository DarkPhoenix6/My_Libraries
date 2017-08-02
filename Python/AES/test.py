import unittest
from Python.AES.gen_key_schedule import *


class TestAES(unittest.TestCase):

    def test_128_keygen(self):
        key = b'\x02L\x1e\x9e\xe7\x13\x0c\xac\xf8j\xd7\xbe`\x87\xe9\xd7'
        get_round_keys(key)


# Won't run if imported
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAES)
    unittest.TextTestRunner(verbosity=2).run(suite)

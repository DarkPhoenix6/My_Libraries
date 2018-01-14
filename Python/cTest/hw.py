# file: hw.py
# cython: language_level=3


def hello_world():
    import sys
    print("Welcome to Python %d.%d!" % sys.version_info[:2])


if __name__ == '__main__':
    hello_world()

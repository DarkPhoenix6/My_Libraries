def get_alphabet() -> str:
    return 'abcdefghijklmnopqrstuvwxyz'


def get_alphabet_upper() -> str:
    return get_alphabet().upper()


def get_alphabet_list() -> list:
    return [i for i in get_alphabet()]


def get_alphabet_dict() -> dict:
    a = {}
    for i in get_alphabet():
        a[i] = 0
    return a


def enum_alphabet():
    return [i for i in enumerate(get_alphabet_list())]


def split_string(in_str):
    b = in_str.replace(",", " ")
    e = b.replace(".", " ")
    a = e.split(" ")
    return a


def count_letters(in_str: str) -> dict:
    a = get_alphabet_dict()
    for i in in_str:
        for j in i:
            if j in a.keys():
                a[j] += 1
    return a


def find_symbol(alphabet, j):
    return alphabet.find(j.upper())


def is_empty(test_structure):
    if test_structure:
        return False
    else:
        return True

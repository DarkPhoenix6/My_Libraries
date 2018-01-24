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


def get_alphabet_upper_dict() -> dict():
    a = {}
    for i in get_alphabet_upper():
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


def memoize(fn):
    """returns a memoized version of any function that can be called
    with the same list of arguments.
    Usage: foo = memoize(foo)
    WORKING!!!
    """

    def handle_item(x):
        if isinstance(x, dict):
            return make_tuple(sorted(x.items()))
        elif hasattr(x, '__iter__'):
            return make_tuple(x)
        else:
            return x

    def make_tuple(L):
        return tuple(handle_item(x) for x in L)

    def foo(*args, **kwargs):
        items_cache = make_tuple(sorted(kwargs.items()))
        args_cache = make_tuple(args)
        if (args_cache, items_cache) not in foo.past_calls:
            foo.past_calls[(args_cache, items_cache)] = fn(*args, **kwargs)
        return foo.past_calls[(args_cache, items_cache)]
    foo.past_calls = {}
    foo.__name__ = 'memoized_' + fn.__name__
    return foo


def add_to_enc_break_dict(break_dict, key, dec_message, message_len_to_show=100):
    break_dict[key] = dec_message[:message_len_to_show]

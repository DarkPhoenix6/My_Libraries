from __future__ import division
from MultiMethod.multimethod import multimethod


@multimethod(int, int, int)
def mod_gen(n, m, s=0):
    """
    Generator function that yields n tuples of m length containing consecutive indices within bounds n
    Such that the set of tuples generated from mod_gen(3, 3) would be ((2, 0, 1), (0, 1, 2), (1, 2, 0))
    :param n: The number of tuples to generate and the bounds of the indices in the tuple
    :param m: The number of indices per tuple
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(n):
        yield(tuple([(i + k + s) % n for k in range(int(m/2)-m+1, int(m/2+1))]))


@multimethod(int, int, int, int)
def mod_gen(n, m, num, s=0):
    """
    Generator function that yields n tuples of m length containing consecutive indices within bounds n
    Such that the set of tuples generated from mod_gen(3, 3) would be ((2, 0, 1), (0, 1, 2), (1, 2, 0))
    :param n: The bounds of the indices in the tuple
    :param m: The number of indices per tuple
    :param num: The number of tuples to generate
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(num):
        yield(tuple([(i + k + s) % n for k in range(int(m/2)-m+1, int(m/2+1))]))


@multimethod(object, int, int)
def list_mod_gen(iterable, m, s=0, **num):
    """ Generator function that yields n tuples of m length containing consecutive list elements within bounds n
    Such that the set of tuples generated from list_mod_gen([a, b, c], 3) would be ((c, a, b), (a, b, c), (b, c, a))
    :param iterable: An iterable object with which we wish to iterate over consecutive elements
    :param m: The number of consecutive elements required
    :param s: The starting index, defaults to 0
    :return: Yields the next tuple in the set
    """
    for i in range(len(iterable)):
        yield(tuple(iterable[(i + k + s) % len(iterable)] for k in range(int(m/2)-m+1, int(m/2)+1)))


def center_sum(iterable):
    """ Sums up the contents of a list putting more weight on the center
    :param iterable: the list
    :return: the sum of the list with more weight on the center
    """
    center = int((len(iterable)+1)/2) - 1
    return sum([a * (float(center) / float(abs(center - i) + 1)) for i, a in enumerate(iterable)])


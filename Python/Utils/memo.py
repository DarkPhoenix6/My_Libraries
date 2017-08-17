def memoize(f):
    memo = {}
    def helper(x):
        if x not in memo:
            memo[x] = f(x)
        return memo[x]
    return helper


class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
    def __call__(self, *args):
        if args not in self.memo:
	    self.memo[args] = self.fn(*args)
        return self.memo[args]


def memoize(function):
    from functools import wraps

    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


def memoize(fn):
    """returns a memoized version of any function that can be called
    with the same list of arguments.
    Usage: foo = memoize(foo)"""

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
            foo.past_calls[(args_cache, items_cache)] = fn(*args,**kwargs)
        return foo.past_calls[(args_cache, items_cache)]
    foo.past_calls = {}
    foo.__name__ = 'memoized_' + fn.__name__
    return foo

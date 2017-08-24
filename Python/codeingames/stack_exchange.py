import sys
import math


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

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

@memoize
def subs(x, y):
    return x - y

@memoize
def check_vals(val1, val2, losses=0):
    return losses < subs(val1, val2)

@memoize
def check_val2(val1, val2):
    return val1 < val2

n = int(input())
vals = []
for i in input().split():
    v = int(i)
    vals.append(v)
print("Debug messages...", vals, file=sys.stderr)
vals = sorted(enumerate(vals, 1), key=lambda x: x[1], reverse=True)
vals1, vals2 = vals[:len(vals) // 2], vals[len(vals) // 2:]
print("Debug messages...", vals, file=sys.stderr)

#for i in range(len(vals) - 1):
#    if not vals[i][1] in checked_dict:
#        for j in range(len(vals) - 1, i, -1):
#            if check_val2(vals[i][0], vals[j][0]) and check_vals(vals[i][1], vals[j][1]):
#                losses = subs(vals[i][1], vals[j][1])
#                break
#            elif check_val2(vals[i][0], vals[j][0]) and 0 < subs(vals[i][1], vals[j][1]):
#                break
#        checked_dict[vals[i][1]] = [0]


def check_loop(arr: list, arr2, count=0, losses=0, max_recursions=995):
    checked_dict = {}
    losses1 = losses
    if len(arr) == 0 and len(arr2) == 0:
        return losses
    elif len(arr) != 0 and len(arr2) == 0:
        for i in range(len(arr) - 1):
            if not arr[i][1] in checked_dict:
                for j in range(len(arr) - 1, i, -1):
                    if check_val2(arr[i][0], arr[j][0]) and check_vals(arr[i][1], arr[j][1], losses1):
                        losses1 = subs(arr[i][1], arr[j][1])
                        break
                    elif check_val2(arr[i][0], arr[j][0]) and 0 < subs(arr[i][1], arr[j][1]):
                        break
                checked_dict[arr[i][1]] = [0]
        return losses1
    elif len(arr) == 0 and len(arr2) != 0:
        for i in range(len(arr2) - 1):
            if not arr2[i][1] in checked_dict:
                for j in range(len(arr2) - 1, i, -1):
                    if check_val2(arr2[i][0], arr2[j][0]) and check_vals(arr2[i][1], arr2[j][1], losses1):
                        losses1 = subs(arr2[i][1], arr2[j][1])
                        break
                    elif check_val2(arr2[i][0], arr2[j][0]) and 0 < subs(arr2[i][1], arr2[j][1]):
                        break
                checked_dict[arr2[i][1]] = [0]
        return losses1
    elif count < max_recursions:
        for i in range(len(arr)):
            if not arr[i][1] in checked_dict:
                for j in range(len(arr2) - 1, -1, -1):
                    if check_val2(arr[i][0], arr2[j][0]) and check_vals(arr[i][1], arr2[j][1], losses1):
                        losses1 = subs(arr[i][1], arr2[j][1])
                        break
                    elif check_val2(arr[i][0], arr2[j][0]) and 0 < subs(arr[i][1], arr2[j][1]):
                        break
                checked_dict[arr[i][1]] = [0]
        if losses1 == 0:
            vals1, vals2 = arr[:len(arr) // 2], arr[len(arr) // 2:]
            vals3, vals4 = arr2[:len(arr2) // 2], arr2[len(arr2) // 2:]
            losses1 = check_loop(vals1, vals2, count + 1)
            losses2 = check_loop(vals3, vals4, count + 1)
            return max(losses1, losses2)
        else:
            return losses1
    else:
        for i in range(len(arr) - 1):
            if not arr[i][1] in checked_dict:
                for j in range(len(arr) - 1, i, -1):
                    if check_val2(arr[i][0], arr[j][0]) and check_vals(arr[i][1], arr[j][1], losses1):
                        losses1 = subs(arr[i][1], arr[j][1])
                        break
                    elif check_val2(arr[i][0], arr[j][0]) and 0 < subs(arr[i][1], arr[j][1]):
                        break
                checked_dict[arr[i][1]] = [0]
        checked_dict = {}
        losses2 = 0
        for i in range(len(arr2) - 1):
            if not arr2[i][1] in checked_dict:
                for j in range(len(arr2) - 1, i, -1):
                    if check_val2(arr2[i][0], arr2[j][0]) and check_vals(arr2[i][1], arr2[j][1], losses2):
                        losses2 = subs(arr2[i][1], arr2[j][1])
                        break
                    elif check_val2(arr2[i][0], arr2[j][0]) and 0 < subs(arr2[i][1], arr2[j][1]):
                        break
                checked_dict[arr2[i][1]] = [0]
        return max(losses1, losses2)


# Write an action using print
# To debug: print("Debug messages...", file=sys.stderr)

print(0 - check_loop(vals1, vals2))

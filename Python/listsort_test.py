import random
from time import clock as now


def fill(n):
    from random import random
    return [random() for i in range(n)]


def mycmp(x, y):
    global ncmp
    ncmp += 1
    return cmp(x, y)


def timeit(values, method):
    global ncmp
    X = values[:]
    bound = getattr(X, method)
    ncmp = 0
    t1 = now()
    bound(mycmp)
    t2 = now()
    return t2-t1, ncmp


format = "%5s  %9.2f  %11d"
f2 = "%5s  %9.2f  %11.2f"

def drive():
    count = sst = sscmp = mst = mscmp = nelts = 0
    while True:
        n = random.randrange(100000)
        nelts += n
        x = fill(n)

        t, c = timeit(x, 'sort')
        sst += t
        sscmp += c

        t, c = timeit(x, 'sort')
        mst += t
        mscmp += c

        count += 1
        if count % 10:
            continue

        print ("count", count, "nelts", nelts)
        print (format % ("sort",  sst, sscmp))
        print (format % ("sort2", mst, mscmp))
        print (f2 % ("", (sst-mst)*1e2/mst, (sscmp-mscmp)*1e2/mscmp))
        if (count % 100) == 0:
            break

drive()


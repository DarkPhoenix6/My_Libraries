# numpy and scipy are available for use
# Aeneas' cryptographic disc (4th c. B.C.)
import numpy
import scipy


mem = {}
letters_deg = {}


# a simple parser for python. use get_number() and get_word() to read
def parser():
    while 1:
        data = list(input().split(' '))
        for number in data:
            if len(number) > 0:
                yield(number)


input_parser = parser()


def get_word():
    global input_parser
    return next(input_parser)


def get_number():
    data = get_word()
    try:
        return int(data)
    except ValueError:
        return float(data)


r = get_number()
rad_sqr = r ** 2
mem[180] = r + r


def calc_distance(angle, radius):
    global mem
    if angle in mem:
        return mem.get(angle)
    else:
        if angle == 0:
            mem[angle] = 0
        elif angle == 90 or angle == 270:
            c_sqrd = rad_sqr + rad_sqr
            mem[angle] = numpy.sqrt(c_sqrd)
        else:
            c_sqrd = rad_sqr + rad_sqr - (2 * rad_sqr) * (numpy.cos(numpy.deg2rad(angle)))
            mem[angle] = numpy.sqrt(c_sqrd)
        return mem[angle]


for i in range(26):
    letter = get_word()
    angle = get_number()
    letters_deg[letter] = angle


ptext = input()
ptext = filter(str.isalpha, ptext)
ptext = "".join(ptext).upper()

dist = r
l1 = ptext[0]
for i in range(1,len(ptext)):
    l2 = ptext[i]
    ang = abs(letters_deg.get(l2) - letters_deg.get(l1))
    dist += calc_distance(ang, r)
    l1 = ptext[i]

if int(dist) < dist:
    dist = int(dist) + 1
print(dist)

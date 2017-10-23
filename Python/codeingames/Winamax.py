import sys
import math
import resource
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
grid = []
move_dict = {"up": "^",
             "down": "v",
             "left": "<",
             "right": ">"}


width, height = [int(i) for i in input().split()]
print("Debug messages...", width, height, file=sys.stderr)
for i in range(height):
    row = input()
    grid.append(row)
    print("Debug messages...", row, file=sys.stderr)
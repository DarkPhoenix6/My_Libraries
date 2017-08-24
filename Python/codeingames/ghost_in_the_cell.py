import sys
import math
from functools import reduce

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

factory_count = int(input())  # the number of factories
link_count = int(input())  # the number of links between factories
for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]


class Entity(object):
    def __init__(self, entity_id, entity_type, arg_1):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.owner = arg_1


class Factory(Entity):
    def __init__(self, entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5):
        Entity.__init__(self, entity_id, entity_type, arg_1)
        self.population = arg_2
        self.production = arg_3
        self.arg_4 = arg_4
        self.arg_5 = arg_5


class Troops(Entity):
    def __init__(self, entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5):
        Entity.__init__(self, entity_id, entity_type, arg_1)
        self.source = arg_2
        self.destination = arg_3
        self.population = arg_4
        self.e_t_a = arg_5


# game loop
troop = "TROOP"
factory = "FACTORY"
neutral = "NEUTRAL"
e_factory = "ENEMY_FACTORY"
while True:
    entity_dict = {
        troop: [],
        factory: [],
        neutral: [],
        e_factory: []
    }

    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for i in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        entity_id = int(entity_id)
        arg_1 = int(arg_1)
        arg_2 = int(arg_2)
        arg_3 = int(arg_3)
        arg_4 = int(arg_4)
        arg_5 = int(arg_5)
        if entity_type == factory:
            entity_dict[factory].append(Factory(entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5))
        else:
            entity_dict[troop].append(Factory(entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    entity_dict[e_factory] = sorted([i for i in entity_dict[factory] if i.owner == -1], key=lambda x: x.population)
    entity_dict[neutral] = sorted([i for i in entity_dict[factory] if i.owner == 0], key=lambda x: x.production,
                                  reverse=True)
    entity_dict[factory] = sorted([i for i in entity_dict[factory] if i.owner == 1], key=lambda x: x.population,
                                  reverse=True)
    # Any valid action, such as "WAIT" or "MOVE source destination cyborgs"
    source = entity_dict.get(factory)[0]
    my_guys = sum(map(lambda x: x.population, entity_dict.get(factory)))
    commands = ""
    for i in entity_dict.get(factory):
        count = i.population
        while count > 10:
            for j in entity_dict.get(neutral):
                if count <= 10:
                    break
                else:
                    commands = "".join(commands + "MOVE " + str(i.entity_id) + " " + str(j.entity_id) + " " +
                                       str(int(count // 10)) + ";")
                    count -= count // 10
            for j in entity_dict.get(e_factory):
                if count <= 10:
                    break
                else:
                    commands = "".join(commands + "MOVE " + str(i.entity_id) + " " + str(j.entity_id) + " " +
                                       str(int(count // 10)) + ";")
                    count -= count // 10
    if not commands:
        print("WAIT")
    else:
        print(commands[:-1])
    # if my_guys >= 50:
    #     if entity_dict.get(neutral):
    #         print("MOVE " + str(source.entity_id) + " " + str(entity_dict.get(neutral)[0].entity_id) + " " + str(
    #             int(source.population // 10)))
    #     elif entity_dict.get(e_factory):
    #         print("MOVE " + str(source.entity_id) + " " + str(entity_dict.get(e_factory)[0].entity_id) + " " + str(
    #             int(source.population // 10)))
    #     else:
    #         print("WAIT")

    # else:
    #     print("WAIT")

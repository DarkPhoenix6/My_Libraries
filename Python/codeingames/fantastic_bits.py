import sys
import math


# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.

class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def square_distance(self, other_point):
        """ Calculates the square distance between this Point2D and another Point2D

        :param other_point: The other Point2D
        :return: The Square Distance
        :rtype: float
        """
        return (self.x - other_point.x) ** 2 + (self.y - other_point.y) ** 2

    def __eq__(self, other_point):
        """ Override the equals operator to compare coordinates

        :param other_point: The other Point2D
        :return: True if points are equal else False
        :type: bool
        """
        return self.x == other_point.x and self.y == other_point.y

    def to_dict(self):
        """ Converts point to python dict

        :return: dict of x,y coordinates
        :rtype: dict
        """
        return {"x": self.x, "y": self.y}

    def slope(self, other_point):
        """ Calculates the slope between this point and another Point2D

        :param other_point: The other point to find the slope with
        :return: Slope as a float
        """
        # TODO Find a better way to handle this error
        if self.x == other_point.x:
            raise None
        # cast to float just in case there is an integer passed in
        return (self.y - other_point.y) / float(self.x - other_point.x)

    def angle_deg(self, other_point):
        """ Calculates the angle in degrees between this point and another Point2D

        :param other_point: The other Point2D
        :return: The angle in Degrees
        """
        if self.x != other_point.x:
            return 180 * math.atan(other_point.slope(self)) / math.pi

        return 90 if other_point.y > self.y else -90

    def pos_angle_deg(self, other_point):
        angle = self.angle_deg(other_point)
        return angle if angle >= 0 else angle + 180.0

    def __str__(self):
        return "Point2D({},{})".format(self.x, self.y)

    def __add__(self, other):
        if type(other) == type(self):
            return Point2D(self.x + other.x, self.y + other.y)
        else:
            return Point2D(self.x + other, self.y + other)

    def __radd__(self, other):
        return Point2D.__add__(self, other)

    @staticmethod
    def find_distance(point1, point2):
        """ finds the distance between points

        :param point1:
        :param point2:
        :return:
        """
        result = math.sqrt(point2.square_distance(point1))
        return result


class Entity(object):
    def __init__(self, position: Point2D, velocity: Point2D, state: int, entity_id: int):
        self.position = position
        self.velocity = velocity
        self.state = state
        self.entity_id = entity_id
        self.velocity_position = self.position + self.velocity
        self.guardian = False
        self.attacker = True

    def find_distance(self, entity2):
        """ finds the distance between points

        :param point2:
        :return:
        """
        return Point2D.find_distance(self.position, entity2.position)

    def find_angle(self, entity2):
        a_b = self.find_distance(entity2)
        a_c = Point2D.find_distance(self.position, self.velocity_position)
        b_c = Point2D.find_distance(entity2.position, self.velocity_position)
        # print("Debug messages...", a_b, a_c, b_c, file=sys.stderr)
        if (-2 * a_c * a_b * b_c) == 0:
            return math.pi
        else:
            top = ((b_c ** 2) - (a_c ** 2) - (a_b ** 2))
            bottom = (-2 * a_c * a_b)
            # print("Debug messages...", top, bottom, file=sys.stderr)

            angle_a = math.acos(top / bottom)
            return angle_a

    def find_thrust(self, entity2):
        thrust_ = abs(int(math.cos(self.find_angle(entity2)) * 150))


def find_closest(entity1, entity_dict, key):
    itr = 0
    lowest = None
    place = 0
    for j in entity_dict.get(key):
        low_check = entity1.find_distance(j)
        # print("Debug messages...D", key, low_check, file=sys.stderr)
        if (lowest is None or low_check < lowest):
            place = itr
            lowest = low_check
        itr += 1
    ent = entity_dict.get(key)[place]
    return ent, lowest


my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left
my_goal = Point2D(0, 3750) if my_team_id == 0 else Point2D(16000, 3750)
obliv_count = 5
cast_obliv = False
mana = 0
cntr_pt = Point2D(8000, 3750)
# game loop
while True:
    mana += 1
    my_score, my_magic = [int(i) for i in input().split()]
    opponent_score, opponent_magic = [int(i) for i in input().split()]
    entities = int(input())  # number of entities still in game
    entity_dict = {
        "WIZARD": [],
        "OPPONENT_WIZARD": [],
        "SNAFFLE": [],
        "BLUDGER": []
    }
    if obliv_count == 5:
        cast_obliv = False
    else:
        obliv_count += 1

    for i in range(entities):
        # entity_id: entity identifier
        # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
        # x: position
        # y: position
        # vx: velocity
        # vy: velocity
        # state: 1 if the wizard is holding a Snaffle, 0 otherwise
        magic = False
        entity_id, entity_type, x, y, vx, vy, state = input().split()
        entity_id = int(entity_id)
        x = int(x)
        y = int(y)
        vx = int(vx)
        vy = int(vy)
        state = int(state)
        # print("Debug messages...", entity_type, x, y, file=sys.stderr)
        entity_dict[entity_type].append(Entity(Point2D(x, y), Point2D(vx, vy), state, entity_id))
    # print("Debug messages...", entity_dict, file=sys.stderr)
    if len(entity_dict.get("SNAFFLE")) == 1:
        if Point2D.find_distance(entity_dict.get("WIZARD")[0].position, my_goal) <= Point2D.find_distance(
                entity_dict.get("WIZARD")[1].position, my_goal):
            entity_dict.get("WIZARD")[0].guardian = True
            entity_dict.get("WIZARD")[1].guardian = False
        else:
            entity_dict.get("WIZARD")[1].guardian = True
            entity_dict.get("WIZARD")[0].guardian = False
    for i in range(2):

        wiz = entity_dict.get("WIZARD")[i]

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        if wiz.state == 0 and not wiz.guardian:
            nearest_snaffle, nearest_snaffle_dist = find_closest(wiz, entity_dict, "SNAFFLE")
            nearest_bludger, nearest_bludger_dist = find_closest(wiz, entity_dict, 'BLUDGER')
            nearest_other_wiz, nearest_other_wiz_dist = find_closest(wiz, entity_dict, "OPPONENT_WIZARD")
            # print("Debug messages...", nearest_bludger, nearest_snaffle_dist, nearest_bludger_dist, nearest_other_wiz_dist, file=sys.stderr)
            if (mana > 25 or (mana % 17 == 0 and mana != 0)) and (
                (nearest_snaffle_dist > 5222) or len(entity_dict.get("SNAFFLE")) <= 2) and magic == False:
                magic = True
                print("ACCIO " + str(nearest_snaffle.entity_id))
                mana -= 15
            elif (mana > 32 or (mana % 22 == 0 and mana != 0)) and (
                nearest_snaffle_dist > nearest_other_wiz.find_distance(nearest_snaffle)):
                magic = True
                mana -= 20
                print("FLIPENDO " + str(nearest_other_wiz.entity_id))
            elif (mana > 32 or (mana % 22 == 0 and mana != 0)) and (nearest_bludger_dist < 3000):
                magic = True
                mana -= 20
                print("FLIPENDO " + str(nearest_bludger.entity_id))
            elif (mana > 25 or (mana % 17 == 0 and mana != 0)) and (
                nearest_snaffle_dist > nearest_other_wiz.find_distance(nearest_snaffle)) and magic == False:
                magic = True
                print("ACCIO " + str(nearest_snaffle.entity_id))
                mana -= 15
            elif (mana > 22 or (mana % 12 == 0 and mana != 0)) and magic == False and nearest_other_wiz_dist < 5222:
                magic = True
                mana -= 10
                print("PETRIFICUS " + str(nearest_other_wiz.entity_id))
            elif (((mana % 6 == 0 and mana != 0 and nearest_bludger_dist <= 3000) or (
                    mana > 16 and nearest_bludger_dist <= 5222)) and nearest_bludger_dist < nearest_other_wiz_dist) and cast_obliv == False:
                obliv_count = 0
                cast_obliv = True
                # magic = True
                print("OBLIVIATE " + str(nearest_bludger.entity_id))
                mana -= 5
            else:
                itr = 0
                lowest = None
                place = 0
                for j in entity_dict.get("SNAFFLE"):
                    low_check = wiz.find_distance(j)
                    if (lowest is None or low_check < lowest) and j.state == 0:
                        place = itr
                        lowest = low_check
                    itr += 1
                ent = entity_dict.get("SNAFFLE")[place]
                thrust = entity_dict.get("WIZARD")[i].find_thrust(ent)
                # print("Debug messages...", thrust, file=sys.stderr)
                print("MOVE " + str(ent.velocity_position.x) + " " + str(ent.velocity_position.y) + " " + str(150))
        elif wiz.guardian:
            nearest_snaffle, nearest_snaffle_dist = find_closest(wiz, entity_dict, "SNAFFLE")
            nearest_bludger, nearest_bludger_dist = find_closest(wiz, entity_dict, 'BLUDGER')
            nearest_other_wiz, nearest_other_wiz_dist = find_closest(wiz, entity_dict, "OPPONENT_WIZARD")
            if entity_dict.get("WIZARD")[i].state == 1:
                if Point2D.find_distance(center_pt, entity_dict.get("WIZARD")[i].position) > Point2D.find_distance(
                        entity_dict.get("WIZARD")[i].position, entity_dict.get("WIZARD")[i - 1].position):
                    print("THROW " + str(entity_dict.get("WIZARD")[i - 1].position.x) + " " + str(
                        entity_dict.get("WIZARD")[i - 1].position.y) + " " + "500")
                else:
                    if my_team_id == 0:
                        print("THROW " + str(16000) + " " + str(3750) + " " + "500")
                    else:
                        print("THROW " + str(0) + " " + str(3750) + " " + "500")
            elif (mana > 32 or (mana % 22 == 0 and mana != 0)) and (
                nearest_snaffle_dist > nearest_other_wiz.find_distance(nearest_snaffle)):
                # magic = True
                mana -= 20
                print("FLIPENDO " + str(nearest_other_wiz.entity_id))
            elif (mana > 22 or (mana % 12 == 0 and mana != 0)) and nearest_other_wiz.find_distance(
                    nearest_snaffle) < 5222:
                # magic = True
                mana -= 10
                print("PETRIFICUS " + str(nearest_other_wiz.entity_id))
            elif nearest_snaffle_dist < 5000:
                print("MOVE " + str(nearest_snaffle.velocity_position.x) + " " + str(
                    nearest_snaffle.velocity_position.y) + " " + str(150))
            else:
                if my_team_id == 0:
                    print("MOVE " + str(122) + " " + str(3750) + " " + "150")
                else:
                    print("MOVE " + str(15878) + " " + str(3750) + " " + "150")
        elif entity_dict.get("WIZARD")[i].state == 1:
            if my_team_id == 0:
                print("THROW " + str(16000) + " " + str(3750) + " " + "500")
            else:
                print("THROW " + str(0) + " " + str(3750) + " " + "500")
        else:
            print("MOVE 8000 3750 100")
            # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
            # i.e.: "MOVE x y thrust" or "THROW x y power"


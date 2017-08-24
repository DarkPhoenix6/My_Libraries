from __future__ import division
import sys
import math


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
            return None
        # cast to float just in case there is an integer passed in
        return (self.y - other_point.y) / float(self.x - other_point.x)

    def angle_deg(self, other_point):
        """ Calculates the angle in degrees between this point and another Point2D

        :param other_point: The other Point2D
        :return: The angle in Degrees
        """
        if self.x != other_point.x:
            slope = other_point.slope(self)
            if slope is not None:
                return 180 * math.atan(slope) / math.pi
            else:
                # vertical line
                return None
        return 90 if other_point.y > self.y else -90

    def pos_angle_deg(self, other_point):
        angle = self.angle_deg(other_point)
        return angle if angle >= 0 else angle + 180.0

    @staticmethod
    def intersect(point1, point2, point3, point4):
        """
        caluculating the intersecting point that will be the new node
        :param point1:
        :param point2:
        :param point3:
        :param point4:
        :return:
        """
        c = (point2.y - point1.y) * (point3.x - point4.x) - (point1.x - point2.x) * (point4.y - point3.y)
        if c != 0:
            return Point2D(((point3.x - point4.x) * (point1.x * point2.y - point2.x * point1.y) - (point1.x - point2.x)
                            * (point3.x * point4.y - point4.x * point3.y)) / c,
                           (-(point4.y - point3.y) * (point1.x * point2.y - point2.x * point1.y) + (point2.y - point1.y)
                            * (point3.x * point4.y - point4.x * point3.y)) / c)
        else:
            return None

    @staticmethod
    def intersect_xy_mp(m, point1, point2, point3):
        """
        caluculating the intersecting point that will be the new node
        :param m: slope
        :param point1:
        :param point2:
        :param point3:
        :return:
        """
        c = m * (point3.x - point2.x) + point2.y - point3.y
        if abs(m) < 100:
            if c != 0:
                x_ = ((point3.x - point2.x) * (m * point1.x - point1.y + point2.y) + (point2.y - point3.y) * point2.x) \
                     / c
                return Point2D(x_, m * (x_ - point1.x) + point1.y)
        elif point3.x != point2.x:
            return Point2D(point1.x, (point1.y - point2.y) * (point3.y - point2.y) / (point3.x - point2.x) + point2.y)
        return Point2D((point1.x + point2.x + point3.x) / 3, (point1.y + point2.y + point3.y) / 3)

    def y_intercept(self, other):
        slope = other.slope(self)
        b = -1 * slope * self.x + self.y
        return b

    def __str__(self):
        return "Point2D({},{})".format(self.x, self.y)

    def __mul__(self, other):
        if type(other) == type(self):
            return Point2D(self.x * other.x, self.y * other.y)
        else:
            return Point2D(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Point2D.__mul__(self, other)

    def __add__(self, other):
        if type(other) == type(self):
            return Point2D(self.x + other.x, self.y + other.y)
        else:
            return Point2D(self.x + other, self.y + other)

    def __radd__(self, other):
        return Point2D.__add__(self, other)

    def __sub__(self, other):
        if type(other) == type(self):
            return Point2D(self.x - other.x, self.y - other.y)
        else:
            return Point2D(self.x - other, self.y - other)

    def __rsub__(self, other):
        return Point2D.__sub__(other, self)

    def __truediv__(self, other):
        if type(other) == type(self):
            return Point2D(self.x / other.x, self.y / other.y)
        else:
            return Point2D(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        return Point2D.__truediv__(other, self)

    @staticmethod
    def find_distance(point1, point2):
        """ finds the distance between points

        :param point1:
        :param point2:
        :return:
        """
        result = math.sqrt(point2.square_distance(point1))
        return result


class Zones(Point2D):
    def __init__(self, x, y):
        super(Zones, self).__init__(x, y)


class Drone(Point2D):
    def __init__(self, x, y, player_id, drone_number, loop_count):
        Point2D.__init__(self, x, y)
        self.player_id = player_id
        self.drone_number = drone_number
        self.loop_count = loop_count

    def closest_zone(self, zones: list):
        closest_zone_ = Point2D(0, 0)
        closest_dist_ = 10000
        for i in zones:
            dist = Drone.find_distance(self, i)
            if dist < closest_dist_:
                closest_dist_, closest_zone_ = dist, i
        return closest_zone_

    def update(self, x, y, player_id, drone_number, loop_count):
        self.x = x
        self.y = y
        self.player_id = player_id
        self.drone_number = drone_number
        self.loop_count = loop_count

            # Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# p: number of players in the game (2 to 4 players)
# id: ID of your player (0, 1, 2, or 3)
# d: number of drones in each team (3 to 11)
# z: number of zones on the map (4 to 8)
p, id, d, z = [int(i) for i in input().split()]
zones = []
for i in range(z):
    # x: corresponds to the position of the center of a zone. A zone is a circle with a radius of 100 units.
    x, y = [int(j) for j in input().split()]
    zones.append(Point2D(x, y))
loop_count = -1
drone_dict = {
    0: [],
    1: [],
    2: [],
    3: []
}
# game loop
while True:
    loop_count += 1
    for i in range(z):
        tid = int(
            input())  # ID of the team controlling the zone (0, 1, 2, or 3) or -1 if it is not controlled. The zones are given in the same order as in the initialization.
    for i in range(p):
        for j in range(d):
            # dx: The first D lines contain the coordinates of drones of a player with the ID 0, the following D lines those of the drones of player 1, and thus it continues until the last player.
            dx, dy = [int(k) for k in input().split()]
            if loop_count < 1:
                drone_dict[i].append(Drone(dx, dy, i, j, loop_count))
            else:
                drone_dict[i][j].update(dx, dy, i, j, loop_count)
    for i in range(d):
        drone = drone_dict.get(id)[i]
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)
        close_zone = drone.closest_zone(zones)

        # output a destination point to be reached by one of your drones. The first line corresponds to the first of your drones that you were provided as input, the next to the second, etc.
        print(str(close_zone.x) + " " + str(close_zone.y))

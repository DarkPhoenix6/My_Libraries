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

    def pythagoras_find_c(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

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


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
class Mars(object):
    def __init__(self, x_arr: list, y_arr: list):
        self.x_arr = x_arr
        self.y_arr = y_arr
        self.surface = []
        self.flat_spots = []
        self.gravity = 3.711
        self.target = Point2D(0, 0)
        for i in range(len(self.x_arr)):
            self.surface.append(Point2D(self.x_arr[i], self.y_arr[i]))
            if (i + 1) != len(self.x_arr):
                temp = self.surface[-1]
                temp2 = Point2D(self.x_arr[i + 1], self.y_arr[i + 1])
                if (temp2.x - temp.x) >= 1000 and temp2.y == temp.y:
                    self.flat_spots = [temp, temp2]
                    self.target = Point2D(temp2.x - temp.x, temp.y)
                slope = temp.slope(temp2)
                b = temp.y_intercept(temp2)
                if slope is not None:
                    for j in range(1, self.x_arr[i + 1] - self.x_arr[i]):
                        self.surface.append(Point2D(j, ((j * slope) + b)))
                else:
                    pass


class MarsLander(object):
    def __init__(self, mars: Mars, x, y, h_velocity, v_velocity, fuel, rotation, power):
        self.mars = mars
        self.current_position = Point2D(x, y)
        self.current_velocity = Point2D(h_velocity, v_velocity)
        self.velocity_angle = math.atan2(self.current_velocity.y, self.current_velocity.x)
        self.fuel = fuel
        self.rotation = rotation
        self.power = power

    def calculate_trajectory(self, target: Point2D):
        temp = self.current_position + (self.current_velocity * 3)
        print("Debug messages... Calculating Trajectory", temp, target, file=sys.stderr)
        if temp.x - target.x != 0:
            trajectory = temp.angle_deg(target)
            # TODO
            if temp.y < target.y:
                return int(trajectory) * -1
            else:
                return int(trajectory) * -1
        elif self.current_position.x - target.x != 0:

            trajectory = temp.angle_deg(target)
            # TODO
            if temp.y < target.y:
                return int(trajectory) * -1
            else:
                return int(trajectory) * -1
        else:
            return 0

    def angle_of_reach(self, distance):
        return (1 / 2) * math.asin(self.mars.gravity * distance / (self.current_velocity.pythagoras_find_c() ** 2))

    def distance_traveled(self):
        v = self.current_velocity.pythagoras_find_c()
        theta = self.velocity_angle
        g = self.mars.gravity
        result1 = v * math.cos(theta) / g
        result2 = (v * math.sin(theta)) + math.sqrt(((v * math.sin(theta)) ** 2) + 2 * g * self.current_position.y)
        return result1 * result2

    def time_of_flight(self):
        v = self.current_velocity.pythagoras_find_c()
        d = self.distance_traveled()
        result =
        return d /
    def landing_sequence(self):
        print("Debug messages... Initiaing Landing Sequence", file=sys.stderr)
        if (self.mars.flat_spots[0].x + 10) <= self.current_position.x <= (self.mars.flat_spots[1].x - 10):
            if -20 < self.current_velocity.x < 20:
                print("Debug messages... 1", file=sys.stderr)
                if self.current_velocity.y <= -30:
                    inst = "0 4"
                else:
                    inst = "0 2"
            else:
                print("Debug messages... 2", file=sys.stderr)
                inst = self.cancel_x_velocity()
        else:
            if -20 < self.current_velocity.x < 20:
                print("Debug messages... 3", file=sys.stderr)
                if self.mars.target.y < self.current_position.y:
                    trajectory = int(self.calculate_trajectory(self.mars.target))
                    if self.current_velocity.y <= -30:
                        power2 = 4
                    else:
                        power2 = 3
                    inst = str(trajectory) + " " + str(power2)
                else:
                    trajectory = int(self.calculate_trajectory(Point2D(self.mars.target.x, self.mars.target.y + 200)))
                    power2 = 4
                    inst = str(trajectory) + " " + str(power2)
            else:
                print("Debug messages... 4", file=sys.stderr)
                inst = self.cancel_x_velocity()
        return inst

    def cancel_x_velocity(self):
        if -15 > self.current_velocity.x:
            if -33 > self.current_velocity.x:
                trajectory = str(-62)
                power2 = str(4)
            elif -15 > self.current_velocity.x:

                if self.current_velocity.y <= -30:
                    power2 = str(4)
                    trajectory = str(-30)
                else:
                    power2 = str(4)
                    trajectory = str(-45)
            else:
                if self.current_velocity.y <= -30:
                    trajectory = str(-45)
                else:
                    trajectory = str(-73)
                power2 = str(4)

        else:
            if 33 < self.current_velocity.x:
                trajectory = str(62)
                power2 = str(4)
                if self.current_velocity.y <= -30:
                    power2 = str(4)
                    trajectory = str(30)
                else:
                    power2 = str(4)
                    trajectory = str(45)
            else:
                if self.current_velocity.y <= -30:
                    trajectory = str(45)
                else:
                    trajectory = str(73)
                power2 = str(4)
        inst = trajectory + " " + power2
        return inst


surface_n = int(input())  # the number of points used to draw the surface of Mars.
x = []
y = []
for k in range(surface_n):
    # land_x: X coordinate of a surface point. (0 to 6999)
    # land_y: Y coordinate of a surface point. By linking all the points together in a sequential fashion, you form the surface of Mars.
    land_x, land_y = [int(j) for j in input().split()]
    x.append(land_x)
    y.append(land_y)
# game loop
mars = Mars(x, y)
while True:
    # h_speed: the horizontal speed (in m/s), can be negative.
    # v_speed: the vertical speed (in m/s), can be negative.
    # fuel: the quantity of remaining fuel in liters.
    # rotate: the rotation angle in degrees (-90 to 90).
    # power: the thrust power (0 to 4).
    x1, y1, h_speed, v_speed, fuel, rotate, power = [int(i) for i in input().split()]
    lander = MarsLander(mars, x1, y1, h_speed, v_speed, fuel, rotate, power)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    if lander.mars.flat_spots[0].x > lander.mars.flat_spots[1].x:
        lander.mars.flat_spots[0], lander.mars.flat_spots[1] = lander.mars.flat_spots[1], lander.mars.flat_spots[0]
    if ((lander.mars.flat_spots[0].x - 1000) <= lander.current_position.x <= (
                lander.mars.flat_spots[1].x + 1000)) and lander.current_position.y > lander.mars.target.y:
        comm = lander.landing_sequence()
        print(comm)
    # rotate power. rotate is the desired rotation angle. power is the desired thrust power.
    else:
        print(str(lander.calculate_trajectory(lander.mars.target)) + " 4")

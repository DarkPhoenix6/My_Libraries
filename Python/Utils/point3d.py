from .utils import methoddispatch
import math

class Point3D(object):
    """ Simple 2D Point2D representation with some utility functions"""

    @methoddispatch
    def __init__(self, x, y, z):
        """ Constructor for Point2D
        :param x: x coord
        :param y: y coord
        """
        self.x = x
        self.y = y
        self.z = z

    def square_distance(self, other_point):
        """ Calculates the square distance between this Point3D and another Point3D

        :param other_point: The other Point2D
        :return: The Square Distance
        :rtype: float
        """
        return (self.x - other_point.x) ** 2 + (self.y - other_point.y) ** 2 + (self.z - other_point.z) ** 2

    def unit_vector(self, other_point):
        """Calculates the 2D UnitVector between this Point2D and another Point2D

        If the two points are equal (the square distance between them is zero) then
        it returns a UnitVector of (x: 0.0, y: 0.0)
        :param other_point: The other Point2D
        :return: The two dimensional UnitVector between two Points
        :rtype: UnitVector
        """
        sq_d = self.square_distance(other_point)
        if sq_d == 0.0:
            return UnitVector(0.0, 0.0)

        uv_x = (self.x - other_point.x) / math.sqrt(sq_d)
        uv_y = (self.y - other_point.y) / math.sqrt(sq_d)
        return UnitVector(uv_x, uv_y)

    def offset_by(self, offset_x, offset_y):
        """ Offsets the x,y properties of the point

        :param offset_x: the offset amount of x coord
        :param offset_y: the offset amount of y coord
        :return: None
        """
        self.x += offset_x
        self.y += offset_y

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

    def scale(self, scale_value):
        """ Scales the polygon by a float value

        :param scale_value:
        :return:
        """
        self.x *= scale_value
        self.y *= scale_value

    def find_point_in_edge(self, point1, point2, threshold):
        """ Determines if this Point2D is within the bounds of the edge formed by point1 and point2 within a threshold

        :param point1: One Point2D of the edge
        :param point2: The other Point2D of the edge
        :param threshold: The threshold value to determine if the point is within the bounds of the edge
        :return: True if this point is within the edge, else False
        """

        # if point2 is above point1 then swap them
        if point2.x < point1.x:
            point1, point2 = point2, point1

        # calculate the slope of the edge from point1 -> point2
        if point1.x != point2.x:
            grad = math.atan(point2.y - point1.y / float(point2.x - point1.x))
        elif point2.y > point1.y:
            grad = 0.5 * math.pi
        else:
            grad = -0.5 * math.pi

        # create four points to form a quadrilateral that encompasses the edge + the threshold
        point1_a1 = Point2D(point1.x - threshold * math.sin(grad), point1.y + threshold * math.cos(grad))
        point2_a2 = Point2D(point2.x - threshold * math.sin(grad), point2.y + threshold * math.cos(grad))
        point1_b1 = Point2D(point1.x + threshold * math.sin(grad), point1.y - threshold * math.cos(grad))
        point2_b2 = Point2D(point2.x + threshold * math.sin(grad), point2.y - threshold * math.cos(grad))

        # check if this point is contained within the quad
        quad = [point1_a1, point2_a2, point2_b2, point1_b1]
        return self.inside_quadrilateral(quad)

    def inner_angle(self, left, right):
        """ Calculates the inner angle of Point2D and it's neighbors

        :param left: the Point2D on one side of the angle
        :param right: the Point2D on the other side of the angle
        :return: the inner angle of this Point2D
        """
        uv_left = left.unit_vector(self)
        uv_right = right.unit_vector(self)

        dot_product = uv_left.dot_product(uv_right)
        cross_product = uv_left.cross_product(uv_right)
        if dot_product != 0:
            arg_rad = math.atan(cross_product / dot_product)
        elif cross_product > 0:
            arg_rad = 0.5 * math.pi
        else:
            arg_rad = -0.5 * math.pi

        if cross_product < 0 <= dot_product:
            # cross product is negative then arg_rad(=atan) will be negative
            arg_rad += math.pi * 2
        elif dot_product < 0:
            # dot product is negative then arg_rad(=atan) will be negative
            arg_rad += math.pi

        return 180 * arg_rad / math.pi

    def turns_right(self, before, after):
        """ Calculates whether a point turns to the left or right while
            traversing the polygon in a clockwise rotation

        :param before: The point that comes before this one while traversing the polygon in a clockwise manner
        :param after:  The point that comes after this one while traversing the polygon in a clockwise manner
        :return: True if the polygon is a right-turn while traversing in a clockwise manner, else False
        """
        c = (self.x - before.x) * (after.y - self.y) - (after.x - self.x) * (self.y - before.y)
        return c < 0

    def slope(self, other_point):
        """ Calculates the slope between this point and another Point2D

        :param other_point: The other point to find the slope with
        :return: Slope as a float
        """
        # TODO Find a better way to handle this error
        if self.x == other_point.x:
            raise ZeroDivisionError
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

    def poly_mag(self, left, right, bisect, right_turn):
        # TODO ask Kenichi about why we need this
        """ Calculates the poly_mag of this point
        :param left: The Point2D before this one
        :param right: The Point2D after this one
        :param bisect: Bisect of this Point2D's angle
        :param right_turn: True if this point is a clockwise Right Turn else False
        :return: new Point2D
        """
        ab_vec = left.unit_vector(self)
        cb_vec = right.unit_vector(self)
        tot_vec = ab_vec.add(cb_vec)
        if right_turn:
            tot_vec = tot_vec.negate()
        new_x = self.x + bisect * tot_vec.x
        new_y = self.y + bisect * tot_vec.y
        return Point3D(new_x, new_y)

    def inside_quadrilateral(self, quad):
        """ Takes a list of 4 Point2D objects and determines if this point is contained within them
        :param quad: 4 Point2D objects forming some sort of quadrilateral
        :return: True if self is inside quad, else False
        """
        for pointA, pointB in list_mod_gen(quad, 2):
            if (pointB.x - pointA.x) * (self.y - pointA.y) - (self.x - pointA.x) * (pointB.y - pointA.y) > 0:
                return False
        return True

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
            return Point2D((point1.x + point2.x + point3.x + point4.x) / 4,
                           (point1.y + point2.y + point3.y + point4.y) / 4)

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

    @staticmethod
    def find_distance(point1, point2):
        """ finds the distance between points

        :param point1:
        :param point2:
        :return:
        """
        result = math.sqrt(point2.square_distance(point1))
        return result

    @staticmethod
    def close_edge_search(polygon, test_points, start_index, end_index):
        """ Determines the closest distance between points

        :param polygon: The list of Point2D objects for the entire polygon
        :param test_points: A list of Point2D objects to create a center point for testing
        :param start_index: The index to start at. (Inclusive)
        :param end_index: The index to stop at. (Inclusive)
        :return: The closest distance between points
        """
        minimum_distance = 1000.0
        unit_vector = test_points[1].unit_vector(test_points[0])
        center_point = Point2D(0.5 * (test_points[0].x + test_points[1].x), 0.5 * (test_points[0].y + test_points[1].y))
        polygon_sublist = polygon[start_index:] + polygon[:end_index + 1]
        for index1, index2 in list_mod_gen(polygon_sublist, 2):
            index_distance = Point2D.find_distance(index1, index2)
            point_product = round(abs(unit_vector.x * (index2.x - index1.x) / index_distance +
                                      unit_vector.y * (index2.y - index1.y) / index_distance), 3)
            if point_product > 0.5:
                check_y1 = unit_vector.x * (index1.x - center_point.x) + unit_vector.y * (index1.y - center_point.y)
                check_y2 = unit_vector.x * (index2.x - center_point.x) + unit_vector.y * (index2.y - center_point.y)
                if (check_y1 * check_y2 < 0.0 or abs(check_y1) < 0.52 * index_distance or
                            abs(check_y2) < 0.52 * index_distance):
                    check_x1 = unit_vector.y * (index1.x - center_point.x) - unit_vector.x * (index1.y - center_point.y)
                    # TODO: Is check_x2 supposed to be used here for something?
                    #                   check_x2 = unit_vector.y * (index2.x - center_point.x) - unit_vector.x * (index2.y - center_point.y)
                    if check_x1 < minimum_distance:
                        minimum_distance = check_x1
        return minimum_distance

    @staticmethod
    def random_sample():
        """ For experimenting, returns a list of 4 points forming some sort of quad
        Guarantees that it will somewhat resemble a quadrilateral by placing one point in each quadrant of the UnitCircle"""
        from random import random
        p1 = Point2D(random() * -10, random() * -10)
        p2 = Point2D(random() * -10, random() * 10)
        p3 = Point2D(random() * 10, random() * 10)
        p4 = Point2D(random() * 10, random() * -10)
        return [p1, p2, p3, p4]

    def __str__(self):
        return "Point2D({},{})".format(self.x, self.y)

    def __repr__(self):
        return Point2D.__str__(self)

    def __unicode__(self):
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
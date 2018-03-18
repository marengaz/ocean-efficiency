
from math import pi, cos, sin, radians, sqrt
from ocean_efficiency.legacy_model.GeoWKT import Point, CircularString
from pygeodesy.ellipsoidalVincenty import LatLon as GCLatLon
from pygeodesy.sphericalTrigonometry import LatLon as RhumbLatLon


class TurnArc(object):
    def __init__(self, turn_radius, incoming_bearing, outgoing_bearing, incoming_point, outgoing_point):
        """
        :param turn_radius: (NM)
        :param incoming_bearing: final bearing of ending sail vector (degrees)
        :param outgoing_bearing: initial bearing of following sail vector (degrees)
        """
        self.turn_radius = turn_radius
        self.incoming_bearing = incoming_bearing
        self.outgoing_bearing = outgoing_bearing
        self.incoming_point = incoming_point
        self.outgoing_point = outgoing_point

    @property
    def length(self):
        """
        calc the 2d arc length between 2 sail vectors
        :return: arc_length (NM)
        """
        if self.incoming_bearing is None or self.outgoing_bearing is None:
            return 0

        full_turn_circumference = 2 * pi * self.turn_radius
        circumference_arc_ratio = abs(self.outgoing_bearing - self.incoming_bearing) / 360

        return full_turn_circumference * circumference_arc_ratio

    @property
    def incoming_wkt_point(self):
        if not isinstance(self.incoming_point, (RhumbLatLon, GCLatLon)):
            raise TypeError('type {} not supported yet'.format(type(self.incoming_point)))
        return Point([self.incoming_point.lon, self.incoming_point.lat])

    @property
    def outgoing_wkt_point(self):
        if not isinstance(self.outgoing_point, (RhumbLatLon, GCLatLon)):
            raise TypeError('type {} not supported yet'.format(type(self.outgoing_point)))
        return Point([self.outgoing_point.lon, self.outgoing_point.lat])

    @property
    def middle_wkt_point(self):
        cor = self.origin_of_rotation
        angle = radians((self.outgoing_bearing - self.incoming_bearing) / 2)

        x = cor.x + (self.turn_radius * cos(angle))
        y = cor.y + (self.turn_radius * sin(angle))

        return Point([x, y])

    @property
    def wkt(self):
        return CircularString([self.incoming_wkt_point, self.middle_wkt_point, self.outgoing_wkt_point])

    @property
    def origin_of_rotation(self):
        x1 = self.incoming_wkt_point.x
        y1 = self.incoming_wkt_point.y
        x2 = self.outgoing_wkt_point.x
        y2 = self.outgoing_wkt_point.y
        r = self.turn_radius

        q = sqrt(pow((x2-x1), 2) + pow((y2-y1), 2))

        y3 = (y1+y2)/2
        
        x3 = (x1+x2)/2
        
        basex = sqrt(pow(r, 2)-pow((q/2), 2))*(y1-y2)/q  # calculate once
        basey = sqrt(pow(r, 2)-pow((q/2), 2))*(x2-x1)/q  # calculate once
        
        centerx1 = x3 + basex  # center x of circle 1
        centery1 = y3 + basey  # center y of circle 1
        # centerx2 = x3 - basex  # center x of circle 2
        # centery2 = y3 - basey  # center y of circle 2

        return Point([centerx1, centery1])
        # return Point([centerx2, centery2])














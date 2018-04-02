from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math

from math import pi, cos, sin, radians, sqrt

from sqlalchemy import text

from ocean_efficiency.legacy_model.GeoWKT import Point, CircularString, LineString
from pygeodesy.ellipsoidalVincenty import LatLon as GCLatLon
from pygeodesy.sphericalTrigonometry import LatLon as RhumbLatLon

from ocean_efficiency.utils.db import provide_session


class LegTurnArc(object):
    """
    Represents the portion of a leg where the ship is turning
    """

    def __init__(self, turn_radius, incoming_bearing, outgoing_bearing, incoming_point=None, outgoing_point=None):
        """
        :param turn_radius: (NM)
        :param incoming_bearing: final bearing of ending sail vector (degrees)
        :param outgoing_bearing: initial bearing of following sail vector (degrees)
        :param incoming_point: point at which the ship starts to turn (pygeodesy LatLon)
        :param outgoing_point: point at which the ship finishes the turn (pygeodesy LatLon)
        """
        self.turn_radius = turn_radius
        self.incoming_bearing = incoming_bearing
        self.outgoing_bearing = outgoing_bearing
        self.incoming_point = incoming_point
        self.outgoing_point = outgoing_point

    @property
    def distance(self):
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
    def wkt_obj(self):
        lon_lat_list = [self.incoming_wkt_point, self.middle_wkt_point, self.outgoing_wkt_point]
        cs = CircularString.from_lon_lat_list(lon_lat_list)
        return cs

    @property
    def origin_of_rotation(self):
        x1 = self.incoming_wkt_point.x
        y1 = self.incoming_wkt_point.y
        x2 = self.outgoing_wkt_point.x
        y2 = self.outgoing_wkt_point.y
        r = self.turn_radius

        q = sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2))

        y3 = (y1 + y2) / 2

        x3 = (x1 + x2) / 2

        basex = sqrt(pow(r, 2) - pow((q / 2), 2)) * (y1 - y2) / q  # calculate once
        basey = sqrt(pow(r, 2) - pow((q / 2), 2)) * (x2 - x1) / q  # calculate once

        centerx1 = x3 + basex  # center x of circle 1
        centery1 = y3 + basey  # center y of circle 1
        # centerx2 = x3 - basex  # center x of circle 2
        # centery2 = y3 - basey  # center y of circle 2

        return Point([centerx1, centery1])
        # return Point([centerx2, centery2])

    @property
    def vector_reduction(self):
        """
        The distance to reduce the leg's straight distance by, due to the turning arc
        :return: vector_reduction (NM)
        """
        if self.outgoing_bearing is None or self.incoming_bearing is None:
            return 0

        return self.turn_radius * math.tan(math.radians(abs(self.outgoing_bearing - self.incoming_bearing) / 2))


class LegStraight(object):
    """
    represents straight portion of leg including modifications due to
    incoming and outgoing arcs
    """

    def __init__(self, sail_vector, incoming_arc, outgoing_arc):
        self.sail_vector = sail_vector
        self.incoming_arc = incoming_arc
        self.outgoing_arc = outgoing_arc
        self.rhumb_mode = sail_vector.rhumb_mode

    @property
    def incoming_point(self):
        origin_latlon = self.sail_vector.origin_latlon
        destination_latlon = self.sail_vector.destination_latlon
        fractional_vector_reduction = self.incoming_arc.vector_reduction / self.sail_vector.distance

        return origin_latlon.intermediateTo(destination_latlon, fractional_vector_reduction)

    @property
    def outgoing_point(self):
        origin_latlon = self.sail_vector.origin_latlon
        destination_latlon = self.sail_vector.destination_latlon
        fractional_vector_reduction = 1 - (self.outgoing_arc.vector_reduction / self.sail_vector.distance)

        return origin_latlon.intermediateTo(destination_latlon, fractional_vector_reduction)

    def to_segmented_linestring(self):
        """
        :return: segmented linestring
        """
        incoming_point = self.incoming_point
        outgoing_point = self.outgoing_point
        num_segments = int(self.distance % 0.1)
        segment_length = num_segments / incoming_point.distanceTo(outgoing_point)
        if self.rhumb_mode:
            points = [[incoming_point.lon, incoming_point.lat]]
            for i in range(1, num_segments):
                next_point = incoming_point.destination(segment_length*i, self.sail_vector.initial_bearing)
                points.append([next_point.lon, next_point.lat])
            points.append([outgoing_point.lon, outgoing_point.lat])
            return LineString(points)
        else:
            # use the db
            lon_lat_list = [
                [incoming_point.lon, incoming_point.lat],
                [outgoing_point.lon, outgoing_point.lat]
            ]
            linestring = LineString.from_lon_lat_list(lon_lat_list, wkt_tag='LineString')
            self._segment_great_circle(linestring, segment_length)

    @provide_session
    def _segment_great_circle(self, linestring, max_segment_length, session=None):
        """
        Executes postgis ST_Segmentize() function to split linestring to points on great circle
        :return: LineString(BaseGeoWKT)
        """
        sql = text("SELECT ST_AsText(ST_Segmentize(ST_GeogFromText( :linestring , :max_segment_length )))")
        params = {
            'linestring': linestring,
            'max_segment_length': max_segment_length,
        }
        result = session.execute(sql, params)
        return LineString.from_wkt(result[0])

    @property
    def distance(self):
        """
        :return: distance of leg straight including modifications due to
            incoming and outgoing arcs (NM)
        """
        return self.sail_vector.distance - self.incoming_arc.vector_reduction - self.outgoing_arc.vector_reduction


class Leg(object):
    def __init__(self, previous_sail_vector, sail_vector, following_sail_vector):
        self.rhumb_mode = sail_vector.rhumb_mode
        self.origin_name = sail_vector.origin_name
        self.destination_name = sail_vector.destination_name
        self.vector_distance = sail_vector.distance
        self.initial_bearing = sail_vector.initial_bearing
        self.final_bearing = sail_vector.final_bearing
        self.incoming_turn_radius = sail_vector.incoming_turn_radius
        self.outgoing_turn_radius = sail_vector.outgoing_turn_radius

        # first leg has no previous sv
        self.incoming_arc = None
        incoming_vector_reduction = 0
        if previous_sail_vector:
            self.incoming_arc = LegTurnArc(
                self.incoming_turn_radius,
                previous_sail_vector.final_bearing,
                self.initial_bearing
            )
            incoming_vector_reduction = self.incoming_arc.vector_reduction

        # last leg has no following sv
        outgoing_arc = None
        outgoing_vector_reduction = 0
        if following_sail_vector:
            self.outgoing_arc = LegTurnArc(
                self.outgoing_turn_radius,
                self.final_bearing,
                following_sail_vector.initial_bearing
            )
            outgoing_vector_reduction = self.outgoing_arc.vector_reduction

        self.leg_straight = LegStraight(sail_vector, self.incoming_arc, outgoing_arc)

        self.leg_distance = self.calc_leg_distance(
            self.vector_distance,
            self.incoming_arc.vector_reduction,
            self.outgoing_arc.vector_reduction,
            self.incoming_arc.distance
        )

    @property
    def leg_distance(self):
        return self.leg_straight.distance + self.incoming_arc.distance

    def __str__(self):
        msg = """From %(origin_name)s to %(destination_name)s\n"""
        msg += """along a """ + "rhumb line" if self.rhumb_mode else "great circle" + "\n"
        msg += """is a distance of %(leg_distance)sNM\n"""
        class_dict = self.__dict__
        class_dict['leg_distance'] = self.leg_distance
        return msg % class_dict



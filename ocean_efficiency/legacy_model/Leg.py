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

from ocean_efficiency.legacy_model.SailVector import SailVector
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
    def mid_arc_wkt_point(self):
        return Point([self.mid_arc_point.lon, self.mid_arc_point.lat])

    @property
    def mid_arc_point(self):
        # calculate by pretending to sail from incoming point to turn origin,
        # then turn origin to the middle of the turning arc
        if self.turn_angle > 0:
            # clockwise turn
            bearing_incoming_to_turn_origin = (self.incoming_bearing + 90) % 360
        else:
            bearing_incoming_to_turn_origin = (self.incoming_bearing + 270) % 360
        bearing_origin_to_mid_arc = (bearing_incoming_to_turn_origin + 180 + (self.turn_angle/2)) % 360
        turn_radius_m = self.turn_radius * 1852

        turn_origin = self.incoming_point.destination(turn_radius_m, bearing_incoming_to_turn_origin)
        return turn_origin.destination(turn_radius_m, bearing_origin_to_mid_arc)

    @property
    def turn_angle(self):
        return ((((self.outgoing_bearing - self.incoming_bearing) % 360) + 540) % 360) - 180

    @property
    def wkt_obj(self):
        point_list = [self.incoming_wkt_point, self.mid_arc_wkt_point, self.outgoing_wkt_point]
        cs = CircularString(point_list)
        return cs

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

    @property
    def wkt_obj(self):
        return self.to_segmented_linestring()

    def to_segmented_linestring(self):
        """
        :return: segmented linestring
        """
        incoming_point = self.incoming_point
        outgoing_point = self.outgoing_point
        num_segments = int(self.distance % 0.1)
        segment_length = num_segments / incoming_point.distanceTo(outgoing_point)
        if self.rhumb_mode:
            points = [Point([incoming_point.lon, incoming_point.lat])]
            for i in range(1, num_segments):
                next_point = incoming_point.destination(segment_length*i, self.sail_vector.initial_bearing)
                points.append(Point([next_point.lon, next_point.lat]))
            points.append(Point([outgoing_point.lon, outgoing_point.lat]))
            return LineString(points)
        else:
            # use the db
            lon_lat_list = [
                [incoming_point.lon, incoming_point.lat],
                [outgoing_point.lon, outgoing_point.lat]
            ]
            linestring = LineString.from_lon_lat_list(lon_lat_list, wkt_tag='LineString')
            return self._segment_great_circle(linestring, segment_length)

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
        if previous_sail_vector:
            self.incoming_arc = LegTurnArc(
                turn_radius=self.incoming_turn_radius,
                incoming_bearing=previous_sail_vector.final_bearing,
                outgoing_bearing=self.initial_bearing
            )
            previous_leg_straight = LegStraight(
                sail_vector=previous_sail_vector,
                incoming_arc=LegTurnArc(0, 0, 0),
                outgoing_arc=self.incoming_arc
            )
        else:
            self.incoming_arc = LegTurnArc(0, 0, 0)
            previous_leg_straight = None

        # last leg has no following sv
        if following_sail_vector:
            self.outgoing_arc = LegTurnArc(
                self.outgoing_turn_radius,
                self.final_bearing,
                following_sail_vector.initial_bearing
            )
        else:
            self.outgoing_arc = LegTurnArc(0, 0, 0)

        self.leg_straight = LegStraight(
            sail_vector,
            self.incoming_arc,
            self.outgoing_arc
        )

        self.incoming_arc.incoming_point = previous_leg_straight.outgoing_point if previous_leg_straight else sail_vector.origin_latlon
        self.incoming_arc.outgoing_point = self.leg_straight.incoming_point

        self.outgoing_arc.incoming_point = self.leg_straight.outgoing_point
        # self.outgoing_arc.outgoing_point = not necessary

    @property
    def leg_distance(self):
        return self.incoming_arc.distance + self.leg_straight.distance

    def __str__(self):
        msg = """From %(origin_name)s to %(destination_name)s\n"""
        msg += """along a """ + "rhumb line" if self.rhumb_mode else "great circle" + "\n"
        msg += """is a distance of %(leg_distance)sNM\n"""
        class_dict = self.__dict__
        class_dict['leg_distance'] = self.leg_distance
        return msg % class_dict



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from math import degrees

from pygeodesy.ellipsoidalVincenty import LatLon as GCLatLon
from pygeodesy.sphericalTrigonometry import LatLon as RhumbLatLon
from pygeodesy.utils import m2NM


class SailVector(object):
    def __init__(self, rhumb_mode,
                 origin_name, destination_name,
                 incoming_turn_radius, outgoing_turn_radius,
                 origin_latlon, destination_latlon):
        self.rhumb_mode = rhumb_mode
        self.origin_name = origin_name
        self.destination_name = destination_name
        self.incoming_turn_radius = incoming_turn_radius
        self.outgoing_turn_radius = outgoing_turn_radius
        self.origin_latlon = origin_latlon
        self.destination_latlon = destination_latlon

    @classmethod
    def from_nothing(cls):
        return cls(True, '', '', 0, 0, RhumbLatLon(0, 0), RhumbLatLon(0, 0))

    @classmethod
    def from_waypoints(cls, origin_waypoint, destination_waypoint):
        rhumb_mode = destination_waypoint.sail_mode
        origin_name = origin_waypoint.name
        destination_name = destination_waypoint.name
        incoming_turn_radius = m2NM(origin_waypoint.radius)
        outgoing_turn_radius = m2NM(destination_waypoint.radius)

        lon1, lat1, lon2, lat2 = map(degrees, [
            origin_waypoint.longitude,
            origin_waypoint.latitude,
            destination_waypoint.longitude,
            destination_waypoint.latitude
        ])

        if rhumb_mode:
            origin_latlon = RhumbLatLon(lat1, lon1)
            destination_latlon = RhumbLatLon(lat2, lon2)
        else:
            origin_latlon = GCLatLon(lat1, lon1)
            destination_latlon = GCLatLon(lat2, lon2)

        return cls(rhumb_mode,
                   origin_name, destination_name,
                   incoming_turn_radius, outgoing_turn_radius,
                   origin_latlon, destination_latlon)

    @property
    def distance(self):
        """
        :return: distance between origin and destination in nautical miles
        """
        return m2NM(self.origin_latlon.distanceTo(self.destination_latlon, wrap=True))

    @property
    def initial_bearing(self):
        """
        :return: initial bearing in degrees
        """
        return self.origin_latlon.initialBearingTo(self.destination_latlon, wrap=True)

    @property
    def final_bearing(self):
        """
        :return: final bearing in degrees
        """
        if self.rhumb_mode:
            return self.initial_bearing
        else:
            return self.origin_latlon.finalBearingTo(self.destination_latlon, wrap=True)


from math import degrees

from pygeodesy.ellipsoidalVincenty import LatLon as GCLatLon
from pygeodesy.sphericalTrigonometry import LatLon as RhumbLatLon
from pygeodesy.utils import m2NM


class SailVector(object):
    def __init__(self, origin_waypoint, destination_waypoint):
        self.rhumb_mode = destination_waypoint.sail_mode
        self.origin_name = origin_waypoint.name
        self.destination_name = destination_waypoint.name
        self.incoming_turn_radius = m2NM(origin_waypoint.radius)
        self.outgoing_turn_radius = m2NM(destination_waypoint.radius)

        lon1, lat1, lon2, lat2 = map(degrees, [
            origin_waypoint.longitude,
            origin_waypoint.latitude,
            destination_waypoint.longitude,
            destination_waypoint.latitude
        ])

        if self.rhumb_mode:
            self.origin_latlon = RhumbLatLon(lat1, lon1)
            self.destination_latlon = RhumbLatLon(lat2, lon2)
        else:
            self.origin_latlon = GCLatLon(lat1, lon1)
            self.destination_latlon = GCLatLon(lat2, lon2)

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


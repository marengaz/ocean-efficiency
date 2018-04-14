from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ocean_efficiency.legacy_model.GeoWKT import CompoundCurve
from ocean_efficiency.legacy_model.Leg import Leg
from ocean_efficiency.legacy_model.SailVector import SailVector
from itertools import tee, islice, chain
from ocean_efficiency.model import Journey as ORMJourney
from ocean_efficiency.utils.db import provide_session


class Journey(object):
    # __tablename__ = 'journey'
    # journey_id = Column(Integer, Sequence('journey_id_seq'), primary_key=True)
    # name = Column(String(100))
    # created_on = Column(DateTime(), default=datetime.now)
    # updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    # geom = Column(Geometry('CompoundCurve', srid=4326))  # , index=True)

    def __init__(self, name, legs, journey_id=None, created_on=None, updated_on=False):
        self.journey_id = journey_id
        self.created_on = created_on
        self.updated_on = updated_on
        self.name = name
        self.legs = legs

    @classmethod
    def from_route_model(cls, route_model):
        sail_vectors = [SailVector.from_waypoints(wp1, wp2) for wp1, wp2 in zip(route_model.waypoints, route_model.waypoints[1:])]

        legs = []
        for psv, sv, nsv in previous_and_next(sail_vectors):
            legs.append(Leg(psv, sv, nsv))

        return cls(route_model.name, legs)

    @property
    def leg_parts(self):
        lps = []
        [lps.append(lp) for l in self.legs for lp in (l.incoming_arc, l.leg_straight)]
        return lps

    @property
    def wkt_obj(self):
        wkt_lps = [lp.wkt_obj for lp in self.leg_parts]
        return CompoundCurve(wkt_lps, srid=4326)

    @property
    def orm(self):
        return ORMJourney(name=self.name, geom=self.wkt_obj.wkt)
        # return ORMJourney(name=self.name, geom=self.wkt_obj.wkt, journey_id=None, created_on=None, updated_on=False)

    @provide_session
    def write_to_db(self, session):
        session.add(self.orm)
        session.commit()

    def __str__(self):
        msgs = [str(l) for l in self.legs]
        return "\n".join(msgs)


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

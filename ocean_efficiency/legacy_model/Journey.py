from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
# from datetime import datetime
# from sqlalchemy import Sequence, Integer, Column, String, DateTime

from ocean_efficiency.legacy_model.Leg import Leg
from ocean_efficiency.legacy_model.SailVector import SailVector
from itertools import tee, islice, chain

# from ocean_efficiency.settings import Session, Base


class Journey(object):
    # __tablename__ = 'journey'
    #
    # journey_id = Column(Integer, Sequence('journey_id_seq'), primary_key=True)
    # name = Column(String(100))
    # created_on = Column(DateTime(), default=datetime.now)
    # updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, route_model):
        self.name = route_model.name
        # Session.add(self)
        self.sail_vectors = [SailVector(wp1, wp2) for wp1, wp2 in zip(route_model.waypoints, route_model.waypoints[1:])]

        legs = []
        for psv, sv, nsv in previous_and_next(self.sail_vectors):
            legs.append(Leg(psv, sv, nsv))
        self.legs = legs

    def __str__(self):
        msgs = [str(l) for l in self.legs]
        return "\n".join(msgs)


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

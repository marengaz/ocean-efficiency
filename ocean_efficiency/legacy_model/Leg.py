from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from math import pi

import math

from sqlalchemy import Column, Integer, Sequence, Boolean, String, Float


class Leg(object):
    # __tablename__ = 'leg'
    #
    # leg_id = Column(Integer, Sequence('leg_id_seq'), primary_key=True)
    # rhumb_mode = Column(Boolean)
    # origin_name = Column(String(100))
    # destination_name = Column(String(100))
    # vector_distance = Column(Float)
    # initial_bearing = Column(Float)
    # final_bearing = Column(Float)
    # incoming_turn_radius = Column(Float)
    # outgoing_turn_radius = Column(Float)
    #
    # previous_leg_final_bearing = Column(Float)
    # following_leg_initial_bearing = Column(Float)
    #
    # incoming_arc_length = Column(Float)
    # incoming_vector_reduction = Column(Float)
    # outgoing_vector_reduction = Column(Float)
    # leg_distance = Column(Float)

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
        self.previous_leg_final_bearing = previous_sail_vector.final_bearing if previous_sail_vector else None
        # last leg has no following sv
        self.following_leg_initial_bearing = following_sail_vector.initial_bearing if following_sail_vector else None

        self.incoming_arc_length = self.calc_arc_length(
            self.incoming_turn_radius,
            self.previous_leg_final_bearing,
            self.initial_bearing
        )

        self.incoming_vector_reduction = self.calc_vector_reduction(
            self.incoming_turn_radius,
            self.previous_leg_final_bearing,
            self.initial_bearing
        )

        self.outgoing_vector_reduction = self.calc_vector_reduction(
            self.outgoing_turn_radius,
            self.final_bearing,
            self.following_leg_initial_bearing
        )

        self.leg_distance = self.calc_leg_distance(
            self.vector_distance,
            self.incoming_vector_reduction,
            self.outgoing_vector_reduction,
            self.incoming_arc_length
        )

    @staticmethod
    def calc_arc_length(turn_radius, final_bearing, initial_bearing):
        """
        calc the 2d arc length between 2 sail vectors
        :param turn_radius: (NM)
        :param final_bearing: final bearing of ending sail vector (degrees)
        :param initial_bearing: initial bearing of following sail vector (degrees)
        :return: arc_length (NM)
        """
        if final_bearing is None or initial_bearing is None:
            return 0

        full_turn_circumference = 2 * pi * turn_radius
        circumference_arc_ratio = abs(initial_bearing - final_bearing) / 360

        return full_turn_circumference * circumference_arc_ratio

    @staticmethod
    def calc_vector_reduction(turn_radius, final_bearing, initial_bearing):
        """
        calc the 2d distance to reduce the leg distance by due to the arc length
        :param turn_radius: (NM)
        :param final_bearing: final bearing of ending sail vector (degrees)
        :param initial_bearing: initial bearing of following sail vector (degrees)
        :return: vector_reduction (NM)
        """
        if final_bearing is None or initial_bearing is None:
            return 0

        return turn_radius * math.tan(math.radians(abs(initial_bearing - final_bearing) / 2))

    @staticmethod
    def calc_leg_distance(vector_distance, incoming_vector_reduction, outgoing_vector_reduction, incoming_arc_length):
        """
        :param vector_distance: the distance between two waypoints in the given sail mode (NM)
        :param incoming_vector_reduction: distance to reduce the vector_distance by
            due to turning arc of previous leg (NM)
        :param outgoing_vector_reduction: distance to reduce the vector_distance by
            due to turning arc of following leg (NM)
        :param incoming_arc_length: distance of turning arc between previous and current leg (NM)
        :return: distance of leg in meters including modifications due to
            incoming and outgoing arcs (NM)
        """
        reduced_vector = vector_distance - incoming_vector_reduction - outgoing_vector_reduction
        return reduced_vector + incoming_arc_length

    def __str__(self):
        msg = """From %(origin_name)s to %(destination_name)s\n"""
        msg += """along a """ + "rhumb line" if self.rhumb_mode else "great circle" + "\n"
        msg += """is a distance of %(leg_distance)sNM\n"""
        class_dict = self.__dict__
        class_dict['leg_distance'] = self.leg_distance
        return msg % class_dict

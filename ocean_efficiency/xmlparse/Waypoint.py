import dexml
from dexml import fields


class Waypoint(dexml.Model):
    class meta:
        tagname = 'Waypoints'

    name = fields.String(tagname="Name")
    latitude = fields.Float(tagname='Latitude')  # radians
    longitude = fields.Float(tagname='Longitude')  # radians
    track_limit = fields.Float(tagname='TrackLimit', default=0)
    course_limit = fields.Float(tagname='CourseLimit', default=0)
    economy = fields.Float(tagname='Economy', default=0)
    max_speed = fields.Float(tagname='MaximalSpeed', default=0)
    controller_type = fields.String(tagname='ControllerType', default='')
    notes = fields.String(tagname="Notes", default='')
    is_parameter_point = fields.Boolean(tagname="IsParameterPoint", default=False)
    is_arrival_point = fields.Boolean(tagname="IsArrivalPoint", default=False)

    # 0 great circle, 1 rhumb
    # latter sailmode corresponds to leg's sailmode
    sail_mode = fields.Integer(tagname="SailMode")
    radius = fields.Float(tagname='Radius')  # meters

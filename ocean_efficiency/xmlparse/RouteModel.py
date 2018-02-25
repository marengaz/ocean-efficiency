import dexml
from dexml import fields

from ocean_efficiency.xmlparse.Waypoint import Waypoint


class RouteModel(dexml.Model):
    class meta:
        namespace = 'http://www.sam-electronics.de/2010/reducedRouteModel.xsd'
        tagname = "RouteModel"

    name = fields.String(tagname="Name")
    waypoints = fields.List(Waypoint)


class RouteModelType(dexml.Model):
    class meta:
        tagname = "RouteModelType"

    name = fields.String(tagname="Name")
    waypoints = fields.List(Waypoint)


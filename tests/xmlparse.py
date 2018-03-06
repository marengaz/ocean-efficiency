from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import unittest
from ocean_efficiency.xmlparse.RouteModel import RouteModel


# class TestStringMethods(unittest.TestCase):
#
#     def test_upper(self):
#         self.assertEqual('foo'.upper(), 'FOO')
#
#     def test_isupper(self):
#         self.assertTrue('FOO'.isupper())
#         self.assertFalse('Foo'.isupper())
#
#     def test_split(self):
#         s = 'hello world'
#         self.assertEqual(s.split(), ['hello', 'world'])
#         # check that s.split fails when the separator is not a string
#         with self.assertRaises(TypeError):
#             s.split(2)


class TestXMLParse(unittest.TestCase):

    demoxml = """
<?xml version="1.0" encoding="utf-8"?>
<RouteModel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.sam-electronics.de/2010/reducedRouteModel.xsd">
    <Name xmlns="">AARHUS-OSLO</Name>
    <Waypoints xmlns="">
        <Name>BASIN</Name>
        <Latitude>0.9801527642</Latitude>
        <Longitude>0.1784168646</Longitude>
        <Notes />
        <SailMode>0</SailMode>
        <Radius>370.4</Radius>
    </Waypoints>
    <Waypoints xmlns="">
        <Name>VIPPETANGEN</Name>
        <Latitude>1.045445822</Latitude>
        <Longitude>0.1875533723</Longitude>
        <Notes />
        <SailMode>1</SailMode>
        <Radius>370.4</Radius>
    </Waypoints>
</RouteModel>
    """

    def test_route_model(self):
        rm = RouteModel.parse(self.demoxml.strip())
        print(rm.name)


if __name__ == '__main__':
    unittest.main()

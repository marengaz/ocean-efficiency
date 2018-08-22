
from optparse import OptionParser

from ocean_efficiency.legacy_model.Journey import Journey
from ocean_efficiency.xmlparse.route_model_parse import parse

"""
eg python load_file.py -f "/Users/ben.marengo/other_code/oceanefficiency/B624.1 - GBSOU - NOSVG.xml"
"""

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")

(options, args) = parser.parse_args()

with open(options.filename, 'r') as content_file:
    xml_str = content_file.read().strip()

rm = parse(xml_str)

j = Journey.from_route_model(rm)
j.write_to_db()
print( str(j) )

import dexml
import logging

from ocean_efficiency.xmlparse.RouteModel import RouteModel, RouteModelType


CLASSES_TO_TRY = [
    RouteModel,
    RouteModelType
]


def parse(xml_str):
    rm = None
    for C in CLASSES_TO_TRY:
        try:
            return C.parse(xml_str)
        except dexml.ParseError as ex:
            logging.error(ex)
        except Exception:
            raise

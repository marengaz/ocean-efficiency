import regex

multi_wkt_pattern = regex.compile('([A-Z]*\((?>[^\(\)]+|(?R))*\))')
single_wkt_pattern = regex.compile('(\w*)\((.*)\)')
lon_lat_pattern = regex.compile('(\d+\.?\d*) (\d+\.?\d*)')


class BaseGeoWKT(object):
    wkt_tag = None

    def __init__(self, obj, wkt_tag=''):
        self.obj = obj
        self.wkt_tag = wkt_tag

    @classmethod
    def from_wkt(cls, wkt_str):
        wkt_match = single_wkt_pattern.findall(wkt_str.upper())
        if wkt_match:
            obj = cls._from_wkt(wkt_match[0][0].strip(), wkt_match[0][1])
        else:
            raise NotImplementedError()

        return cls(obj)

    @classmethod
    def _from_wkt(cls, wkt_tag, wkt_str):
        obj = []
        wkt_elements = multi_wkt_pattern.findall(wkt_str)
        if wkt_elements:
            for wkt_element in wkt_elements:
                wkt_element_match = single_wkt_pattern.findall(wkt_element)[0]
                wkt_element_tag = wkt_element_match[0].strip()
                wkt_element_data = wkt_element_match[1]
                if wkt_element_tag in WKT_TAG_CLASS:
                    obj.append(cls._from_wkt(wkt_element_tag, wkt_element_data))
                elif wkt_element_tag == '' and wkt_tag == 'COMPOUNDCURVE':
                    obj.append(cls._from_wkt('LINESTRING', wkt_element_data))
                else:
                    raise NotImplementedError()
        else:
            points = [Point(p) for p in lon_lat_pattern.findall(wkt_str)]
            obj = WKT_TAG_CLASS[wkt_tag](points)
        return obj

    @property
    def wkt(self):
        if self.wkt_tag is None:
            raise NotImplementedError('Set wkt_tag in class')
        return '{0}({1})'.format(self.wkt_tag, self)

    def __str__(self):
        return ', '.join(v.wkt for v in self.obj)


class Point(BaseGeoWKT):
    """
    p = Point([0, 0])
    p.wkt = (0 0)
    """
    def __init__(self, obj, wkt_tag=''):
        if type(obj) not in (list, tuple) and len(obj) != 2:
            raise ValueError('Only supply list or tuple')
        super(Point, self).__init__(obj, wkt_tag)
        self.x = obj[0]
        self.y = obj[1]

    @property
    def wkt(self):
        return str(self)

    def __str__(self):
        return ' '.join(str(v) for v in self.obj)


class LineString(BaseGeoWKT):
    """
    ls = LineString.from_lon_lat_list([[0, 0], [1, 1], [1, 0]])
    ls = LineString([Point([0, 0]), Point([1, 1]), Point([1, 0])])
    ls.wkt = (0 0, 1 1, 1 0)
    """

    def __init__(self, obj, wkt_tag=''):
        super(LineString, self).__init__(obj)
        self.wkt_tag = wkt_tag

    @classmethod
    def from_lon_lat_list(cls, lon_lat_list, wkt_tag=''):
        data = [Point(l) for l in lon_lat_list]
        return cls(data, wkt_tag)


class CircularString(BaseGeoWKT):
    """
    cs = CircularString.from_lon_lat_list([[0, 0], [1, 1], [1, 0]])
    cs = CircularString([Point([0, 0]), Point([1, 1]), Point([1, 0])])
    cs.wkt = CIRCULARSTRING(0 0, 1 1, 1 0)
    """
    def __init__(self, obj, wkt_tag='CircularString'):
        super(CircularString, self).__init__(obj, wkt_tag)

    @classmethod
    def from_lon_lat_list(cls, lon_lat_list, wkt_tag='CircularString'):
        data = [Point(l) for l in lon_lat_list]
        return cls(data, wkt_tag)


class CompoundCurve(BaseGeoWKT):
    """
    cc = CompoundCurve( [cs, ls] )
    cc.wkt = COMPOUNDCURVE( CIRCULARSTRING(0 0, 1 1, 1 0), (1 0, 0 1) )
    """
    def __init__(self, obj, wkt_tag='CompoundCurve'):
        if type(obj) not in (list, tuple):
            raise ValueError('Only supply list or tuple')

        for o in obj:
            if type(o) not in (CircularString, LineString):
                raise ValueError('Only supply CircularString or LineString')

        super(CompoundCurve, self).__init__(obj, wkt_tag)


WKT_TAG_CLASS = {
    'POINT': Point,
    'LINESTRING': LineString,
    'CIRCULARSTRING': CircularString,
    'COMPOUNDCURVE': CompoundCurve,
}

if __name__ == '__main__':
    ls = LineString.from_lon_lat_list([[0, 0], [1, 1], [1, 0]])
    cs = CircularString.from_lon_lat_list([[0, 0], [1, 1], [1, 0]])
    cc = CompoundCurve([cs, ls])
    print(ls.wkt)
    print(cs.wkt)
    print(cc.wkt)
    cc = CompoundCurve.from_wkt(cc.wkt)









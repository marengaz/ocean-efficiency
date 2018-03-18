

class BaseGeoWKT(object):
    wkt_tag = None

    def __init__(self, obj):
        self.obj = obj

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
    wkt_tag = ''

    def __init__(self, obj):
        if type(obj) not in (list, tuple) and len(obj) != 2:
            raise ValueError('Only supply list or tuple')
        super(Point, self).__init__(obj)
        self.x = obj[0]
        self.y = obj[1]

    @property
    def wkt(self):
        return str(self)

    def __str__(self):
        return ' '.join(str(v) for v in self.obj)


class LineString(BaseGeoWKT):
    """
    ls = LineString([[0, 0], [1, 1], [1, 0]])
    ls = LineString([Point([0, 0]), Point([1, 1]), Point([1, 0])])
    ls.wkt = (0 0, 1 1, 1 0)
    """
    wkt_tag = ''

    def __init__(self, obj):
        if isinstance(obj[0], list):
            obj = [Point(v) for v in obj]
        super(LineString, self).__init__(obj)


class CircularString(BaseGeoWKT):
    """
    cs = CircularString([[0, 0], [1, 1], [1, 0]])
    cs = CircularString([Point([0, 0]), Point([1, 1]), Point([1, 0])])
    cs.wkt = CIRCULARSTRING(0 0, 1 1, 1 0)
    """
    wkt_tag = 'CircularString'

    def __init__(self, obj):
        if isinstance(obj[0], list):
            obj = [Point(v) for v in obj]
        super(CircularString, self).__init__(obj)


class CompoundCurve(BaseGeoWKT):
    """
    cc = CompoundCurve( cs, ls )
    cc.wkt = COMPOUNDCURVE( CIRCULARSTRING(0 0, 1 1, 1 0), (1 0, 0 1) )
    """
    wkt_tag = 'CompoundCurve'

    def __init__(self, obj):
        if type(obj) not in (list, tuple) and len(obj) != 2:
            raise ValueError('Only supply list or tuple')

        for o in obj:
            if type(o) not in (CircularString, LineString):
                raise ValueError('Only supply CircularString or LineString')

        super(CompoundCurve, self).__init__(obj)


if __name__ == '__main__':
    ls = LineString([[0, 0], [1, 1], [1, 0]])
    cs = CircularString([[0, 0], [1, 1], [1, 0]])
    cc = CompoundCurve([cs, ls])
    print(ls.wkt)
    print(cs.wkt)
    print(cc.wkt)









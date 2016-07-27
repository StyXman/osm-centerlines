from unittest import TestCase

import centerlines

from shapely.geometry import LineString, MultiLineString, Point, Polygon

class TestLineEnds (TestCase):

    def testSimple (self):
        points= ( (0, 0), (1, 1) )
        line= LineString (points)

        ends= centerlines.line_ends (line)

        self.assertEqual (ends, points)

    def testLong (self):
        points= ( (0, 0), (1, 1), (2, 1) )
        line= LineString (points)

        ends= centerlines.line_ends (line)

        self.assertEqual (ends, ( (0, 0), (2, 1) ))

class TestMedialsEnds (TestCase):

    def testSimple (self):
        points= ( (0, 0), (1, 1) )
        medials= [ LineString (points) ]

        ends= centerlines.medials_ends (medials)

        self.assertEqual (ends, [ [Point (p) for p in points] ])

    def testDouble (self):
        points= (( (0, 0), (1, 1) ), ( (1, 1), (2, 1) ), ( (1, 1), (0, 1) ))
        medials= MultiLineString (points)

        ends= centerlines.medials_ends (medials)

        self.assertEqual (ends, [ [Point (0, 0)], [Point (2, 1)], [Point (0, 1)] ])

    def testTriple (self):
        points= (( (-1, 0), (0, 0) ), ( (0, 0), (1, 1) ), ( (1, 1), (2, 1) ), ( (1, 1), (0, 1) ))
        medials= MultiLineString (points)

        ends= centerlines.medials_ends (medials)

        self.assertEqual (ends, [ [Point (-1, 0)], [], [Point (2, 1)], [Point (0, 1)] ])


class TestPointsInWay (TestCase):

    def testNone (self):
        way= Polygon (( (0, 0), (4, 0), (4, 2), (0, 2), (0, 0) ))
        line= LineString (( (1, 1), (3, 3) ))

        self.assertEqual (centerlines.points_in_way (line, way), [])



class TestMiddlePoint (TestCase):

    def testSimple (self):
        self.assertEqual (centerlines.middle_point (Point (0, 0), Point (2, 2)),
                          Point (1, 1))


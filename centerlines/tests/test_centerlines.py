import unittest

import centerlines

from shapely.geometry import LineString, MultiLineString, Point

class TestLineEnds (unittest.TestCase):

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

class TestMedialsEnds (unittest.TestCase):

    def testSimple (self):
        points= ( (0, 0), (1, 1) )
        medials= LineString (points)

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

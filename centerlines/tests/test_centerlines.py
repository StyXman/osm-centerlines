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


class TestRadialPoints (TestCase):
    # it doesn't use real skeletons or medials

    def testSimple (self):
        # simple rectangle with >--< skel and -- medial
        way= Polygon (( (0, 0), (4, 0), (4, 2), (0, 2), (0, 0) ))
        skel_points= (( (0, 0), (1, 1) ),
                      ( (1, 1), (0, 2) ),
                      # this is the central bar from which the radials radiate :)
                      ( (1, 1), (3, 1) ),
                      ( (3, 1), (4, 2) ),
                      ( (4, 0), (3, 1) ))
        skel= MultiLineString (skel_points)
        medials_points= (( (1, 1), (3, 1) ), )
        medials= MultiLineString (medials_points)

        # notice they are the 4 points from way, but separated by medial ends
        expected= [ ([ Point (0, 0), Point (0, 2) ],
                     [ Point (4, 0), Point (4, 2) ]) ]

        radials= centerlines.radial_points (way, skel, medials)

        for m_index, medial in enumerate (radials):
            for end_index, end in enumerate (medial):
                for p_index, point in enumerate (end):
                    a=  radials[m_index][end_index][p_index]
                    b= expected[m_index][end_index]
                    # points can be in any order, so test belongness (???) only
                    self.assertIn (a, b)


class TestMiddlePoint (TestCase):

    def testSimple (self):
        self.assertEqual (centerlines.middle_point (Point (0, 0), Point (2, 2)),
                          Point (1, 1))

from unittest import TestCase

import centerlines

from shapely.geometry import LineString, MultiLineString, Point, Polygon

# conventions:
# a line is a n-tuple of 2-tuples (points)
# put spaces inside the parenthesis defining the line
# a multi line is a *list* of lines

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

    def testTriple (self):
        # T, Y cases
        points= [( (0, 0), (1, 1) ),
                 ( (1, 1), (2, 1) ),
                 ( (1, 1), (0, 1) )]
        medials= MultiLineString (points)

        ends= centerlines.medials_ends (medials)

        self.assertEqual (ends, [ [Point (0, 0), None],
                                  [None, Point (2, 1)],
                                  [None, Point (0, 1)] ])

    def testQuintuple (self):
        # a Y with a Y for arm
        points= (( (-1, 0), (0, 0) ),
                 (  (0, 0), (0, 1) ),
                 (  (0, 0), (1, 1) ),
                 (  (1, 1), (2, 1) ),
                 (  (1, 1), (1, 2) ))
        medials= MultiLineString (points)

        ends= centerlines.medials_ends (medials)

        self.assertEqual (ends, [ [Point (-1, 0), None],
                                  [None, Point (0, 1)],
                                  [None, None],
                                  [None, Point (2, 1)],
                                  [None, Point (1, 2)] ])


class TestPointsInWay (TestCase):

    def testNone (self):
        way= Polygon (( (0, 0), (4, 0), (4, 2), (0, 2), (0, 0) ))
        line= LineString (( (1, 1), (3, 3) ))

        self.assertEqual (centerlines.points_in_way (line, way), [])

    def testOne (self):
        way= Polygon (( (0, 0), (4, 0), (4, 2), (0, 2), (0, 0) ))
        line= LineString (( (1, 1), (4, 0) ))

        self.assertEqual (centerlines.points_in_way (line, way),
                          [(4, 0)])


# syntetic data
# simple rectangle with >--< skel and -- medial
# yes, this is the simple example :)
rectangle= Polygon (( (0, 0), (4, 0), (4, 2), (0, 2), (0, 0) ))
rect_skel= MultiLineString ( [( (0, 0), (1, 1) ),
                              ( (1, 1), (0, 2) ),
                              # this is the central bar from which the radials radiate :)
                              ( (1, 1), (3, 1) ),
                              ( (3, 1), (4, 2) ),
                              ( (4, 0), (3, 1) )] )
rect_medials= MultiLineString ( [( (1, 1), (3, 1) )] )

l_shape= Polygon (( (0, 0), (4, 0),
                    (4, 5), (2, 5),
                    (2, 2), (0, 2), (0, 0) ))
l_skel= MultiLineString ( [( (0, 0), (1, 1) ),
                           ( (1, 1), (0, 2) ),
                           ( (1, 1), (3, 1) ),
                           ( (3, 1), (4, 0) ),
                           ( (3, 1), (2, 2) ),
                           ( (3, 1), (3, 4) ),
                           ( (3, 4), (2, 5) ),
                           ( (3, 4), (4, 5) )] )
l_medials= MultiLineString ([ ( (1, 1), (3, 1), (3, 4) )] )

t_shape= Polygon (( (0, 0), (6, 0), (6, 2),
                    (4, 2), (4, 5), (2, 5),
                    (2, 2), (0, 2), (0, 0) ))
t_skel= MultiLineString ( [( (0, 0), (1, 1) ),
                           ( (1, 1), (0, 2) ),
                           ( (1, 1), (3, 1) ),
                           ( (3, 1), (5, 1) ),
                           ( (5, 1), (6, 2) ),
                           ( (6, 0), (5, 1) ),
                           ( (3, 1), (2, 2) ),
                           ( (3, 1), (4, 2) ),
                           ( (3, 1), (3, 4) ),
                           ( (3, 4), (2, 5) ),
                           ( (3, 4), (4, 5) )] )
t_medials= MultiLineString ( [( (1, 1), (3, 1) ),
                              ( (3, 1), (3, 4) ),
                              ( (3, 1), (5, 1) )] )

class TestSynteticRadialPoints (TestCase):
    # it doesn't use real skeletons or medials

    def check_radials (self, count, radials, expected):
        self.assertEqual (len (radials), count)

        for m_index, medial in enumerate (radials):
            self.assertEqual (len (medial), 2)  # one for start, one for end

            for end_index, end in enumerate (medial):
                b= expected[m_index][end_index]

                self.assertEqual (len (end), len (b))

                for p_index, point in enumerate (end):
                    a=  radials[m_index][end_index][p_index]
                    # points can be in any order, so test belongness (???) only
                    self.assertIn (a, b)


    def testSimple (self):

        radials= centerlines.radial_points (rectangle, rect_skel, rect_medials)

        # notice they are the 4 points from way, but partitioned by medial ends
        expected= [ ([ (0, 0), (0, 2) ],    # start
                     [ (4, 0), (4, 2) ]) ]  # end
        self.check_radials (1, radials, expected)

    def testLShape (self):

        radials= centerlines.radial_points (l_shape, l_skel, l_medials)

        expected= [ ([ (0, 0), (0, 2) ],
                     [ (4, 5), (2, 5) ])]
        self.check_radials (1, radials, expected)

    def testTShape (self):

        radials= centerlines.radial_points (t_shape, t_skel, t_medials)

        expected= [ ([ (0, 0), (0, 2) ], [  ]),
                    ([  ], [ (4, 5), (2, 5) ]),
                    ([  ], [ (6, 2), (6, 0) ])]
        self.check_radials (3, radials, expected)


class TestMiddlePoint (TestCase):

    def testSimple (self):
        self.assertEqual (centerlines.middle_point ((0, 0), (2, 2)),
                          (1, 1))


class TestSynteticExtendMedials (TestCase):

    def testRectangle (self):

        medials= centerlines.extend_medials (rectangle, rect_skel, rect_medials)

        expected= MultiLineString ( [( (0, 1), (1, 1), (3, 1), (4, 1) )] )
        self.assertEqual (medials, expected)

    def testLShape (self):

        medials= centerlines.extend_medials (l_shape, l_skel, l_medials)

        expected= MultiLineString ( [( (0, 1), (1, 1), (3, 1), (3, 4), (3, 5) )] )
        self.assertEqual (medials, expected)

    def testTShape (self):

        medials= centerlines.extend_medials (t_shape, t_skel, t_medials)

        expected= MultiLineString ( [( (0, 1), (1, 1), (3, 1) ),
                                     ( (3, 1), (3, 4), (3, 5) ),
                                     ( (3, 1), (5, 1), (6, 1) )] )
        self.assertEqual (medials, expected)

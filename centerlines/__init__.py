from shapely.geometry import Point, LineString, MultiLineString
from shapely import wkb
import shapely.ops

import fiona
import fiona.crs

from collections import OrderedDict
import codecs


def line_ends (line):
    """Returns the coords (not Points) of the ends of a LineString."""
    return ( line.coords[0], line.coords[-1] )


def medials_ends (medials):
    """Returns a list of (start, end) points in medial order. start or end
    might be None if they happen to be a common point among the medials."""
    # NOTE: Vs could be a bitch

    ends= [ [None, None] for i in medials ]
    added= {}
    removed= set ()

    for m_index, medial in enumerate (medials):
        for end_index, coords in enumerate (line_ends (medial)):
            if coords not in added and coords not in removed:
                ends[m_index][end_index]= Point (*coords)
                # save the index of the medial and the point for potential removal
                added[coords]= (m_index, end_index)
            elif coords in added:
                # see comment above
                i, j= added.pop (coords)  # this also removes the (k, v) pair
                ends[i][j]= None
                removed.add (coords)

    return ends


def points_in_way (line, way):
    """Returns the points in line that are in way too."""
    return [ p for p in line.coords if Point (p).touches (way) ]


def radial_points (way, skel, medials):
    """Finds the points on the radials that are on the way.
    Returns a list of (tuples containing (a list of points) for each of start,
    end) for each medial."""
    ends= medials_ends (medials)
    radial_points= [ ([], []) for medial in medials ]

    def get_radial_points (end, end_index, m_index, line):
        # the rest of the params are taken from the scope
        if line.touches (end):
            points= points_in_way (line, way)
            if len (points)==1: # there might be none!
                radial_points[m_index][end_index].append (points[0])

    for line in skel.geoms:
        for m_index, (start, end) in enumerate (ends):
            if start is not None:
                get_radial_points (start, 0, m_index, line)
            if end is not None:
                get_radial_points (end,   1, m_index, line)

    return radial_points


# but not really, because the computations are done in Point()s anyways
def middle_point (p1, p2):
    """Returns the point between p1 and p2"""
    # TODO: support more points!
    return ((p1[0]+p2[0])/2,
            (p1[1]+p2[1])/2)


# finally we get somewhere
def extend_medials (way, skel, medials):
    """Extends medial with segments that go from the middle point of the
    way's flow segments to the ends of the medial."""
    points_per_medial_per_end= radial_points (way, skel, medials)

    new_medials= []

    for m_index, (start_points, end_points) in enumerate (points_per_medial_per_end):
        new_start_point= None
        new_end_point= None
        # TODO: support more points!
        if len (start_points)==2:
            new_start_point= middle_point (*start_points)
        if len (end_points)==2:
            new_end_point=   middle_point (*end_points)

        if new_start_point and new_end_point:
            # extend both ends
            new_medials.append ((new_start_point, *medials[m_index].coords, new_end_point))
        elif new_start_point and not new_end_point:
            # you see the picture...
            new_medials.append ((new_start_point, *medials[m_index].coords))
        elif not new_start_point and new_end_point:
            new_medials.append ((*medials[m_index].coords, new_end_point))
        else:
            # it's an internal medial, copy as-is
            new_medials.append (medials[m_index].coords)

    return MultiLineString (new_medials)


# helper functions
def decode (way):
    """convert a str() with a wkb (what usually comes out of postgis)
    into a shapely.geometry."""
    return wkb.loads (codecs.decode (str (way), 'hex'))


def skeleton_medial_from_postgis (connection, way):
    """Returns the skeleton for way as calculated by PostGIS.
    connection must be a psycopg2 connection and way must be a shapey.geometry."""
    way= wkb.dumps (way)

    cursor= connection.cursor ()
    cursor.execute ("SELECT ST_StraightSkeleton(%s), ST_ApproximateMedialAxis(%s);",
                    (way, way))
    skel, medials= [ decode (i) for i in (cursor.fetchone ()) ]

    cursor.close ()

    # medial comes as a series of segments, convert to lines as much as possible
    medials= shapely.ops.linemerge (medials)
    # linemerge() returns a single LineString if it can, but the rest of the algos
    # work with MultiLineString
    if type (medials)==LineString:
        medials= MultiLineString ([ medials ])

    return skel, medials


def write (file_name, line):
    """Writes the LineString to the given filename, appending if the file already
    exists, or creating a new file if not."""
    crs= fiona.crs.from_epsg (900913)
    # I don't know where this 11 comes from, or why it's converted to 0
    # when the records are written
    properties= OrderedDict ([ ('FID', 'int:11') ])
    schema= dict (geometry='LineString', properties=properties)
    driver= 'ESRI Shapefile'

    try:
        f= fiona.open (file_name, 'a', driver=driver, crs=crs, schema=schema)
    except OSError as e:
        # the file does not exist, create a new one
        f= fiona.open (file_name, 'w', driver=driver, crs=crs, schema=schema)

    # prepare the record
    r= r= dict (geometry=dict (type='LineString', coordinates=line.coords),
                properties=properties)
    f.write (r)
    f.close ()

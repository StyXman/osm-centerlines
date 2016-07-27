# /usr/bin/python3

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

import geoalchemy2

import shapely.wkb
import shapely.ops
from shapely.geometry import Point, LineString

import fiona
import fiona.crs

import codecs
import errno
from collections import OrderedDict

# too much boilerplate!
e= sqla.create_engine ('postgresql:///gis')
S= orm.sessionmaker (bind=e)
s= S()
m= sqla.MetaData (e)
Base= declarative_base(metadata=m)

class OSM_Polygons (Base):
    __tablename__= 'planet_osm_polygon'
    __table_args__= { 'autoload': True }
    osm_id= sqla.Column (sqla.Integer, primary_key=True)
    way= sqla.Column (geoalchemy2.Geometry('POLYGON'))

class OSM_Lines (Base):
    __tablename__= 'planet_osm_line'
    __table_args__= { 'autoload': True }
    osm_id= sqla.Column (sqla.Integer, primary_key=True)
    way= sqla.Column (geoalchemy2.Geometry('POLYGON'))

class PgSkel (Base):
    __tablename__= 'planet_osm_riverbank_skel'
    __table_args__= { 'autoload': True }
    osm_id= sqla.Column (sqla.Integer, primary_key=True)
    way= sqla.Column (geoalchemy2.Geometry('POLYGON'))
    skel= sqla.Column (geoalchemy2.Geometry('POLYGON'))

class PgMedial (Base):
    __tablename__= 'planet_osm_riverbank_medial'
    __table_args__= { 'autoload': True }
    osm_id= sqla.Column (sqla.Integer, primary_key=True)
    way= sqla.Column (geoalchemy2.Geometry('POLYGON'))
    medial= sqla.Column (geoalchemy2.Geometry('POLYGON'))

def way_skel_medials (osm_id):
    def get (table, osm_id):
        return s.query (table).filter (table.osm_id==osm_id).first ()

    def decode (way):
        # this is strange, I would expect codecs.decode() to accept bytes() only
        # but so it happens that codecs can en/decode to/from bytes or str at will
        # in particular, 'hex' encodes to str and decodes to bytes
        # which makes sense (the str is the representation of the bytes,
        # not the other way around.
        return shapely.wkb.loads (codecs.decode (str (way), 'hex'))

    way= decode (get (OSM_Polygons, osm_id).way)
    skel= decode (get (PgSkel, osm_id).skel)
    medials= shapely.ops.linemerge (decode (get (PgMedial, osm_id).medial))
    # this might still return MultiLineString; f.i., in case of branches
    # if not, convert it to an iterable for the rest of the algos
    if type (medials)==LineString:
        medials= ( medials, )

    return (way, skel, medials)


def medial_in_skel (skel, medial):
    """Finds the index of the LineString in skel that's the medial."""
    for index, line in enumerate (skel.geoms):
        if line.equals (medial.geoms[0]):
            return index

def radials (skel, medial):
    """Finds the LineStrings in skel that radiate from the ends of the medial."""
    start= Point (medial.geoms[0].coords[0])
    end= Point (medial.geoms[0].coords[-1])
    radials= [ [], [] ]

    for line in list (skel.geoms):
        if line.touches (start):
            radials[0].append (line)
        elif line.touches (end):
            radials[1].append (line)

    return radials


def line_ends (line):
    """Returns the coords (not Points) of the ends of a LineString."""
    return ( line.coords[0], line.coords[-1] )


def medials_ends (medials):
    """Finds the points at the end of several lines, which
    might have points in common. think of Ts, Vs or Ys.

    The result is a list in medial order with a list of points (0, 1 or 2)."""
    # NOTE: Vs could be a bitch

    ends= [ [] for i in medials ]
    added= {}
    removed= set ()

    for index, medial in enumerate (medials):
        for coords in line_ends (medial):
            if coords not in added and coords not in removed:
                point= Point (*coords)
                ends[index].append (point)
                # save the index of the medial and the point for potential removal
                added[coords]= (index, point)
            elif coords in added:
                # see comment above
                i, point= added.pop (coords)  # this also removes the (k, v) pair
                ends[i].remove (point)
                removed.add (coords)

    return ends


# in fact I need something more specific
def radial_points (way, skel, medial):
    """Finds the points on the radials that are on the way."""
    start= Point (medial.coords[0])
    end= Point (medial.coords[-1])
    radial_points= [[], []]

    def points_in_way (line, way):
        points= [ Point (p) for p in line.coords ]
        return [ p for p in points if p.touches (way) ]

    for line in skel.geoms:
        # ignore medial
        # NOTE: since medials are now LineString, this is no longer True
        # except in the most simple case
        if line.equals (medial):
            continue

        if line.touches (start):
            points= points_in_way (line, way)
            if len (points)==1: # there might be none!
                radial_points[0].append (points[0])
        elif line.touches (end):
            points= points_in_way (line, way)
            if len (points)==1: # there might be none!
                radial_points[1].append (points[0])

    return radial_points

# but not really, because the computations are done in Point()s anyways
def middle_point (p1, p2):
    """Returns the point between p1 and p2"""
    # Point does not have + or / defined!
    return Point (*[ (p1.coords[0][i]+p2.coords[0][i])/2 for i in (0, 1) ])

# finally we get somewhere
def extend_medial (way, skel, medial):
    """Extends medial with segments that go from the middle point of the
    way's flow segments to the ends of the medial."""
    ((p1, p2), (p3, p4))= radial_points (way, skel, medial)

    # now, p1, p2 are related to start
    # and p3, p4 to end
    # so it should be
    # [ middle_point (p1, p2), start, ..., end, middle_point (p3, p4) ]
    return LineString ([ middle_point (p1, p2), *medial.coords, middle_point (p3, p4) ])

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

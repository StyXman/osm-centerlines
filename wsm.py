#! /usr/bin/python3

import sqlalchemy as sqla
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

import geoalchemy2

import shapely.wkb
import shapely.ops
from shapely.geometry import LineString, MultiLineString

from centerlines import decode

import sys


# the following list of riverbanks has some, but not all the usecase tests
# we want to solve, but I will be expanding as I find new examples
# and osm_ids are changed
examples = (
    147639890,  # simplest case, isolated rectangle, medial a straight segment,
                # skel includes the parted X   >----<
    147639834,  # slightly more complex, several segments, but still basically
                # >----<
    147639866,  # T shape

    # untested
    # L'Eygoutier section close to the Tennis Club du Littoral, Toulon
    147639843,  # section with centerline, flow-in and through 224939728, flow out 27335952
                # has branch
    147639869,  # section without centerline, no flow-in or flow-out lines
    147639871,  # section without centerline, flow-in 271441410
    147639931,  # section without centerline, flow-in close to 27046147
    147639837,  # calculated centerline coincides with flow-in point, but
                # centerline is 27554300 and flow-in is 27351558,
                # touches the first, but not the latter, they share endpoint
    147639884,  # has flow-in, centerline, flow-out 27554300, several branches
                # one is a tributary 31104263
    147639857,  # calculated centerline does not reach node at flow-in
                # real flow-in, centerline is 27554300, flow-out is 30839685
    147639874,  # 30847660 is flow-in, centerline, close to be flow-out but quite
                # no real flow-out
                # can we really do anything about it?
    147639896,  # slightly more complex, flow-in close to medial, flow-out
                # deviates, complex
    )

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

    way= decode (get (OSM_Polygons, osm_id).way)
    skel= decode (get (PgSkel, osm_id).skel)
    medials= shapely.ops.linemerge (decode (get (PgMedial, osm_id).medial))
    # linemerge() returns a single LineString if it can, but the rest of the algos
    # work with MultiLineString
    if type (medials)==LineString:
        medials= MultiLineString ([ medials ])

    return (way, skel, medials)

if __name__=='__main__':
    w, s, m= way_skel_medials (int (sys.argv[1]))

    print (str (w))
    print (str (s))
    print (str (m))

#! /usr/bin/env python3

import centerlines
import psycopg2
import json
import sys
import shapely.geometry
import time

# TODO: parameter
tolerance= 0.00001

s= sys.stdin.read()
# print (s, file=sys.stderr)
try:
    data= json.loads(s)
except json.decoder.JSONDecodeError:
    print ('Malformed JSON: >%s<' % s, file=sys.stderr)
else:
    ans= dict (type='FeatureCollection',features=[])
    conn= psycopg2.connect (dbname='gis')

    for feature in data['features']:
        shape= shapely.geometry.shape (feature['geometry'])

        start= time.perf_counter ()
        shape= shape.simplify (tolerance, False)
        mid1= time.perf_counter ()
        skel, medials= centerlines.skeleton_medials_from_postgis (conn, shape)
        mid2= time.perf_counter ()
        medials= centerlines.extend_medials (shape, skel, medials)
        mid3= time.perf_counter ()
        medials= shapely.geometry.MultiLineString ([ medial.simplify (tolerance, False)
                                                     for medial in medials ])
        end= time.perf_counter ()

        print ("simp1: %.6f; pg: %.6f; ext: %.6f; simp2: %.6f" %
               (mid1-start, mid2-mid1, mid3-mid2, end-mid3),
               file=sys.stderr)

        ans['features'].append (dict (type='Feature',
                                      geometry=shapely.geometry.mapping (medials)))

    s= json.dumps (ans)
    # print (s, file=sys.stderr)
    print (s)

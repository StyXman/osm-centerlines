# osm-centerlines

This project is an attempt to automatcally generate centerlines for riverbanks
that have none in OSM's data. You can read about the rationale behind it
[here](http://www.grulic.org.ar/~mdione/glob/posts/deriving-centerlines-from-riverbanks-without/).
As per @imagico's idea, one goal for this project is to become a JOSM plugin.

## Instalation

So far the project is divided in two parts. The module itself has just a couple
of dependencies: `python-shapely` for the processing and `python-fiona` for
writing into a shapefile.

The problem is that, so far, the algos force you to provide now only the polygon
you want to process, but also its
[skeleton](https://en.wikipedia.org/wiki/Topological_skeleton) and
[medial](https://en.wikipedia.org/wiki/Medial_axis). The code extends the
medial using info extracted from the skeleton in such a way that the resulting
medial ends on a segment of the polygon, hopefully the one(s) that cross
from one riverbank to another at down and upstream. Calculating the skeleton
could be performed by [`CGAL`](http://www.cgal.org/), but the current
[Python binding](https://github.com/cgal/cgal-swig-bindings) doesn't include
that function yet. As for the medial, SFCGAL (a C++ wrapper for CGAL)
[exports a function that calculates an approximative medial](https://oslandia.github.io/SFCGAL/doxygen/group__public__api.html#ga85786b4c262436d1f1fccad17f3cb7f2),
but there seem to be no Python bindings for them yet.

So, a partial solution would be to use PostGIS-2.2's `ST_StraightSkeleton()` and
`ST_ApproximateMedialAxis()`, and that's what I added in the second part of this
project. `wsm.py` has functions that, given a `osm_id`, it returns the way, its
skeleton and medial ready to be fed into `extend_medials()`, which is the main
and probably only entry point of this module. If you want to use `wsm.py`, please
execute this in your OSM's imported data in a PostgreSQl+PostGIS server:

    CREATE VIEW planet_osm_riverbank_skel   AS SELECT osm_id, way, ST_StraightSkeleton (way)      AS skel   FROM planet_osm_polygon WHERE waterway = 'riverbank';
    CREATE VIEW planet_osm_riverbank_medial AS SELECT osm_id, way, ST_ApproximateMedialAxis (way) AS medial FROM planet_osm_polygon WHERE waterway = 'riverbank';

Also, if your data is big (Europe or planet big), you'll probably also will want
this:

    CREATE INDEX planet_osm_polygon_osm_id ON planet_osm_polygon (osm_id);

This will speed up riverbank extraction by id.

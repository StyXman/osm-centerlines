# osm-centerlines

This project is an attempt to automatcally generate centerlines for riverbanks
that have none in OSM's data. You can read about the rationale behind it
[here](http://www.grulic.org.ar/~mdione/glob/posts/deriving-centerlines-from-riverbanks-without/).
As per @imagico's idea, one goal for this project is to become a JOSM plugin.

## Instalation

So far the project is divided in two parts. The module itself has just a couple
of dependencies: `python3-shapely` for the processing and `python3-fiona` for
writing into a shapefile, and optionaly.`python3-psycopg2` for usgin PostGIS
as the source for the skeleton and the medial.

See `requirements.txt`.

## Usage

If you have your way, skeleton and medials as `shapely.geometry` objects, just
call:

    import centerlines

    c_lines= centerlines.extend_medials (way, skeleton, medials)

This returns the medials extended to the way, in form of a `MultiLineString`.

If you only have your way, but have a PostgreSQL+PostGIS database you can access,
then you can use the helper function:

    import psycopg2

    c= psycopg2.connect (...)

    skeleton, medials= centerlines.skeleton_medials_from_postgis (c, way)
    c_lines= centerlines.extend_medials (way, skeleton, medials)

# -*- coding: utf-8 -*-

from .common import logger

from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform
from shapely.affinity import translate, scale, rotate
from shapely import wkt, wkb
import mercantile
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

from mapbox_vector_tile import encode as mvt_encode
from py4web import response as rsp
from py4web.core import Fixture

def merc2xy(x, y, z, sgeom):
    """ Apply some affine transformations to input shapely geometry for coordinates
    transformation from Mercatore to local tile pixels.

    sgeom @shapely.geom : Input polygon

    Returns a brand new shapely polygon in the new coordinates.
    """
    logger.error("Still some geometrc problems to solve here! Soome othr debug is requred. Do not use for production.")

    MVT_EXTENT = 4096
    X_min, Y_max = mercantile.xy(*mercantile.ul(x, y, z))
    X_max, Y_min = mercantile.xy(*mercantile.ul(x+1, y-1, z))

    geom_3857 = transform(transformer.transform, sgeom)
    geom_XY = translate(geom_3857, -X_min, -Y_min)
    geom_xy = scale(geom_XY, MVT_EXTENT/(X_max-X_min), MVT_EXTENT/(Y_max-Y_min), origin=(0,0,0))
    # geom_xy = rotate(geom_xyr, 120, origin='center')
    return geom_xy

def geom2tile(x, y, z, geom):
    geom_xy = merc2xy(x, y, z, shape(geom))
    as_json = mapping(wkt.loads(wkt.dumps(geom_xy, rounding_precision=0)))
    as_json['coordinates'] = [list(map(lambda c: list(map(int, [c[0], c[1]])), as_json['coordinates'][0]))]
    return as_json

class as_pbf(Fixture):
    def transform(self, data, *_):
        rsp.headers["Content-Type"]="application/x-protobuf"
        return mvt_encode(data)

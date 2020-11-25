# -*- coding: utf-8 -*-

from ..common import logger
from .models import db
from ..planetstore.populate.tile import tilebbox

import datetime
import mercantile
import re
from collections import OrderedDict
from itertools import chain
from functools import reduce

from psycopg2.errors import InternalError_
from psycopg2.errors import SyntaxError as PGSyntaxError

from .pbftools import geom2tile
import h3
import mercantile as mt

def fetch_by_id(*ids):
    result = db(db.points.id.belongs(ids)).select()
    return {"type": "FeatureCollection", "features": list(map(lambda row: row.feature, result))}

def fetch_points(minlon=None, minlat=None, maxlon=None, maxlat=None, all=True, source_name='__GENERIC__'):

    basequery = (db.points.source_name==source_name)

    # Spatial query: "Within bounding box"
    if not any(map(lambda cc: cc is None, [minlon, minlat, maxlon, maxlat])):
        basequery &= "ST_Within(points.geom, ST_MakeEnvelope({}, {}, {}, {}, 4326))".format(
            minlon, minlat, maxlon, maxlat
        )

    # delivery_form_fields = {ff.name: ff for ff in _delivery_form_fields()}
    # Text search in property values
    # if not flt is None:
    #     basequery &= '({})'.format(' OR '.join(["((points.properties->>'{}')::text ILIKE '%{}%')".format(
    #         ff.name, flt) for ff in delivery_form_fields.values()
    #     ]))

    # if not all:
    #     basequery &= "((points.properties->>'created_by')::text = '{}')".format(auth.user_id)

    result = db(basequery).select()

    return {
        "type": "FeatureCollection",
        "features": list(map(lambda row: row.feature, result))
    }

def _get_buffered_bounds(minlon, minlat, maxlon, maxlat, zoom=18, classic=True):
    """
    minlon, minlat, maxlon, maxlat @float : Bbox limits;
    zoon @integer : Square tile zoom level or hexagonal tile resolution;
    classic @boolean : Whether to use classic square tiles or Uber H3 hexagonal ones.

    Returns the bbox limits that fits to the tiles touched by the bbox area introduced.
    In this way you are sure to fetch all the inolved points.
    """

    if classic:
        resolution = zoom
        ultile = mt.tile(minlon, maxlat, zoom)
        left, top = mt.ul(*ultile)
        rbtile = mt.tile(maxlon, minlat, zoom)
        brtile = lambda x, y, z: (x+1, y+1, z)
        right, bottom = mt.ul(*brtile(*rbtile))
        # get_tile = lambda lon, lat: mt.tile(lon, lat, zoom)
    else:
        # ultile = h3.geo_to_h3(maxlat, minlon, zoom)
        resolution = min(12, zoom)

        ultile = h3.geo_to_h3(maxlat, minlon, resolution)
        ulboundary = h3.h3_to_geo_boundary(ultile)

        rbtile = h3.geo_to_h3(minlat, maxlon, resolution)
        rbboundary = h3.h3_to_geo_boundary(rbtile)
        lats, lons = zip(*chain(ulboundary, rbboundary))
        left, right = min(lons), max(lons)
        top, bottom = max(lats), min(lats)

    return left, bottom, right, top, resolution,

def _geomdbset(tab, minlon=None, minlat=None, maxlon=None, maxlat=None, source_name='__GENERIC__', tags=[]):
    """
    tab @pydal.table : DB table to query.
    minlon @float : Bounding box left limit longitude coordinate.
    minlat @float : Bounding box bottom limit latitude coordinate.
    maxlon @float : Bounding box right limit longitude coordinate.
    maxlat @float : Bounding box top limit latitude coordinate.
    source_name @text : Source name (ex.: osm).
    tags @list : List of dictionaries of tags to query for (ex.: [{'amenity': 'bar'}, ...]);
        Geometries resulting from query will must have at least all tags from any dictionary in the list.
    otags : Tags to query for.
        Geometries resulting from query will must be tagged as one of the passed tag.

    """
    basequery = (tab.source_name==source_name)
    if not any(map(lambda cc: cc is None, [minlon, minlat, maxlon, maxlat])):
        basequery &= "ST_Intersects({}.geom, ST_MakeEnvelope({}, {}, {}, {}, 4326))".format(
            tab, minlon, minlat, maxlon, maxlat
        )

    if tags:
        basequery &= "("+" OR ".join([
            " AND ".join([
                "({tab}.tags->>'{key}' = '{value}')".format(key=key, value=value, tab=tab) \
                    for key,value in tt.items()
                ]) for tt in tags
            ])+")"

    # logger.debug(db(basequery)._select())
    return db(basequery)

def fetch_(minlon=None, minlat=None, maxlon=None, maxlat=None, source_name='__GENERIC__', tags=[]):
    """ Returns a multi geometry type FeatureCollection accordingly to given tags
    and bounding box limits.
    """

    def feats():
        yield _geomdbset(db.points, minlon, minlat, maxlon, maxlat, source_name, tags=tags).select()
        yield _geomdbset(db.ways, minlon, minlat, maxlon, maxlat, source_name, tags=tags).select()
        yield _geomdbset(db.polys, minlon, minlat, maxlon, maxlat, source_name, tags=tags).select()
        yield _geomdbset(db.mpolys, minlon, minlat, maxlon, maxlat, source_name, tags=tags).select()

    return map(lambda row: row.feature, chain(*feats()))

def fetch(minlon=None, minlat=None, maxlon=None, maxlat=None, source_name='__GENERIC__', tags=[]):
    return {
        "type": "FeatureCollection",
        "features": list(fetch_(**vars()))
    }

def fetcharound(lon, lat, dist=200, bdim=None, buffer=0, source_name='__GENERIC__', tags=[]):
    """ Returns a multi geometry type FeatureCollection accordingly to given tags
    around a center point.
    """
    _extra = {}
    if not bdim is None: _extra['bdim'] = bdim
    bbox = tilebbox(dist=dist, lon=lon, lat=lat, buffer=buffer, **_extra)
    logger.debug(bbox)
    return fetch(
        minlon = bbox.minx,
        minlat = bbox.miny,
        maxlon = bbox.maxx,
        maxlat = bbox.maxy,
        source_name = source_name,
        tags = tags
    )

def vtile(x, y, z=18, source_name='__GENERIC__', tags=[]):
    """ """
    bounds = mercantile.bounds(x, y, z)
    feats_ = fetch_(
        minlon = bounds.west,
        minlat = bounds.south,
        maxlon = bounds.east,
        maxlat = bounds.north,
        source_name = source_name,
        tags = tags
    )
    return dict(
        name = 'mytiles',
        # extent = 4096,
        # version = 2,
        features = [dict(
            id = feat["id"],
            type = 3,
            geometry = geom2tile(x, y, z, feat["geometry"]),
            properties = {}# feat["properties"]
        ) for feat in feats_]
    )

def housenumber_components(hn):
    def loopOlettrs(ll):
        for l in ll:
            if l.isdigit():
                yield l
            else:
                break
    # components = {}
    number = ''.join(loopOlettrs(hn))
    letter, color = '', '',
    if hn.endswith('r'):
        color = 'r'
        letters = hn[len(number):-1].strip()
    elif hn.lower().endswith('rosso'):
        color = 'r'
        letters = hn[len(number):-len('rosso')].strip()
    else:
        letters = hn[len(number):]
    if letters:
        letter = letters
    return number and int(number), letter, color, hn,

def guess_street(sugg, comune, source=None, limit=10):
    """ """

    if source=='disabled': return dict()

    words = filter(lambda e: e, re.split(";|,|\.|\n| |'", sugg))
    query = (db.housenumbers.housenumber!='') & \
        db.housenumbers.street.contains(list(words), all=True) & \
        db.housenumbers.city.contains(comune)

    if not source is None:
        query &= (db.housenumbers.source_name==source)

    housenumbers = "array_agg(housenumbers.housenumber)"

    res = db(query).select(
        housenumbers,
        db.housenumbers.street,
        db.housenumbers.city,
        db.housenumbers.street.lower(),
        groupby = db.housenumbers.street|db.housenumbers.city,
        orderby = db.housenumbers.street,
        limitby = (0,min((int(limit), 50,)),)
    ).group_by_value(db.housenumbers.street)

    return OrderedDict(
        sorted((k, OrderedDict(map(lambda tt: (tt[-1], {k: tt[i] for i,k in enumerate(['number', 'letter', 'color']) if tt[i]}), sorted(map(housenumber_components, [r[housenumbers] for r in v][0])))),) \
        # sorted((k, map(housenumber_components, [r[housenumbers] for r in v][0]),) \
            for k,v in res.items()
        )
    )

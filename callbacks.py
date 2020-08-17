# -*- coding: utf-8 -*-

from .models import db

import datetime
import mercantile
import re
from collections import OrderedDict
from itertools import chain

from psycopg2.errors import InternalError_
from psycopg2.errors import SyntaxError as PGSyntaxError

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

def _geomdbset(tab, minlon=None, minlat=None, maxlon=None, maxlat=None, source_name='__GENERIC__', **tags):
    basequery = (tab.source_name==source_name)
    if not any(map(lambda cc: cc is None, [minlon, minlat, maxlon, maxlat])):
        basequery &= "ST_Intersects({}.geom, ST_MakeEnvelope({}, {}, {}, {}, 4326))".format(
            tab, minlon, minlat, maxlon, maxlat
        )
    if tags:
        basequery &= " AND ".join(["({tab}.tags->>'{key}' = '{value}')".format(key=key, value=value, tab=tab) \
            for key,value in tags.items()])

    return db(basequery)

def fetch(minlon=None, minlat=None, maxlon=None, maxlat=None, source_name='__GENERIC__', **tags):
    """ Returns a multi geometry type FeatureCollection accordingly to given tags and bbox
    """

    def feats():
        yield _geomdbset(db.points, minlon, minlat, maxlon, maxlat, source_name, **tags).select()
        yield _geomdbset(db.ways, minlon, minlat, maxlon, maxlat, source_name, **tags).select()
        yield _geomdbset(db.polys, minlon, minlat, maxlon, maxlat, source_name, **tags).select()
        yield _geomdbset(db.mpolys, minlon, minlat, maxlon, maxlat, source_name, **tags).select()

    return {
        "type": "FeatureCollection",
        "features": list(map(lambda row: row.feature, chain(*feats())))
    }

def vtile(x, y, z=18, source_name='__GENERIC__', **tags):
    """ """
    bounds = mercantile.bounds(x, y, z)
    return fetch(
        minlon = bounds.west,
        minlat = bounds.south,
        maxlon = bounds.east,
        maxlat = bounds.north,
        source_name = source_name,
        **tags
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

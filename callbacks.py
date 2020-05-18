# -*- coding: utf-8 -*-

from .models import db

import datetime
import mercantile

def fetch_by_id(*ids):
    result = db(db.points.id.belongs(ids)).select()
    return {"type": "FeatureCollection", "features": list(map(lambda row: row.feature, result))}

def fetch_points(minlon=None, minlat=None, maxlon=None, maxlat=None, all=True, source_name='__GENERIC__'):

    basequery = (db.points.source_name==source_name)

    # Spatial query: "Within bounding nox"
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

    return {"type": "FeatureCollection", "features": list(map(lambda row: row.feature, result))}

def vtile(x, y, z=18, source_name='__GENERIC__'):
    """ """
    bounds = mercantile.bounds(x, y, z)
    return fetch_points(
        minlon = bounds.west,
        minlat = bounds.south,
        maxlon = bounds.east,
        maxlat = bounds.north,
        source_name = source_name
    )

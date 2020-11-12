# -*- coding: utf-8 -*-

import geojson
# import shapely.wkt
from hashids import Hashids
from pydal.objects import Table
from py4web import Field
from geomet import wkt
import mercantile as mc
import h3

from .common import db

def geojsonFeature(id, geometry, properties):
    return geojson.Feature(
        geometry = geometry,
        properties = properties,
        id = id
    )

def raise_error(err):
    raise err

class PlanetTable(Table):
    """docstring for PlanetTable."""

    def __init__(self, *args, **kwargs):
        super(PlanetTable, self).__init__(*args, **kwargs)
        self._set_encoder()
        self._set_feature_co()

    def _set_encoder(self):
        self._extra = {'encoder': Hashids(min_length=1)}
        self._extra["_decode"] = lambda encoded: self._extra['encoder'].decode(encoded) or \
            raise_error(Exception('String expected, "{}" found'.format(encoded)))
        self._extra["decode"] = lambda encoded: dict(zip(['src_id', 'id'], self._extra['encoder'].decode(encoded)))
        self._extra["get_by_hash"] = lambda encoded: self(**self._extra["decode"](encoded))
        # self._extra["fetch_info"] = lambda encoded: info(id=self._extra["_decode"](encoded)[1])

    def _set_alias(self, alias, fieldname):
        """ Sets an alias for the given field value """

        setattr(self, alias, Field.Virtual(alias,
            lambda row: row[self._tablename][fieldname]
        ))


    def _set_hashid(self, fieldname, first, *ofields):

        setattr(self, fieldname, Field.Virtual(fieldname,
            lambda row: self._extra['encoder'].encode(
                row[self._tablename][first],
                *map(lambda ff: row[self._tablename][ff], ofields)
            )
        ))

    def _set_feat_properties(self, **kwargs):

        def _props(row):
            properties = dict(
                row[self._tablename].properties or row[self._tablename].tags,
                id = row[self._tablename].hashid,
                # **{"_{}_".format(row[self._tablename].source_name): row[self._tablename].source_id}
            )
            properties.update({
                k: row[self._tablename][v] if not callable(v) else v(row[self._tablename])\
                    for k,v in kwargs.items()})
            return properties

        setattr(self, 'feat_properties', Field.Virtual('feat_properties', _props))

    def _set_geometry(self):

        if 'geom' in self.fields and self['geom'].type=='geometry()':
            self.feat_geometry = Field.Virtual('feat_geometry', lambda row: wkt.loads(row[self._tablename].geom))

    def _set_feature_co(self):
        self._set_hashid('hashid', 'src_id', 'id')
        self._set_feat_properties()
        self._set_geometry()

        if 'geom' in self.fields and self['geom'].type=='geometry()':

            self.feature = Field.Virtual('feature', lambda row: geojsonFeature(
                geometry = row[self._tablename].feat_geometry,
                properties = row[self._tablename].feat_properties,
                id = row[self._tablename].hashid
            ))

def get_tile(lon, lat, zoom, classic=True):
    if classic is True:
        return mc.tile(lon, lat, zoom)
    elif classic is False:
        return h3.geo_to_h3(lat, lon, resolution=zoom)

# def foo(row, zoom, classic=True):
#     import pdb; pdb.set_trace()

class PlanetPointTable(PlanetTable):
    """docstring for PlanetPointTable."""

    def __init__(self, *args, **kwargs):
        super(PlanetPointTable, self).__init__(*args, **kwargs)
        self._set_tile()

    def _set_tile(self):
        self.tile = Field.Method(
            'tile',
            lambda row, zoom, classic=True: get_tile(
                *wkt.loads(row[self._tablename].geom)["coordinates"],
                zoom = zoom,
                classic = classic
            )
        )

class PlanetGraphTable(PlanetTable):
    """docstring for PlanetGraphTable."""

    def _set_encoder(self):
        PlanetTable._set_encoder(self)
        self._extra['node_encoder'] = db.points._extra['encoder']

    def _set_node_hashid(self, fieldname, first, *ofields):

        setattr(self, fieldname, Field.Virtual(fieldname,
            lambda row: self._extra['node_encoder'].encode(
                row[self._tablename][first],
                *map(lambda ff: row[self._tablename][ff], ofields)
            )
        ))

    def _set_feature_co(self):
        self._set_hashid('hashid', 'src_id', 'id')
        self._set_node_hashid('shashid', 'src_id', 'sinfo_id')
        self._set_node_hashid('thashid', 'src_id', 'tinfo_id')

        # self._set_alias("shid", 'shashid')
        # self._set_alias("thid", 'thashid')

        self._set_feat_properties(weight=lambda row: round(row.len, 3))
        if 'geom' in self.fields and self['geom'].type=='geometry()':

            self.feature = Field.Virtual('feature', lambda row: geojson.Feature(
                geometry = wkt.loads(row[self._tablename].geom),
                properties = row[self._tablename].feat_properties,
                id = row[self._tablename].hashid
            ))

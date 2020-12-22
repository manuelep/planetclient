# -*- coding: utf-8 -*-

from py4web import action, request, abort, redirect, URL, HTTP

from .callbacks import vtile as vtile_
from .callbacks import guess_street as guess_street_
from .callbacks import fetch as fetch_
from .callbacks import fetcharound as fetcharound_

# from .pbftools import as_pbf
# from .protobuf import Protobuf

# from geopbf import Protobuf
# from geopbf.pbfpp import Prototizerpp as Prototizer
# from geopbf import Prototizer

from kilimanjaro.frameworks.py4web.controller import LocalsOnly

from .common import webWrapper, pbfWebWrapper

@action('planet/vtile/<xtile:int>/<ytile:int>/<zoom:int>', method=['GET'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile_xyz(xtile, ytile, zoom):
    return pbfWebWrapper(vtile_, x=xtile, y=ytile, z=zoom, source_name='osm')()

@action('planet/vtile/<xtile:int>/<ytile:int>', method=['GET','POST'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile_xy(xtile, ytile):
    return pbfWebWrapper(vtile_, x=xtile, y=ytile, source_name='osm')()

@action('planet/vtile', method=['GET','POST'])
@action.uses(LocalsOnly())
@action.uses(pbfWebWrapper)
def vtile():
    return pbfWebWrapper(vtile_, source_name='osm')()

@action('planet/fetch', method=['GET', 'POST'])
@action.uses(LocalsOnly())
def fetch():
    return webWrapper(fetch_, source_name='osm')()

@action('planet/fetcharound', method=['GET', 'POST'])
@action.uses(LocalsOnly())
def fetcharound():
    return webWrapper(fetcharound_, source_name='osm')()

@action('planet/guess_street/<sugg>', method=['GET'])
@action.uses(LocalsOnly())
def guess_street(sugg):
    return webWrapper(guess_street_, sugg=sugg, comune='Genova', source='osm')()

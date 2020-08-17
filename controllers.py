# -*- coding: utf-8 -*-

from .callbacks import vtile as vtile_
from .callbacks import guess_street as guess_street_
from .callbacks import fetch as fetch_

from py4web import action, request, abort, redirect, URL, HTTP

from swissknife.py4web import brap, LocalsOnly

@action('planet/vtile/<xtile:int>/<ytile:int>/<zoom:int>', method=['GET'])
@action.uses(LocalsOnly())
def vtile_xyz(xtile, ytile, zoom):
    return brap(x=xtile, y=ytile, z=zoom, source_name='osm')(vtile_)()

@action('planet/vtile/<xtile:int>/<ytile:int>', method=['GET','POST'])
@action.uses(LocalsOnly())
def vtile_xy(xtile, ytile):
    return brap(x=xtile, y=ytile, source_name='osm')(vtile_)()

@action('planet/vtile', method=['GET','POST'])
@action.uses(LocalsOnly())
def vtile():
    return brap(source_name='osm')(vtile_)()

@action('planet/fetch', method=['GET', 'POST'])
@action.uses(LocalsOnly())
def fetch():
    return brap(source_name='osm')(fetch_)()

@action('planet/guess_street/<sugg>', method=['GET'])
@action.uses(LocalsOnly())
def guess_street(sugg):
    return brap(sugg=sugg, comune='Genova', source='osm')(guess_street_)()

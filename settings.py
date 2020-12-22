# -*- coding: utf-8 -*-

from ..settings import *

from geopbf import settings as gpbfsettings

# gpbfsettings.CACHE_NEW = True
# gpbfsettings.DB_URI = "postgres://postgres:postgres@localhost/vtile_cache"
# gpbfsettings.DB_POOL_SIZE = 20
gpbfsettings.DB_FOLDER = DB_FOLDER
gpbfsettings.UPLOAD_FOLDER = UPLOAD_FOLDER
gpbfsettings.STATIC_UPLOAD_FOLDER = os.path.join(APP_FOLDER, "static", "uploads")

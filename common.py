# -*- coding: utf-8 -*-

import os
from . import settings
from ..planetstore.common import logger

try:
    from ..planetstore.models import db
except ImportError:
    raise
    from py4web import DAL
    # connect to db
    db = DAL(settings.DB_URI,
        folder=settings.DB_FOLDER, pool_size=settings.DB_POOL_SIZE,
        lazy_tables=False, migrate=False, fake_migrate=False,
        check_reserved=False
    )

from geopbf.pbfpp import Prototizerpp as PbfPrototizer
from kilimanjaro.frameworks.py4web.controller import WebWrapper

webWrapper = WebWrapper()
pbfWebWrapper = PbfPrototizer()

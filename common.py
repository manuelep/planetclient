# -*- coding: utf-8 -*-

from .import settings
from ..settings import DB_FOLDER

from ..planetstore.common import logger

try:
    from ..planetstore.models import db
except ImportError:
    raise
    from py4web import DAL
    # connect to db
    db = DAL(settings.DB_URI,
        folder=DB_FOLDER, pool_size=settings.DB_POOL_SIZE,
        lazy_tables=False, migrate=False, fake_migrate=False,
        check_reserved=False
    )

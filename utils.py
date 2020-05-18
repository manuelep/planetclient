# -*- coding: utf-8 -*-

from .models import db

def point2record(eid):
    """
    eid @string : The encoded info_id
    """
    _, info_id =  db.points._extra["_decode"](eid)
    _rec = db.points(id=info_id)
    if _rec is None:
        return None
    else:
        record = dict(_rec.properties)
        record['longitude'], record['latitude'] = _rec.crds
        record["id"] = _rec.source_id
        return record

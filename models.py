# -*- coding: utf-8 -*-

from ..common import T
from .tools import PlanetTable, PlanetPointTable, PlanetGraphTable
from .common import db
from py4web import Field
from itertools import chain

addrsfields = lambda *of: (Field("source_name"), Field("city"), Field("street"),) + of

db.define_table("addresses",
    *addrsfields(),
    # Field("codvia"),
    migrate = False
)

db.define_table("housenumbers",
    *addrsfields(
        Field('housenumber')
    ),
    migrate = False
)

# db.define_table("addons",
#     Field("src_id"),
#     Field("source_name"),
#     Field("source_id"),
#     Field("properties", "json"),
#     singular = T("addon"), plural = T("addons"),
#     table_class = PlanetTable,
#     migrate = False
# )

db.define_table("points",
    Field("node_id", "bigint"),
    Field("src_id"),
    Field("source_name"),
    Field("source_id"),
    Field("geom", "geometry()"),
    Field("tags", "json"),
    Field("properties", "json"),
    Field("crds", "json"),
    singular = T("point"), plural = T("points"),
    table_class = PlanetPointTable,
    migrate = False
)

polyssfields = lambda *of: (
    Field("src_id"),
    Field("source_name"),
    Field("source_id"),
    Field("geom", "geometry()"),
    # Field("centroid", "geometry()"),
    Field("tags", "json"),
    Field("properties", "json"),
) + of

db.define_table("ways",
    *polyssfields(),
    # Field("centroid", "geometry()"),
    table_class = PlanetTable,
    migrate = False
)

db.define_table("polys",
    *polyssfields(),
    Field("centroid", "geometry()"),
    table_class = PlanetTable,
    migrate = False
)

db.define_table("mpolys",
    *polyssfields(),
    Field("centroid", "geometry()"),
    table_class = PlanetTable,
    migrate = False
)

# db.define_table("splitted_polys",
#     *polyssfields(),
#     table_class = PlanetTable,
#     migrate = False,
#     rname = "_splitted_polys"
# )

db.define_table("graph",
    Field("src_id"),
    Field("source_id", readable=False),
    Field("source_name"),
    Field("geom", "geometry()", readable=False),
    # Field("ssource_id", readable=False),
    Field("sinfo_id", "bigint", readable=False),
    Field("snode_id", "bigint", readable=False),
    Field("stags", "json", readable=False),
    # Field("tsource_id", readable=False),
    Field("tinfo_id", "bigint", readable=False),
    Field("tnode_id", "bigint", readable=False),
    Field("ttags", "json", readable=False),
    Field("tags", "json"),
    Field("properties", "json"),
    # Field("crds", "json", readable=False),
    Field("len", "double"),
    # Field("crs"),
    # Field("snid", "reference node", label='Source node id'),
    # Field("tnid", "reference node", label='Target node id'),
    table_class = PlanetGraphTable,
    migrate = False
)

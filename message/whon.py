from collections import namedtuple
from .header import Header

class WhonRequest(Header):
    field_names = namedtuple(
        "WhonRequest", Header.field_names._fields
    )
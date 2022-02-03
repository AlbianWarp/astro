from collections import namedtuple
from rebabel_server.message.header import Header


class WhonRequest(Header):
    field_names = namedtuple("WhonRequest", Header.field_names._fields)

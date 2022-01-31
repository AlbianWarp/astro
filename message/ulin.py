from struct import unpack, pack
from collections import namedtuple
from . import Package
from .header import Header

class UlinRequest(Header):
    field_names = namedtuple(
        "UlinRequest", Header.field_names._fields
    )

class UlinReply(Package):
    field_names = namedtuple("UlinReply", "type echo pkg_count status")
    fmt = "<I8s8xI4xI"
    data = None
    unpacked_data = None

    def __init__(self, header, online=False):
        if online:
            self.data = pack(self.fmt, 19, header.echo, header.pkg_count, 10)
        else:
            self.data = pack(self.fmt, 19, b"\x00" * 8, header.pkg_count, 0)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))

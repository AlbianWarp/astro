from struct import unpack, pack
from collections import namedtuple
from rebabel_server.message.header import Header
from rebabel_server.message import Package


class RusoReply(Package):
    field_names = namedtuple("RusoReply", Header.field_names._fields)
    fmt = Header.fmt
    data = None
    unpacked_data = None

    def __init__(self, header, user_id, user_hid):
        self.data = pack(
            self.fmt,
            545,
            header.echo,
            user_id,
            b"\x01\x00",
            b"\x0a\x00",
            header.pkg_count,
            b"\x00\x00\x00\x00\x01\x00\x00\x00",
        )
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))

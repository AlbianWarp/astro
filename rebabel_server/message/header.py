from struct import unpack, pack
from collections import namedtuple
from rebabel_server.message import Package


def pack_header(
    type, echo, user_id, user_hid, unknown01, pkg_count, unknown02=8 * b"\x00"
):
    return Header(
        pack(Header.fmt, type, echo, user_id, user_hid, unknown01, pkg_count, unknown02)
    )


class Header(Package):
    field_names = namedtuple(
        "Header", "type echo user_id user_hid unknown01 pkg_count unknown02"
    )
    fmt = "<I8sI2s2sI8s"
    data = None
    unpacked_data = None

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) == bytes:
            self.data = args[0]
        else:
            self.data = pack(self.fmt, *args)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))

    @property
    def type(self):
        return self.unpacked_data.type

    @property
    def pkg_count(self):
        return self.unpacked_data.pkg_count

    @property
    def echo(self):
        return self.unpacked_data.echo

    @property
    def user_id(self):
        return self.unpacked_data.user_id

    @property
    def unknown01(self):
        return self.unpacked_data.unknown01

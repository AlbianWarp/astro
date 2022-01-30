from struct import unpack, pack
from collections import namedtuple
from . import Package

def pack_header(request_type, echo, sender_id, sender_hid, unknown01, pkg_count):
    return Header(pack(Header.fmt,request_type, echo, sender_id, sender_hid, unknown01, pkg_count))

class Header(Package):
    field_names = namedtuple(
        "Header", "request_type echo sender_id sender_hid unknown01 pkg_count"
    )
    fmt = "<I8sI2s2sI8x"
    data = None
    unpacked_data = None

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) == bytes:
            self.data = args[0]
        else:
            self.data = pack(self.fmt,*args)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))


    @property
    def request_type(self):
        return self.unpacked_data.request_type

    @property
    def pkg_count(self):
        return self.unpacked_data.pkg_count

    @property
    def echo(self):
        return self.unpacked_data.echo

    @property
    def sender_id(self):
        return self.unpacked_data.sender_id

    @property
    def unknown01(self):
        return self.unpacked_data.unknown01


from struct import unpack, pack
from collections import namedtuple
from . import Package

class UlinRequest(Package):
    field_names = namedtuple(
        "UlinRequest", "request_type echo user_id unk1 pkg_count unk2 unk3"
    )
    fmt = "<I8sIIIII"
    def __init__(self, data):
        self.data = data
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
    def user_id(self):
        return self.unpacked_data.user_id
    @property
    def unk1(self):
        return self.unpacked_data.unk1
    @property
    def unk2(self):
        return self.unpacked_data.unk2
    @property
    def unk3(self):
        return self.unpacked_data.unk3


class UlinReply(Package):
    field_names = namedtuple(
        "UlinReply", "type echo pkg_count status"
    )
    fmt = "<I8s8xI4xI"
    data = None
    unpacked_data = None

    def __init__(self, header, online=False):
        if online:
            self.data = pack(self.fmt, 19, header.echo,header.pkg_count, 10)
        else:
            self.data = pack(self.fmt, 19, b"\x00"*8,header.pkg_count,0)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))
from struct import unpack, pack
from collections import namedtuple
from . import Package

class WhonRequest(Package):
    field_names = namedtuple(
        "WhonRequest", "request_type echo user_id unk1 pkg_count unk2 unk3"
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

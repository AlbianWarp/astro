from struct import unpack
from collections import namedtuple

class Header():
    field_names = namedtuple("Header", "request_type echo sender_id unknown01 pkg_count")
    fmt = "<I8sI4sI8x"
    data = None
    unpacked_data = None
    def __init__(self, data):
        self.data = data
        self.unpacked_data = self.field_names._make(unpack(self.fmt, data))

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

from struct import unpack
from collections import namedtuple

class LoginRequest():
    field_names = namedtuple("LoginRequest", "unk1 unk2 unk3 nlen plen name password")
    fmt = "<IIIII%dsx%dsx"  # (nlen -1 , plen -1 )
    data = None
    unpacked_data = None
    def __init__(self, data):
        self.data = data
        len(data)
        nlen,plen = unpack("<II",self.data[12:20])
        self.fmt = self.fmt % (nlen -1 ,plen -1)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, data))

    @property
    def unk1(self):
        return self.unpacked_data.unk1
    @property
    def unk2(self):
        return self.unpacked_data.unk2
    @property
    def unk3(self):
        return self.unpacked_data.unk3
    @property
    def nlen(self):
        return self.unpacked_data.nlen
    @property
    def plen(self):
        return self.unpacked_data.plen
    @property
    def name(self):
        return self.unpacked_data.name.decode("latin-1")
    @property
    def password(self):
        return self.unpacked_data.password

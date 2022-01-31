from struct import unpack, pack
from collections import namedtuple
from .header import pack_header, Header
from . import Package


class LoginRequest(Package):
    field_names = namedtuple("LoginRequest", "unk1 unk2 unk3 nlen plen name password")
    fmt = "<IIIII%dsx%dsx"  # (nlen -1 , plen -1 )
    data = None
    unpacked_data = None

    def __init__(self, header, request):
        self.header = header
        self.data = request.recv(20)
        nlen, plen = unpack("II", self.data[12:20])
        self.data += request.recv(nlen + plen)
        self.fmt = self.fmt % (nlen - 1, plen - 1)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))

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


class FailedLoginReply(Package):
    field_names = namedtuple("FailedLoginReply", "type pkg_count")
    data = None
    unpacked_data = None
    fmt = "<I16xI36x"

    def __init__(self, header):
        self.data = pack(self.fmt, 10, header.pkg_count)
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))


class SuccessfullLoginReply(Package):
    field_names = namedtuple(
        "SuccessfullLoginReply",
        Header.field_names._fields
        + namedtuple(
            "A",
            "unk01 payload_len unk02 unk03 unk04 server_cfg_port unk05 server_cfg_host server_cfg_name",
        )._fields,
    )
    """
    unk01, unk02, unk03, unk04 could be the number of servers provided.
    unk05 is probably the Server Number for the given server.
    payload_len is `len(server_cfg["name"]) + len(server_cfg["host"] + 22`
    """
    data = None
    unpacked_data = None
    fmt = "4xI4xIIIIII%dsx%dsx"

    def __init__(self, header, echo, user_id, user_hid, server_cfg):
        payload_length = len(server_cfg["host"]) + len(server_cfg["name"]) + 22
        self.fmt = Header.fmt + self.fmt % (
            len(server_cfg["host"]),
            len(server_cfg["name"]),
        )
        self.data = pack(
            self.fmt,
            10,
            echo,
            user_id,
            b"\x01\x00",
            b"\x0a\x00",
            header.pkg_count,
            8*b"\x00",
            1,
            payload_length,
            1,
            1,
            1,
            server_cfg["port"],
            1,
            bytes(server_cfg["host"], "latin-1"),
            bytes(server_cfg["name"], "latin-1"),
        )
        self.unpacked_data = self.field_names._make(unpack(self.fmt, self.data))

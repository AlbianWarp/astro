from struct import unpack
from collections import namedtuple

login = bytes.fromhex("2500000000000000000000002609000001000a000a00000000000000000000000100000002000000000000000b0000000f0000004d79557365726e616d650053656372657450617373776f726400")
PackageHeader = namedtuple('PackageHeader', "type echo sender_id unknown pkg_count")
ph = PackageHeader._make(unpack("4s8sI4sI8x",login[0:32]))
print(ph.sender_id)

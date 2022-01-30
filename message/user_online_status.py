from . import Package

class UserOnlineStatus(Package):
    def __init__(self, username, user_id, user_hid, online=False):
        payld_len = 34 + len(username)
        if online:
            self.data = bytes.fromhex(
                f"0d0000000000000000000000{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}000000000000{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}cccc0500000005000000{len(username).to_bytes(4, byteorder='little').hex()}48617070794d65696c69{username.encode('latin-1').hex()}"
            )
        else:
            self.data = bytes.fromhex(
                f"0e0000000000000000000000{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}0a0000000000{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}cccc0500000005000000{len(username).to_bytes(4, byteorder='little').hex()}48617070794d65696c69{username.encode('latin-1').hex()}"
            )
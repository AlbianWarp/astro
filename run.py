import random
import socketserver
from socket import SHUT_RDWR
import cmd
import threading
from threading import Thread
from struct import unpack, pack
from collections import namedtuple
from time import sleep



player_database = {
    "alice": {"id": 123, "password": "alice"},
    "bob": {"id": 234, "password": "bob"},
    "ham5ter": {"id": 1337, "password": "notsecure"},
}

sessions = []

online_player = {}

PackageHeader = namedtuple("PackageHeader", "type echo sender_id unknown pkg_count")
package_header_fmt = "I8sI4sI8x"


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection, and overrides the
    handle() method to implement communication to the client.
    """

    def dbg(self, message: str,color="\033[00m"):
        print(f"{self.client_address} - {color}{message}\033[00m")

    def setup(self):
        """
        called before the handle method, set the Stage!
        """
        pass

    def handle(self):
        """
        Handle the Client Socket!
        """
        sessions.append(self)
        try:
            self.dbg(f"New session")
            self.session_run = False
            self.data = self.request.recv(52)
            ph = PackageHeader._make(unpack(package_header_fmt, self.data[0:32]))
            if ph.type != 37:
                self.dbg(
                    f"Something diffrent than a login was sent! Bye bye!"
                )
                return
            if self._handle_login(): # NET: LINE
                self.dbg(
                    f"{(self.username,self.user_id)} successfully logged in! "
                )
                self.session_run = True
            while self.session_run:
                try:
                    self.data = self.request.recv(32)
                    if self.data == b'':
                        self.dbg(f"data is empty! Farewell!")
                        break
                    ph = PackageHeader._make(
                        unpack(package_header_fmt, self.data[0:32])
                    )
                    if ph.type == 19:  # NET: ULIN
                        self._handle_ulin()
                    else:
                        self.dbg("Uh Oh! Unknown Package Type! Cant Handle this :( Stuff might BREAK!", color="\033[93m")
                        self.dbg(f"data: {self.data.hex()}", color="\033[93m")
                        self.dbg(f"{ph}", color="\033[93m")
                except ConnectionResetError:
                    self.dbg(
                        f"Connection Reset by Peer! Farewell!"
                    )
                    self.session_run = False
                    break
        finally:
            try:
                sessions.remove(self)
                if self.user_id:
                    del online_player[self.user_id]
                    self.dbg(f"removed {self.user_id} from online_players!")
            except Exception as e:
                self.dbg(
                    f"Something went wrong while removing the Session or player from the online_player database: {e}"
                )

    def finish(self):
        """
        called after the handle method, use this to clean up afterwards!
        """
        pass


    def _handle_user_status(self):
        # user_id = int.from_bytes(data[12:16], byteorder="little")
        # user_hid = int.from_bytes(data[16:18], byteorder="little")
        # reply = user_status_package(user_id=user_id, user_hid=user_hid)
        UserStatusReply = namedtuple("UserStatusReply", "type_I user_id1_I user_hid1_H unk1_H payload_len1_I payload_len2_I user_id2_I user_hid2_H unk2_s name_len_I surename_len_I username_len_I name_s surename_s username_s")
        user_status_reply_fmt = "I8xIHH4xI4xII4sIIH2sI%ds%ds%ds" % name_len_I surename_len_I username_len_I

        username = None
        for name, user in player_database.items():
            if user["id"] == user_id:
                username = name
                break
        if not username:
            username = "ERROR"


    def _handle_ulin(self):
        """
        ULIN Requests do only consist of 32 Byte.
        """
        # Request:
        UlinRequest = namedtuple("UlinRequest", "echo_load user_id pkg_count")
        ulin_request_fmt = "4x8sI4xI8x"
        ulin_request = UlinRequest._make(unpack(ulin_request_fmt, self.data[0:32]))
        if ulin_request.user_id in online_player:
            self.request.sendall(
                pack(
                    "I8s8xI4xI", 19, ulin_request.echo_load, ulin_request.pkg_count, 10
                )
            )
            self.dbg(f"{self.user_id} requested online Status of {ulin_request.user_id}: Status: online")
        else:
            self.request.sendall(
                pack(
                    "I16xI8x",
                    19,
                    ulin_request.pkg_count,
                )
            )
            self.dbg(f"{self.user_id} requested online Status of {ulin_request.user_id}: Status: offline")

    def _handle_login(self):  # sourcery skip: move-assign
        # Request:
        LoginRequest = namedtuple(
            "LoginRequest",
            "unk1 unk2 unk3 username_length password_length name password",
        )
        login_request_fmt = "4s4s4sII%dsx%dsx"  # (name_lenght , password_length )
        # Responses:
        SuccessfullLoginReply = namedtuple(
            "SuccessfullLoginReply",
            "unk1 unk2 unk3 payload_length unk4 unk5 unk6 port server_id , server_name, server_friendly_name",
        )
        successfull_login_reply_fmt = (
            "IIIIIIIII%dsx%dsx"  # (len(server_host),len(server_friendly_name)
        )
        # FailesLoginReply = namedtuple("FailesLoginReply", "unk1")
        failed_login_reply_fmt = "28x"

        incomming_package_header = PackageHeader._make(
            unpack(package_header_fmt, self.data[0:32])
        )
        username_length, password_length = unpack("II", self.data[44:52])
        self.data += self.request.recv(username_length + password_length)
        ilp = LoginRequest._make(
            unpack(
                login_request_fmt % (username_length - 1, password_length - 1),
                self.data[32 : 52 + username_length + password_length],
            )
        )
        self.username = ilp.name.decode("latin-1")
        # TODO: Actual authentication lol!
        if self.username not in player_database:
            self.dbg("Well I dont know you! so you get the GO AWAY Message!")
            rhp = pack(
                package_header_fmt,
                10,
                b"happymoo",
                0,
                incomming_package_header.unknown,
                incomming_package_header.pkg_count,
            )
            sleep(5)  # slow down failed logins!
            self.request.sendall(rhp + pack(failed_login_reply_fmt))
            return False
        self.user_id = player_database[self.username]["id"]
        online_player[self.user_id] = self
        rhp = pack(
            package_header_fmt,
            10,
            b"happymoo",
            self.user_id,
            incomming_package_header.unknown,
            incomming_package_header.pkg_count,
        )
        server_host = b"192.168.0.185"
        server_friendly_name = b"Heart"
        rlp = pack(
            "IIIIIIIII%dsx%dsx" % (len(server_host), len(server_friendly_name)),
            0,
            1,
            0,
            40,
            1,
            1,
            1,
            1337,
            1,
            server_host,
            server_friendly_name,
        )
        self.request.sendall(rhp + rlp)
        return True


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True


def main():
    """
    The Main Function, which is executed when the server is run directly!
    """
    HOST, PORT = "0.0.0.0", 1337
    ThreadedTCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = Thread(target=server.serve_forever)
    server_thread.name = "ServerThread"
    server_thread.daemon = True
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()

    # Comandline Interface for debugging and Fun!
    class RebabelShell(cmd.Cmd):
        intro = "Hello, Welcome to Rebabel Shell. Type help or ? to list commands.\n"
        prompt = "(rebabel)"
        file = None

        def do_hello(self, arg):
            """
            Says Hello for fun! : HELLO
            """
            print("Hello There!")

        def do_info(self, arg):
            """
            Print Server Information! : INFO
            """
            print(f"Server loop running in thread: {server_thread.name}")
            print(f"IP: {ip} Port: {port}")
            print(f"{server}")

        def do_ls(self, arg):
            """
            Print Server Information! : INFO
            """
            for session in sessions:
                print(session.client_address)

        def do_bye(self, arg):
            """
            Stop ReBabel Shell, and exit! : BYE
            """
            print("Thank you for flying with ReBabel!")
            self.close()
            return True

        def close(self):
            if self.file:
                self.file.close()
                self.file = None

    RebabelShell().cmdloop()


if __name__ == "__main__":
    main()

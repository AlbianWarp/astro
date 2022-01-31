from time import sleep
import socketserver
from rebabel_server.message.header import Header
from rebabel_server.message.login import LoginRequest, SuccessfullLoginReply, FailedLoginReply
from rebabel_server.message.ulin import UlinReply, UlinRequest
from rebabel_server.message.whon import WhonRequest
from rebabel_server.message.ruso import RusoReply
from rebabel_server.message.user_online_status import UserOnlineStatus
import random
from hexdump import hexdump


echo_load = b"Call2Ark"
users = {
    "adam": 1,
    "eve": 2,
    "moep": 3,
}
server_cfg = {
    "host": "192.168.178.50",
    "port": 1337,
    "name": "Astro",
}

requests = {}
threads = []


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection, and overrides the
    handle() method to implement communication to the client.
    """

    def setup(self):
        """
        called before the handle method, set the Stage!
        """
        print(f"{self.request.getpeername()} connected")
        threads.append(self)


    def _handle(self):
        """
        Handle incomming Packages based on their Header information
        """
        self.data = self.request.recv(32)
        if len(self.data) == 0:
            self.session_run = False
            return
        header = Header(self.data[0:32])
        if header.type == 37:  # login
            self._handle_login_package(header=header)
        elif header.type == 16:  # net: whon
            self._handle_whon_package(header=header)
        elif header.type == 19:  # net: ulin
            self._handle_ulin_package(header=header)
        elif header.type == 545:  # net: ruso
            self._handle_ruso_package(header=header)
        else:
            print(
                f"Unknown type: {header.type} {header.data[0:4].hex()}"
            )
            print(hexdump(header.data))

    def handle(self):
        """
        Handle the Client Socket!
        """
        self.session_run = False
        self._handle()
        while self.session_run:
            self._handle()
            if len(self.data) == 0:
                sleep(0.005)
                continue

    def finish(self):
        """
        called after the handle method, use this to clean up afterwards!
        """
        print(f"{self.client_address} disconnected")
        threads.remove(self)
        if 'user_id' in self.__dict__:
            requests.pop(self.user_id)

    def _handle_login_package(self, header):
        login_request = LoginRequest(header=header, request=self.request)
        self.username = str(login_request.name)
        self.user_id = users[self.username]
        if not self.username in users:
            self.request.sendall(FailedLoginReply(header).data)
        else:
            self.request.sendall(
                SuccessfullLoginReply(
                    header=header,
                    echo=echo_load,
                    user_id=self.user_id,
                    user_hid=1,
                    server_cfg=server_cfg,
                ).data
            )
            requests[self.user_id] = self
            self.session_run = True

    def _handle_ulin_package(self, header):
        ulin_request = UlinRequest(header.data)
        ulin_reply = UlinReply(header, online=ulin_request.user_id in requests)
        self.request.sendall(ulin_reply.data)

    def _handle_ruso_package(self, header):
        user_id = random.choice(list(requests.keys()))
        ruso_reply = RusoReply(header=header,user_id=user_id,user_hid=1)
        self.request.sendall(ruso_reply.data)

    def _handle_whon_package(self, header):
        whon_request = WhonRequest(header.data)
        username = "None"
        for k, v in users.items():
            if whon_request.user_id == v:
                username = k
        user_online_status_reply = UserOnlineStatus(
            username=username,
            user_id=whon_request.user_id,
            user_hid=1,
            online=whon_request.user_id in requests,
        )
        self.request.sendall(user_online_status_reply.data)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


from cmath import log
from concurrent.futures import thread
import imp
from time import sleep
import socketserver
from socket import SHUT_RDWR
import cmd
import threading
from threading import Thread
from struct import unpack
from collections import namedtuple
from message import whon
from message.header import Header
from message.login import LoginRequest, SuccessfullLoginReply, FailedLoginReply
from message.ulin import UlinReply, UlinRequest
from message.whon import WhonRequest
from message.user_online_status import UserOnlineStatus
from hexdump import hexdump


try:
    from rich import print
except:
    print(f"rich is not installed, using regular print(). ☹️")

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
threads = {}

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

    def _handle(self):
        """
        Handle incomming Packages based on their Header information
        """
        self.data = self.request.recv(32)
        if len(self.data) == 0:
            self.session_run = False
            return
        header = Header(self.data[0:32])
        if header.request_type == 37:  # login
            self._handle_login_package(header=header)
        elif header.request_type == 19: # net: ulin
            self._handle_ulin_package(header=header)
        elif header.request_type == 16: # net: whon
            self._handle_whon_package(header=header)
        else:
            print(
                f"Unknown request_type: {header.request_type} {header.data[0:4].hex()}"
            )

    def handle(self):
        """
        Handle the Client Socket!
        """
        self.session_run = False
        print(f"{self.client_address} connected")
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
        pass

    def _handle_login_package(self, header):
        login_request = LoginRequest(header=header, request=self.request)
        # Cut of Header + Package Data from self.data
        # TODO: this must be wrong, maybe these bytes should be part of the login_request? how long is that one anyway?
        self.data = self.data[len(login_request.data) + 3 :]
        self.username = str(login_request.name)
        self.user_id = users[self.username]
        print(f"{self.username},{self.user_id}")
        if not self.username in users:
            self.request.sendall(FailedLoginReply(header).data)
        else:
            self.request.sendall(SuccessfullLoginReply(header=header,echo=echo_load,user_id=self.user_id,user_hid=1,server_cfg=server_cfg).data)
            self.session_run = True

    def _handle_ulin_package(self, header):
        ulin_request = UlinRequest(header.data)
        ulin_reply = UlinReply(header,online=ulin_request.user_id in requests)
        self.request.sendall(ulin_reply.data)

    def _handle_whon_package(self, header):
        whon_request = WhonRequest(header.data)
        username = "None"
        for k,v in users.items():
            if whon_request.user_id == v:
                username = k
        user_online_status_reply = UserOnlineStatus(username=username, user_id=whon_request.user_id,user_hid=1,online=whon_request.user_id in requests)
        self.request.sendall(user_online_status_reply.data)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():
    """
    The Main Function, which is executed when the server is run directly!
    """
    HOST, PORT = "0.0.0.0", 1337
    ThreadedTCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request.
    server_thread = Thread(target=server.serve_forever)
    server_thread.name = "ServerThread"
    server_thread.daemon = True
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()

    # Comandline Interface for debugging and Fun!
    class RebabelShell(cmd.Cmd):
        intro = "Hello, Welcome to Rebabel Shell. Type help or ? to list commands.\n"
        prompt = "(astro)"
        file = None

        def do_info(self, arg):
            """
            Print Server Information! : INFO
            """
            print(f"Server loop running in thread: {server_thread.name}")
            print(f"IP: {ip} Port: {port}")
            print(f"{server}")
            print(f"{server.daemon_threads}")

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

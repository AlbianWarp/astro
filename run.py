from cmath import log
from concurrent.futures import thread
from time import sleep
import socketserver
from socket import SHUT_RDWR
import cmd
from threading import Thread
from struct import unpack
from collections import namedtuple
from message.header import Header
from message.login import LoginRequest

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
        pass

    def handle(self):
        """
        Handle the Client Socket!
        """
        self.data = self.request.recv(32)
        self.session_run = False
        header = Header(self.data[0:32])
        if header.request_type == 37: #login
            self._handle_login_package()
        else:
            print(f"Unknown request_type: {header.request_type}")
            print(header.unpacked_data)
        while self.session_run:
            self.data = self.request.recv(32)
            if len(self.data) == 0:
                sleep(0.005)
                continue
            header = Header(self.data[0:32])
            if header.request_type == 37: #login
                print(f"recieved Login Type package")
            else:
                print(f"Unknown request_type: {header.request_type}")
                print(header.unpacked_data)


    def finish(self):
        """
        called after the handle method, use this to clean up afterwards!
        """
        pass

    def _handle_login_package(self):
        header = Header(self.data)
        print(header.pkg_count, header.request_type, header.sender_id, header.echo)
        self.data += self.request.recv(20)
        nlen, plen = unpack("II", self.data[44:52])
        self.data += self.request.recv(nlen + plen)
        login_request = LoginRequest(self.data[32 : 52 + nlen + plen])
        # Cut of Header + Package Data from self.data
        self.data = self.data[52 + nlen + plen :]
        reply = self.__net_line_reply_package(package_count=header.pkg_count,username=login_request.name, password=login_request.password)
        self.request.sendall(reply)

    def __net_line_reply_package(self, package_count,username,password):
        echo_load = "40524b28eb000000"
        users = {
            "adam": 1,
            "eve": 2,
            "moep": 3,
            }
        server_ehlo = {
            "host": "192.168.178.50",
            "port": 1337,
            "name": "Astro",
        }
        if not str(username) in users:
            print("message: username or password incorrect")
            return bytes.fromhex(
                    f"0a00000000000000000000000000000000000000{package_count.to_bytes(4, byteorder='little').hex()}000000000000000000000000000000000000000000000000000000000000000000000000"
                )
        user_hid = 1
        print(f"{username} has joined!")
        self.session_run = True
        return bytes.fromhex(f"0a000000{echo_load}{ users[username].to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}0a00{package_count.to_bytes(4, byteorder='little').hex()}0000000000000000"
                + f"00000000"
                + f"01000000"
                + f"00000000"
                + (len(server_ehlo["host"]) + len(server_ehlo["name"]) + 22)
                .to_bytes(4, byteorder="little")
                .hex()
                + f"01000000"
                + f"01000000"
                + f"01000000"
                + server_ehlo["port"].to_bytes(4, byteorder="little").hex()
                + f"01000000"
                + server_ehlo["host"].encode("latin-1").hex()
                + f"00"
                + server_ehlo["name"].encode("latin-1").hex()
                + f"00")


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

import random
import socketserver
from socket import SHUT_RDWR
import cmd
import threading
from threading import Thread
from struct import unpack
from collections import namedtuple


PackageHeader = namedtuple("PackageHeader", "type echo sender_id unknown pkg_count")
package_header_fmt = "4s8sI4sI8x"

LoginPackage = namedtuple("LoginPackage", "unk1 unk2 unk3 nlen plen name password")
login_package_fmt = "4s4s4sII%dsx%dsx"  # (name_lenght , password_length )


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
        self.data = self.request.recv(52)
        if self.data[0:4] != bytes.fromhex("25000000"):
            return
        self._handle_login_package()

    def finish(self):
        """
        called after the handle method, use this to clean up afterwards!
        """
        pass

    def _handle_login_package(self):
        ph = PackageHeader._make(unpack(package_header_fmt, self.data[0:32]))
        nlen, plen = unpack("II", self.data[44:52])
        self.data += self.request.recv(nlen + plen)
        lp = LoginPackage._make(
            unpack(
                login_package_fmt % (nlen - 1, plen - 1),
                self.data[32 : 52 + nlen + plen],
            )
        )
        # Cut of Header + Package Data from self.data
        self.data = self.data[52 + nlen + plen :]
        print(ph)
        print(lp)
        print(self.data)


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

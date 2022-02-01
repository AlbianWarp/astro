from threading import Thread
from rebabel_server import ThreadedTCPServer,ThreadedTCPRequestHandler
from rebabel_shell import RebabelShell
def main():
    """
    The Main Function, which is executed when the server is run directly!
    """
    HOST, PORT = "0.0.0.0", 1337
    ThreadedTCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    # Start a thread with the server -- that thread will then start one
    # more thread for each request.
    server_thread = Thread(target=server.serve_forever)
    server_thread.name = "ServerThread"
    server_thread.daemon = True
    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()

    # Comandline Interface for debugging and Fun!
    RebabelShell().cmdloop(rebabel_server=server)


if __name__ == "__main__":
    main()

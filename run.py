from rebabel_shell import RebabelShell
from rebabel_server import ReBabelServer
def main():
    server = ReBabelServer("0.0.0.0",1337)

    # Comandline Interface for debugging and Fun!
    RebabelShell().cmdloop(rebabel_server=server.threaded_tcp_server)

if __name__ == "__main__":
    main()

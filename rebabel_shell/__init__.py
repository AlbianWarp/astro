from socket import SHUT_RDWR
from rich import print
import cmd

class RebabelShell(cmd.Cmd):
    intro = "Hello, Welcome to Rebabel Shell. Type help or ? to list commands.\n"
    prompt = "(astro)"
    file = None
    loop = True

    def cmdloop(self, rebabel_server=None, intro=None):
        print(self.intro)
        self.rebabel_server = rebabel_server
        while self.loop:
            try:
                super(RebabelShell, self).cmdloop(intro="")
                break
            except KeyboardInterrupt:
                self.do_bye("^C")

    def do_info(self, arg):
        """
        Print Server Information! : INFO
        """
        print(f"{self.rebabel_server.__dict__}")

    def do_bye(self, arg):
        """
        Stop ReBabel Shell, and exit! : BYE
        """
        print("Thank you for flying with ReBabel!")
        for thread in self.rebabel_server.threads:
            thread.request.shutdown(SHUT_RDWR)
        self.close()
        return True

        def close(self):
            self.loop = False
            if self.file:
                self.file.close()
                self.file = None

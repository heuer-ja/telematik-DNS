
import socket

from constants import Constants 

CONST = Constants()

class RecursiveResolver:
    def __init__(self) -> None:
        self.ip = CONST.IP_REC_RESOLVER
        self.port = CONST.PORT
        
        # setup server
        self.rec_resolver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.rec_resolver.bind((self.ip, self.port))
        print(f"RECURSIVE RESOLVER running ...")



    def listen(self) -> None:
        print(f"RECURSIVE RESOLVER listining ...")

        while True:
            msg, client = self.rec_resolver.recvfrom(1024)
            msg = msg.decode("utf-8")

            # TODO ask root

            print(f"RECURSIVE RESOLVER received: '{msg}' from {client}")


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()
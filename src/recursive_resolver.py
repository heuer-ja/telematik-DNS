
import socket

from constants import Constants
from dns_format import DnsFormat 

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
            print(f"RECURSIVE RESOLVER received: '{msg}' from {client}")

            # TODO ask root

            # send request
            dns_format = DnsFormat()


            # receive: request + response

    def recursion(self, dns_format:DnsFormat):

        # search ip adress for nameserver

        # recursion anchor

        # recursion step
        pass 


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()
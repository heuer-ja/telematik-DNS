import socket
import json

from constants import Constants
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat, QryType

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

       # while True:
            # msg, client = self.rec_resolver.recvfrom(CONST.BUFFER)
            # msg = msg.decode("utf-8")
            # print(f"RECURSIVE RESOLVER received: '{msg}' from {client}")

            # TODO 
        req: DnsFormat = DnsFormat(
            request=DnsRequestFormat(
                name="www.switch.telematik",
                dns_qry_type=QryType.A.value,
            )
        )
        self.recursion_TODO(dns_request=req, nameserver="root")

    def recursion_TODO(self, dns_request: DnsFormat, nameserver: str = "root"):

        # send
        ip = CONST.get_ip(nameserver)
        msg_req:str= str.encode(dns_request.toJsonStr())
        self.rec_resolver.sendto(msg_req, (ip, CONST.PORT))
        print(f"REC. RES. sent: \n{msg_req}\n")

        # receive
        msg, _ = self.rec_resolver.recvfrom(CONST.BUFFER)
        msg = msg.decode("utf-8")
        response: DnsFormat = DnsFormat.fromJson(json.loads(msg))

        # recursion anchor
        # recursion step
        print(f"REC. RES. received: \n {response.toJsonStr()}\n")


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()

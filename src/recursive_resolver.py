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
        dns_response: DnsFormat = self.recursion_TODO(dns_request=req)
        print(f"dns_response is {dns_response.toJsonStr()}")

    def recursion_TODO(self, dns_request: DnsFormat) -> DnsFormat:

        # [recursion anchor]
        if dns_request.response.dns_flags_authoritative:
            return dns_request

        # [calculation]
        # send
        msg_req: str = str.encode(dns_request.toJsonStr())
        addr_nameserver = (dns_request.response.dns_a, CONST.PORT)
        self.rec_resolver.sendto(msg_req, addr_nameserver)

        # receive
        msg, _ = self.rec_resolver.recvfrom(CONST.BUFFER)
        msg = msg.decode("utf-8")
        dns_response: DnsFormat = DnsFormat.fromJson(json.loads(msg))
        print(f"REC. RES. received: \n {dns_response.toJsonStr()}\n")

        # [recusion step]
        return self.recursion_TODO(dns_request=dns_response)


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()

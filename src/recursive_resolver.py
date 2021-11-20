import socket
import json

from constants import Constants
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat, QryType

CONST = Constants()


class RecursiveResolver:
    '''
    class that simulates the recursive resolver
        - receives request from stub resolver
        - starts recursive name resolution by running through dns-tree
        - sends name resoluation back to stub resolver 
    '''
    def __init__(self) -> None:
        self.ip = CONST.IP_REC_RESOLVER
        self.port = CONST.PORT

        # setup server
        self.rec_resolver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.rec_resolver.bind((self.ip, self.port))
        print(f"RECURSIVE RESOLVER running ...")

    def listen(self) -> None:
        '''listens for stub resolver request and sends response back'''

        print(f"RECURSIVE RESOLVER listining ...")

        while True:
            # receive request
            msg, addr_client = self.rec_resolver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")
            print(f"RECURSIVE RESOLVER received: '{msg}' from {addr_client}")


            # tramsform request into format
            msg = msg.split(" ")
            ns_of_interest: str = msg[0]
            record: int = (
                QryType.A.value
                if msg[1] == "A"
                else QryType.NS.value
                if msg[1] == "NS"
                else None
            )
            req: DnsFormat = DnsFormat(
                request=DnsRequestFormat(name=ns_of_interest, dns_qry_type=record)
            )

            # recursion - search for nameserver
            print(f"recursively searching for {ns_of_interest} {record}-record")
            dns_response: DnsFormat = self.recursion(dns_request=req)

            # send response
            print(f"dns_response is {dns_response.toJsonStr()}")
            msg_resolved: str = dns_response.toJsonStr()
            self.rec_resolver.sendto(str.encode(msg_resolved), addr_client)

    def recursion(self, dns_request: DnsFormat) -> DnsFormat:
        '''starts recursive name resolution by running through dns-tree'''
        # [recursion anchor]
        if dns_request.response.dns_flags_authoritative:
            return dns_request

        # [calculation]
        # send to nameserver
        msg_req: str = str.encode(dns_request.toJsonStr())
        addr_nameserver = (dns_request.response.dns_a, CONST.PORT)
        self.rec_resolver.sendto(msg_req, addr_nameserver)

        # receive from nameserver
        msg, _ = self.rec_resolver.recvfrom(CONST.BUFFER)
        msg = msg.decode("utf-8")
        dns_response: DnsFormat = DnsFormat.fromJson(json.loads(msg))
        print(f"REC. RES. received: \n {dns_response.toJsonStr()}\n")

        # [recusion step]
        return self.recursion(dns_request=dns_response)


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()

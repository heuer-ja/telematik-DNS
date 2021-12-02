# client
import socket
import json
from constants import ColorsPr, Constants, ServerTypes
from dns_format import DnsFormat, RCodes

CONST = Constants()


class StubResolver:
    """
    class that simulates stub resolver
        - gets request (input) from client
        - sends request to recursive resolver & gets response
        - shows response to client
    """

    def __init__(self) -> None:
        # setup client
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    @staticmethod
    def print(msg: str) -> str:
        print(f"{ColorsPr.GREEN}{msg}{ColorsPr.NORMAL}")

    def resolve_name(self) -> None:

        # input & send
        msg_request = str.encode(
            input(f"{ColorsPr.GREEN}Enter message: {ColorsPr.NORMAL}")
        )
        self.client.sendto(msg_request, (CONST.IP_REC_RESOLVER, CONST.PORT))

        # receive
        msg_response, _ = self.client.recvfrom(CONST.BUFFER)
        msg_response: str = msg_response.decode("utf-8")
        dns_response: DnsFormat = DnsFormat().fromJson(json.loads(msg_response))

        # print
        StubResolver.print(
            f"response for {dns_response.request.name} {dns_response.request.dns_qry_type} is:\n{dns_response.response}"
        )


# start stub resolver (client)
stub_resolver = StubResolver()
stub_resolver.resolve_name()

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
        self.client = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)


    @staticmethod
    def print(msg: str) -> str:
        print(f"{ColorsPr.GREEN}{msg}{ColorsPr.NORMAL}")


    def resolve_name(self) -> None:
        msg_request = str.encode(input(f"{ColorsPr.GREEN}Enter message: {ColorsPr.NORMAL}"))
        rec_res_info = (CONST.IP_REC_RESOLVER, CONST.PORT)
        self.client.sendto(msg_request, rec_res_info)
        msg_response, _ = self.client.recvfrom(CONST.BUFFER)
        msg_response: str = msg_response.decode("utf-8")

        dns_response: DnsFormat = DnsFormat().fromJson(json.loads(msg_response))

        StubResolver.print(dns_response)
        # TODO check for error
        if dns_response.response.dns_flags_rcode == RCodes.NOERROR.value:
            StubResolver.print(
                f"{dns_response.request.name} has ip adress {dns_response.response.dns_a}"
            )

        else:
            StubResolver.print(f"name {dns_response.request.name} could not be resolved")


# start stub resolver (client)
stub_resolver = StubResolver()
stub_resolver.resolve_name()

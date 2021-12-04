# client
import socket
import json
import time
import datetime
import math

from constants import Constants, ServerTypes
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

    def resolve_name(self) -> None:
        msg_request = str.encode(input("Enter message:"))
        rec_res_info = (CONST.IP_REC_RESOLVER, CONST.PORT)
        timestamp_req: datetime.datetime = datetime.datetime.now()
        time.sleep(.100)
        self.client.sendto(msg_request, rec_res_info)
        msg_response, _ = self.client.recvfrom(CONST.BUFFER)
        msg_response: str = msg_response.decode("utf-8")

        dns_response: DnsFormat = DnsFormat().fromJson(json.loads(msg_response))
        timestamp_resp: datetime.datetime = datetime.datetime.now()
        query_time_delta: int = math.ceil((timestamp_resp - timestamp_req).total_seconds() * 1000)

        print(dns_response)
        # TODO check for error
        if dns_response.response.dns_flags_rcode == RCodes.NOERROR.value:
            print(
                f"{dns_response.request.name} has ip adress {dns_response.response.dns_a}\n"
                f"Query Time: {query_time_delta} msec"
            )

        else:
            print(
                f"name {dns_response.request.name} could not be resolved\n"
                f"Query Time: {query_time_delta} msec"
            )


# start stub resolver (client)
stub_resolver = StubResolver()
stub_resolver.resolve_name()

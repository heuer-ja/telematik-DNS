# client
import socket
import time
import json
from typing import List
import time
import datetime
import math

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

    def resolve_name(self, input_query: str) -> None:

        # input & send
        StubResolver.print(f"\n-------------------------\nQuery: {input_query}")
        timestamp_req: datetime.datetime = datetime.datetime.now()
        time.sleep(0.100)
        self.client.sendto(str.encode(input_query), (CONST.IP_REC_RESOLVER, CONST.PORT))

        # receive
        msg_response, _ = self.client.recvfrom(CONST.BUFFER)
        msg_response: str = msg_response.decode("utf-8")
        dns_response: DnsFormat = DnsFormat().fromJson(json.loads(msg_response))
        timestamp_resp: datetime.datetime = datetime.datetime.now()
        query_time_delta: int = math.ceil(
            (timestamp_resp - timestamp_req).total_seconds() * 1000
        )

        # TODO check for error
        StubResolver.print(
            f"\nResponse: \n{dns_response.response}\n"
            f"Query Time: {query_time_delta} msec"
        )


# start stub resolver (client)
stub_resolver = StubResolver()

test_queries: List[str] = [
    "root",
    #"root A",
    #"root NS",
    #"ns.root A",
    #"ns.root NS",
#
    #"telematik A",
    #"fuberlin NS",
    #"ns.fuberlin NS",
    #"ns.fuberlin A",
#
    #"switch.telematik NS",
    #"router.telematik A",
    #"ns.switch.telematik NS",
    #"ns.router.telematik A",
    #
    #"easy.homework.fuberlin A",
    #"easy.homework.fuberlin NS",

    #"youtube.com NS",
]

for query in test_queries:
    stub_resolver.resolve_name(input_query=query)

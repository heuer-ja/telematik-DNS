# client
import socket
import json
from constants import Constants, ServerTypes

CONST = Constants()


class StubResolver:
    def __init__(self) -> None:
        # setup client
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def checkpoint_a(self) -> None:
        # input
        input_auth_server = "homework.fuberlin"
        input_server_of_interest = f"easy.{input_auth_server}"

        # get ip adress
        ip = CONST.get_ip(server_name=input_auth_server)

        # send query to server
        self.client.sendto(str.encode(input_server_of_interest), (ip, CONST.PORT))
        response, _ = self.client.recvfrom(1024)
        print(response.decode("utf-8"))

    def checkpoint_b(self) -> None:
        name: str = "news.router.telematik"
        record: str = "A"

        msg = str.encode(f"{name} {record}")
        rec_res_info = (CONST.IP_REC_RESOLVER, CONST.PORT)
        self.client.sendto(msg, rec_res_info)




# start stub resolver (client)
stub_resolver = StubResolver()
stub_resolver.checkpoint_b()

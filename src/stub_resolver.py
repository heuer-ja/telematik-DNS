# client 
import socket
import json
from constants import Constants
from dns_format import DnsFormat

CONST = Constants()


class StubResolver:
    def __init__(self) -> None:
        # setup client
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


    def checkpoint_a(self) -> None:
        # laod nameservers
        with open('../res/config.json') as f:
            servers = json.load(f)

        # input 
        input_auth_server = "homework.fuberlin"
        input_server_of_interest = f"easy.{input_auth_server}"

        # get ip adress
        ip = next((ip for ip,name in list(servers['DnsConfig'].items()) 
                if name==input_auth_server ), None)


        # send query to server
        self.client.sendto(str.encode(input_server_of_interest), (ip, CONST.PORT))
        response, server = self.client.recvfrom(1024)
        print(response.decode("utf-8"))


    def checkpoint_b(self) -> None:
        name:str = "news.router.telematik"
        record:str = "A"

        msg = str.encode(f"{name} {record}")
        rec_res_info = (CONST.IP_REC_RESOLVER, CONST.PORT)
        self.client.sendto(msg,rec_res_info)


# start stub resolver (client)
stub_resolver = StubResolver()
stub_resolver.checkpoint_b()
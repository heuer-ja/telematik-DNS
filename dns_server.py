from threading import Thread
from typing import Dict
import time
import socket

from res.constants import Constants

CONST = Constants()

class DnsServerStarter:
    def __init__(self, dns_servers: Dict[str,str]):
        self.dns_servers = dns_servers
        return
  
    def _start_dns_server(ip:str, name:str):
        print(f"server '{name}'' runs ...")
        thread_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        thread_server.bind((ip, CONST.PORT))

        while True:
            msg = thread_server.recvfrom(1024)
            print(f"server '{name}' received: {msg}")


    def start_all_dns_servers(self):
        for ip, name in self.dns_servers.items():
            thread = Thread(target = DnsServerStarter._start_dns_server, args = (ip, name))
            thread.start()





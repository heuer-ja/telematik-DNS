from threading import Thread
from typing import Dict
import time
import socket
from typing import List
import codecs

from res.constants import Constants
import pandas as pd


CONST = Constants()

class DnsServerStarter:
    def __init__(self, dns_servers: Dict[str,str]):
        self.dns_servers:List[DnsServer] =[ DnsServer(
            name=name,
            ip=ip,
            port=CONST.PORT,
            zone_file=  f"res/zone_files/{name}.zone"
            ) 
        for ip, name in dns_servers.items()]

    def start_all_dns_servers(self):
        for server in self.dns_servers:
            thread = Thread(target = server.start, args = ())
            thread.start()


class DnsServer:
    def __init__(self, name:str, ip:str, port:int, zone_file:str) -> None:
        self.name = name
        self.ip = ip 
        self.port = port 
        self.zone_file = zone_file 

    def start(self):
        thread_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        thread_server.bind((self.ip, self.port))
        print(f"server '{self.name}'' runs ...")

        while True:
            msg = thread_server.recvfrom(1024)
            print(f"server '{self.name}' received: {msg}")


    def get_record(self, name:str):
        ''' TODO
         idea:
           1) load zone_file (if existing!) as .... pandas.df (seperator tab)?
           2) is server author?
                True: return fitting row (record)
                False: return author server
         '''      

        df = pd.read_csv(
            self.zone_file, 
            sep='\t', 
            header=None, # no column names in .zone-files
            names=["name", "record"]
        )
                
        record = df[df['name']==name]["record"]
        print(record)
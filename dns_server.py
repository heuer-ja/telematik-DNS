from threading import Thread
from typing import Dict
import socket
from typing import List

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
            # receive msg
            msg, client = thread_server.recvfrom(1024)
            msg = msg.decode("utf-8")

            print(f"server '{self.name}' received query: '{msg}' from {client}")

            # search for record
            record = self.get_record(name=msg)
            
            # response to client
            response = f"{msg} has record: {record}"
            thread_server.sendto(
                str.encode(response), client
            )
            


    def get_record(self, name:str) -> str: 
        df = pd.read_csv(
            self.zone_file, 
            sep='\t', 
            header=None, # no column names in .zone-files
            names=["name", "record"]
        )
                
        list_of_records = df.loc[df['name']==name]["record"]
        record = list_of_records.iloc[0]
        return record
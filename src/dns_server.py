import socket
import pandas as pd
import json
from threading import Thread
from typing import Dict, List
from constants import Constants, ServerTypes
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat


CONST = Constants()


class DnsServerStarter:
    def __init__(self, dns_servers: Dict[str, str]):
        self.dns_servers: List[DnsServer] = [
            DnsServer(
                name=name,
                ip=ip,
                port=CONST.PORT,
                zone_file=f"../res/zone_files/{name}.zone",
            )
            for ip, name in dns_servers.items()
        ]

    def start_all_dns_servers(self):
        for server in self.dns_servers:
            thread = Thread(target=server.checkpoint_b, args=())
            thread.start()


class DnsServer:
    def __init__(self, name: str, ip: str, port: int, zone_file: str) -> None:
        self.name = name
        self.ip = ip
        self.port = port
        self.zone_file = zone_file

        # setup server
        self.nameserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.nameserver.bind((self.ip, self.port))
        print(f"server '{self.name}'' runs ...")

    def load_zone_file(self) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.zone_file,
            sep="\t",
            header=None,  # no column names in .zone-files
            names=["name", "record"],
        )
        return df

    ####################[checkpoint a]#############################
    def get_record(self, name: str) -> str:
        df = pd.read_csv(
            self.zone_file,
            sep="\t",
            header=None,  # no column names in .zone-files
            names=["name", "record"],
        )

        list_of_records = df.loc[df["name"] == name]["record"]
        record = list_of_records.iloc[0]
        return record

    def checkpoint_a(self):
        while True:
            # receive msg
            msg, client = self.nameserver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")

            print(f"server '{self.name}' received query: '{msg}' from {client}")

            # search for record
            record = self.get_record(name=msg)

            # response to client
            response = f"{msg} has record: {record}"
            self.nameserver.sendto(str.encode(response), client)

    ####################[checkpoint b]#############################

    def resolve_qry(self, dns_query: DnsRequestFormat) -> DnsResponseFormat:
        df_zonefile: pd.DataFrame = self.load_zone_file()
        name_of_interest:str= dns_query.name

        # start suffix search
        for i, row in df_zonefile.iterrows():
            if name_of_interest.endswith(row["name"]):
                break

        print(row["record"])

        # TODO check for empty row

        # transform row into response
        record: List[str] = str(row["record"]).split("  ")
        response: DnsResponseFormat = DnsResponseFormat(
            dns_ns=row["name"],
            dns_a=record[2],
            dns_flags_authoritative= name_of_interest==row["name"]
        )
        return response

    def checkpoint_b(self):

        while True:
            # receive msg
            msg, addr_rec_resolver = self.nameserver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")
            print(
                f"\nserver '{self.name}' received query: '{msg}' from {addr_rec_resolver}"
            )

            # resolve request
            dns_req: DnsFormat = DnsFormat().fromJson(json.loads(msg))
            res: DnsResponseFormat = self.resolve_qry(dns_query=dns_req.request)

            # response
            dns_res: DnsFormat = DnsFormat(
                request=dns_req.request,
                response=res,
            )
            msg_res: str = str.encode(dns_res.toJsonStr())
            self.nameserver.sendto(msg_res, addr_rec_resolver)


# load nameservers
servers = CONST.MAP_IP_SERVERS[ServerTypes.DNS.name]

# start nameservers (servers)
starter = DnsServerStarter(dns_servers=servers)
starter.start_all_dns_servers()

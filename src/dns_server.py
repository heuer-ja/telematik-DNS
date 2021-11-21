from datetime import datetime
import socket
import pandas as pd
import json
import os
import csv
from threading import Thread
from typing import Dict, List
from constants import Constants, ServerTypes
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat, QryType, RCodes


CONST = Constants()


class DnsServerStarter:
    """
    manages all nameservers
    """

    def __init__(self, dns_servers: Dict[str, str]):
        self.dns_servers: List[DnsServer] = [
            DnsServer(
                name=name,
                ip=ip,
                port=CONST.PORT,
                zone_file=f"{os.getcwd()}/res/zone_files/{name}.zone",
                log_file=f"{os.getcwd()}/res/logs/{ip}.log"
            )
            for ip, name in dns_servers.items()
        ]

    def start_all_dns_servers(self):
        """starts all nameservers at one"""
        for server in self.dns_servers:
            thread = Thread(target=server.checkpoint_b, args=())
            thread.start()


class DnsServer:
    """
    class that simulates one nameserver (ns)
        - receives request from recusive resolver
        - searches child-nameserver in its zone file
        - updates dns-response-flags
        - sends response back to recursive resolver
    """

    def __init__(self, name: str, ip: str, port: int, zone_file: str, log_file: str) -> None:
        """name of ns"""
        self.name = name
        """ip of ns"""

        self.ip = ip

        """port of ns"""
        self.port = port

        """zone file of ns"""
        self.zone_file = zone_file

        """log file of ns"""
        self.log_file = log_file

        """Initialise log file if not present"""
        self.log_init()

        # setup server
        self.nameserver = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.nameserver.bind((self.ip, self.port))
        print(f"server '{self.name}'' runs ...")

    def log_init(self):
        if not os.path.exists(self.log_file):
            timestamp = pd.Timestamp.now()
            ip = self.ip
            responses_send = 0
            responses_recieved = 0
            requests_send = 0
            requests_recieved = 0
            row = [timestamp, ip, requests_send, requests_recieved,
                   responses_send, responses_recieved]
            log_df = pd.DataFrame([row], columns=CONST.LOG_COLUMNS)
            log_df.to_csv(self.log_file, index=False)

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

            print(
                f"server '{self.name}' received query: '{msg}' from {client}")

            # search for record
            record = self.get_record(name=msg)

            # response to client
            response = f"{msg} has record: {record}"
            self.nameserver.sendto(str.encode(response), client)

    ####################[checkpoint b]#############################

    def resolve_qry(self, dns_query: DnsRequestFormat) -> DnsResponseFormat:
        """searches in zone file for requested ns and its record"""
        name_of_interest: str = dns_query.name

        # [case 0] - this ns is sought ns
        if self.name == name_of_interest:
            return DnsResponseFormat(
                dns_flags_response=True,
                dns_flags_rcode=RCodes.NOERROR.value,
                dns_flags_authoritative=True,
                dns_ns=self.name,
                dns_a=CONST.get_ip(server_name=self.name),
                # TODO
                dns_count_answers=0,
                dns_resp_ttl=0,
            )

        # [case 1] - a child (in zone file) is sought ns
        df_zonefile: pd.DataFrame = self.load_zone_file()

        entry = None
        # start suffix search
        for i, row in df_zonefile.iterrows():
            if name_of_interest.endswith(row["name"]):
                entry = row
                break

        #  check whether entry is valid or not
        response: DnsResponseFormat = None
        if entry is None:
            response = DnsResponseFormat(
                dns_flags_response=False,
                dns_flags_rcode=RCodes.NOTZONE.value,
                dns_flags_authoritative=None,
                dns_ns=None,
                dns_a=None,
                dns_resp_ttl=None,
                # TODO
                dns_count_answers=0,
            )

        else:
            # transform row into response
            record: List[str] = str(entry["record"]).split("  ")

            isAuth: bool = name_of_interest == entry["name"]
            response = DnsResponseFormat(
                dns_flags_response=True,
                dns_flags_rcode=RCodes.NOERROR.value
                if isAuth
                else RCodes.NOTAUTH.value,
                dns_flags_authoritative=isAuth,
                dns_ns=entry["name"],
                dns_a=record[2],
                # TODO
                dns_count_answers=0,
                dns_resp_ttl=0,
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
            self.increment_req_recieved_log()

            # resolve request
            dns_req: DnsFormat = DnsFormat().fromJson(json.loads(msg))
            res: DnsResponseFormat = self.resolve_qry(
                dns_query=dns_req.request)

            # response
            dns_res: DnsFormat = DnsFormat(
                request=dns_req.request,
                response=res,
            )
            msg_res: str = str.encode(dns_res.toJsonStr())
            self.nameserver.sendto(msg_res, addr_rec_resolver)

    def increment_req_recieved_log(self):
        with open(self.log_file, "r") as f:
            log_df = pd.read_csv(f)
            last_log = log_df.iloc[-1].to_dict()
            print(last_log)
            timestamp = pd.Timestamp.now()
            requests_recieved = int(last_log["Requests Recieved"]) + 1
            requests_send = last_log["Requests Send"]
            responses_send = last_log["Responses Send"]
            responses_recieved = last_log["Responses Recieved"]
            log_df.loc[len(log_df)] = [timestamp, last_log["IP"], requests_send,
                                       requests_recieved, responses_send, responses_recieved]
            log_df.to_csv(self.log_file, index=False)

    def __increment_empty(self):
        timestamp = pd.Timestamp.now()
        ip = self.ip
        responses_send = 0
        responses_recieved = 0
        requests_send = 0
        requests_recieved = 1
        row = [timestamp, ip, requests_send, requests_recieved,
               responses_send, responses_recieved]
        log_df = pd.DataFrame([row], columns=CONST.LOG_COLUMNS)
        log_df.to_csv(self.log_file, index=False)


        # load nameservers
servers = CONST.MAP_IP_SERVERS[ServerTypes.DNS.name]

# start nameservers (servers)
starter = DnsServerStarter(dns_servers=servers)
starter.start_all_dns_servers()

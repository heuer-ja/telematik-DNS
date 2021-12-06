import socket
import pandas as pd
import json
import threading
import os
import time
from threading import Thread
from typing import Dict, List
from constants import Constants, ServerTypes, ColorsPr
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
                zone_file=f"./res/zone_files/{name[3:]}.zone",
                log_file=f"./res/logs/{ip}.log",
            )
            for ip, name in dns_servers.items()
        ]

    def start_all_dns_servers(self):
        """starts all nameservers at one"""
        for server in self.dns_servers:
            thread = Thread(target=server.recv, args=())
            thread.start()


class DnsServer:
    """
    class that simulates one nameserver (ns)
        - receives request from recusive resolver
        - searches child-nameserver in its zone file
        - updates dns-response-flags
        - sends response back to recursive resolver
    """

    def __init__(
        self, name: str, ip: str, port: int, zone_file: str, log_file: str
    ) -> None:
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

        # init temporary cycle log variables
        self.requests_send = 0
        self.requests_received = 0
        self.responses_send = 0
        self.responses_received = 0

        # setup server
        self.nameserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.nameserver.bind((self.ip, self.port))
        DnsServer.print(f"server '{self.name}'' is running ...")

    @staticmethod
    def print(msg: str) -> str:
        print(f"{ColorsPr.PURPLE}{msg}{ColorsPr.NORMAL}")

    def log_init(self):
        if not os.path.exists(self.log_file):
            timestamp = pd.Timestamp.now()
            ip = self.ip
            responses_send = 0
            responses_received = 0
            requests_send = 0
            requests_received = 0
            row = [
                timestamp,
                ip,
                requests_send,
                requests_received,
                responses_send,
                responses_received,
            ]
            log_df = pd.DataFrame([row], columns=CONST.LOG_COLUMNS)
            log_df.to_csv(self.log_file, index=False)
        threading.Timer(120, self.__log_procedure).start()

    def __log_procedure(self):
        with open(self.log_file, "r") as f:
            # read our log csv
            log_df: pd.DataFrame = pd.read_csv(f)
            # take last log
            last_log: dict = log_df.iloc[-1].to_dict()
            # add the current accumulators to the last status
            timestamp = pd.Timestamp.now()
            requests_received = last_log["Requests Received"] + self.requests_received
            requests_send = last_log["Requests Send"] + self.requests_send
            responses_send = last_log["Responses Send"] + self.responses_send
            responses_received = last_log["Responses Received"] + self.requests_received
            # zero out the accumulators
            (
                self.requests_received,
                self.responses_received,
                self.responses_send,
                self.requests_send,
            ) = (0, 0, 0, 0)
            # append row in dataframe
            log_df.loc[len(log_df)] = [
                timestamp,
                last_log["IP"],
                requests_send,
                requests_received,
                responses_send,
                responses_received,
            ]
            # save
            log_df.to_csv(self.log_file, index=False)
        threading.Timer(120, self.__log_procedure).start()

    def load_zone_file(self) -> pd.DataFrame:
        df: pd.DataFrame = pd.read_csv(
            self.zone_file,
            sep=" ",
            header=None,  # no column names in .zone-files
            names=["name", "ttl", "protocol", "record_type", "value"],
        )

        df["record_type"] = df["record_type"].apply(
            lambda x: QryType.A.value if x == "A" else QryType.NS.value
        )
        return df

    ####################[checkpoint b]#############################

    def resolve_qry(self, dns_format: DnsFormat) -> DnsResponseFormat:
        # [case 0] - is root
        if dns_format.request.name in ["root"]:
            return DnsResponseFormat(
                dns_flags_response=True,
                dns_flags_rcode=RCodes.NOERROR.value
                if dns_format.request.dns_qry_type == QryType.A.value
                else RCodes.SERVFAIL.value,
                dns_flags_authoritative=True,
                dns_ns=self.name,
                dns_a=CONST.get_ip(server_name=self.name),
                dns_count_answers=1,
                dns_resp_ttl=300
                if dns_format.request.dns_qry_type == QryType.A.value
                else None,
            )

        # [case 1] - child or suffix
        df_zonefile: pd.DataFrame = self.load_zone_file()

        for _, row in df_zonefile.iterrows():

            # [case 1a] - a child (in zone file) has sought name & record
            if dns_format.request.name == row["name"]:
                # record exists
                if dns_format.request.dns_qry_type == row["record_type"]:

                    # NS-Record
                    if dns_format.request.dns_qry_type == QryType.NS.value:
                        ns = row["value"]
                        row = df_zonefile[df_zonefile["name"] == ns].iloc[0]

                    # A-Record
                    return DnsResponseFormat(
                        dns_flags_response=True,
                        dns_flags_rcode=RCodes.NOERROR.value,
                        dns_ns=row["name"],
                        dns_a=row["value"],
                        dns_count_answers=1,
                        dns_flags_authoritative=True,
                        dns_resp_ttl=int(row["ttl"]),
                    )

                # record does not exists, but is A record
                elif dns_format.request.dns_qry_type == QryType.A.value:
                    row = df_zonefile[df_zonefile["name"] == row["value"]].iloc[0]
                    return DnsResponseFormat(
                        dns_flags_response=True,
                        dns_flags_rcode=RCodes.NOERROR.value,
                        dns_ns=row["name"],
                        dns_a=row["value"],
                        dns_count_answers=1,
                        dns_flags_authoritative=True,
                        dns_resp_ttl=int(row["ttl"]),
                    )

                # record does not exist and is NS record
                else:
                    return DnsResponseFormat(
                        dns_flags_response=True,
                        dns_flags_rcode=RCodes.SERVFAIL.value,
                        dns_flags_authoritative=False,
                        dns_ns=None,
                        dns_a=None,
                        dns_count_answers=1,
                        dns_resp_ttl=None,
                    )

            # [case 1b] - suffix
            elif dns_format.request.name.endswith(row["name"]):
                ns = row["value"]
                row = df_zonefile[df_zonefile["name"] == ns].iloc[0]

                # suffix is what we are searching
                if row["name"] == dns_format.request.name:

                    if row["record_type"] == dns_format.request.dns_qry_type:

                        return DnsResponseFormat(
                            dns_flags_response=True,
                            dns_flags_rcode=RCodes.NOERROR.value,
                            dns_flags_authoritative=True,
                            dns_ns=row["name"],
                            dns_a=row["value"],
                            dns_count_answers=1,
                            dns_resp_ttl=int(row["ttl"]),
                        )
                    else:
                        return DnsResponseFormat(
                            dns_flags_response=True,
                            dns_flags_rcode=RCodes.SERVFAIL.value,
                            dns_flags_authoritative=False,
                            dns_ns=None,
                            dns_a=None,
                            dns_count_answers=1,
                            dns_resp_ttl=None,
                        )

                # is real suffix and ns
                elif (
                    row["name"] != dns_format.request.name
                    and row["record_type"] == QryType.NS.value
                ):
                    return DnsResponseFormat(
                        dns_flags_response=False,
                        dns_flags_rcode=RCodes.NOTAUTH.value,
                        dns_flags_authoritative=False,
                        dns_ns=row["name"],
                        dns_a=row["value"],
                        dns_count_answers=1,
                        dns_resp_ttl=int(row["ttl"]),
                    )
                # is real suffix and a
                else:
                    return DnsResponseFormat(
                        dns_flags_response=True,
                        dns_flags_rcode=RCodes.NOTAUTH.value,
                        dns_flags_authoritative=False,
                        dns_ns=row["name"],
                        dns_a=row["value"],
                        dns_count_answers=1,
                        dns_resp_ttl=int(row["ttl"]),
                    )

        # [case 2] - does not exist
        return DnsResponseFormat(
            dns_flags_response=False,
            dns_flags_rcode=RCodes.NXDOMAIN.value,
            dns_flags_authoritative=None,
            dns_ns=None,
            dns_a=None,
            dns_resp_ttl=None,
            dns_count_answers=0,
        )

    def recv(self):
        """
        waits for query from rec. res.
        """
        while True:
            # receive msg
            msg, addr_rec_resolver = self.nameserver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")
            self.requests_received += 1

            # resolve request
            dns_req: DnsFormat = DnsFormat().fromJson(json.loads(msg))
            DnsServer.print(
                f"""------------------------\nnameserver {self.name} received query: {dns_req.request.name} {dns_req.request.dns_qry_type}"""
            )
            res: DnsResponseFormat = self.resolve_qry(dns_format=dns_req)

            self.requests_send += 1

            # response
            dns_res: DnsFormat = DnsFormat(
                request=dns_req.request,
                response=res,
            )
            DnsServer.print(f"nameserver {self.name} sends response:{dns_res.response}")
            msg_res: str = str.encode(dns_res.toJsonStr())
            time.sleep(0.100)
            self.nameserver.sendto(msg_res, addr_rec_resolver)


# load nameservers
servers = CONST.MAP_IP_SERVERS[ServerTypes.DNS.name]

# start nameservers (servers)
starter = DnsServerStarter(dns_servers=servers)
starter.start_all_dns_servers()

import socket
import json
import os
import time

import pandas as pd
import threading

from constants import Constants
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat, QryType, RCodes

CONST = Constants()


class RecursiveResolver:
    """
    class that simulates the recursive resolver
        - receives request from stub resolver
        - starts recursive name resolution by running through dns-tree
        - sends name resoluation back to stub resolver
    """

    def __init__(self) -> None:
        self.ip = CONST.IP_REC_RESOLVER
        self.port = CONST.PORT
        self.log_file = f"./res/logs/{self.ip}.log"

        # accumulator variables
        self.requests_received = 0
        self.requests_send = 0
        self.responses_received = 0
        self.responses_send = 0

        # initialise the log procedure
        self.log_init()

        # setup server
        self.rec_resolver = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.rec_resolver.bind((self.ip, self.port))
        print(f"RECURSIVE RESOLVER running ...")

    def log_init(self) -> None:
        if not os.path.exists(self.log_file):
            timestamp = pd.Timestamp.now()
            ip = self.ip
            responses_send = 0
            responses_received = 0
            requests_send = 0
            requests_received = 0
            row = [timestamp, ip, requests_send, requests_received,
                   responses_send, responses_received]
            log_df = pd.DataFrame([row], columns=CONST.LOG_COLUMNS)
            log_df.to_csv(self.log_file, index=False)
        threading.Timer(5, self.__log_procedudre).start()

    def __log_procedudre(self):
        with open(self.log_file, "r") as f:
            # read our log csv
            log_df: pd.DataFrame = pd.read_csv(f)
            # take last log
            last_log: dict = log_df.iloc[-1].to_dict()
            # add the current accumulators to the last status
            timestamp = pd.Timestamp.now()
            requests_received = last_log["Requests Received"] + \
                self.requests_received
            requests_send = last_log["Requests Send"] + self.requests_send
            responses_send = last_log["Responses Send"] + self.responses_send
            responses_received = last_log["Responses Received"] + \
                self.requests_received
            # zero out the accumulators
            self.requests_received, self.responses_received, self.responses_send, self.requests_send = 0, 0, 0, 0
            # append row in dataframe
            log_df.loc[len(log_df)] = [timestamp, last_log["IP"], requests_send,
                                       requests_received, responses_send, responses_received]
            # save
            log_df.to_csv(self.log_file, index=False)
        threading.Timer(30, self.__log_procedudre).start()

    def listen(self) -> None:
        """listens for stub resolver request and sends response back"""

        print(f"RECURSIVE RESOLVER listining ...")

        while True:
            # receive request
            msg, addr_client = self.rec_resolver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")
            print(f"RECURSIVE RESOLVER received: '{msg}' from {addr_client}")
            self.requests_received += 1
            # tramsform request into format
            msg = msg.split(" ")
            ns_of_interest: str = msg[0]

            # check if record type is provided
            if len(msg) < 2:
                msg.append("A")
            record: int = (
                QryType.A.value
                if msg[1] == "A"
                else QryType.NS.value
                if msg[1] == "NS"
                else None
            )
            req: DnsFormat = DnsFormat(
                request=DnsRequestFormat(
                    name=ns_of_interest, dns_qry_type=record)
            )

            # recursion - search for nameserver
            print(
                f"recursively searching for {ns_of_interest} {record}-record")
            dns_response: DnsFormat = self.recursion(dns_request=req)

            # caching function

            # send response
            print(f"dns_response is {dns_response.toJsonStr()}")
            msg_resolved: str = dns_response.toJsonStr()
            self.responses_send += 1
            time.sleep(.100)
            self.rec_resolver.sendto(str.encode(msg_resolved), addr_client)

    def recursion(self, dns_request: DnsFormat) -> DnsFormat:
        """starts recursive name resolution by running through dns-tree"""
        # [recursion anchor]
        # success
        print(dns_request.response)
        if dns_request.response.dns_flags_authoritative:
            # here do not return the request
            return dns_request

        # error
        if (
            dns_request.response.dns_flags_rcode != RCodes.NOERROR.value
            and dns_request.response.dns_flags_rcode != RCodes.NOTAUTH.value
        ):
            return dns_request

        # [calculation]
        # send to nameserver
        msg_req: str = str.encode(dns_request.toJsonStr())
        addr_nameserver = (dns_request.response.dns_a, CONST.PORT)
        time.sleep(.100)
        self.rec_resolver.sendto(msg_req, addr_nameserver)
        self.requests_send += 1

        # receive from nameserver
        msg, _ = self.rec_resolver.recvfrom(CONST.BUFFER)
        msg = msg.decode("utf-8")
        dns_response: DnsFormat = DnsFormat.fromJson(json.loads(msg))
        self.responses_received += 1
        print(f"REC. RES. received: \n {dns_response.toJsonStr()}\n")

        # [recusion step]
        return self.recursion(dns_request=dns_response)


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()

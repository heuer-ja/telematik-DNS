import datetime
import socket
import json
import os
import time
import math
import dns_resolver_cache

import pandas as pd
import threading

from constants import ColorsPr, Constants
from dns_format import DnsFormat, DnsRequestFormat, DnsResponseFormat, QryType, RCodes
from dns_resolver_cache import CacheEntry

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
        self.cache = dns_resolver_cache.Cache()

        # accumulator variables
        self.requests_received = 0
        self.requests_send = 0
        self.responses_received = 0
        self.responses_send = 0

        # initialise the log procedure
        self.log_init()

        # setup server
        self.rec_resolver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.rec_resolver.bind((self.ip, self.port))
        RecursiveResolver.print(f"RECURSIVE RESOLVER is running ...")

    @staticmethod
    def print(msg: str) -> str:
        print(f"{ColorsPr.YELLOW}{msg}{ColorsPr.NORMAL}")

    def log_init(self) -> None:
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

    def listen(self) -> None:
        """listens for stub resolver request and sends response back"""

        RecursiveResolver.print(f"RECURSIVE RESOLVER listening ...")

        while True:
            # receive request
            msg, addr_client = self.rec_resolver.recvfrom(CONST.BUFFER)
            msg = msg.decode("utf-8")
            RecursiveResolver.print(f"------------------------")
            RecursiveResolver.print(
                f"RECURSIVE RESOLVER received query: '{msg}' from {addr_client}"
            )
            self.requests_received += 1

            # transform request into format
            msg_parts = msg.split()
            ns_of_interest: str = msg_parts[0]

            if len(msg_parts) < 2:
                record = QryType.A.value
            else:
                record = (
                    QryType.A.value
                    if msg_parts[1] == "A"
                    else QryType.NS.value
                    if msg_parts[1] == "NS"
                    else QryType.INVALID.value
                )
            req: DnsFormat = DnsFormat(
                request=DnsRequestFormat(name=ns_of_interest, dns_qry_type=record),
                response=DnsResponseFormat(),
            )

            cache_record_type: int = record
            if cache_record_type is None:
                cache_record_type = QryType.A.value

            cache_entry: CacheEntry = self.cache.get(
                (ns_of_interest, cache_record_type)
            )

            if cache_entry is None:
                if record == QryType.A.value:
                    ns_of_interest_suffix_2: str = ns_of_interest
                    if ns_of_interest_suffix_2.startswith("ns."):
                        ns_of_interest_suffix_temp: str = ns_of_interest_suffix_2[3:len(ns_of_interest_suffix_2)]
                        cache_entry = self.cache.get(
                            (ns_of_interest_suffix_temp, QryType.NS.value)
                        )

            if cache_entry is None:
                ns_of_interest_suffix: str = ns_of_interest

                while len(ns_of_interest_suffix) > 0:
                    index_sep: int = ns_of_interest_suffix.find(".")
                    # no more dots in name
                    if index_sep == -1:
                        break
                    else:
                        ns_of_interest_suffix = ns_of_interest_suffix[
                            index_sep + 1:len(ns_of_interest_suffix)
                        ]
                        cache_entry = self.cache.get(
                            (ns_of_interest_suffix, QryType.NS.value)
                        )
                        if cache_entry is not None:
                            break
                if cache_entry is not None:
                    req.response.dns_ns = ns_of_interest_suffix
                    req.response.dns_a = cache_entry.value

                # recursion - search for nameserver
                RecursiveResolver.print(
                    f"recursively searching for {ns_of_interest} {record}-record"
                )
                dns_response: DnsFormat = self.recursion(dns_request=req)
            else:
                ttl: int = math.ceil(
                    (
                        cache_entry.timestamp_remove - datetime.datetime.now()
                    ).total_seconds()
                )
                dns_response: DnsFormat = DnsFormat(
                    request=req.request,
                    response=DnsResponseFormat(
                        dns_flags_response=True,
                        dns_flags_rcode=0,
                        dns_count_answers=0,
                        dns_flags_authoritative=True,
                        dns_a=cache_entry.value,
                        dns_ns=req.request.name,
                        dns_resp_ttl=ttl,
                    ),
                )
                # if ns record comes directly out of cache we have to prepend the ".ns"
                if dns_response.request.dns_qry_type == QryType.NS.value:
                    if not dns_response.response.dns_ns.startswith("ns."):
                        dns_response.response.dns_ns = "ns." + dns_response.response.dns_ns

            # send response
            msg_resolved: str = dns_response.toJsonStr()
            self.responses_send += 1
            time.sleep(0.100)
            self.rec_resolver.sendto(str.encode(msg_resolved), addr_client)

    def recursion(self, dns_request: DnsFormat) -> DnsFormat:
        """starts recursive name resolution by running through dns-tree"""
        # [recursion anchor]
        # success
        if dns_request.response.dns_flags_authoritative:
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
        time.sleep(0.100)
        self.rec_resolver.sendto(msg_req, addr_nameserver)
        self.requests_send += 1

        # receive from nameserver
        msg, _ = self.rec_resolver.recvfrom(CONST.BUFFER)
        msg = msg.decode("utf-8")
        dns_response: DnsFormat = DnsFormat.fromJson(json.loads(msg))
        self.responses_received += 1

        # call caching function if request was successful or points to another name server
        if (
            dns_response.response.dns_flags_rcode == RCodes.NOERROR.value
            or dns_response.response.dns_flags_rcode == RCodes.NOTAUTH.value
        ):
            ttl = dns_response.response.dns_resp_ttl
            timestamp_remove: datetime.datetime = (
                datetime.datetime.now() + datetime.timedelta(0, float(ttl))
            )

            # just put the value into the cache
            if dns_response.response.dns_flags_rcode == RCodes.NOERROR.value:
                self.cache[
                    dns_response.request.name, dns_response.request.dns_qry_type
                ] = CacheEntry(dns_response.response.dns_a, timestamp_remove)

            # Don't put the name of the NS into the cache but instead the domain it is responsible for, by cutting
            # off the leading ".ns"
            elif dns_response.response.dns_flags_rcode == RCodes.NOTAUTH.value:
                dns_ns_suffix: str = (
                    dns_response.response.dns_ns[3 : len(dns_response.response.dns_ns)]
                    if dns_response.response.dns_ns.startswith("ns.")
                    else dns_response.response.dns_ns
                )

                self.cache[dns_ns_suffix, QryType.NS.value] = CacheEntry(
                    dns_response.response.dns_a, timestamp_remove
                )

        RecursiveResolver.print(f"REC. RES. received: \n {dns_response.toJsonStr()}")

        # [recursion step]
        return self.recursion(dns_request=dns_response)


# start recursive resolver (middleman)
rec_resolver = RecursiveResolver()
rec_resolver.listen()

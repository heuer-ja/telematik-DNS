from enum import Enum
import json
from typing import Dict


class RCodes(Enum):
    NOERROR = 0  # DNS Query completed successfully
    FORMERR = 1  # DNS Query Format Error
    SERVFAIL = 2  # Server failed to complete the DNS request
    NXDOMAIN = 3  # Domain name does not exist
    NOTIMP = 4  # Function not implemented
    REFUSED = 5  # The server refused to answer for the query
    YXDOMAIN = 6  # Name that should not exist, does exist
    XRRSET = 7  # RR set that should not exist, does exist
    NOTAUTH = 8  # Server not authoritative for the zone
    NOTZONE = 9  # Name not in zone


class QryType(Enum):
    NS = 1  # ns record
    A = 2  # a record


class DnsRequestFormat:
    def __init__(
        self,
        dns_flags_recdesired: bool = False,
        name: str = "root",
        dns_qry_type: int = QryType.A.value,
    ) -> None:
        self.dns_flags_recdesired: bool = dns_flags_recdesired
        self.name: str = name
        self.dns_qry_type: int = dns_qry_type


class DnsResponseFormat:
    def __init__(
        self,
        dns_flags_response: bool = False,
        dns_flags_rcode: int = RCodes.NOTAUTH.value,
        dns_count_answers: int = 0,
        dns_flags_authoritative: bool = False,
        dns_a: str = "127.0.0.11",  # root
        dns_ns: str = "root",
        dns_resp_ttl: int = 0,
    ) -> None:
        self.dns_flags_response: bool = dns_flags_response
        self.dns_flags_rcode: int = dns_flags_rcode
        self.dns_count_answers: int = dns_count_answers
        self.dns_flags_authoritative: bool = dns_flags_authoritative
        self.dns_a: str = dns_a
        self.dns_ns: str = dns_ns
        self.dns_resp_ttl: int = dns_resp_ttl


class DnsFormat:
    """
    class for the dns format
        - message format of udp-communication between (a) stub (b) rec. res. (c) ns
        - contains request & response
    """
    def __init__(
        self,
        request: DnsRequestFormat = DnsRequestFormat(),
        response: DnsResponseFormat = DnsResponseFormat(),
    ) -> None:

        self.request: DnsRequestFormat = request
        self.response: DnsResponseFormat = response

    @staticmethod
    def fromJson(json):
        json_req = json["request"]
        request: DnsRequestFormat = DnsRequestFormat(
            dns_flags_recdesired=json_req["dns.flags.recdesired"],
            name=json_req["dns.qry.name"],
            dns_qry_type=json_req["dns.qry.type"],
        )

        json_res = json["response"]
        response: DnsResponseFormat = DnsResponseFormat(
            dns_flags_response=json_res["dns.flags.response"],
            dns_flags_rcode=json_res["dns.flags.rcode"],
            dns_count_answers=json_res["dns.count.answers"],
            dns_flags_authoritative=json_res["dns.flags.authoritative"],
            dns_a=json_res["dns.a"],
            dns_ns=json_res["dns.ns"],
            dns_resp_ttl=json_res["dns.resp.ttl"],
        )

        return DnsFormat(request=request, response=response)

    def toJson(self) -> Dict:
        json = {
            "request": {
                "dns.flags.recdesired": self.request.dns_flags_recdesired,  # True <-> recursion should be used by the server
                "dns.qry.name": self.request.name,  # requested name
                "dns.qry.type": self.request.dns_qry_type,  # requested type: A=1, NS=2
            },
            "response": {
                "dns.flags.response": self.response.dns_flags_response,  # True <-> a result was found
                "dns.flags.rcode": self.response.dns_flags_rcode,  # response code, more information see above at rcodes
                "dns.count.answers": self.response.dns_count_answers,  # count of answers
                "dns.flags.authoritative": self.response.dns_flags_authoritative,  # True <-> auth. DNS server |  False <-> recursive DNS server
                "dns.a": self.response.dns_a,  # ip adress
                "dns.ns": self.response.dns_ns,  # name of ns server if existing
                "dns.resp.ttl": self.response.dns_resp_ttl,  # TTL of the record
            },
        }
        return json

    def toJsonStr(self) -> str:
        return json.dumps(self.toJson(), indent=4, sort_keys=True)

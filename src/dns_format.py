from enum import Enum


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


class DnsFormat:
    def __init__(self) -> None:
        self.format = {
            "request": {
                "dns.flags.recdesired": False,  # True, if recursion should be used by the server
                "dns.qry.name": "root",  # requested name
                "dns.qry.type": 2,  # requested type: A=1, NS=2
            },
            "response": {
                "dns.flags.response": False,  # True <-> a result was found
                "dns.flags.rcode": RCodes.NXDOMAIN,  # response code, more information see above at rcodes
                "dns.count.answers": 0,  # count of answers
                "dns.flags.authoritative": True,  # True <-> auth. DNS server |  False <-> recursive DNS server
                "dns.a": "",  # ip adress
                "dns.ns": None,  # name of ns server if existing
                "dns.resp.ttl": 0,  # TTL of the record
            },
        }

    def updateRequest(
        self, recdesired: bool = None, name: str = None, type: int = None
    ):
        obj = self.format["request"]

        # update values if not None
        obj["dns.flags.recdesired"] = (
            recdesired if recdesired is not None else obj["dns.flags.recdesired"]
        )
        obj["dns.qry.name"] = name if name is not None else obj["dns.qry.name"]
        obj["dns.qry.type"] = type if name is not None else obj["dns.qry.type"]

        return

    def updateResponse(
        self,
        isResponse: bool = None,
        rcode: int = None,
        answers: int = None,
        isAuthoritative: bool = None,
        a: str = None,
        ns: str = None,
        ttl: int = None,
    ):
        obj = self.format["request"]

        # update values if not None
        obj["dns.flags.response"] = (
            isResponse if isResponse is not None else obj["dns.flags.response"]
        )
        obj["dns.flags.rcode"] = rcode if rcode is not None else obj["dns.flags.rcode"]
        obj["dns.count.answers"] = answers if answers is not None else obj["answers"]
        obj["dns.flags.authoritative"] = (
            isAuthoritative
            if isAuthoritative is not None
            else obj["dns.flags.authoritative"]
        )
        obj["dns.a"] = a if a is not None else obj["dns.a"]
        obj["dns.ns"] = ns if ns is not None else obj["dns.ns"]
        obj["dns.resp.ttl"] = ttl if ttl is not None else obj["dns.resp.ttl"]

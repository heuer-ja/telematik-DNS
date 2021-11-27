from enum import Enum
from os import name
from typing import Dict


class ServerTypes(Enum):
    DNS = 1
    HTTP = 2


class Constants:
    def __init__(self):
        self.PORT = 53053
        self.IP_REC_RESOLVER = "127.0.0.10"
        self.BUFFER = 1024*2

        self.MAP_IP_SERVERS: Dict = {
            "DNS": {
                "127.0.0.11": "root",
                "127.0.0.12": "telematik",
                "127.0.0.13": "switch.telematik",
                "127.0.0.14": "router.telematik",
                "127.0.0.15": "fuberlin",
                "127.0.0.16": "homework.fuberlin",
                "127.0.0.17": "pcpools.fuberlin",
            }
        }
        self.LOG_COLUMNS = [
            "Timestamp",
            "IP",
            "Requests Send",
            "Requests Received",
            "Responses Send",
            "Responses Received"
        ]

    def get_ip(
        self, server_name: str, server_type: ServerTypes = ServerTypes.DNS
    ) -> str:
        return next(
            (
                ip
                for ip, name in list(self.MAP_IP_SERVERS[server_type.name].items())
                if name == server_name
            ),
            None,
        )

    def get_name(self, ip: str, server_type: ServerTypes = ServerTypes.DNS) -> str:
        return self.MAP_IP_SERVERS[server_type.name][ip]

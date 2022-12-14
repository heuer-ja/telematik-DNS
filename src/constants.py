from enum import Enum
from typing import Dict


class ServerTypes(Enum):
    DNS = 1
    HTTP = 2


class ColorsPr:
    """'
    use for colored prints, e.g.
    print(f"{ColorsPr.YELLOW}Test message{ColorsPr.NORMAL}")
    """

    NORMAL = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"


class Constants:
    def __init__(self):
        self.PORT = 53053
        self.HTTP_PORT = 8080

        self.IP_REC_RESOLVER = "127.0.0.10"
        self.BUFFER = 1024 * 2

        self.MAP_IP_SERVERS: Dict = {
            "DNS": {
                "127.0.0.11": "ns.root",
                "127.0.0.12": "ns.telematik",
                "127.0.0.13": "ns.switch.telematik",
                "127.0.0.14": "ns.router.telematik",
                "127.0.0.15": "ns.fuberlin",
                "127.0.0.16": "ns.homework.fuberlin",
                "127.0.0.17": "ns.pcpools.fuberlin",
            }
        }
        self.LOG_COLUMNS = [
            "Timestamp",
            "IP",
            "Requests Send",
            "Requests Received",
            "Responses Send",
            "Responses Received",
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

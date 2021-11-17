import json
from dns_server import DnsServer, DnsServerStarter

# load nameservers
with open('res/config.json') as f:
    servers = json.load(f)

# start nameservers
starter = DnsServerStarter(dns_servers=servers["DnsConfig"])

# ask a specific nameserver for an (A) record
auth_server:DnsServer = next(
    (server for server in starter.dns_servers if server.name=="homework.fuberlin"), None)
auth_server.get_record(name="easy.homework.fuberlin")



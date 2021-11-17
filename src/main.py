import json
from dns_server import DnsServerStarter

# load nameservers
with open('../res/config.json') as f:
    servers = json.load(f)

# start nameservers
starter = DnsServerStarter(dns_servers=servers["DnsConfig"])
starter.start_all_dns_servers()


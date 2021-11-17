# client 
import socket
import json

from res.constants import Constants
from dns_server import DnsServer

CONST = Constants()

# laod nameservers
with open('res/config.json') as f:
    servers = json.load(f)

# setup stub resoliver
client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# send to servers
for ip, name in servers['DnsConfig'].items():
    server_info = (ip, CONST.PORT)
    client.sendto(str.encode('test'), server_info)



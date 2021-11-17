# client 
import socket
import json
from res.constants import Constants

CONST = Constants()

# laod nameservers
with open('res/config.json') as f:
    servers = json.load(f)

# setup stub resoliver
client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# input 
input_auth_server = "homework.fuberlin"
input_server_of_interest = f"easy.{input_auth_server}"

# get ip adress
ip = next((ip for ip,name in list(servers['DnsConfig'].items()) 
        if name==input_auth_server ), None)


# send query to server
client.sendto(str.encode(input_server_of_interest), (ip, CONST.PORT))
response, server = client.recvfrom(1024)
print(response.decode("utf-8"))




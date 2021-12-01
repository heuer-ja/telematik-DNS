from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import urllib.request
from constants import Constants
from dns_format import DnsFormat, RCodes
import socket
import requests
import json


CONST = Constants()

session_url = ""


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_adress, server, **kwargs):
        self.session_url = ""
        self.socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        super(SimpleHTTPRequestHandler, self).__init__(
            request, client_adress, server, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # handle requests, inspect query string
        query = urlparse(self.path).query
        query_entries = query.split("&")
        if query_entries[0] != '':
            query_components = dict(qc.split("=") for qc in query.split("&"))
            if "url" not in query_components:
                print("URL NOT IN Q COMP")
            else:
                url = query_components["url"]

                # see if suffix is within local dns
                suffix_helper = url.split(".")
                suffix = suffix_helper[len(suffix_helper)-1]
                local_dns_suffixes = ["telematik", "fuberlin"]
                # needed for additional ressources like icons
                self.server.session_url = url
                if suffix in local_dns_suffixes:
                    msg_request = str.encode(url)
                    rec_res_info = (CONST.IP_REC_RESOLVER, CONST.PORT)
                    client = socket.socket(
                        family=socket.AF_INET, type=socket.SOCK_DGRAM)
                    client.sendto(msg_request, rec_res_info)
                    msg_response, _ = client.recvfrom(CONST.BUFFER)
                    msg_response: str = msg_response.decode("utf-8")
                    dns_response: DnsFormat = DnsFormat().fromJson(json.loads(msg_response))
                    if dns_response.response.dns_flags_rcode == RCodes.NOERROR.value:
                        entries = dns_response.response.dns_a.split(":")
                        ip = entries[0]
                        # connect via tcp
                        print(entries)
                        if len(entries) > 1:
                            adress = "http://" + dns_response.response.dns_a
                            # self.send_response(page)
                            # self.copyfile(handle, self.wfile)
                            req = urllib.request.Request(adress)
                            with urllib.request.urlopen(req) as response:
                                the_page = response.read()
                                self.wfile.write(the_page)
                        print(
                            f"{dns_response.request.name} has ip adress {dns_response.response.dns_a}"
                        )

                    else:
                        print(
                            f"name {dns_response.request.name} could not be resolved")
                else:
                    if not url.startswith("http://"):
                        url = "http://" + url
                    self.server.session_url = url
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req) as response:
                        the_page = response.read()
                        self.wfile.write(the_page)
        else:
            url = self.server.session_url + self.path
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                the_page = response.read()
                self.wfile.write(the_page)
        # we do assume, that the query parameter is named url, this will also be documented.


server = HTTPServer(("127.0.0.90", 8090), Handler)
server.serve_forever()
print("Running http server on port 8080!")

from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import urllib.request
from constants import Constants
from dns_format import DnsFormat, RCodes
import socket
import http.client
import requests


CONST = Constants()


class Handler(SimpleHTTPRequestHandler):
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
                message = "Sorry, but your query is invallid."
            else:
                url = query_components["url"]

                # see if suffix is within local dns
                suffix_helper = url.split(".")
                suffix = suffix_helper[len(suffix_helper)-1]
                local_dns_suffixes = ["telematik", "fuberlin"]
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
                        print(
                            f"{dns_response.request.name} has ip adress {dns_response.response.dns_a}"
                        )

                    else:
                        print(
                            f"name {dns_response.request.name} could not be resolved")
                else:
                    # conn = http.client.HTTPConnection(url)
                    # conn.request("GET", "/")
                    # response = conn.getresponse()
                    # message = response
                    if url.startswith("http://"):
                        self.copyfile(urllib.request.urlopen(url), self.wfile)
                    else:
                        url = "http://" + url
                        self.copyfile(urllib.request.urlopen(url), self.wfile)
                    message = "test"
        else:
            message = "No query parameters passed."

        # we do assume, that the query parameter is named url, this will also be documented.
        self.wfile.write(bytes(message, "utf8"))


with HTTPServer(("127.0.0.90", 8090), Handler) as server:
    server.serve_forever()
    print("Running http server on port 8080!")

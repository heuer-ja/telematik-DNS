# General Knowledge
- **stub resolver**: client side
- **recursive resolver**: middleman between client and lots of dns-servers (root NS, top-level-domain NS, second-level-domain NS). 
    - when trying to resolve a domain, it asks n *root NS*.
    - n-1 response with "no answer", 1 response with "answer"
    - rec. res. asks "answer", which also gives and answer
    - ... some answer gives information (records) for domain
- **A record** of a domain/name is its ip adress (IPv4)


### Resources
- iterative vs. recursive lookup https://stackoverflow.com/questions/9966280/difference-between-recursive-and-iterative-dns-lookup
    --> we do recursive


----------------------------------------------------------------------

# Task
The goal is to implement basic functionalities of 
- a stub resolver
- a recursive resolver
- an authoritative DNS server, 
    
- and to operate namespaces.

### Hints
    - top level domains can be hardcoded
    - dns format can be simple: e.g. json


## Milestones
List of milestones 

### (a) A-record
Your stub resolver is able to (directly) request an A record from the authorative server.

    - random data tranfer (udp) between client and author. NS


### (b) Recusive Resolver
Your recursive resolver is able to discover the authoritative server of a name, and resolve the A record for this name.

### (c) Cache
Your stub resolver is able to resolve any name in the list via the recursive resolver and profits from faster replies in the case of cache hits at the recursive resolver.

    TIPPS:
    - since we are using localhost (127.0.0.x), there is just little delay
        --> use sleep()-method for sending methods


### Logging
The logging procedure is implemented at the recursive resolver and the dns servers. If log files are not initialised, this is taken care of at server start. Furthermore, there are several accumulator counters at each server, which do keep track of the incoming/outgoing requests/responses and every *n* seconds a new line with the incremented with the accumulator old values from the log is added, in order to keep track of the measures. The procedure runs in the background and does so, until the server is shut down.

### (d) HTTP Proxy
Your DNS implementation is used by an application (see HTTP proxy below).

Two http servers were implemented in order to solve the second part of the project description. 

- The HTTP server is implemented in the <code>http_server.py</code> file and runs on 127.0.0.80 and port 8080. We did add the server to the zone file of the switch.telematik authorative dns server, in order to be able to obtain it afterwards in the http proxy. The server does return a simple web-page, which says "You reached the server!". The domain name we chose corresponds to **http.switch.telematik**
- The HTTP proxy is implemented in the <code>http_proxy.py</code> file. As a GET request is required, we pass the domain name as an url [query parameter](https://en.wikipedia.org/wiki/Query_string).
  - the ip adress of the HTTP proxy is 127.0.0.90 and the chosen port is 8090.
  - The query parameter is named url. Therefore a request shall be formatted in the following way: 
  > http://127.0.0.90:8090?url=www.google.com
  
  where www.google.com is just an example url. Addititonal cases like google.com are not considered, due to the overcomplication of the task.
  If 
  > http://127.0.0.90:8090?url=http.switch.telematik
  
  is requested, then the response from the HTTP server from the previous point shall be returned. Otherwise the response shall be returned by another server, whose IP is resolved by the system and not by our own DNS server.

----------------------------------------------------------------------


# Execution

## Script (milestone b)
1. `python3 src/dns_server.py` - run all nameservers
2. `python3 src/recursive_resolver.py` - run recursive resolver
3. `python3 src/stub_resolver.py` - run stub resolver
    - input sth. like "linux.pcpools.fuberlin"
4. `python3 src/http_proxy.py` - run HTTP proxy
5. `python3 src/http_server.py` - run HTTP server  
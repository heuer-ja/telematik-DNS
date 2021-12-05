# 1. Execution
Start programs from root directory

## Prerequirements
One must install <code>pandas</code>, as it is required for our project.
This could be done, depending on the package manager with: 
>conda install pandas

or 

>pip3 install pandas


## Commands
1. `python3 src/dns_server.py` - run all nameservers
2. `python3 src/recursive_resolver.py` - run recursive resolver
3. `python3 src/stub_resolver.py` - run stub resolver
    - input sth. like "linux.pcpools.fuberlin NS"
4. `python3 src/http_proxy.py` - run HTTP proxy
5. `python3 src/http_server.py` - run HTTP server  


### Error handling
- If, for whatever reason, the used addresses are blocked after running the scripts, the following command will help under *Ubuntu*:



`pkill -9 -f src/dns_server.py && pkill -9 -f src/recursive_resolver.py && pkill -9 -f src/stub_resolver.py`

    
## 2. Documentation

## 2.1 General
### Local DNS
- Our local DNS consists of the following domains and IPs in the form of the tree structure shown:

```
Tree structure:
(0) root 
    (1) telematik [127.0.0.12]
        (2) switch.telematik [127.0.0.13]
            (3) www.switch.telematik [127.0.0.21]
            (3) mail.switch.telematik [127.0.0.22]
        (2) router.telematik [27.0.0.14]
            (3) news.router.telematik [127.0.0.23]
            (3) store.router.telematik [127.0.0.24]
    (1) fuberlin [127.0.0.15]
        (2) homework.fuberlin [127.0.0.16]
            (3) easy.homework.fuberlin [127.0.0.25]
            (3) hard.homework.fuberlin [127.0.0.26]
        (2) pcpools.fuberlin [127.0.0.17]
            (3) linux.pcpools.fuberlin [127.0.0.27]
            (3) macos.pcpools.fuberlin [127.0.0.28]
            (3) windows.pcpools.fuberlin [127.0.0.29]
```

### Zone Files
- We use *zone files* to store for each nameserver `DnsServer` its children within the tree structure as well as their records.
- The attribute `DnsServer.zone_file` gives a nameserver access to its own *zone file*. 
- The totality of all *zone files* then finally results in the tree structure shown above. 
For example, the *zone file* `telematik.zone` for the name server *telematik* looks like this:
```
switch.telematik;300 IN NS 127.0.0.13
router.telematik;300 IN NS 127.0.0.14
```

### DNS Format
- The `DnsFormat` class contains all DNS flags specified from the task. 
- Instances of `DnsFormat` are passed back and forth from the `StubResolver`, `RecursiveResolver` and `DnsServer` classes in the form of `json` strings. 
- The given flags are divided into *Request` with `DnsFormatRequest` and *Response` with `DnsFormatResponse`.

```
Our DNS format represented as JSON

dns_format = {
    "request": {
        "dns.flags.recdesired": Bool, # True <-> recursion should be used by the server
        "dns.qry.name": str, # requested name
        "dns.qry.type": int, # requested type: A=1, NS=2, Invalid=0
    }
    "response": {
        "dns.flags.response": Bool, # True <-> a result was found
        "dns.flags.rcode": int, # response code, more information see above at rcodes
        "dns.count.answers": int, # count of answers
        "dns.flags.authoritative": boolean, # True <-> auth. DNS server | False <-> rec. DNS server
        "dns.a": str, # ip address
        "dns.ns": str, # name of ns server if existing
        "dns.resp.ttl": int # TTL of the record
    }
}

```

### Parallel execution
- Threads are used for all name servers `DnsServer`. 
- This ensures parallel execution of these instances.


## 2.2 Local Name Resolution
### Stub Resolver
1. send
    - `StubResolver` sends a request to `RecursiveResolver`, which receives it. 
    - The request is divided into two components: (a) domain to be resolved (b) record type. 
    - An example request from `StubResolver` looks like this: *switch.telematics NS*
2. receive
    - `StubResolver` receives response from `RecursiveResolver`.
3. output
    - After receiving the response from `RecursiveResolver`, the response is printed.

### Recursive Resolver
1. receive
    - `RecursiveResolver` receives the request from `StubResolver`. 
    - The request is converted into a suitable `DnsFormat` that holds certain flags for *Request* and *Response*.
2. name resolution by recursion
    - DNS tree is traversed by `RecurisveResolver` first sending the request to the *root* name server. 
    - The response from *root* then leads to either the recursion anchor or another recursion step. 
    - If the recursion leads up to a leaf and the request cannot be resolved, the recursion terminates. Otherwise, the recursion continues.
3. return answer 
    - The response determined in the recursion is sent back to the `StubResolver` in the form of `DnsFormat`



### Nameservers
1. receive
    - Each name server `DnsServer` runs in its own thread and uses polling to wait for a request from `RecursiveResolver`.  
    - In total, 7 threads are running locally - all servers at tree level (0), (1) and (2). 
2. name resolution by zone-file
    - If one of the `DnsServer` receives a request, it tries to resolve it with `DnsServer.resolve_qry()`. 
    - Several cases exist here (ns = requested nameserver):
        1. [recursion anchor] ns is root & root is searched for
        2 [recursion anchor] ns knows a direct child that is being searched for  
        3. [recursion anchor] ns does not know a child being searched for or a child with matching suffix
        4. [recursion anchor] ns knows a child with matching suffix of the searched domain
3. return answer 
    - The determined answer is sent back to the `RecursiveResolver` in the form of `DnsFormat`


*Note:*
If query asks for NS record of a auth. nameserver (e.g. `ns.telematik NS`) our program throws ErrorCode.SERVFAIL, 
because it is already the auth. NS.

### Logging
The logging procedure is implemented at the recursive resolver and the dns servers. If log files are not initialised, this is taken care of at server start. Furthermore, there are several accumulator counters at each server, which do keep track of the incoming/outgoing requests/responses and every *n* seconds a new line with the incremented with the accumulator old values from the log is added, in order to keep track of the measures. The procedure runs in the background and does so, until the server is shut down.

## 2.3. Cache
`TODO Lukas`

## 2.4. HTTP Proxy / HTTP Server
HTTP Proxy
Your DNS implementation is used by an application (see HTTP proxy below).

Two http servers were implemented in order to solve the second part of the project description. 

- The HTTP server is implemented in the <code>http_server.py</code> file and runs on 127.0.0.80 and port 8080. We did add the server to the zone file of the switch.telematik authorative dns server, in order to be able to obtain it afterwards in the http proxy. The server does return a simple web-page, which says "You reached the server!". The domain name we chose corresponds to **http.switch.telematik**
- The HTTP proxy is implemented in the <code>http_proxy.py</code> file. As a GET request is required, we pass the domain name as an url [query parameter](https://en.wikipedia.org/wiki/Query_string).
  - the ip adress of the HTTP proxy is 127.0.0.90 and the chosen port is 8090.
  - The query parameter is named url. Therefore a request shall be formatted in the following way: 
  > http://127.0.0.90:8090?url=www.google.com
  
  where www.google.com is just an example url. Addititonal cases like google.com are not considered, due to the overcomplication of the task.
  If 
  > http://127.0.0.90:8090?url=www.switch.telematik
  
  is requested, then the response from the HTTP server from the previous point shall be returned. Otherwise the response shall be returned by another server, whose IP is resolved by the system and not by our own DNS server.



## 3. Team & Participation

**Legende**
- Leo (Leo Lojewski)
- Leslie (Leslie Hoferichter)
- Lukas (Lukas Ludwig) 
- Joel (Joel Heuer)
- Viktoriya (Viktoriya Kraleva)


| task          | people involved                     |
| ------------- | ----------------------------------- |
| Milestone (a) | Leo, Leslie, Joel                   |
| Milestone (b) | Leo, Leslie, Joel                   |
| Milestone (c) | Lukas                               |
| Milestone (d) | Viktoriya                           |
| Management    | Leo, Leslie, Joel                   |
| Documentation | Leo, Leslie, Lukas, Joel, Viktoriya |




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


----------------------------------------------------------------------


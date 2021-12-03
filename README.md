# 1. Execution
Start programs from root directory

1. `python3 src/dns_server.py` - run all nameservers
2. `python3 src/recursive_resolver.py` - run recursive resolver
2. `python3 src/stub_resolver.py` - run stub resolver
    input sth. like "linux.pcpools.fuberlin NS"


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

## 2.3. Cache
`TODO Lukas`

## 2.4. Web Proxy
`TODO Viki`


## 3. Team & Participation

**Legende**
- Leo (Leo Lojewski)
- Leslie (Leslie Hoferichter)
- Lukas (Lukas Ludwig) 
- Joel (Joel Heuer)
- Viktoriya (Viktoriya Kraleva)


| task | people involved |
| ----------- | ----------- |
| Milestone (a) | Leo, Leslie, Joel |
| Milestone (b) | Leo, Leslie, Joel |
| Milestone (c) | Luke |
| Milestone (d) | Viktoriya |
| Management | Leo, Leslie, Joel |
| Documentation | Leo, Leslie, Lukas, Joel, Viktoriya |





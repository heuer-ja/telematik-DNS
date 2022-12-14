# Table of Contents
1. [ Execution ](#exe)
    1. [ Prerequirements ](#prereq)
        1. [ Operating System ](#os)
        2. [ Python Libraries/Packages](#libs)
        3. [ Directories ](#directories)
    2. [ Commands ](#commands)
        1. [ Variant 1: Run Script ](#run)
        2. [ Variant 2: Separate Files ](#separate)
        3. [ Error Handling ](#errorhandling)
    3. [ Prints & Colors  ](#prints)
    4. [ Tests ](#tests)
2. [ Documentation ](#docu)
    1. [ General ](#general)
        1. [ Local DNS ](#localdns)
        2. [ Zone Files](#zonefiles)
        3. [ DNS Format ](#dnsformat)
        4. [ Parallel Execution ](#parallel)
    2. [ Local Name Resolution ](#localnameresolution)
        1. [ Stub Resolver ](#stub)
        2. [ Recursive Resolver ](#recursiveresolver)
        3. [ Nameservers ](#nameservers)
        4. [ Logging ](#logging)
    3. [ Cache ](#cache)
    4. [ HTTP Proxy / HTTP Server ](#http)
3. [ Limitations ](#limits)
3. [ Team & Participation ](#team)


<a name="exe"></a>
# 1. Execution


<a name="prereq"></a>
## 1.1. Prerequirements


<a name="os"></a>
### Operating System 
- Linux is required for using the specified `commands` in this file. 

<a name="libs"></a>
### Python Libraries/Packages
- One must install `pandas`, as it is required for our project.
- This could be done, depending on the package manager with: 

| pip                   | conda                  |
| --------------------- | ---------------------- |
| `pip install pandas`  | `conda install pandas` |


<a name="directories"></a>
### Directories
- directory `res/logs` has to exist, otherwise logging throws an error 
    - when properly cloning this repository, it already exists


<a name="commands"></a>
## 1.2. Commands
Start programs from root directory

<a name="run"></a>
### Variant 1: Run Script
- You can start the entire *DNS* with a *run script* called `run.sh`:
- Run with combined command (Linux): `chmod u+x run.sh && ./run.sh`
- or separate:
    1. `chmod u+x run.sh`
    2. `./run.sh`

<a name="separate"></a>
### Variant 2: Separate Files
- Alternatively, you can run all files on its own.
- Therefore, start all files on a separate terminal.
    1. `python3 src/dns_server.py` - run all nameservers
    2. `python3 src/recursive_resolver.py` - run recursive resolver
    3. `python3 src/stub_resolver.py` - run stub resolver
        - `python3 src/stub_resolver.py 1` - run test1 (some examplary queries)
        - `python3 src/stub_resolver.py 2` - run test2 (cache)
        - `python3 src/stub_resolver.py 3` - run test3 (http proxy)
        - `python3 src/stub_resolver.py 4 www.switch.telematik A` run test4 (own query)

    4. `python3 src/http_proxy.py` - run HTTP proxy
    5. `python3 src/http_server.py` - run HTTP server  

<a name="errorhandling"></a>
### Error Handling
- If, for whatever reason, the used addresses are blocked after running the scripts, the following command will help under *Linux*:
    1. Combined `pkill -9 -f "^python3 src/.*"`
    2. Separate: 
        1. pkill -9 -f src/dns_server.py
        2. pkill -9 -f src/recursive_resolver.py
        3. pkill -9 -f src/stub_resolver.py
        4. pkill -9 -f src/http_proxy.py
        5. pkill -9 -f src/http_server.py

<a name="prints"></a>
## 1.3. Prints & Colors 
- During execution, the run is printed. 
- If you use a console/terminal that supports colors, colors will be displayed.

| Class | Color | Prints |
| ------ | ------| -------- |
| `StubResolver`  | green | (1) input query (2) final response from `RecurisveResolver` |
| `RecursiveResolver`  | yellow | (1) input Query from `StubResolver` (2) responses from different `DnsServer` |
| `DnsServer`  | purple | (1) redirected query from `RecurisveResolver` (2) calculated response (name resolution) |

<a name="tests"></a>
## 1.4. Tests
- In total there are 4 tests
- The easiest way to start these tests is via `run.sh`
- Test description
    - Test 1 (*Checkpoint b - Recursive Resolver*)
        - tests whether the recursive resolver can resolve names
        - several different queries are sent from `StubResolver` to `RecursiveResolver`
        - multiple responses are printed
    - Test 2 (*Checkpoint c - Cache*)
        - tests whether the cache is working
        - several similar queries are sent from `StubResolver` to `RecursiveResolver`
        - you can see that the measured time is reduced
    - Test 3 (*Checkpoint d - HTTP Proxy*)
        - tests the *HTTP Proxy* and *HTTP Server*.
        - opens internet browser in several tabs
            - Tab 1: *www.switch.telematik* (local DNS)
            - Tab 2: *wikepedia.com* (external DNS)
    - Test 4 (*Do it yourself - Local DNS*)
        - here you can enter your own queries
        - Access to HTTP proxy not possible via console
        - repeating test 4 allows to test the cache  
    - Test 5 (*Do it yourself 2 - HTTP Proxy*)
        - not included in `run.sh`
        - you have to open your browser 
        - enter the URL *http://127.0.0.90:8090/?url={YOUR_DOMAIN}*
        - replace *{YOUR_DOMAIN}* with any domain you like 
        - see whether your domain is resolved by our DNS


<a name="docu"></a>
# 2. Documentation

<a name="general"></a>
## 2.1. General

<a name="localdns"></a>
### Local DNS
- Our local DNS consists of the following domains and IPs in the form of the tree structure shown:

```
Domain Tree structure:
(0) root 
    (1) telematik [127.0.0.32]
        (2) switch.telematik [127.0.0.33]
            (3) www.switch.telematik [127.0.0.80]
            (3) mail.switch.telematik [127.0.0.22]
        (2) router.telematik [27.0.0.34]
            (3) news.router.telematik [127.0.0.23]
            (3) store.router.telematik [127.0.0.24]
    (1) fuberlin [127.0.0.35]
        (2) homework.fuberlin [127.0.0.36]
            (3) easy.homework.fuberlin [127.0.0.25]
            (3) hard.homework.fuberlin [127.0.0.26]
        (2) pcpools.fuberlin [127.0.0.37]
            (3) linux.pcpools.fuberlin [127.0.0.27]
            (3) macos.pcpools.fuberlin [127.0.0.28]
            (3) windows.pcpools.fuberlin [127.0.0.29]
```

- Meanwhile the Name Servers are structured as follows:
```
Name Server Tree structure:
(0) ns.root [127.0.0.11]
    (1) ns.telematik [127.0.0.12]
        (2) ns.switch.telematik [127.0.0.13]
        (2) ns.router.telematik [127.0.0.14]
    (1) ns.fuberlin [127.0.0.15]
        (2) ns.homework.fuberlin [127.0.0.16]
        (2) ns.pcpools.fuberlin [127.0.0.17]
```
- Every Name Server is authoritative for the subdomain that has the same name (without the leading "ns.")
- Additionally the Name Servers on layer (2) are authoritative for the subdomains on layer (3) (e.g. ns.switch.telematik is authoritative for www.switch.telematik) 


<a name="zonefiles"></a>
### Zone Files
- We use *zone files* to store for each nameserver `DnsServer` its children within the tree structure as well as their records. This is done by using Glue Records.
- The attribute `DnsServer.zone_file` gives a nameserver access to its own *zone file*. 
- The totality of all *zone files* then finally results in the tree structure shown above. 
For example, the *zone file* `telematik.zone` for the name server *telematik* looks like this:

```
switch.telematik 300 IN NS ns.switch.telematik
ns.switch.telematik 300 IN A 127.0.0.13

router.telematik 300 IN NS ns.router.telematik
ns.router.telematik 300 IN A 127.0.0.14

telematik 300 IN A 127.0.0.32
```

<a name="dnsformat"></a>
### DNS Format
- The `DnsFormat` class contains all DNS flags specified from the task. 
- Instances of `DnsFormat` are passed back and forth from the `StubResolver`, `RecursiveResolver` and `DnsServer` classes in the form of `json` strings. 
- The given flags are divided into *Request` with `DnsFormatRequest` and *Response` with `DnsFormatResponse`.

```
Our DNS format represented as JSON:

dns_format = {
    "request": {
        "dns.flags.recdesired": Bool,       # True <-> recursion should be used by the server
        "dns.qry.name": str,                # requested name
        "dns.qry.type": int,                # requested type: A=1, NS=2, Invalid=0
    }
    "response": {
        "dns.flags.response": Bool,         # True <-> a result was found
        "dns.flags.rcode": int,             # response code, more information see above at rcodes
        "dns.count.answers": int,           # count of answers
        "dns.flags.authoritative": Bool,    # True <-> auth. DNS server | False <-> rec. DNS server
        "dns.a": str,                       # ip address
        "dns.ns": str,                      # name of ns server if existing
        "dns.resp.ttl": int                 # TTL of the record
    }
}
```
<a name="parallel"></a>
### Parallel execution
- Threads are used for all name servers `DnsServer`. 
- This ensures parallel execution of these instances.

<a name="localnameresolution"></a>
## 2.2. Local Name Resolution

<a name="stub"></a>
### Stub Resolver
1. send
    - `StubResolver` sends a request to `RecursiveResolver`, which receives it. 
    - The request is divided into two components: (a) domain to be resolved (b) record type. 
    - An example request from `StubResolver` looks like this: *switch.telematics NS*
2. receive
    - `StubResolver` receives response from `RecursiveResolver`.
3. output
    - After receiving the response from `RecursiveResolver`, the response is printed.

<a name="recursiveresolver"></a>
### Recursive Resolver
1. receive
    - `RecursiveResolver` receives the request from `StubResolver`. 
    - The request is converted into a suitable `DnsFormat` that holds certain flags for *Request* and *Response*.
2. name resolution by recursion
    - DNS tree is traversed by `RecursiveResolver` first sending the request to the *root* name server, assuming the cache is empty. For more details see section [Cache](#cache)
    - The response from *root* then leads to either the recursion anchor or another recursion step. 
    - If the recursion leads up to a leaf and the request cannot be resolved, the recursion terminates. Otherwise, the recursion continues.
3. return answer 
    - The response determined in the recursion is sent back to the `StubResolver` in the form of `DnsFormat`

<a name="nameservers"></a>
### Nameservers
1. receive
    - Each name server `DnsServer` runs in its own thread and uses polling to wait for a request from `RecursiveResolver`.  
    - In total, 7 threads are running locally - all servers at tree level (0), (1) and (2). 
2. name resolution by zone-file
    - If one of the `DnsServer` receives a request, it tries to resolve it with `DnsServer.resolve_qry()`. 
    - Several cases exist here (ns = requested nameserver):
        1. [recursion anchor] NS is root & root is searched for
        2. [recursion anchor] NS knows a direct child that is being searched for  
        3. [recursion anchor] NS knows a child with matching suffix of the searched domain
        4. [recursion anchor] NS does not know a child being searched for or a child with matching suffix 
3. return answer 
    - The determined answer is sent back to the `RecursiveResolver` in the form of `DnsFormat`


*Note:*
If query asks for NS record of a auth. nameserver (e.g. `ns.telematik NS`) our program throws ErrorCode.SERVFAIL, 
because it is already the auth. NS.


<a name="logging"></a>
### Logging
- The logging procedure is implemented at the `RecursiveResolver` and the dns servers. 
- If log files are not initialised, this is taken care of at server start. 
- Furthermore, there are several accumulator counters at each server, which do keep track of the incoming/outgoing requests/responses and every *n* seconds a new line with the incremented with the accumulator old values from the log is added, in order to keep track of the measures. The procedure runs in the background and does so, until the server is shut down.


<a name="cache"></a>
## 2.3. Cache
- The `Cache` is basically a dictionary with the domain name and query type (*NS-RR* or *A-RR* represented through an Enum as an Integer) as key and a `CacheEntry` object as value.
- A `CacheEntry` consists of a value (for this project always an IP address) and a timestamp after which the entry has to be removed, that is calculated by using a timestamp of the current time and adding the ttl.
- Expired cache entries are periodically removed by an extra thread.
- In this project only the `RecursiveResolver` has a cache and every response to the `RecursiveResolver`, that is not an error, is cached.
- There are two ways cache entries are used to reduce the number of requests sent to the Name Servers:
  1. The requested name together with the requested Resource Record is already contained in the cache, then the corresponding value (IP address) is used for the response.
  2. A suffix of the requested name together with Resource Record type *NS* is already contained in the cache, then the `RecursiveResolver` sends its request to the IP address of that Name Server instead of to root. A simplified example: The cache already contains the key for name fuberlin with Resource Record *NS*, then it will send a request for the *A-RR* of homework.fuberlin to fuberlin (to ns.fuberlin to be exact) instead of to root.
- The leading "`ns.`" of our name servers is cut before it is written in the cache, so that the cache entry always points to a domain name.
- Caching can be tested by making subsequent requests to the `StubResolver` without stopping the `RecursiveResolver`. As every send operation waits 100ms before executing, and the `StubResolver` prints out the total Query time for each request, the Query Time should noticeably decrease if the cache is used.


<a name="http"></a>
## 2.4. HTTP Proxy / HTTP Server
Two http servers were implemented in order to solve the second part of the project description. 

- The HTTP server is implemented in the <code>http_server.py</code> file and runs on 127.0.0.80 and port 8080. The server is included in the zone file of the switch.telematik authorative dns server, in order to be able to obtain it afterwards in the http proxy. The server does return a simple web-page, which says "You reached the server!". The domain name we chose corresponds to **www.switch.telematik**
- The HTTP proxy is implemented in the <code>http_proxy.py</code> file. As a GET request is required, we pass the domain name as an url [query parameter](https://en.wikipedia.org/wiki/Query_string).
  - the ip adress of the HTTP proxy is 127.0.0.90 and the chosen port is 8090.
  - The query parameter is named url. Therefore a request shall be formatted in the following way: 
  > http://127.0.0.90:8090?url=www.google.com
  
  where www.google.com is just an example url. Additional cases like google.com are not considered, due to the overcomplication of the task.
  If 
  > http://127.0.0.90:8090?url=www.switch.telematik
  
  is requested, then the response from the HTTP server from the previous point shall be returned. Otherwise the response shall be returned by another server, whose IP is resolved by the system and not by our own DNS server.

<a name="limits"></a>
## 3. Limitations
Our implementation of a DNS provides only the basic functionalities. Limitations of our implementation are among other things:
- For the zone *root*, some things are hardcoded since no *zone file* exists that specifies a nameserver or IP address for it.
- All our *zone files* only cover *A* and *NS records*.
- For one *zone* exists exactly one nameserver  
- HTTP proxy cannot find a favicon and therefore gives warnings when entering URLs

<a name="team"></a>
## 4. Team & Participation
**Legend**
- Leo (Leo Lojewski)
- Leslie (Leslie Hoferichter)
- Lukas (Lukas Ludwig) 
- Joel (Joel Heuer)
- Viktoriya (Viktoriya Kraleva)


| Task          | People involved                     |
| ------------- | ----------------------------------- |
| Milestone (a) | Leo, Leslie, Joel, Lukas            |
| Milestone (b) | Leo, Leslie, Joel, Lukas            |
| Milestone (c) | Lukas                               |
| Milestone (d) | Viktoriya                           |
| Management    | Leo, Leslie, Joel                   |
| Documentation | Leo, Leslie, Lukas, Joel, Viktoriya |



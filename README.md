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


### (d) HTTP Proxy
Your DNS implementation is used by an application (see HTTP proxy below).

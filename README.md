# 1. Execution
Start programs from root directory

1. `python3 src/dns_server.py` - run all nameservers
2. `python3 src/recursive_resolver.py` - run recursive resolver
2. `python3 src/stub_resolver.py` - run stub resolver
    input sth. like "linux.pcpools.fuberlin NS"


### Error handling
- Falls, warum auch immer, nach Ausführung der Scripte die genutzten Adressen blockiert sein sollten, helfen unter *Ubuntu* folgende Befehle:

`pkill -9 -f src/dns_server.py  && pkill -9 -f src/recursive_resolver.py && pkill -9 -f src/stub_resolver.py`

    
# 2. Documentation

## 2.1. General
### Lokales DNS
- Unser lokales DNS besteht aus folgenden Domains und IPs in der Form der dargestellten Baumstruktur:

```
Baumstruktur:
(0) root 
    (1) telematik [127.0.0.12]
        (2) switch.telematik [127.0.0.13]
            (3) www.switch.telematik [127.0.0.21]
            (3) mail.switch.telematik [127.0.0.22]
        (2) router.telematik [27.0.0.14]
            (3) news.router.telematik [127.0.0.23]
            (3) shop.router.telematik [127.0.0.24]
    (1) fuberlin [127.0.0.15]
        (2) homework.fuberlin [127.0.0.16]
            (3) easy.homework.fuberlin [127.0.0.25]
            (3) hard.homework.fuberlin [127.0.0.26]
        (2) pcpools.fuberlin [127.0.0.17]
            (3) linux.pcpools.fuberlin [127.0.0.27]
            (3) macos.pcpools.fuberlin [127.0.0.28]
            (3) windows.pcpools.fuberlin [127.0.0.29]
```

### Zone files
- Wir benutzen *zone files* um für jeden Nameserver `DnsServer` seine Kinder innerhalb der Baumstruktur sowie deren Records abzuspeichern.
- Durch das Attribut `DnsServer.zone_file` erlangt ein Nameserver auf sein eigenes *zone file* Zugriff. 
- Die Gesamtheit aller zone-files ergibt dann letztlich die oben dargestellte Baumstruktur. 
Das *zone file* `telematik.zone` für den Nameserver *telematik* sieht zum Beispiel so aus:
```
switch.telematik;300 IN NS 127.0.0.13
router.telematik;300 IN NS 127.0.0.14
```

### DNS Format
- Die Klasse `DnsFormat` enthält alle aus der Aufgabenstellung vorgegebenen DNS-Flags. 
- Instanzen von `DnsFormat` werden von den Klassen `StubResolver`, `RecursiveResolver` und `DnsServer` als `json`-String hin- und hergesendet. 
- Die vorgebenen Flags werden in *Request* mit `DnsFormatRequest` und *Response* mit `DnsFormatResponse` unterteilt.

```
Unser DNS Format dargestellt als JSON

dns_format = {
    "request": {
        "dns.flags.recdesired": Bool,    # True <-> recursion should be used by the server
        "dns.qry.name": str,             # requested name
        "dns.qry.type": int,             # requested type: A=1, NS=2, Invalid=0
    }
    "response": {
        "dns.flags.response": Bool,      # True <-> a result was found
        "dns.flags.rcode": int,          # response code, more information see above at rcodes
        "dns.count.answers": int,        # count of answers
        "dns.flags.authoritative": Bool, # True <-> auth. DNS server |  False <-> rec. DNS server
        "dns.a": str,                    # ip adress
        "dns.ns": str,                   # name of ns server if existing
        "dns.resp.ttl": int              # TTL of the record
    }
}

```

### Paralelle Ausführung
- Für alle Nameserver `DnsServer` werden Threads genutzt. 
- Dadurch wird ein parallele Ausführung dieser Instanzen gewährleistet.


## 2.2. Lokale Namensauflösung
### Stub Resolver
1. Senden
    - Der Stub-Resolver `StubResolver` sendet eine Anfrage an `RecursiveResolver`, der diese empfängt. 
    - Die Anfrage ist in zwei Bestandteile unterteilt: (a) aufzulösende Domain (b) Record-Typ. 
    - Eine beispielhafte Anfrage vom `StubResolver` sieht so aus: *switch.telematik NS*
2. Empfangen
    - `StubResolver` empfängt Antwort von `RecursiveResolver`
3. Ausgeben
    - Nach Empfang der Antwort vom `RecursiveResolver` wird die Antwort ausgegeben.

### Recursive Resolver
1. Empfangen
    - Der `RecursiveResolver` empfängt die Anfrage vom `StubResolver`. 
    - Die Anfrage wird in ein passendes `DnsFormat` überführt, das bestimmte Flags für *Request* und *Response* bereithält.
2. Namensauflösung durch Rekursion
    - Der DNS-Tree wird durchlaufen,  indem der `RecurisveResolver` die Anfrage zuerst zum *root*-Nameserver sendet. 
    - Die Antwort von *root* führt dann entweder zum Rekursionsanker oder einem weiteren Rekursionsschritt. 
    - Falls die Rekursion bis zu einem Blatt führt und die Anfrage nicht aufgelöst werden kann, terminiert die Rekursion.
3. Antwort zurücksenden 
    - Die in der Rekursion ermittelte Antwort wird als `DnsFormat` an den `StubResolver` zurückgesendet

### Nameservers
1. Empfangen
    - Jeder Nameserver `DnsServer` läuft in einem eigenen Thread und wartet mithilfe von Polling auf eine Anfrage von `RecursiveResolver`.  
    - Insgesamt laufen lokal 7 Threads - alle Server auf Baumebene (0), (1) und (2). 
2. Namensauflösung durch zone-file
    - Erhält einer der `DnsServer` eine Anfrage, versucht er diese aufzulösen mit `DnsServer.resolve_qry()`. 
    - Hier existieren mehrere Fälle (ns = angefragter nameserver):
        1. [Rekursionsanker] ns ist root & root wird gesucht
        2. [Rekursionsanker] ns kennt ein direktes Kind, das gesucht wird
        4. [Rekursionsanker] ns kennt kein Kind, das gesucht wird und auch kein Kind mit passenden Suffix
        3. [Rekursionsschritt] ns kennt ein Kind mit passenden Suffix der gesuchten Domain
3. Antwort zurücksenden 
    - Die ermittelte Antwort wird als `DnsFormat` an den `RecursiveResolver` zurückgesendet

## 2.3. Cache
`TODO Lukas`

## 2.4. WebProxy
`TODO Viki`


# 3. Team & Arbeitsaufteilung

**Legende:**
- Leo (Leo TODO)
- Leslie (Leslie Hoferichter)
- Lukas (Lukas Ludwig) 
- Joel (Joel Heuer)
- Viktoriya (Viktoriya Kraleva)


| Aufgabe      | Beteiligte Personen |
| ----------- | ----------- |
| Milestone (a) | Leo, Leslie, Joel |
| Milestone (b) | Leo, Leslie, Joel |
| Milestone (c) | Lukas |
| Milestone (d) | Viktoriya |
| Management    | Leo, Leslie, Joel |
| Dokumentation | Leo, Leslie, Lukas, Joel, Viktoriya |





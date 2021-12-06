#!/bin/bash


# run with: chmod u+x run.sh && ./run.sh
# check which threads are running: ps -fA | grep python
# pkill -9 -f src/dns_server.py && pkill -9 -f src/recursive_resolver.py && pkill -9 -f src/stub_resolver.py    
# pkill -9 -f src/dns_server.py 
# pkill -9 -f src/recursive_resolver.py
# pkill -9 -f src/stub_resolver.py
# pkill -9 -f src/http_server.py
# pkill -9 -f src/http_proxy.py


# kill all processes of previous runs to clear addresses
pkill -9 -f "^python3 src/.*"

# start rec. resolver & nameservers
python3 src/recursive_resolver.py &
python3 src/dns_server.py  & 
python3 src/http_server.py  & 
python3 src/http_proxy.py  & 


# start stub_resolver
sleep 1
python3 src/stub_resolver.py  &

# wait for execution


sleep 3
echo Press [q] + [Enter] to stop execution.

while true
do
    read ipt

    if [[ $ipt == "Q" || $ipt == "q" ]]; then
        pkill -9 -f "^python3 src/.*"
        break 

    else
        echo 
    fi
done




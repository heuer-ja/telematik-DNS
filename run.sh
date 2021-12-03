#!/bin/bash


# run with: chmod u+x run.sh && ./run.sh
# check which threads are running: ps -fA | grep python


# kill all processes of previous runs to clear addresses
# pkill -9 -f src/dns_server.py && pkill -9 -f src/recursive_resolver.py && pkill -9 -f src/stub_resolver.py
pkill -9 -f src/dns_server.py 
pkill -9 -f src/recursive_resolver.py
pkill -9 -f src/stub_resolver.py

# start rec. resolver & nameservers
python3 src/recursive_resolver.py &
python3 src/dns_server.py  & 

# start stub_resolver
sleep 1
python3 src/stub_resolver.py  &

# wait for execution
wait


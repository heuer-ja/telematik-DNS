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




# wait for execution
sleep 3

while true
do
    read -p "
    What do you want to do:
    [q] : terminate program
    [1] : test recursive resolver
    [2] : test cache
    [3] : test http proxy
    " -n 1 -r
    echo 

    case $REPLY in 
        "q" | "Q")
            pkill -9 -f "^python3 src/.*"
            break
            ;;
        "1")
            python3 src/stub_resolver.py 1 &
            sleep 3
            ;;
        "2")
            python3 src/stub_resolver.py 2 &
            sleep 3
            ;;
        "3")
            python3 src/stub_resolver.py 3 &
            sleep 3
            ;;
        *)
        ;;
    esac

done




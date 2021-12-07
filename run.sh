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


echo "
#####        ##     ##    ########
##  ###      ##     ##   ###
##    ###    ###    ##   ##
##      ##   ## #   ##   ##
##      ##   ##  #  ##     ######
##      ##   ##   # ##          ##   
##    ###    ##    ###          ##
##  ###      ##     ##         ###
#####        ##     ##   ########
"

# start rec. resolver & nameservers
python3 src/dns_server.py  & 
python3 src/http_server.py  & 
python3 src/http_proxy.py  & 

# wait for execution
sleep 1
echo "..."
sleep 2
green=`tput setaf 2`
yellow=`tput setaf 3`
magenta=`tput setaf 5`

reset=`tput sgr0`

while true
do
    read -p "
    Colors:
    $green[green]  - stub resolver$reset
    $yellow[yellow] - recursive resolver $reset
    $magenta[purple] - name servers $reset

    What do you want to do:
    [q] : terminate program
    [1] : test recursive resolver       (8 exemplary queries | WARNING: a lot of prints)
    [2] : test cache                    (same name is searched 2x)
    [3] : test http proxy               (opens your browser)
    [4] : test your own query           (e.g. 'switch.telematik A')
    " -n 1 -r
    echo 

    pkill -9 -f src/recursive_resolver.py

    case $REPLY in 
        "q"|"Q")
            pkill -9 -f "^python3 src/.*"
            break
            ;;
        "1")
            python3 src/recursive_resolver.py &
            sleep 3
            python3 src/stub_resolver.py 1 &
            sleep 10
            ;;
        "2")
            python3 src/recursive_resolver.py &
            sleep 3
            python3 src/stub_resolver.py 2 &
            sleep 5
            ;;
        "3")
            python3 src/recursive_resolver.py &
            sleep 3
            python3 src/stub_resolver.py 3 &
            sleep 10
            ;;

        "4") 
            python3 src/recursive_resolver.py &
            sleep 3
            read -p "Your Query [name] [record type]: " qry
            echo $qry
            python3 src/stub_resolver.py 4 $qry  $

            sleep 3

            while :  ; 
            do 
                read -p "Another Query? [Y]/[N]" -n 1 -r 
                echo 
                case $REPLY in  
                    "y"|"Y") 
                        read -p "Your Query [name] [record type]: " qry
                        echo
                        python3 src/stub_resolver.py 4 $qry $
                        sleep 3
                        ;;
                    *) 
                        break
                        ;; 
                esac

            done 

            ;;
        *)
        ;;
    esac
done
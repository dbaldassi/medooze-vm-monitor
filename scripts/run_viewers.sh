#!/bin/bash

(jscli cmd.json -d | (wscli client monitor -p 9000 -s -t viewer_launcher 2> /dev/null > ws_fifo)) &
# wscli client monitor -p 9000 -s -t viewer_launcher 2> /dev/null > ws_fifo &

while true
do
    if read msg; then
	echo "Received  : $(echo $msg | jscli -p)" 
	if [ "$(echo $msg | jscli --get cmd | tr -d \")" == "env" ]
	then
	    echo "Setting up new environment"
	    export MEDOOZE_HOST=$(echo $msg | jscli --get medooze_host | tr -d \")
	    export MEDOOZE_PORT=$(echo $msg | jscli --get medooze_port)
	    export MONITOR_HOST=$(echo $msg | jscli --get monitor_host | tr -d \")
	    export MONITOR_PORT=$(echo $msg | jscli --get monitor_port)

	    echo "MEDOOZE_HOST=$MEDOOZE_HOST;MEDOOZE_PORT=$MEDOOZE_PORT;MONITOR_HOST=$MONITOR_HOST;MONITOR_PORT=$MONITOR_PORT"
	fi

	if [ "$(echo $msg | jscli --get cmd | tr -d \")" == "run" ]
	then
	    COUNT=$(echo $msg | jscli --get count)
	    echo "Running $COUNT viewer(s)"
	    
	    for i in $(seq 1 $COUNT)
	    do
		./vm-native-viewer/build/vmviewer &
	    done
	fi

	if [ "$(echo $msg | jscli --get cmd | tr -d \")" == "stop" ]
	then
	    echo "Stopping all viewers"
	    pkill vmviewer
	fi
	
    fi
done < ws_fifo

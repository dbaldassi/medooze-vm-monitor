#!/bin/bash

echo "Stop running medooze"
virsh shutdown medooze

while [ $? -eq 0 ]
do
    echo "Waiting for medooze to stop"
    sleep 20
    virsh shutdown medooze
done

echo "Start new medooze"
virsh start medooze
echo "Wait 10secs to start"
sleep 20

echo "Config slice"
./config_slice.sh

echo "Run node"
node . $@

#!/bin/bash

REPET=20
SCENARIO=("ballooning" "reclaim-reduction")

for scenar in ${SCENARIO[@]}
do
    for i in $(seq 1 $REPET)
    do
		export LIBVIRT_DEFAULT_URI=qemu:///system
		echo "Stop running medooze"
		su tobias -c "virsh shutdown medooze"

		while [ $? -eq 0 ]
		do
			echo "Waiting for medooze to stop"
			sleep 20
			su tobias -c "virsh shutdown medooze"
		done

		echo "Start new medooze"
		su tobias -c "virsh start medooze"

		while [ -z "$(find /sys/fs/cgroup/machine.slice/ -name "*medooze.scope")" ]
		do
			echo "Waiting for slice to be created"
			sleep 1
		done
	
		echo "Config slice"
		./config_slice.sh

		echo "Wait for system to boot"
		sleep 10

		echo "Run node"
		su tobias -c "source ~/.bashrc; node . $scenar"
    done
    
    cd results/$(jsoncli scenario/$scenar.json --get name | tr -d \")
    su tobias -c "../../scripts/average_exp.py"
    cd - 
done

date

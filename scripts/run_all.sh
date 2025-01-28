#!/bin/bash

REPET=5
SCENARIO=("reduction-viewers" "ballooning-viewers" "reclaim-reduction-viewers")
# SCENARIO=("reclaim-reduction" "ballooning" "reduction")
VIEWERS=(10 45 70)

export LIBVIRT_DEFAULT_URI=qemu:///system

restart_vm() {
	echo "Stop running medooze"
	su tobias -c "virsh shutdown medooze"
	
	while [ $? -eq 0 ] # Run until there is an error because you can shutdown a domain not active
	do
		echo "Waiting for medooze to stop"
		sleep 20
		su tobias -c "virsh shutdown medooze"
	done

	echo "Start new medooze"
	su tobias -c "virsh start medooze"

	# if the shut off was not complete
	while [ $? -ne 0 ]
	do
		echo "Medooze was not shut off completly, retrying in 10secs"
		sleep 10
		su tobias -c "virsh start medooze"
	done

	while [ -z "$(find /sys/fs/cgroup/machine.slice/ -name "*medooze.scope")" ]
	do
		echo "Waiting for slice to be created"
		sleep 1
	done
	
	echo "Config slice"
	./config_slice.sh

	echo "Wait for system to boot"
	sleep 10
}

for scenar in ${SCENARIO[@]}
do
    for i in $(seq 1 $REPET)
    do
		for viewer in ${VIEWERS[@]}
		do
	    	restart_vm

	    	echo "Run node"
	    	su tobias -c "source ~/.bashrc; node . $scenar num_viewers:$viewer"
	    	# su tobias -c "source ~/.bashrc; node . $scenar"
		done
    done
    
    # cd results/$(jsoncli scenario/$scenar.json --get name | tr -d \")
    # su tobias -c "../../scripts/average_exp.py"
    # cd - 
done

date

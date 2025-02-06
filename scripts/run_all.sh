#!/bin/bash

REPET=10
# SCENARIO=("normal-viewers")
# SCENARIO=("spawn-cgroup-reclaim" "spawn-cgroup-max" "spawn-balloon")
SCENARIO=("max2500")
VIEWERS=(10 45 70)
# VIEWERS=(10)

export LIBVIRT_DEFAULT_URI=qemu:///system

PROGRESS_HOST=134.59.133.57
PROGRESS_PORT=9001

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

run_with_viewers() {
    for scenar in ${SCENARIO[@]}
    do
	for i in $(seq 1 $REPET)
	do
	    for viewer in ${VIEWERS[@]}
	    do
		curl -k -d "name=$scenar-$i" -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/new
	    done
	done
    done

    curl -k -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/start

    for scenar in ${SCENARIO[@]}
    do
	for i in $(seq 1 $REPET)
	do
	    for viewer in ${VIEWERS[@]}
	    do
		restart_vm
		echo "Run node"
		su tobias -c "source ~/.bashrc; node . $scenar num_viewers:$viewer"
		curl -k -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/next
	    done
	done
    done
}

run() {
    for scenar in ${SCENARIO[@]}
    do
	for i in $(seq 1 $REPET)
	do
	    curl -k -d "name=$scenar-$i" -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/new
	done
    done

    curl -k -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/start

    for scenar in ${SCENARIO[@]}
    do
	for i in $(seq 1 $REPET)
	do
	    restart_vm
	    echo "Run node"
	    su tobias -c "source ~/.bashrc; node . $scenar num_viewers:$viewer"
	    curl -k -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/next
	done
	
	cd results/$(jsoncli scenario/$scenar.json --get name | tr -d \")
	su tobias -c "../../scripts/average_exp.py"
	cd - 
    done
}

trap_sigint() {
    curl -k -d "code=1" -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/stop
    exit 1
}

curl -k -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/reset

trap 'trap_sigint' INT

run
# run_with_viewers

curl -k -d "code=0" -X POST https://$PROGRESS_HOST:$PROGRESS_PORT/stop

date

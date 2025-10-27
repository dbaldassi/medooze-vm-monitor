#!/bin/bash

SCRIPT_DIR=/home/these/Documents/vm-project/medooze-vm-monitor/scripts

function do_it {
    # rm *_average*
    # for j in $(ls)
    # do
    # 	$SCRIPT_DIR/uniformize_room.py $j
    # done
    # $SCRIPT_DIR/average_room.py
    $SCRIPT_DIR/plot_room.py *_average.csv
}

for i in $(find . -name "room")
do
    cd $i
    do_it
    cd -
done

for i in $(find . -name "room1")
do
    cd $i
    do_it
    cd -
done

here=$(pwd)

for i in $(find . -name "rooms")
do
    echo $here
    cd $i

    if [ -d "room1" ]; then
	for room in $(ls -d room*)
	do
	    cd $room
	    do_it
	    cd ..
	done
    else
	do_it
    fi
    
    cd $here
done

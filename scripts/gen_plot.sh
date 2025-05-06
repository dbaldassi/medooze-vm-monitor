#!/bin/bash

INDICATORS=("avg" "median")

for i in $@
do
    echo $i
    for indicator in ${INDICATORS[@]}
    do
        # memory x pressure
        # ./scripts/plot.py $i $indicator TIME MEMORY_USED,MEMORY_FREE,MEMORY_MAX,SWAP,VM_MEMORY_USAGE,VM_MEMORY_FREE MEMORY_PRESSURE_AVG10
	    ./scripts/plot.py $i $indicator TIME MEMORY_USED,SWAP,VM_MEMORY_USAGE MEMORY_PRESSURE_AVG10
        # bitrate x delays
        ./scripts/plot.py $i $indicator TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY
        # bitrate x fps
        ./scripts/plot.py $i $indicator TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_FPS,VIEWER_FPS
        # cpu
        ./scripts/plot.py $i $indicator TIME VM_CPU_USAGE
        # RIDS for simulcast
        ./scripts/plot.py $i $indicator TIME VIEWER_RID_H,VIEWER_RID_M,VIEWER_RID_L
        # Virsh stats
        ./scripts/plot.py $i $indicator TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE
        # Viewer count
        ./scripts/plot.py $i $indicator TIME VIEWER_COUNT
    done
done

STATS=("PUBLISHER_BITRATE" "MEMORY_PRESSURE_AVG10" "VIRSH_SWAP_OUT" "SWAP" "VM_CPU_USAGE" "VIEWER_COUNT")

for i in $@
do
    echo $i
    for stat in ${STATS[@]}
    do
        ./scripts/plot.py $i avg,1stq,median,3rdq,min,max TIME $stat
    done
done

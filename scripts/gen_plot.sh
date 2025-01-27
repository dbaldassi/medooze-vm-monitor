#!/bin/bash

for i in $@
do
    # memory x pressure
    ./scripts/plot.py $i TIME MEMORY_USED,MEMORY_FREE,MEMORY_MAX,SWAP,VM_MEMORY_USAGE,VM_MEMORY_FREE MEMORY_PRESSURE_AVG10
    # bitrate x delays
    ./scripts/plot.py $i TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY
    # bitrate x fps
    ./scripts/plot.py $i TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_FPS,VIEWER_FPS
    # cpu
    ./scripts/plot.py $i TIME VM_CPU_USAGE
    # RIDS for simulcast
    ./scripts/plot.py $i TIME VIEWER_RID_H,VIEWER_RID_M,VIEWER_RID_L
    # Virsh stats
    ./scripts/plot.py $i TIME VIRSH_ACTUAL,VIRSH_UNUSED,VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE,MEMORY_USED MEMORY_PRESSURE_AVG10
    # Viewer count
    ./scripts/plot.py $i TIME VIEWER_COUNT
done

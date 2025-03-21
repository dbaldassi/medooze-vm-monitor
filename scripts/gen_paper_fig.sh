#!/bin/bash

# legend location
BEST=0
UPPER_RIGHT=1
UPPER_LEFT=2
LOWER_LEFT=3
LOWER_RIGHT=4
RIGHT=5
CENTER_LEFT=6
CENTER_RIGHT=7
LOWER_CENTER=8
UPPER_CENTER=9
CENTER=10

function move_files() {
    SRC=$1
    DEST=$2

    mv $SRC/*2_1.pdf $DEST/2_1
    mv $SRC/*1_1.pdf $DEST/1_1
}

# create file tree

# sfu mem
mkdir -p figures/sfu-memory/2_1
mkdir -p figures/sfu-memory/1_1

# progressive reduction
mkdir -p figures/progressive-reduction/ballooning/2_1
mkdir -p figures/progressive-reduction/ballooning/1_1
mkdir -p figures/progressive-reduction/cgroups-max/2_1
mkdir -p figures/progressive-reduction/cgroups-max/1_1
mkdir -p figures/progressive-reduction/cgroups-reclaim/2_1
mkdir -p figures/progressive-reduction/cgroups-reclaim/1_1
mkdir -p figures/progressive-reduction/all/2_1
mkdir -p figures/progressive-reduction/all/1_1

# one step closer
mkdir -p figures/steps/2_1
mkdir -p figures/steps/1_1

# pid regulation
mkdir -p figures/regulation/ballooning/scenario1/2_1
mkdir -p figures/regulation/ballooning/scenario1/1_1
mkdir -p figures/regulation/ballooning/scenario2/2_1
mkdir -p figures/regulation/ballooning/scenario2/1_1

# viewer burst
mkdir -p figures/viewer-burst/ballooning/2_1
mkdir -p figures/viewer-burst/ballooning/1_1
mkdir -p figures/viewer-burst/cgroups/2_1
mkdir -p figures/viewer-burst/cgroups/1_1
mkdir -p figures/viewer-burst/all/2_1
mkdir -p figures/viewer-burst/all/1_1

# save path
root_wd=$PWD
plot_exe=$root_wd/scripts/plot.py
boxplot_exe=$root_wd/scripts/line-step.py
sfu_mem_exe=$root_wd/scripts/sfu_memory.py

# start generate pics

# progressive reduction
# cd $root_wd/results/ok/reduction-stable

# balloon_avg_file=ballooning-simulcast-vp8/ballooning-simulcast-vp8_2025-02-04-13-37-49_average_20.csv
# reclaim_avg_file=cgroups-reclaim/cgroups-reclaim_2025-02-19-23-59-01_average_20.csv
# max_avg_file=cgroups-max-reduction-async/cgroups-max-reduction-simulcast-vp8_2025-02-04-13-37-50_average_20.csv

# $plot_exe $balloon_avg_file avg TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE MEMORY_PRESSURE_AVG10 [50,380]
# move_files ballooning-simulcast-vp8 $root_wd/figures/progressive-reduction/ballooning

# $plot_exe $balloon_avg_file,$max_avg_file,$reclaim_avg_file avg TIME PUBLISHER_BITRATE PUBLISHER_RTT loc=$LOWER_RIGHT
# move_files . $root_wd/figures/progressive-reduction/all

# $plot_exe $max_avg_file avg TIME MEMORY_USED,MEMORY_MAX,SWAP,VM_MEMORY_USAGE MEMORY_PRESSURE_AVG10 [84,200]
# move_files cgroups-max-reduction-async $root_wd/figures/progressive-reduction/cgroups-max

# $plot_exe $reclaim_avg_file avg TIME MEMORY_USED,VM_MEMORY_USAGE,SWAP MEMORY_PRESSURE_AVG10 [50,200]
# move_files cgroups-reclaim $root_wd/figures/progressive-reduction/cgroups-reclaim

# # one step closer
# cd $root_wd/results/ok/one-step-closer

# $boxplot_exe cgroups-max cgroups-reclaim ballooning
# move_files . $root_wd/figures/steps

# # viewer burst
# cd $root_wd/results/ok/viewer-burst-no-increase

# balloon_avg_file=ballooning/ballooning-lowthresh-viewers70-thresh50-increase0/ballooning-lowthresh-viewers70-thresh50-increase0_2025-02-13-13-45-34_average_5.csv
# reclaim_avg_file=cgroups-reclaim/cgroups-reclaim-viewersburst70-thresh50-increase0/cgroups-reclaim-viewersburst70-thresh50-increase0_2025-02-18-15-43-31_average_5.csv
# max_avg_file=cgroups-max/cgroups-max-reduction-viewers70-thresh50-increase0/cgroups-max-reduction-viewers70-thresh50-increase0_2025-02-18-15-43-20_average_5.csv

# balloon_dir=ballooning/ballooning-lowthresh-viewers70-thresh50-increase0
# reclaim_dir=cgroups-reclaim/cgroups-reclaim-viewersburst70-thresh50-increase0
# max_dir=cgroups-max/cgroups-max-reduction-viewers70-thresh50-increase0

# $plot_exe $balloon_avg_file avg TIME VIRSH_AVAILABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE [320,450]
# move_files $balloon_dir $root_wd/figures/viewer-burst/ballooning

# $plot_exe $max_avg_file avg TIME MEMORY_USED,MEMORY_MAX,SWAP,VM_MEMORY_USAGE MEMORY_PRESSURE_AVG10 [320,450] loc=$UPPER_LEFT
# move_files $max_dir $root_wd/figures/viewer-burst/cgroups

# $plot_exe $balloon_avg_file,$max_avg_file,$reclaim_avg_file avg TIME PUBLISHER_BITRATE [320,450] loc=$LOWER_LEFT
# move_files ballooning $root_wd/figures/viewer-burst/all

# # pid regul
# # ballooning - scenario 1
# cd $root_wd/results/balloon-viewersburst70-thresh200-pid
# balloon_avg_file=balloon-viewersburst70-thresh200-pid_2025-03-05-16-56-17_average_10.csv

# $plot_exe $balloon_avg_file avg TIME VM_MEMORY_USAGE,VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT [50,230]
# $plot_exe $balloon_avg_file avg TIME PUBLISHER_BITRATE PUBLISHER_RTT loc=$CENTER_RIGHT

# balloon_avg_file=alone_2025-03-06-10-56-07_average_1.csv
# $plot_exe $balloon_avg_file avg TIME VIRSH_AVAILABLE,VIRSH_USABLE [55,90]
# $plot_exe $balloon_avg_file avg TIME VIRSH_USABLE,VIRSH_AVAILABLE [170,240] loc=$CENTER_RIGHT

# move_files . $root_wd/figures/regulation/ballooning/scenario1

# # balooning - scenario 2
# cd $root_wd/results/balloon-process-viewersburst20-thresh200-pid
# balloon_avg_file=balloon-process-viewersburst20-thresh200-pid_2025-03-06-10-25-48_average_10.csv

# $plot_exe $balloon_avg_file avg TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE [1,270]

# move_files . $root_wd/figures/regulation/ballooning/scenario2 

# sfu mem
cd $root_wd/results/nothing

$sfu_mem_exe
move_files . $root_wd/figures/sfu-memory


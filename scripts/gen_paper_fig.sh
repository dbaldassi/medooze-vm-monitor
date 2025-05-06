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
OUT_TOP=11

function move_files() {
    SRC=$1
    DEST=$2

    # mv $SRC/*2_1.pdf $DEST/2_1
    # mv $SRC/*1_1.pdf $DEST/1_1
    mv $SRC/*.pdf $DEST/ieee
}

# create file tree

# sfu mem
# mkdir -p figures/sfu-memory/2_1
# mkdir -p figures/sfu-memory/1_1

# progressive reduction
# mkdir -p figures/progressive-reduction/ballooning/2_1
# mkdir -p figures/progressive-reduction/ballooning/1_1
mkdir -p figures/progressive-reduction/cgroups-max/2_1
mkdir -p figures/progressive-reduction/cgroups-max/1_1
mkdir -p figures/progressive-reduction/cgroups-max/ieee
mkdir -p figures/progressive-reduction/cgroups-reclaim/2_1
mkdir -p figures/progressive-reduction/cgroups-reclaim/1_1
mkdir -p figures/progressive-reduction/cgroups-reclaim/ieee
mkdir -p figures/progressive-reduction/all/2_1
mkdir -p figures/progressive-reduction/all/1_1
mkdir -p figures/progressive-reduction/all/ieee

# one step closer
mkdir -p figures/steps/2_1
mkdir -p figures/steps/1_1
mkdir -p figures/steps/ieee

# pid regulation
mkdir -p figures/regulation/ballooning/regul-par20viewers/2_1
mkdir -p figures/regulation/ballooning/regul-par20viewers/1_1
mkdir -p figures/regulation/ballooning/regul-par20viewers/ieee
mkdir -p figures/regulation/baseline/regul-par20viewers/2_1
mkdir -p figures/regulation/baseline/regul-par20viewers/1_1
mkdir -p figures/regulation/baseline/regul-par20viewers/ieee
mkdir -p figures/regulation/cgroups/regul-par20viewers/2_1
mkdir -p figures/regulation/cgroups/regul-par20viewers/1_1
mkdir -p figures/regulation/cgroups/regul-par20viewers/ieee

# viewer burst
# mkdir -p figures/viewer-burst/ballooning/2_1
# mkdir -p figures/viewer-burst/ballooning/1_1
# mkdir -p figures/viewer-burst/cgroups/2_1
# mkdir -p figures/viewer-burst/cgroups/1_1
# mkdir -p figures/viewer-burst/all/2_1
# mkdir -p figures/viewer-burst/all/1_1

# save path
root_wd=$PWD
plot_exe=$root_wd/scripts/plot.py
cgroup_plot_exe=$root_wd/scripts/plot_cgroup.py
boxplot_exe=$root_wd/scripts/line-step.py
sfu_mem_exe=$root_wd/scripts/sfu_memory.py

# start generate pics

# # progressive reduction
# cd $root_wd/results/cgroups-stats/cgroups-max-reduction/cgroups_stats
# avg_file=cgroups-max_stats_2025-03-19-11-02-01_average_10.csv
# avg_reclaim=cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv 

# $cgroup_plot_exe $avg_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/figures/progressive-reduction/cgroups-max

# cd ../../cgroups-reclaim/cgroup_stats
# $cgroup_plot_exe $avg_reclaim TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/figures/progressive-reduction/cgroups-reclaim

# cd ../../

# $cgroup_plot_exe cgroups-max-reduction/cgroups_stats/cgroups-max_stats_2025-03-19-11-02-01_average_10.csv,cgroups-reclaim/cgroup_stats/cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv TIME PGMAJFAULT loc=$LOWER_RIGHT
# cd cgroups-max-reduction
# move_files . $root_wd/figures/progressive-reduction/all

# # regulation

INDICATOR=median

## cgroups

cd $root_wd/results/double/cgroups-regul-stddev-30-viewer-double-increase-par20
avg_bitrate_file=cgroups-regul-stddev-30-viewer-double-increase-par20_2025-05-01-18-59-48_average_10.csv
avg_cgroup_file=cgroup_stats_2025-05-01-18-58-18_average_10.csv

$plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY   loc=$LOWER_CENTER leg_col=2
move_files . $root_wd/figures/regulation/cgroups/regul-par20viewers

cd cgroup_stats

$cgroup_plot_exe $avg_cgroup_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
move_files . $root_wd/figures/regulation/cgroups/regul-par20viewers

# ## ballooning
# cd $root_wd/results/double/balloon-pid-viewer-increase-double-longer-par20
# avg_bitrate_file=balloon-pid-viewer-increase-double-longer-par20_2025-05-01-19-01-11_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE ylim=4400
# move_files . $root_wd/figures/regulation/ballooning/regul-par20viewers

# ## baseline
# cd $root_wd/results/double/noregul-viewer-increase-double-longer-par20
# avg_bitrate_file=noregul-viewer-increase-double-longer-par20_2025-05-01-19-03-18_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 annotate
# move_files . $root_wd/figures/regulation/baseline/regul-par20viewers

# # one step closer
# cd $root_wd/results/ok/one-step-closer

# $boxplot_exe cgroups-max cgroups-reclaim ballooning
# move_files . $root_wd/figures/steps


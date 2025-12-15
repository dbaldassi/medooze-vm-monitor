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
    DST=$2

    echo "DST=$DST"
    # mv $SRC/*2_1.pdf $DEST/2_1
    # mv $SRC/*1_1.pdf $DEST/1_1
    mv $SRC/*.pdf $DST/
}


DEST=figure

# create file tree

# sfu mem
# mkdir -p $DEST/sfu-memory/2_1
# mkdir -p $DEST/sfu-memory/1_1

# progressive reduction
# mkdir -p $DEST/progressive-reduction/ballooning/2_1
# mkdir -p $DEST/progressive-reduction/ballooning/1_1
mkdir -p $DEST/progressive-reduction/cgroups-max/2_1
mkdir -p $DEST/progressive-reduction/cgroups-max/1_1
mkdir -p $DEST/progressive-reduction/cgroups-max/ieee
mkdir -p $DEST/progressive-reduction/cgroups-reclaim/2_1
mkdir -p $DEST/progressive-reduction/cgroups-reclaim/1_1
mkdir -p $DEST/progressive-reduction/cgroups-reclaim/ieee
mkdir -p $DEST/progressive-reduction/all/2_1
mkdir -p $DEST/progressive-reduction/all/1_1
mkdir -p $DEST/progressive-reduction/all/ieee

# one step closer
mkdir -p $DEST/steps/2_1
mkdir -p $DEST/steps/1_1
mkdir -p $DEST/steps/ieee

# pid regulation
mkdir -p $DEST/regulation/ballooning/regul-par20viewers/2_1
mkdir -p $DEST/regulation/ballooning/regul-par20viewers/1_1
mkdir -p $DEST/regulation/ballooning/regul-par20viewers/ieee
mkdir -p $DEST/regulation/baseline/regul-par20viewers/2_1
mkdir -p $DEST/regulation/baseline/regul-par20viewers/1_1
mkdir -p $DEST/regulation/baseline/regul-par20viewers/ieee
mkdir -p $DEST/regulation/cgroups/regul-par20viewers/2_1
mkdir -p $DEST/regulation/cgroups/regul-par20viewers/1_1
mkdir -p $DEST/regulation/cgroups/regul-par20viewers/ieee

# visio regulation
mkdir -p $DEST/visio/regulation/ballooning/regul-par20viewers/2_1
mkdir -p $DEST/visio/regulation/ballooning/regul-par20viewers/1_1
mkdir -p $DEST/visio/regulation/ballooning/regul-par20viewers/ieee
mkdir -p $DEST/visio/regulation/baseline/regul-par20viewers/2_1
mkdir -p $DEST/visio/regulation/baseline/regul-par20viewers/1_1
mkdir -p $DEST/visio/regulation/baseline/regul-par20viewers/ieee
mkdir -p $DEST/visio/regulation/cgroups/regul-par20viewers/2_1
mkdir -p $DEST/visio/regulation/cgroups/regul-par20viewers/1_1
mkdir -p $DEST/visio/regulation/cgroups/regul-par20viewers/ieee

# db
mkdir -p $DEST/db/cgroups
mkdir -p $DEST/db/baseline
mkdir -p $DEST/db/ballooning


# viewer burst
# mkdir -p $DEST/viewer-burst/ballooning/2_1
# mkdir -p $DEST/viewer-burst/ballooning/1_1
# mkdir -p $DEST/viewer-burst/cgroups/2_1
# mkdir -p $DEST/viewer-burst/cgroups/1_1
# mkdir -p $DEST/viewer-burst/all/2_1
# mkdir -p $DEST/viewer-burst/all/1_1

# save path
root_wd=$PWD
plot_exe=$root_wd/scripts/plot.py
cgroup_plot_exe=$root_wd/scripts/plot_cgroup.py
boxplot_exe=$root_wd/scripts/line-step.py
sfu_mem_exe=$root_wd/scripts/sfu_memory.py

# start generate pics

# # progressive reduction
# cd $root_wd/results/1ton/cgroups-stats/cgroups-max-reduction/cgroups_stats
# avg_file=cgroups-max_stats_2025-03-19-11-02-01_average_10.csv
# avg_reclaim=cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv 

# $cgroup_plot_exe $avg_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/$DEST/progressive-reduction/cgroups-max

# cd ../../cgroups-reclaim/cgroup_stats
# $cgroup_plot_exe $avg_reclaim TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/$DEST/progressive-reduction/cgroups-reclaim

# cd ../../

# $cgroup_plot_exe cgroups-max-reduction/cgroups_stats/cgroups-max_stats_2025-03-19-11-02-01_average_10.csv,cgroups-reclaim/cgroup_stats/cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv TIME PGMAJFAULT loc=$LOWER_RIGHT
# cd cgroups-max-reduction
# move_files . $root_wd/$DEST/progressive-reduction/all

# $cgroup_plot_exe cgroups-max-reduction/cgroups_stats/cgroups-max_stats_2025-03-19-11-02-01_average_10.csv,cgroups-reclaim/cgroup_stats/cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv TIME PRESSURE_AVG10 # loc=$LOWER_RIGHT

# cd cgroups-max-reduction
# move_files . $root_wd/$DEST/progressive-reduction/all





# cd /home/these/Documents/vm-project/medooze-vm-monitor/results/cgroups-heuristic/cgroups-reclaim-prog-new-100/cgroups

# avg_file=cgroups_2025-10-27-13-45-57_average_10.csv

# $cgroup_plot_exe $avg_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE,INACTIVE_ANON PGMAJFAULT loc=$LOWER_RIGHT

# cd /home/these/Documents/vm-project/medooze-vm-monitor/results/cgroups-heuristic/cgroups-regul-stddev-30-new/cgroups

# avg_file=cgroups_2025-10-27-10-46-33_average_10.csv

# $cgroup_plot_exe $avg_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE,INACTIVE_ANON PGMAJFAULT loc=$UPPER_LEFT

# # # regulation

INDICATOR=median

# # cgroups

# cd $root_wd/results/1ton/double/cgroups-regul-stddev-30-viewer-double-increase-par20
# avg_bitrate_file=cgroups-regul-stddev-30-viewer-double-increase-par20_2025-05-01-18-59-48_average_10.csv
# avg_cgroup_file=cgroup_stats_2025-05-01-18-58-18_average_10.csv

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$CENTER_LEFT annotate # leg_col=2
# # move_files . $root_wd/$DEST/regulation/cgroups/regul-par20viewers

# cd cgroup_stats

# $cgroup_plot_exe $avg_cgroup_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE,INACTIVE_ANON ylim=4400 loc=$LOWER_CENTER leg_col=3 annotate # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/regulation/cgroups/regul-par20viewers

## ballooning
# cd $root_wd/results/1ton/double/balloon-pid-viewer-increase-double-longer-par20
# avg_bitrate_file=balloon-pid-viewer-increase-double-longer-par20_2025-05-01-19-01-11_average_10.csv

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$CENTER_LEFT annotate # leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE  loc=$LOWER_CENTER leg_col=3 annotate # ylim=4400
# move_files . $root_wd/$DEST/regulation/ballooning/regul-par20viewers

# # baseline
# cd $root_wd/results/1ton/double/noregul-viewer-increase-double-longer-par20
# avg_bitrate_file=noregul-viewer-increase-double-longer-par20_2025-05-01-19-03-18_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE  loc=$LOWER_CENTER leg_col=3 annotate # ylim=4400
# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 annotate
# move_files . $root_wd/$DEST/regulation/baseline/regul-par20viewers

# cd cgroup_stats

# avg_file=cgroup_stats_2025-11-25-13-33-52_average_10.csv
# $cgroup_plot_exe $avg_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE,INACTIVE_ANON ylim=4400 loc=$LOWER_CENTER leg_col=3 annotate # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/regulation/baseline/regul-par20viewers

# # delta regul
# cd $root_wd/results/1ton/double/noregul-viewer-increase-double-longer-par20
# avg_baseline=noregul-viewer-increase-double-longer-par20_2025-05-01-19-03-18_average_10.csv
# avg_balloon=$root_wd/results/1ton/double/balloon-pid-viewer-increase-double-longer-par20/balloon-pid-viewer-increase-double-longer-par20_2025-05-01-19-01-11_average_10.csv
# avg_cgroup=$root_wd/results/1ton/double/cgroups-regul-stddev-30-viewer-double-increase-par20/cgroups-regul-stddev-30-viewer-double-increase-par20_2025-05-01-18-59-48_average_10.csv

# $plot_exe $avg_baseline,$avg_balloon,$avg_cgroup $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE,PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 annotate
# move_files . $root_wd/$DEST/regulation/baseline/regul-par20viewers


# redis 

cd results/redis-10-again

# cd baseline-pid-mongodb
# pwd
# file=baseline-pid-mongodb_2025-10-30-15-03-16_average_10.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,VM_MEMORY_USAGE,SWAP,VIRSH_AVAILABLE loc=$LOWER_CENTER leg_col=2 
# # $plot_exe $file $INDICATOR TIME MEMORY_USED,VM_MEMORY_USAGE loc=$LOWER_CENTER [50,250]
# move_files . $root_wd/$DEST/db/baseline

# cd ..

# cd balloon-pid-mongodb

# file=balloon-pid-mongodb_2025-10-30-15-01-13_average_10.csv
# $plot_exe $file $INDICATOR TIME VIRSH_AVAILABLE,VM_MEMORY_USAGE,SWAP loc=$LOWER_LEFT # loc=$LOWER_CENTER # leg_col=2

# cd ..

# cd cgroups-pid-mongodb

# file=cgroups-pid-mongodb_2025-10-30-15-03-33_average_10.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,VM_MEMORY_USAGE,SWAP loc=$LOWER_LEFT # loc=$LOWER_CENTER # leg_col=2

cd $root_wd/results/baseline-pid-mongodb-latest
file=baseline-pid-mongodb-latest_2025-10-31-17-30-58_average_11.csv
$plot_exe $file $INDICATOR TIME MEMORY_USED,VM_MEMORY_USAGE,SWAP,VIRSH_AVAILABLE loc=$LOWER_CENTER leg_col=2 
move_files . $root_wd/$DEST/db/baseline

# cd $root_wd/results/cgroups-pid-mongodb-latest
# file=cgroups-pid-mongodb-latest_2025-10-31-11-11-35_average_11.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,VM_MEMORY_USAGE,SWAP loc=$LOWER_LEFT # loc=$LOWER_CENTER # leg_col=2
# move_files . $root_wd/$DEST/db/cgroups

# cd $root_wd/results/balloon-pid-mongodb-latest-300

# file=balloon-pid-mongodb-latest-300_2025-10-31-16-59-12_average_10.csv
# $plot_exe $file $INDICATOR TIME VIRSH_AVAILABLE,VM_MEMORY_USAGE,SWAP loc=$LOWER_LEFT # loc=$LOWER_CENTER # leg_col=2
# move_files . $root_wd/$DEST/db/ballooning


# # one step closer
# cd $root_wd/results/1ton/ok/one-step-closer

# $boxplot_exe cgroups-reclaim ballooning
# move_files . $root_wd/$DEST/steps

# # visio baseline
# cd $root_wd/results/10-participants/visio-base-10
# avg_bitrate_file=visio-base-10_2025-06-11-12-49-11_average_10.csv

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 # annotate
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE # ylim=4400
# move_files . $root_wd/$DEST/visio/regulation/baseline/regul-par20viewers

# cd cgroups
# avg_cgroup_file=cgroups_2025-09-28-23-45-26_average_10.csv

# $cgroup_plot_exe $avg_cgroup_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/visio/regulation/baseline/regul-par20viewers

# # visio ballooning
# cd $root_wd/results/10-participants/visio-ballooning-regulation-10
# avg_bitrate_file=visio-ballooning-regulation-10_2025-06-11-10-30-45_average_10.csv

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE # ylim=4400
# move_files . $root_wd/$DEST/visio/regulation/ballooning/regul-par20viewers

# # visio cgroups
# cd $root_wd/results/10-participants/visio-reclaim-regulation-10
# avg_bitrate_file=visio-reclaim-regulation-10_2025-06-11-10-33-56_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR # ylim=4400
# move_files . $root_wd/$DEST/visio/regulation/cgroups/regul-par20viewers

# # cd cgroups
# # avg_cgroup_file=cgroups_2025-06-11-10-34-46_average_10.csv

# # $cgroup_plot_exe $avg_cgroup_file TIME RAM_USAGE,ACTIVE_ANON,SWAP_USAGE,INACTIVE_ANON ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/visio/regulation/cgroups/regul-par20viewers

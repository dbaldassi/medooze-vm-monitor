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
    mv $SRC/*.pdf $DST/ieee
}


DEST=figure-fr

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
cd $root_wd/results/1ton/cgroups-stats/cgroups-max-reduction/cgroups_stats
# avg_file=cgroups-max_stats_2025-03-19-11-02-01_average_10.csv
# avg_reclaim=cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv 

# $cgroup_plot_exe $avg_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/$DEST/progressive-reduction/cgroups-max

# cd ../../cgroups-reclaim/cgroup_stats
# $cgroup_plot_exe $avg_reclaim TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE
# move_files . $root_wd/$DEST/progressive-reduction/cgroups-reclaim

cd ../../

# $cgroup_plot_exe cgroups-max-reduction/cgroups_stats/cgroups-max_stats_2025-03-19-11-02-01_average_10.csv,cgroups-reclaim/cgroup_stats/cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv TIME PGMAJFAULT loc=$LOWER_RIGHT
# cd cgroups-max-reduction
# move_files . $root_wd/$DEST/progressive-reduction/all

$cgroup_plot_exe cgroups-max-reduction/cgroups_stats/cgroups-max_stats_2025-03-19-11-02-01_average_10.csv,cgroups-reclaim/cgroup_stats/cgroup-reclaim_stats_2025-03-19-11-05-53_average_10.csv TIME PRESSURE_AVG10 # loc=$LOWER_RIGHT

cd cgroups-max-reduction
move_files . $root_wd/$DEST/progressive-reduction/all

# # regulation

INDICATOR=median

## cgroups

# cd $root_wd/results/1ton/double/cgroups-regul-stddev-30-viewer-double-increase-par20
# avg_bitrate_file=cgroups-regul-stddev-30-viewer-double-increase-par20_2025-05-01-18-59-48_average_10.csv
# avg_cgroup_file=cgroup_stats_2025-05-01-18-58-18_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/regulation/cgroups/regul-par20viewers

# cd cgroup_stats

# $cgroup_plot_exe $avg_cgroup_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/regulation/cgroups/regul-par20viewers

# cd ~/redis-10-again

# cd balloon-pid-mongodb

# file=balloon-pid-mongodb_2025-07-06-17-25-12_average_10.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,SWAP,VM_MEMORY_USAGE loc=$LOWER_CENTER leg_col=2

# cd ..

# cd baseline-pid-mongodb

# file=baseline-pid-mongodb_2025-07-06-17-25-12_average_10.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,SWAP,VM_MEMORY_USAGE loc=$LOWER_CENTER leg_col=2

# cd ..

# cd cgroups-pid-mongodb

# file=cgroups-pid-mongodb_2025-07-06-17-25-13_average_10.csv
# $plot_exe $file $INDICATOR TIME MEMORY_USED,SWAP,VM_MEMORY_USAGE loc=$LOWER_CENTER leg_col=2

# ## ballooning
# cd $root_wd/results/1ton/double/balloon-pid-viewer-increase-double-longer-par20
# avg_bitrate_file=balloon-pid-viewer-increase-double-longer-par20_2025-05-01-19-01-11_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE # ylim=4400
# move_files . $root_wd/$DEST/regulation/ballooning/regul-par20viewers

# ## baseline
# cd $root_wd/results/1ton/double/noregul-viewer-increase-double-longer-par20
# avg_bitrate_file=noregul-viewer-increase-double-longer-par20_2025-05-01-19-03-18_average_10.csv

# $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 annotate
# move_files . $root_wd/$DEST/regulation/baseline/regul-par20viewers

# # one step closer
# cd $root_wd/results//1ton/ok/one-step-closer

# $boxplot_exe cgroups-max cgroups-reclaim ballooning
# move_files . $root_wd/$DEST/steps









# # visio baseline
# cd $root_wd/results/10-participants/visio-base-10
# avg_bitrate_file=visio-base-10_2025-06-11-12-49-11_average_10.csv

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=3 # annotate
# $plot_exe $avg_bitrate_file $INDICATOR TIME VIRSH_AVAILABLE,VIRSH_USABLE,VIRSH_SWAP_OUT,VM_MEMORY_USAGE # ylim=4400
# move_files . $root_wd/$DEST/visio/regulation/baseline/regul-par20viewers

# cd cgroups
# avg_cgroup_file=cgroups_2025-09-28-23-45-26_average_10.csv

# $cgroup_plot_exe $avg_cgroup_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
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

# # $plot_exe $avg_bitrate_file $INDICATOR TIME PUBLISHER_BITRATE,VIEWER_BITRATE PUBLISHER_RTT,VIEWER_DELAY loc=$LOWER_CENTER leg_col=2
# $plot_exe $avg_bitrate_file $INDICATOR # ylim=4400
# move_files . $root_wd/$DEST/visio/regulation/cgroups/regul-par20viewers

# cd cgroups
# avg_cgroup_file=cgroups_2025-06-11-10-34-46_average_10.csv

# $cgroup_plot_exe $avg_cgroup_file TIME ACTIVE_ANON,INACTIVE_ANON,RAM_USAGE,SWAP_USAGE ylim=4400 loc=$UPPER_LEFT # loc=$LOWER_CENTER leg_col=2
# move_files . $root_wd/$DEST/visio/regulation/cgroups/regul-par20viewers

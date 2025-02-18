#!/usr/bin/python3

import sys
import csv
import os
from matplotlib import pyplot as plt

DURATION=0
CPU_AVG=1
PRESSURE_AVG=2
PUBLISHER_BITRATE_AVG=3
VIEWER_BITRATE_AVG=4
PUBLISHER_FPS_AVG=5
VIEWER_FPS_AVG=6
PUBLISHER_RTT_AVG=7
PRESSURE_DURATION=8
PRESSURE_DURATION_AVG=9
PRESSURE_DURATION_PEAK=10
PUBLISHER_COLLAPSE_DURATION=11
PUBLISHER_COLLAPSE_AVG=12
PUBLISHER_COLLAPSE_PEAK=13

LABELS = [ "Duration (s)", "CPU (%)", "Pressure_Stall_Information (PSI)", "Publisher_Bitrate (kbps)", "Viewers_bitrate (kbps)",
           "Publisher_FPS (FPS)", "Viewer_FPS (FPS)", "Publisher_RTT (ms)", 
           "Pressure_duration (s)", "Pressure_average (PSI)", "Pressure_Peak (PSI)",
           "Publisher_Collapse_Duration (s)", "Publisher_Collapse_Bitrate (kbps)", "Publisher_Collapse_peak (kbps)" ]

NUM=PUBLISHER_COLLAPSE_PEAK+1

plt.rc('font', size=18)          # controls default text sizes
plt.rc('axes', titlesize=22)     # fontsize of the axes title
plt.rc('axes', labelsize=22)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=20)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

if __name__ == "__main__":

    increment = []
    all_stats = {}

    for f in os.listdir():
        if(os.path.isdir(f) and "-step-" in f):
            # format csv file name
            avg_file = "{}/average_step.csv".format(f)

            with open(avg_file, 'r') as csv_file:
                # find the increment step value
                split = f.split("-")
                incr = split[split.index('step')+1]
                increment.append(int(incr))

                # load csv file into array
                lines = [ list(map(float, line)) for line in csv.reader(csv_file, delimiter=',') ]

                # put it in dict
                all_stats[incr] = lines

    
    # order increment by numerical value and convert back to str
    increment.sort()
    increment = [ str(i) for i in increment ]

    # reorder stats and convert from dico to array
    all_stats = [ all_stats[incr] for incr in increment ]

    # pixel in inches
    px = 1 / plt.rcParams['figure.dpi']

    # now generates a figure for each stats
    for i in range(NUM):
        fig,ax = plt.subplots(figsize=(1920*px, 960*px)) # 2:1 ratio

        # get current stat for all steps
        # should be a 2d array
        to_plot = [ line[i] for line in all_stats ]

        # plot
        ax.boxplot(to_plot)

        # Set label name
        ax.set_xlabel("Increment (MiB)")
        ax.set_ylabel(LABELS[i].replace("_", " "))
        ax.set_xticklabels(increment)

        ax.grid()

        # Image destination path
        dest_path = "box_{}.png".format(LABELS[i].split(' ')[0])

        # save fig !
        plt.savefig(dest_path)




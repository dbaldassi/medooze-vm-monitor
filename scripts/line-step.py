#!/usr/bin/python3

import sys
import csv
import os
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

plt.rc('font', size=18)          # controls default text sizes
plt.rc('axes', titlesize=22)     # fontsize of the axes title
plt.rc('axes', labelsize=22)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=20)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


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

NUM=PUBLISHER_COLLAPSE_PEAK+1

COLOR={
    "cgroups-max": 'r',
    "ballooning": 'b',
    "cgroups-reclaim": 'g'
}

LABELS = [ "Duration (s)", "CPU (%)", "Pressure_Stall_Information (PSI)", "Publisher_Bitrate (kbps)", "Viewers_bitrate (kbps)",
           "Publisher_FPS (FPS)", "Viewer_FPS (FPS)", "Publisher_RTT (ms)", 
           "Pressure_duration (s)", "Pressure_average (PSI)", "Pressure_Peak (PSI)",
           "Publisher_Collapse_Duration (s)", "Publisher_Collapse_Bitrate (kbps)", "Publisher_Collapse_peak (kbps)" ]

class StatsMethod:
    def __init__(self):
        self.color = None
        self.stats = []
        self.increment = []

def check_no(f, no):
    split = f.split('-')
    last = split[-1]
    for n in no:
        if n == last:
            print(f,last)
            return False
        
    return True

if __name__ == "__main__":
    methods = []
    all_stats = {}

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if not os.path.isdir(sys.argv[i]):
                print("This is not a valid directory", sys.argv[i])
                exit(1)

            methods.append(sys.argv[i])
    else:
        print("Please provide at least one folder")
        exit(1)

    increment_xticks = []
    no = [ "1500", "3000", "2000", "0"]
    # no = []
    for m in methods:
        tmp_stats = {}
        increment = []
        for f in os.listdir(m):
            if(os.path.isdir("{}/{}".format(m,f)) and "-step-" in f and check_no(f, no)):
                # format csv file name
                avg_file = "{}/{}/average_step.csv".format(m,f)

                with open(avg_file, 'r') as csv_file:
                    # find the increment step value
                    split = f.split("-")
                    incr = int(split[split.index('step')+1])
                    increment.append(incr)

                    # load csv file into array
                    lines = [ list(map(float, line)) for line in csv.reader(csv_file, delimiter=',') ]
                    # print(line)

                    # temp, waiting to have 20exp for this one
                    if(m == "cgroups-reclaim"):
                        lines = [[l for l in line for _ in range(2 if len(line) == 10 else 1)] for line in lines]

                    # put it in dict
                    tmp_stats[incr] = lines

        # order increment by numerical value and convert back to str
        increment.sort()

        for i in increment:
            if not i in increment_xticks:
                increment_xticks.append(i)

        s = StatsMethod()
        s.color = COLOR[m]
        s.stats = [ tmp_stats[incr] for incr in increment ]
        s.increment = increment

        all_stats[m] = s

    increment_xticks.sort()
    increment_xticks = [ str(i) for i in increment_xticks]
    # print(increment_xticks)

    # pixel in inches
    px = 1 / plt.rcParams['figure.dpi']


    # now generates a figure for each stats
    for i in range(NUM):
        fig,ax = plt.subplots(figsize=(1920*px, 960*px)) # 2:1 ratio

        # curve for each method
        dfs = []
        for incr in increment_xticks:
            values = {}

            for m in methods:
                stats = all_stats[m]

                if int(incr) in stats.increment:
                    index = stats.increment.index(int(incr))
                    values[m] = stats.stats[index][i].copy()

            # print(values)
            dfs.append(pd.DataFrame(data=values).assign(Size=incr))


        # for m in methods:
            # stats = all_stats[m]
            # get current stat for all steps
            # to_plot = [ sum(line[i]) / len(line[i]) for line in stats.stats ]
            # values.append( pd.DataFrame([line[i] for line in stats.stats ]).assign(Size=m))
            # print(i, m, len(to_plot))
            
            # if(m == "ballooning" and i == DURATION):
            #     dy = to_plot[-1] - to_plot[0]
            #     dx = stats.increment[-1] - stats.increment[0]
            #     a = dy / dx
            #     b = to_plot[-1] - a * stats.increment[-1]
            #     print("{}x + {}".format(a, b))
            # print(to_plot, stats.increment)
            # plot
            # ax.plot(stats.increment, to_plot, "o-", color=stats.color, label=m, linewidth=3)

        concat = pd.concat(dfs)
        to_plot = pd.melt(concat, id_vars=['Size'], var_name=['Method'])  
        # print(to_plot)
        ax = sns.boxplot(x="Size", y="value", hue="Method", data=to_plot, palette=['r', 'g', 'b'])

        # Set label name
        ax.set_xlabel("Size (MiB)")
        ax.set_ylabel(LABELS[i].replace("_", " "))
        # ax.set_xticklabels(increment_xticks)
        # ax.grid()
        # ax.legend()
        

        # Image destination path
        dest_path = "allbox_{}.png".format(LABELS[i].split(' ')[0])
        # save fig !
        plt.savefig(dest_path)



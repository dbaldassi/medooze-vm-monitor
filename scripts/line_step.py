#!/usr/bin/python3

import sys
import csv
import os
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

import scienceplots
import matplotlib

colors = matplotlib.cm.get_cmap('tab20').colors

plt.style.use(['science','ieee'])

plt.rcParams.update({
    "font.size": 16
})

# plt.rc('font', size=40)          # controls default text sizes
# plt.rc('axes', titlesize=44)     # fontsize of the axes title
# plt.rc('axes', labelsize=44)    # fontsize of the x and y labels
# # plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# # plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('legend', fontsize=42)    # legend fontsize
# # plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

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
VIEWER_RID_H_PEAK=14
VIEWER_RID_M_PEAK=15
VIEWER_RID_L_PEAK=16

NUM=VIEWER_RID_L_PEAK+1

FIRST_INACTIVE=0
FIRST_SWAP=1
# ALL_ACTIVE=3
ALL_INACTIVE_TO_ACTIVE=2
ALL_INACTIVE_TO_SWAP=3
ALL_MEMORY_TO_SWAP=4
ACTIVE_SUM=5
ALL_FREE=6

# NUM = ALL_FREE + 1

COLOR={
    "cgroups-max": 'r',
    "ballooning": colors[1],
    "cgroups-reclaim": colors[0]
}

LABELS = [ "Durée (s)", "CPU (\\%)", "Pressure_Stall_Information (PSI)", "Débit_émetteur (kbps)",
           "Débit_récepteur (kbps)",
           "FPS_émetteur (FPS)", "Viewer_FPS (FPS)", "RTT_Émetteur (ms)", 
           "Durée_Pression (s)", "Moyenne_pression (PSI)", "Pic_pression (PSI)",
           "Durée_chute (s)", "Débit_émetteur_chute (kbps)", "Débit_émetteur_chute_pic (kbps)", "Haute_qualité ()",
            "Moyenne_qualité ()", "Basse_qualité ()" ]

# LABELS = [ "Duration (s)", "CPU (\\%)", "Pressure_Stall_Information (PSI)", "Publisher_Bitrate (kbps)",
#            "Viewers_bitrate (kbps)",
#            "Publisher_FPS (FPS)", "Viewer_FPS (FPS)", "Publisher_RTT (ms)", 
#            "Pressure_duration (s)", "Pressure_average (PSI)", "Pressure_Peak (PSI)",
#            "Publisher_Collapse_Duration (s)", "Publisher_Collapse_Bitrate (kbps)", "Publisher_Collapse_peak (kbps)", "High quality ()",
#             "Medium quality ()", "Low quality ()" ]

# LABELS = [ "Active_to_inactive (%)", "First_Swap (%)", "Inactive_to_active (%)", "Inactive_to_swap (%)", "Memory_to_swap (%)", "Active cumulated sum (MiB)", "Free_memory_?? (MiB)"]

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

def process_and_plot(settings):
    methods = settings["reclamation"]
    all_stats = {}

    increment_xticks = []
    no = [ "1500", "3000", "2000", "0"]
    # no = []
    for m in methods:
        tmp_stats = {}
        increment = []
        for f in os.listdir(m):
            if(os.path.isdir("{}/{}".format(m,f)) and "-step-" in f and check_no(f, no)):
                # format csv file name
                avg_file = "{}/{}/average_step_with_rid.csv".format(m,f)

                with open(avg_file, 'r') as csv_file:
                    # find the increment step value
                    split = f.split("-")
                    incr = int(split[-1])
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

    print("Increments found:", increment_xticks)
    print(NUM)

    # fig, ax = plt.subplots()

    # stats = all_stats["cgroups-max"]

    # pressure = np.array([ incr[PRESSURE_AVG] for incr in stats.stats])
    # publisher_bitrate = np.array([ incr[PUBLISHER_BITRATE_AVG] for incr in stats.stats])
    # viewer_bitrate = np.array([ incr[VIEWER_BITRATE_AVG] for incr in stats.stats])

    # # Aplatir le tableau de tableaux `pressure`
    # flattened_pressure = [p for sublist in pressure for p in sublist]
    # flattened_publisher_bitrate = [p for sublist in publisher_bitrate for p in sublist]
    # flattened_viewer_bitrate = [p for sublist in viewer_bitrate for p in sublist]

    # ax.set_xscale('log')
    # # scatter plot 
    # ax.scatter(flattened_pressure, flattened_publisher_bitrate, color='b', label="Publisher Bitrate")
    # # set logarithmic scale

    # # Configurer les étiquettes et la légende
    # plt.xlabel("Memory Pressure (PSI)")
    # plt.ylabel("Bitrate (kbps)")
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=False)

    # plt.savefig("pressure_bitrate_correlation.pdf");
    # plt.close()
    
    # now generates a figure for each stats
    for i in range(NUM):
        # for r in res:
        # fig,ax = plt.subplots(figsize=(r[0]*px, r[1]*px))
        fig,ax = plt.subplots(figsize=(5,5))
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')
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
            dfs.append(pd.DataFrame(data=values).assign(Taille="0" if incr == "1"else incr))


        # for m in methods:
            # stats = all_stats[m]
            # get current stat for all steps
            # to_plot = [ sum(line[i]) / len(line[i]) for line in stats.stats ]
            # if(m == "ballooning" and i == DURATION):
            #     dy = to_plot[-1] - to_plot[0]
            #     dx = stats.increment[-1] - stats.increment[0]
            #     a = dy / dx
            #     b = to_plot[-1] - a * stats.increment[-1]
            #     print("{}x + {}".format(a, b))
            # plot
            # ax.plot(stats.increment, to_plot, "o-", color=stats.color, label=m, linewidth=3)

        concat = pd.concat(dfs)
        to_plot = pd.melt(concat, id_vars=['Taille'], var_name='Method')
        # print(to_plot)
        ax = sns.boxplot(x="Taille", y="value", hue="Method", data=to_plot, palette=[colors[0], colors[1]])

        label =  LABELS[i].replace("_", " ")
        # Set label name
        ax.set_facecolor('none')
        ax.set_xlabel("Taille (MiB)")
        ax.set_ylabel("Débit (kbps)" if "Débit" in label else ("Durée (s)" if "Durée" in label else label))
        # ax.set_xticklabels(increment_xticks)
        # ax.grid()

        if i == DURATION:
            ax.legend(loc='upper left')
        elif i == PUBLISHER_COLLAPSE_AVG:
            ax.legend(loc='lower left', ncol=1, frameon=True)
        elif i == PUBLISHER_COLLAPSE_PEAK:
            ax.legend(loc='lower left', ncol=1, frameon=True)
        elif i == PUBLISHER_COLLAPSE_DURATION:
            ax.legend(loc='upper left', ncol=1, frameon=True)
        else:
            ax.legend(loc=0)
        

        # Image destination path
        dest_path = "allbox_{}_{}_{}.pdf".format(LABELS[i].split(" ")[0], 2, 1)
        # save fig !
        plt.savefig(dest_path, format='pdf', transparent=True)
        plt.close()


def run(settings):
    for method in settings.get("reclamation", []):
        if not os.path.isdir(method):
            print("This is not a valid directory: ", method)
            return

    process_and_plot(settings)


if __name__ == "__main__":
    methods = []

    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if not os.path.isdir(sys.argv[i]):
                print("This is not a valid directory", sys.argv[i])
                exit(1)

            methods.append(sys.argv[i])
    else:
        print("Please provide at least one folder")
        exit(1)

    settings = {
        reclamation: methods
    }

    process_and_plot(settings)

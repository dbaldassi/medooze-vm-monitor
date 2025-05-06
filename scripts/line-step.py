#!/usr/bin/python3

import sys
import csv
import os
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

import scienceplots

plt.style.use(['science','ieee'])

plt.rcParams.update({
    "font.size": 10
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
    "ballooning": 'b',
    "cgroups-reclaim": 'g'
}

LABELS = [ "Duration (s)", "CPU (%)", "Pressure_Stall_Information (PSI)", "Publisher_Bitrate (kbps)",       
           "Viewers_bitrate (kbps)",
           "Publisher_FPS (FPS)", "Viewer_FPS (FPS)", "Publisher_RTT (ms)", 
           "Pressure_duration (s)", "Pressure_average (PSI)", "Pressure_Peak (PSI)",
           "Publisher_Collapse_Duration (s)", "Publisher_Collapse_Bitrate (kbps)", "Publisher_Collapse_peak (kbps)", "High quality ()",
            "Medium quality ()", "Low quality ()" ]

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
    no = [ "1500", "3000", "2000", "0", "1"]
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
    # print(increment_xticks)

    # res = [(1920,960), (1024,1024)]

    # fig,ax = plt.subplots(figsize=(res[0][0]*px, res[0][1]*px))
    # fig,ax = plt.subplots()    
    
    # for m in methods:
    #     stats = all_stats[m]
    #     # get current stat for all steps
    #     # to_plot = [ sum(line[FIRST_INACTIVE]) / len(line[FIRST_INACTIVE]) for line in stats.stats ]
    #     to_plot = [ sorted(line[FIRST_INACTIVE])[len(line[FIRST_INACTIVE])//2] for line in stats.stats ]
    #     print(m, stats.increment, to_plot)
    #     ax.plot(stats.increment, to_plot, "o-", color=stats.color, label="{} active to inactive".format(m), linewidth=4, markersize=12)

    # for m in methods:
    #     stats = all_stats[m]
    #     # get current stat for all steps
    #     # to_plot = [ sum(line[ALL_INACTIVE_TO_ACTIVE]) / len(line[ALL_INACTIVE_TO_ACTIVE]) for line in stats.stats ]
    #     to_plot = [ sorted(line[ALL_INACTIVE_TO_ACTIVE])[len(line[ALL_INACTIVE_TO_ACTIVE])//2] for line in stats.stats ]
    #     print(m, stats.increment, to_plot)
    #     ax.plot(stats.increment, to_plot, marker="s",linestyle='dotted', color=stats.color, label="{} inactive to active".format(m), linewidth=4, markersize=18)

    # for m in methods:
    #     stats = all_stats[m]
    #     # get current stat for all steps
    #     # to_plot = [ sum(line[ALL_INACTIVE_TO_SWAP]) / len(line[ALL_INACTIVE_TO_SWAP]) for line in stats.stats ]
    #     to_plot = [ sorted(line[ALL_INACTIVE_TO_SWAP])[len(line[ALL_INACTIVE_TO_SWAP])//2] for line in stats.stats ]
    #     print(m, stats.increment, to_plot)
    #     ax.plot(stats.increment, to_plot, "v--", color=stats.color, label="{} inactive to swap".format(m), linewidth=4, markersize=12)

    # for m in methods:
    #     stats = all_stats[m]
    #     # get current stat for all steps
    #     # to_plot = [ sum(line[ALL_INACTIVE_TO_SWAP]) / len(line[ALL_INACTIVE_TO_SWAP]) for line in stats.stats ]
    #     to_plot = [ sorted(line[ACTIVE_SUM])[len(line[ACTIVE_SUM])//2] for line in stats.stats ]
    #     print(m, stats.increment, to_plot)
    #     ax.plot(stats.increment, to_plot, "v--", color=stats.color, label="{} active cumul sum".format(m), linewidth=4, markersize=12)


    # ax.legend()
    # ax.set_xlabel("Size (MiB)")
    # ax.set_ylabel("(%)")
    # dest_path = "inactive_usage.pdf"
    # # save fig !
    # plt.savefig(dest_path, format='pdf')
    # plt.close()

    fig, ax = plt.subplots()

    stats = all_stats["cgroups-max"]
    # print(stats.stats)
    # pressure = [ sum(incr[PRESSURE_AVG]) / len(incr[PRESSURE_AVG]) for incr in stats.stats]
    # publisher_bitrate = [ sum(incr[PUBLISHER_BITRATE_AVG]) / len(incr[PUBLISHER_BITRATE_AVG]) for incr in stats.stats]
    # viewer_bitrate = [ sum(incr[VIEWER_BITRATE_AVG]) / len(incr[VIEWER_BITRATE_AVG]) for incr in stats.stats]

    #pressure = [ sorted(incr[PRESSURE_AVG])[len(incr[PRESSURE_AVG]) // 2] for incr in stats.stats]
    #publisher_bitrate = [ sorted(incr[PUBLISHER_BITRATE_AVG])[len(incr[PUBLISHER_BITRATE_AVG])//2] for incr in stats.stats]
    #viewer_bitrate = [ sorted(incr[VIEWER_BITRATE_AVG])[len(incr[VIEWER_BITRATE_AVG])//2] for incr in stats.stats]

    # pressure = [ min(incr[PRESSURE_AVG]) for incr in stats.stats]
    # publisher_bitrate = [ max(incr[PUBLISHER_BITRATE_AVG]) for incr in stats.stats]
    # viewer_bitrate = [ max(incr[VIEWER_BITRATE_AVG]) for incr in stats.stats]
    # publisher_bitrate = [ sorted(incr[PUBLISHER_BITRATE_AVG])[len(incr[PUBLISHER_BITRATE_AVG]) * 3 // 4] for incr in stats.stats]
    # viewer_bitrate = [ sorted(incr[VIEWER_BITRATE_AVG])[len(incr[VIEWER_BITRATE_AVG])*3 // 4] for incr in stats.stats]

    #for incr in stats.stats:
    #    print(incr[PRESSURE_AVG])
    
    pressure = np.array([ incr[PRESSURE_AVG] for incr in stats.stats])
    publisher_bitrate = np.array([ incr[PUBLISHER_BITRATE_AVG] for incr in stats.stats])
    viewer_bitrate = np.array([ incr[VIEWER_BITRATE_AVG] for incr in stats.stats])

    # pressure = pressure.flatten().tolist()
    # publisher_bitrate = publisher_bitrate.flatten().tolist()
    # viewer_bitrate = viewer_bitrate.flatten().tolist()

    # # print(pressure)
    
    # pressure.sort()
    # publisher_bitrate.sort(reverse=True)
    # viewer_bitrate.sort(reverse=True)

    # # print(pressure, publisher_bitrate)

    # # ax.set_xlim(0,10)

    # bar_width = 0.2 
    
    # step = 0.5
    # # interpolated_pressure = np.arange(0, max(pressure), step)
    # interpolated_pressure = np.arange(0, max(pressure), step)

    # # Interpoler les valeurs de publisher_bitrate et viewer_bitrate
    # publisher_bitrate_interpolated = np.interp(interpolated_pressure, pressure, publisher_bitrate)
    # viewer_bitrate_interpolated = np.interp(interpolated_pressure, pressure, viewer_bitrate)

    # # Indices pour les barres
    # interpolated_indices = np.arange(len(interpolated_pressure))

    # filtered_indices = [i for i, p in enumerate(interpolated_pressure) if 0 <= p <= 5]
    # filtered_pressure = [interpolated_pressure[i] for i in filtered_indices]
    # filtered_publisher_bitrate = [publisher_bitrate_interpolated[i] for i in filtered_indices]
    # filtered_viewer_bitrate = [viewer_bitrate_interpolated[i] for i in filtered_indices]

    # # Ajuster les barres avec les nouvelles valeurs filtrées
    # ax.bar(np.arange(len(filtered_pressure)) - bar_width, filtered_publisher_bitrate, bar_width, color='b', label="publisher")
    # ax.bar(np.arange(len(filtered_pressure)), filtered_viewer_bitrate, bar_width, color='g', label="viewers")

    # Aplatir le tableau de tableaux `pressure`
    flattened_pressure = [p for sublist in pressure for p in sublist]
    flattened_publisher_bitrate = [p for sublist in publisher_bitrate for p in sublist]
    flattened_viewer_bitrate = [p for sublist in viewer_bitrate for p in sublist]

    ax.set_xscale('log')
    # scatter plot 
    ax.scatter(flattened_pressure, flattened_publisher_bitrate, color='b', label="Publisher Bitrate")
    # set logarithmic scale

    # # # Filtrer les données pour ne conserver que les valeurs de pression entre 0 et 5
    # # filtered_indices = [i for i, p in enumerate(flattened_pressure) if 0 <= p <= 5]
    # # filtered_pressure = [flattened_pressure[i] for i in filtered_indices]
    # # filtered_publisher_bitrate = [flattened_publisher_bitrate[i] for i in filtered_indices]
    # # filtered_viewer_bitrate = [flattened_viewer_bitrate[i] for i in filtered_indices]

    # # Définir les bins avec un pas de 0.5
    # bin_edges = np.arange(0, max(flattened_pressure) + 0.5, 0.5)
    # bin_labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(bin_edges) - 1)]

    # # Regrouper les données dans les bins
    # binned_data = {
    #     "Pressure": [],
    #     "Publisher": [],
    #     # "Viewer": []
    # }

    # for i in range(len(bin_edges) - 1):
    #     lower, upper = bin_edges[i], bin_edges[i + 1]
    #     indices_in_bin = [j for j, p in enumerate(flattened_pressure) if lower <= p < upper]

    #     # Ajouter les données correspondantes aux bins
    #     binned_data["Pressure"].extend([bin_labels[i]] * len(indices_in_bin))
    #     binned_data["Publisher"].extend([flattened_publisher_bitrate[j] for j in indices_in_bin])
    #     # binned_data["Viewer"].extend([flattened_viewer_bitrate[j] for j in indices_in_bin])

    # # Convertir les données en DataFrame pour seaborn
    # df = pd.DataFrame(binned_data)

    # # Transformer les données pour seaborn
    # melted_df = pd.melt(df, id_vars=["Pressure"], var_name="Metric", value_name="Value")

    # Créer les boxplots
    # plt.figure()
    # sns.boxplot(x="Pressure", y="Value", hue="Metric", data=melted_df, palette=['b'])

    # Configurer les étiquettes et la légende
    plt.xlabel("Memory Pressure (PSI)")
    plt.ylabel("Bitrate (kbps)")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=False)
    # plt.title("Boxplot of Publisher and Viewer Bitrates by Memory Pressure Bins")



    # print(filtered_indices, filtered_pressure)

    # ax.set_xticks(np.arange(len(filtered_pressure)))
    # ax.set_xticklabels([f"{x:.1f}" for x in filtered_pressure])  
    # ax.set_xlabel("Memory Pressure (PSI)")
    # ax.set_ylabel("Bitrate (kbps)")
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=False)
    # ax2.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, frameon=False)

    plt.savefig("pressure_bitrate_correlation.pdf");
    plt.close()
    
    # now generates a figure for each stats
    for i in range(NUM):
        # for r in res:
        # fig,ax = plt.subplots(figsize=(r[0]*px, r[1]*px))
        fig,ax = plt.subplots()
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
            # if(m == "ballooning" and i == DURATION):
            #     dy = to_plot[-1] - to_plot[0]
            #     dx = stats.increment[-1] - stats.increment[0]
            #     a = dy / dx
            #     b = to_plot[-1] - a * stats.increment[-1]
            #     print("{}x + {}".format(a, b))
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

        if i == DURATION:
            ax.legend(loc='upper left')
        elif i == PUBLISHER_COLLAPSE_PEAK:
            ax.legend(loc='upper right', ncol=1, frameon=True)
        elif i == PUBLISHER_COLLAPSE_DURATION:
            ax.legend(loc='upper left', ncol=1, frameon=True)
        else:
            ax.legend(loc=0)
        

        # Image destination path
        dest_path = "allbox_{}_{}_{}.pdf".format(LABELS[i].split(" ")[0], 2, 1)
        # save fig !
        plt.savefig(dest_path, format='pdf')
        plt.close()



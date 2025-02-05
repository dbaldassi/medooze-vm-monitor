#!/usr/bin/python3

import csv
import sys
import os
from matplotlib import pyplot as plt

plt.rc('font', size=18)          # controls default text sizes
plt.rc('axes', titlesize=22)     # fontsize of the axes title
plt.rc('axes', labelsize=22)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=20)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


INDEX=0
COLOR=1
PROCESS=2
LABEL=3

# plt.rcParams["figure.figsize"] = (20,3)

headers = { 'TIME': [0, None, lambda x : float(x) / 1000., "time (s)" ],
'MEMORY_USED':[1, 'b', lambda x : float(x), "Memory (MiB)" ],
'MEMORY_FREE':[2, 'm', lambda x : float(x), "Memory (MiB)" ],
'MEMORY_MAX':[3, 'k', lambda x : float(x), "Memory (MiB)" ],
'SWAP':[4, 'g', lambda x : float(x), "Memory (MiB)" ],
'CGROUP_CACHE':[5, 'y', lambda x : float(x) / 1024 / 1024, "Memory (MiB)" ],
'CGROUP_SWAPPABLE':[6, 'c', lambda x : float(x) / 1024 / 1024, "Memory (MiB)" ],
'MEMORY_PRESSURE_AVG10':[7, 'darkRed', lambda x : float(x), "Pressure Stall Information (PSI)"],
'MEMORY_PRESSURE_AVG60':[8],
'MEMORY_PRESSURE_AVG300':[9],
'MEMORY_PRESSURE_TOTAL':[10],
'VIRSH_ACTUAL':[11, 'k', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_UNUSED':[12, 'tomato', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_USABLE':[13, 'm', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_AVAILABLE':[14, 'r', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_SWAP_IN':[15, '', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_SWAP_OUT':[16, 'g', lambda x : float(x) / 1024., "Memory (MiB)" ],
'VIRSH_MINOR_FAULT':[17],
'VIRSH_MAJOR_FAULT':[18],
'PUBLISHER_BITRATE':[19, 'b', lambda x : float(x), "Bitrate (kbps)"],
'PUBLISHER_FPS':[20, 'r', lambda x : float(x), "FPS" ],
'PUBLISHER_RES':[21],
'PUBLISHER_RTT':[22, 'r', lambda x : float(x), "Delay (ms)"],
'CONNECTION_STATE':[23],
'VIEWER_COUNT':[24, 'y', lambda x : float(x), "Viewer Count"],
'VM_MEMORY_USAGE':[25, 'midnightBlue', lambda x : float(x), "Memory (MiB)"],
'VM_MEMORY_FREE':[26, 'tomato', lambda x : float(x), "Memory (MiB)" ],
'VM_CPU_USAGE':[27, 'b', lambda x : float(x) * 100, "CPU (%)"],
'MEDOOZE_INCOMING_LOST':[28],
'MEDOOZE_INCOMING_DROP':[29],
'MEDOOZE_INCOMING_BITRATE':[30],
'MEDOOZE_INCOMING_NACK':[31],
'MEDOOZE_INCOMING_PLI':[32],
'RX_PACKET':[33],
'RX_DROPPED':[34],
'RX_ERRORS':[35],
'RX_MISSED':[36],
'TX_PACKET':[37],
'TX_DROPPED':[38],
'TX_ERRORS':[39],
'TX_MISSED':[40],
'VIEWER_TARGET':[41, 'k', lambda x : float(x), "Bitrate (kbps)"],
'VIEWER_BITRATE':[42, 'g', lambda x : float(x), "Bitrate (kbps)"],
'VIEWER_RTT':[43],
'VIEWER_DELAY':[44, 'm', lambda x : float(x), "Delay (ms)"],
'VIEWER_FPS':[45, 'm', lambda x : float(x), "FPS"],
# 'VIEWER_RES':[44],
'VIEWER_RID_H':[46, 'g', lambda x : float(x), "RID Count"],
'VIEWER_RID_M':[47, 'b', lambda x : float(x), "RID Count"],
'VIEWER_RID_L':[48, 'r', lambda x : float(x), "RID Count"],
}

indicators = ["avg", "1stq", "median", "3rdq", "min", "max"]
indicators_color = ['b', 'y', 'r', 'c', 'g', 'k']

def check_args(axis):
    for name in axis:
        if not name in headers:
            print(name)
            return False
    return True


def open_csv(filename):
     with open(filename, 'r') as csv_file:
        lines = [ line for line in csv.reader(csv_file, delimiter=',') ] # read file
        lines.pop(0) # remove headers
        return lines
     
     return None

def get_index(idx, indicator):
    indicator_idx = indicators.index(indicator)
    return idx * len(indicators) + indicator_idx

if __name__ == "__main__":
    x_axis = None
    y_axis = []
    y2_axis = []

    if len(sys.argv) >= 5:
        filename = sys.argv[1]

        indicator = sys.argv[2].split(',')
        x_axis = sys.argv[3]
        y_axis = sys.argv[4].split(',')
    
        if len(sys.argv) == 6:
            y2_axis = sys.argv[5].split(',')
    else:
        print("Usage : {} <file> <avg|1stq|median|3rdq|min|max> <key_x_axis> <key1_y_axis[,k2,...,kn]> [keys_y2_axis]".format(sys.arvg[0]))
        exit(1)

    print(x_axis, y_axis, y2_axis)

    for i in indicator:
        if not i in indicators:
            print("You specifed an invalid indicator")

    is_valid = check_args([x_axis, *y_axis, *y2_axis])
    if not is_valid:
        print("You specified a column not valid")
        exit(1)

    lines = open_csv(filename)

    px = 1 / plt.rcParams['figure.dpi']  # pixel in inches

    fig,ax = plt.subplots(figsize=(1920*px, 960*px)) # 2:1 ratio

    ax.set_xlabel(headers[x_axis][LABEL])
    ax.set_ylabel(headers[y_axis[0]][LABEL])

    x_axis_idx = get_index(headers[x_axis][INDEX], indicator[0])
    x_axis_values = [ headers[x_axis][PROCESS](line[x_axis_idx]) for line in lines ]

    if len(indicator) == 1:
        ax.set_title(y_axis[0])

    for y in y_axis:
        if len(indicator) == 1:
            y_idx = get_index(headers[y][INDEX], indicator[0])
            y_axis_value = [ headers[y][PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
            ax.plot(x_axis_values, y_axis_value, color=headers[y][COLOR], label=y, linewidth=4)
        else:
            for ind in indicator:
                y_idx = get_index(headers[y][INDEX], ind)
                y_axis_value = [ headers[y][PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
                ax.plot(x_axis_values, y_axis_value, color=indicators_color[indicators.index(ind)], label=ind, linewidth=4)

    if len(y2_axis) > 0:
        bx = ax.twinx()
        bx.set_ylabel(headers[y2_axis[0]][LABEL])

        for y in y2_axis:
            y_idx = get_index(headers[y][INDEX], indicator[0])
            y_axis_value = [ headers[y][PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
            bx.plot(x_axis_values, y_axis_value, color=headers[y][COLOR], label=y, linestyle='--', linewidth=4)

    ax.grid()
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)

    dest_path = filename.split('/')

    if len(y2_axis):
        dest_path[-1] = "plot_{}x{}x{}_{}.png".format(x_axis, y_axis[0],y2_axis[0], "-".join(indicator))
    else:
        dest_path[-1] = "plot_{}x{}_{}.png".format(x_axis, y_axis[0], "-".join(indicator))

    plt.savefig("/".join(dest_path))


    
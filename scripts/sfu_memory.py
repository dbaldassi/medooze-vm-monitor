#!/usr/bin/python3

import os
import csv
from matplotlib import pyplot as plt

plt.rc('font', size=22)          # controls default text sizes
plt.rc('axes', titlesize=26)     # fontsize of the axes title
plt.rc('axes', labelsize=26)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=24)    # legend fontsize
# plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
LINEWIDTH=4

# constants to access fields
VIEWER_COUNT=24
VM_MEMORY_USAGE=25
MEMORY_USED=1

data = {}

for d in os.listdir():
    if not os.path.isdir(d):
        continue

    filename = "{}/{}".format(d, os.listdir(d)[0])

    viewers = int(d.split('-')[1])

    with open(filename, 'r') as csv_file:
        lines = [ [line[VIEWER_COUNT], line[VM_MEMORY_USAGE], line[MEMORY_USED]] for line in csv.reader(csv_file, delimiter=',') ]

        i = 1
        while lines[i][0] and int(lines[i][0]) < viewers:
            i += i

        data[viewers] = [int(lines[-1][1]), int(lines[-1][2])]

x_values = sorted(data.keys())
y_values = [ data[x] for x in x_values]
# y2_values = [data[x][0] for x in x_values]

# print(x_values)
# print(y_values)

res = [(1920,960), (1024,1024)]

for r in res:
    fig,ax = plt.subplots(figsize=(r[0]*px, r[1]*px))

    ax.set_xlabel("Viewers")
    ax.set_ylabel("Memory (MiB)")
    print(x_values, y_values)
    ax.plot(x_values, y_values, linestyle="-", marker='s', linewidth=LINEWIDTH, label=['guest memory', 'cgroup memory'], markersize=15)
    ax.legend()

    dest_path = "sfu_memory_{}_{}.pdf".format(r[0]//r[1], 1)
    plt.savefig(dest_path, format = 'pdf')
    plt.close()
#!/usr/bin/python3

import sys
import csv
import os
from datetime import datetime

TIME=0
MEMORY_USED=1
MEMORY_FREE=2
MEMORY_MAX=3
SWAP=4
CGROUP_CACHE=5
CGROUP_SWAPPABLE=6
MEMORY_PRESSURE_AVG10=7
MEMORY_PRESSURE_AVG60=8
MEMORY_PRESSURE_AVG300=9
MEMORY_PRESSURE_TOTAL=10
VIRSH_ACTUAL=11
VIRSH_UNUSED=12
VIRSH_USABLE=13
VIRSH_AVAILABLE=14
VIRSH_SWAP_IN=15
VIRSH_SWAP_OUT=16
VIRSH_MINOR_FAULT=17
VIRSH_MAJOR_FAULT=18
PUBLISHER_BITRATE=19
PUBLISHER_FPS=20
PUBLISHER_RES=21
PUBLISHER_RTT=22
CONNECTION_STATE=23
VIEWER_COUNT=24
VM_MEMORY_USAGE=25
VM_MEMORY_FREE=26
VM_CPU_USAGE=27
MEDOOZE_INCOMING_LOST=28
MEDOOZE_INCOMING_DROP=29
MEDOOZE_INCOMING_BITRATE=30
MEDOOZE_INCOMING_NACK=31
MEDOOZE_INCOMING_PLI=32
RX_PACKET=33
RX_DROPPED=34
RX_ERRORS=35
RX_MISSED=36
TX_PACKET=37
TX_DROPPED=38
TX_ERRORS=39
TX_MISSED=40
VIEWER_TARGET:41
VIEWER_BITRATE=42
VIEWER_RTT=43
VIEWER_DELAY=44
VIEWER_FPS=45
VIEWER_RES=46
VIEWER_RID=47

DURATION=0
CPU_AVG=1
PRESSURE_AVG=2
PUBLISHER_BITRATE_AVG=3
VIEWER_BITRATE_AVG=4
PUBLISHER_FPS_AVG=5
VIEWER_FPS_AVG=6
PUBLISHER_RTT_AVG=7

def find_duration_ballooning(stats_tab, start_hint):
    duration = [0,0]
    start = 0

    for i in range(len(stats_tab)):
        time = float(stats_tab[i][0]) / 1000

        if(time < start_hint):
            continue
        else: 
            start = i
            break

    start_value = stats_tab[start][VIRSH_ACTUAL]
    while(stats_tab[start][VIRSH_ACTUAL] == start_value):
        start += 1
    
    duration[0] = start - 1
    end = start

    while(stats_tab[end][VIRSH_ACTUAL] != stats_tab[-1][VIRSH_ACTUAL]):
        end += 1

    duration[1] = end

    return duration

def find_duration_cgroups_max(stats_tab, start_hint):
    duration = [0,0]
    start = 0

    # find start_hint index
    for i in range(len(stats_tab)):
        time = float(stats_tab[i][0]) / 1000

        if(time < start_hint):
            continue
        else: 
            start = i
            break

    # find index when max start decreasing
    start_value = stats_tab[start][MEMORY_MAX]
    while(stats_tab[start][MEMORY_MAX] == start_value):
        start += 1

    duration[0] = start - 1
    end = start

    while(end < len(stats_tab) and stats_tab[end][MEMORY_USED] > stats_tab[end+1][MEMORY_USED]):
        end += 1

    if(end == len(stats_tab)):
        end -= 1

    duration[1] = end

    return duration

def find_duration_cgroups_reclaim(stats_tab, start_hint):
    duration = [0,0]



    return duration

def get_stats(stats_tab, results, columns, duration):
    n = duration[1] - duration[0]

    for i in range(len(columns)):
        results[columns[i][0]].append(0)

    for i in range(duration[0], duration[1], 1):
        for j in range(len(columns)):
            col = columns[j]
            try:
                value = float(stats_tab[i][col[1]]) / n
            except:
                value = 0

            if(col[1] == VM_CPU_USAGE):
                value *= 100

            results[col[0]][-1] += value

if __name__ == "__main__":
    all_stats = []
    average_stats = []
    columns = [(CPU_AVG, VM_CPU_USAGE), (PRESSURE_AVG, MEMORY_PRESSURE_AVG10), (PUBLISHER_BITRATE_AVG, PUBLISHER_BITRATE),
               (PUBLISHER_FPS_AVG, PUBLISHER_FPS), (PUBLISHER_RTT_AVG, PUBLISHER_RTT),
               (VIEWER_BITRATE_AVG, VIEWER_BITRATE), (VIEWER_FPS_AVG, VIEWER_FPS)               
               ]
    
    if len(sys.argv) == 1:
        print("Please provide used method to decrease memory")
        exit(1)

    # load all stats
    for f in os.listdir():
        if not f.endswith('_average.csv') or f.startswith('.'):
            continue
        
        with open(f, 'r') as csv_file:
            lines = [ line for line in csv.reader(csv_file, delimiter=',') ]
            all_stats.append(lines)

    for i in range(len(columns)+1):
        average_stats.append([])

    for stat in all_stats:
        stat.pop(0)

        duration = [0,0]
        if(sys.argv[1] == 'ballooning'):
            duration = find_duration_ballooning(stat, 45)
        elif(sys.argv[1] == 'cgroups-max'):
            duration = find_duration_cgroups_max(stat, 45)
        elif(sys.argv[1] == 'cgroups-reclaim'):
            duration = find_duration_cgroups_max(stat, 45)
        else:
            print("NOPE")
            exit(1)

        average_stats[0].append((int(stat[duration[1]][0]) - int(stat[duration[0]][0])) / 1000)

        get_stats(stat, average_stats, columns, duration)

    out_filename = "average_step.csv"

    # open and write csv file
    with open(out_filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for row in average_stats:
            writer.writerow(row)


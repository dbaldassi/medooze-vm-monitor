#!/usr/bin/python3

import os
import csv

filename = 'stats.csv'

stats_csv = open(filename, 'r')
lines = [ line for line in csv.reader(stats_csv, delimiter=',') ]
lines.pop(0) # remove header line

stats_csv.close()

result = []

TIME=0
MEMORY_USED=1
MEMORY_FREE=2
MEMORY_MAX=3
SWAP=4
PUBLISHER_BITRATE=5
CONNECTION_STATE=6
VIEWER_COUNT=7
VM_MEMORY_USAGE=8
VM_MEMORY_FREE=9
VM_CPU_USAGE=10
MEDOOZE_INCOMING_LOST=11
MEDOOZE_INCOMING_DROP=12
MEDOOZE_INCOMING_BITRATE=13
MEDOOZE_INCOMING_NACK=14
MEDOOZE_INCOMING_PLI=15

FIXED_HEADER_LENGTH=MEDOOZE_INCOMING_PLI + 1


for viewer_ind in range(FIXED_HEADER_LENGTH+1, len(lines[-1]), 3):
    viewer_count = 0
    bitrate_avg = 0
    bitrate_avg_n = 0

    for line in lines:
        current_viewer_count = int(line[VIEWER_COUNT])

        if viewer_count != current_viewer_count:
            if(bitrate_avg_n > 0):
                result.append([viewer_count, bitrate_avg // bitrate_avg_n])

            viewer_count = current_viewer_count
            bitrate_avg = 0
            bitrate_avg_n = 0

        if viewer_ind < len(line) and line[viewer_ind] != None and line[viewer_ind] != '' and int(line[viewer_ind]) >= 0:
            bitrate_avg += int(line[viewer_ind])
            bitrate_avg_n += 1


bitrate_avg_viewer = []
for i in range(1, int(lines[-1][VIEWER_COUNT])+1, 1):
    avg = 0
    n = 0
    for row in result:
        if(row[0] == i):
            avg += row[1]
            n += 1

    if n > 0:
        bitrate_avg_viewer.append(avg//n)

for i in range(len(bitrate_avg_viewer)):
    result[i].append(bitrate_avg_viewer[i])


viewer_count = 0
result_tmp = [0,0,0] # publisher, mem hypervisor, mem vm
n = 0
result.insert(0, [0,0,0])

for line in lines:
    current_viewer_count = int(line[VIEWER_COUNT])
    
    if viewer_count != current_viewer_count:
        if(n > 0):
            result[viewer_count].extend([v // n for v in result_tmp])

        viewer_count = current_viewer_count
        result_tmp = [0,0,0]
        n = 0
    
    if line[PUBLISHER_BITRATE] != '':
        n += 1
        result_tmp[0] += int(line[PUBLISHER_BITRATE])
        result_tmp[1] += int(line[MEMORY_USED])
        result_tmp[2] += int(line[VM_MEMORY_USAGE])

result.insert(0, ["VIEWER COUNT", "VIEWER BITRATE", "AVERAGE VIEWER BITRATE", "PUBLISHER BITRATE", "HYPERVISOR MEMORY", "VM MEMORY"])

reorder_csv = open('stats_reordered.csv', 'w')
writer = csv.writer(reorder_csv, delimiter=',')

for row in result:
    writer.writerow(row)

reorder_csv.close()
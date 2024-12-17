#!/usr/bin/python3

''''
This file is needed to redorder the csv columns output by the the monitor app
for libreoffice to show each viewer bitrate in function of the number of viewers.
In libre office in order to have several Y values per X, you need to repeat the X value in the same column
and put the Y value in front of each.
We also compute the average of the viewer bitrate (because it seems libre office can't do that, only interpolation)
And the number viewer using a specific Simulcast/SVC layer during the experiment
'''

import sys
import csv

filename=""

# get file passed as argument
if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print(f"Need one argument : {sys.argv[0]} <filename.csv>")
    sys.exit(1)

# open file for readin
stats_csv = open(filename, 'r')
lines = [ line for line in csv.reader(stats_csv, delimiter=',') ] # load csv in array
lines.pop(0) # remove header line

stats_csv.close()

result = []

# constants to access fields
TIME=0
MEMORY_USED=1
MEMORY_FREE=2
MEMORY_MAX=3
SWAP=4
PUBLISHER_BITRATE=5
PUBLISHER_FPS=6
PUBLISHER_RES=7
CONNECTION_STATE=8
VIEWER_COUNT=9
VM_MEMORY_USAGE=10
VM_MEMORY_FREE=11
VM_CPU_USAGE=12
MEDOOZE_INCOMING_LOST=13
MEDOOZE_INCOMING_DROP=14
MEDOOZE_INCOMING_BITRATE=15
MEDOOZE_INCOMING_NACK=16
MEDOOZE_INCOMING_PLI=17
RX_PACKET=18
RX_DROPPED=19
RX_ERRORS=20
RX_MISSED=21
TX_PACKET=22
TX_DROPPED=23
TX_ERRORS=24
TX_MISSED=25

FIXED_HEADER_LENGTH=TX_MISSED + 1

NUM_VIEWER_HEADERS=5

for viewer_ind in range(FIXED_HEADER_LENGTH+1, len(lines[-1]), NUM_VIEWER_HEADERS):
    viewer_count = 0
    bitrate_avg = 0
    bitrate_avg_n = 0
    res = []
    rid = []

    for line in lines:
        current_viewer_count = int(line[VIEWER_COUNT])

        if viewer_count != current_viewer_count:
            if(bitrate_avg_n > 0):
                # print(viewer_count)
                result.append([viewer_count, bitrate_avg // bitrate_avg_n, res[-1], rid[-1]])

            if(current_viewer_count < viewer_count):
                break # it means there was an issue, the viewer count is not supposed to go down in this exp

            viewer_count = current_viewer_count
            bitrate_avg = 0
            bitrate_avg_n = 0
            res = []
            rid = []

        if viewer_ind < len(line) and line[viewer_ind] != None and line[viewer_ind] != '' and int(line[viewer_ind]) >= 0:
            bitrate_avg += int(line[viewer_ind])
            bitrate_avg_n += 1
            # print(len(line), viewer_ind, line, line[viewer_ind])
            res.append(line[viewer_ind + 2])
            rid.append(line[viewer_ind + 3])

# print(result)
# compute average bitrate for each viewer count
bitrate_avg_viewer = []
rid_count = [] # get number of viewer using the same rid per viewer
for i in range(1, int(result[-1][0])+1, 1):
   #  print("1:", i)
    avg = 0
    n = 0
    rids = { 'h': 0, 'm': 0, 'l': 0 }
    for row in result:
        if(row[0] == i):
            # print("2:", i, row)
            avg += row[1]
            n += 1
            if row[3] in rids: 
                rids[row[3]] += 1

    if n > 0:
        # print(i, rids)
        bitrate_avg_viewer.append(avg//n)
        rid_count.append(rids)

# add average value into a new column
for i in range(len(bitrate_avg_viewer)):
    result[i].append(bitrate_avg_viewer[i])
    for key in rid_count[i]:
        result[i].append(rid_count[i][key])

# print(result)
viewer_count = 0
result_tmp = [0,0,0,0] # publisher bitrate, publisher resolution, mem hypervisor, mem vm
n = 0
result.insert(0, [0,0,0,0,0,0,0])

# Get publisher bitrate and VM memory usage per viewer count
for line in lines:
    current_viewer_count = int(line[VIEWER_COUNT])
    
    # New viewer, we save the average bitrate found for this viewer
    if viewer_count != current_viewer_count:
        if(n > 0):
            result[viewer_count].extend([v if type(v) == str else v // n for v in result_tmp])

        # reset the value
        viewer_count = current_viewer_count
        result_tmp = [0,0,0,0]
        n = 0
    
    if line[PUBLISHER_BITRATE] != '':
        # Add value for the current viewer to compute the average when the viewer count change
        n += 1
        result_tmp[0] += int(line[PUBLISHER_BITRATE])
        result_tmp[1] = line[PUBLISHER_RES]
        result_tmp[2] += int(line[MEMORY_USED])
        result_tmp[3] += int(line[VM_MEMORY_USAGE])

# insert headers
result.insert(0, ["VIEWER COUNT", "VIEWER BITRATE", "VIEWER RESOLUTION", "VIEWER RID", "AVERAGE VIEWER BITRATE", "h", "m", "l", "PUBLISHER BITRATE", "PUBLISHER RESOLUTION", "HYPERVISOR MEMORY", "VM MEMORY"])

# write into csv
dest_file=filename.replace(".csv", "_reordered.csv")
reorder_csv = open(dest_file, 'w')
writer = csv.writer(reorder_csv, delimiter=',')

for row in result:
    writer.writerow(row)

reorder_csv.close()
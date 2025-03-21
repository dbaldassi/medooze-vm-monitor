#!/usr/bin/python3

''''
This file is used to to compture the average bitrate and fps of each viewer. 
(don't want to do it in libre office when there are too much viewers)
Also sm up used simulcast layer
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

stats_csv.close()

result = []

# constants to access fields
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
VM_FREE_TOTAL=28 
VM_FREE_USED=29
VM_FREE_BUFCACHE=30
MEDOOZE_INCOMING_LOST=31
MEDOOZE_INCOMING_DROP=32
MEDOOZE_INCOMING_BITRATE=33
MEDOOZE_INCOMING_NACK=34
MEDOOZE_INCOMING_PLI=35
RX_PACKET=36
RX_DROPPED=37
RX_ERRORS=38
RX_MISSED=39
TX_PACKET=40
TX_DROPPED=41
TX_ERRORS=42
TX_MISSED=43

FIXED_HEADER_LENGTH=TX_MISSED + 1

NUM_VIEWER_HEADERS=7

# Constant to viewer columns
VIEWER_TARGET=0
VIEWER_BITRATE=1
VIEWER_RTT=2
VIEWER_DELAY=3
VIEWER_FPS=4
VIEWER_RES=5
VIEWER_RID=6

headers = lines.pop(0)

rids = { 'h': 0, 'm': 0, 'l': 0 }

# Remove viewer headers
headers = headers[:FIXED_HEADER_LENGTH]
# Add viewer average headers
headers.extend(["VIEWERS TARGET AVERAGE", "VIEWERS BITRATE AVERAGE", "VIEWERS RTT AVG", "VIEWERS E2E AVG", "VIEWERS FPS AVERAGE"])
# add rid headers
headers.extend(list(rids))

result = [headers]
bla=0
for line in lines:
    # init
    rids = { 'h': 0, 'm': 0, 'l': 0 }
    average = [0,0,0,0,0] # target, bitrate, fps
    n = 0

    # for each viewer
    for v in range(FIXED_HEADER_LENGTH, len(line), NUM_VIEWER_HEADERS):
        # Sum to compute the average later
        if(line[v+VIEWER_TARGET] == ''):
            continue

        average[VIEWER_TARGET]  += int(line[v + VIEWER_TARGET])
        average[VIEWER_BITRATE] += int(line[v + VIEWER_BITRATE])
        average[VIEWER_RTT] += int(line[v + VIEWER_RTT])
        average[VIEWER_DELAY] += int(line[v + VIEWER_DELAY])
        average[VIEWER_FPS]     += int(line[v + VIEWER_FPS])
        n += 1

        # Add to the used layer sum
        rid = line[v + VIEWER_RID]
        if rid in rids:
            rids[rid] += 1

    # remove old viewer fields
    line = line[:FIXED_HEADER_LENGTH]

    # If there was viewer compute average and add them to the line
    if n > 0:
        line.extend([s // n for s in average])
        line.extend(list(rids.values()))

    # Add the line to the result
    # line is a copy not a pointer of the corresponding array in lines
    result.append(line)


# write into csv
dest_file=filename.replace(".csv", "_average.csv")
reorder_csv = open(dest_file, 'w')
writer = csv.writer(reorder_csv, delimiter=',')

for row in result:
    writer.writerow(row)

reorder_csv.close()
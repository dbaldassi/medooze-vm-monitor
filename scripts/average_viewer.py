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
VIRSH_ACTUAL=5
VIRSH_UNUSED=6
VIRSH_USABLE=7
VIRSH_AVAILABLE=8
VIRSH_SWAP_IN=9
VIRSH_SWAP_OUT=10
VIRSH_MINOR_FAULT=11
VIRSH_MAJOR_FAULT=12
PUBLISHER_BITRATE=13
PUBLISHER_FPS=14
PUBLISHER_RES=15
CONNECTION_STATE=16
VIEWER_COUNT=17
VM_MEMORY_USAGE=18
VM_MEMORY_FREE=19
VM_CPU_USAGE=120
MEDOOZE_INCOMING_LOST=21
MEDOOZE_INCOMING_DROP=22
MEDOOZE_INCOMING_BITRATE=23
MEDOOZE_INCOMING_NACK=24
MEDOOZE_INCOMING_PLI=25
RX_PACKET=26
RX_DROPPED=27
RX_ERRORS=28
RX_MISSED=29
TX_PACKET=30
TX_DROPPED=31
TX_ERRORS=32
TX_MISSED=33

FIXED_HEADER_LENGTH=TX_MISSED + 1

NUM_VIEWER_HEADERS=5

# Constant to viewer columns
VIEWER_TARGET=0
VIEWER_BITRATE=1
VIEWER_FPS=2
VIEWER_RES=3
VIEWER_RID=4

headers = lines.pop(0)

rids = { 'h': 0, 'm': 0, 'l': 0 }

# Remove viewer headers
headers = headers[:FIXED_HEADER_LENGTH]
# Add viewer average headers
headers.extend(["VIEWERS TARGET AVERAGE", "VIEWERS BITRATE AVERAGE", "VIEWERS FPS AVERAGE"])
# add rid headers
headers.extend(list(rids))

result = [headers]

for line in lines:
    # init
    rids = { 'h': 0, 'm': 0, 'l': 0 }
    average = [0,0,0] # target, bitrate, fps
    n = 0
    
    # for each viewer
    for v in range(FIXED_HEADER_LENGTH, len(line), NUM_VIEWER_HEADERS):
        # Sum to compute the average later
        average[VIEWER_TARGET]  += int(line[v + VIEWER_TARGET])
        average[VIEWER_BITRATE] += int(line[v + VIEWER_BITRATE])
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
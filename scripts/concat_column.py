#!/usr/bin/python3

import csv
import sys
import os

if len(sys.argv) == 2:
    target = sys.argv[1] # get target column
else:
    print("Missing which column to concat")
    exit(1)

headers = { 'TIME': 0,
'MEMORY_USED':1,
'MEMORY_FREE':2,
'MEMORY_MAX':3,
'SWAP':4,
'MEMORY_PRESSURE_AVG10':5,
'MEMORY_PRESSURE_AVG60':6,
'MEMORY_PRESSURE_AVG300':7,
'MEMORY_PRESSURE_TOTAL':8,
'VIRSH_ACTUAL':9,
'VIRSH_UNUSED':10,
'VIRSH_USABLE':11,
'VIRSH_AVAILABLE':12,
'VIRSH_SWAP_IN':13,
'VIRSH_SWAP_OUT':14,
'VIRSH_MINOR_FAULT':15,
'VIRSH_MAJOR_FAULT':16,
'PUBLISHER_BITRATE':17,
'PUBLISHER_FPS':18,
'PUBLISHER_RES':19,
'PUBLISHER_RTT':20,
'CONNECTION_STATE':21,
'VIEWER_COUNT':22,
'VM_MEMORY_USAGE':23,
'VM_MEMORY_FREE':24,
'VM_CPU_USAGE':25,
'MEDOOZE_INCOMING_LOST':26,
'MEDOOZE_INCOMING_DROP':27,
'MEDOOZE_INCOMING_BITRATE':28,
'MEDOOZE_INCOMING_NACK':29,
'MEDOOZE_INCOMING_PLI':30,
'RX_PACKET':31,
'RX_DROPPED':32,
'RX_ERRORS':33,
'RX_MISSED':34,
'TX_PACKET':35,
'TX_DROPPED':36,
'TX_ERRORS':37,
'TX_MISSED':38,
'VIEWER_TARGET':39,
'VIEWER_BITRATE':40,
'VIEWER_RTT':41,
'VIEWER_DELAY':42,
'VIEWER_FPS':43,
'VIEWER_RES':44,
'VIEWER_RID':45
}

if not target in headers:
    print(target, "is not a valid coloumn name")
    exit(1)

result = []

# browse directories
for dir in sorted(os.listdir()):
    avg_exp_file = None
    
    # do not consider regular files
    if not os.path.isdir(dir):
        continue

    for f in os.listdir(dir):
        # print(f[0])
        if "_average" in f and not "_average.csv" in f and not ".ods" in f and f[0] != '.':
            avg_exp_file = f # this is our file, save it
            break
    
    # no avg exp file
    if avg_exp_file == None:
        continue # pass to next dir

    # concat dir and filename to get the path
    path = "{}/{}".format(dir, avg_exp_file)
    print(path)
    
    with open(path, 'r') as csv_file:
        lines = [ line for line in csv.reader(csv_file, delimiter=',') ] # read file

        lines[0][headers[target]] += " {}".format(dir)

        if(len(result) == 0): # if first file, get the X axis, here time
            for line in lines:
                result.append([line[headers["TIME"]], line[headers[target]]])
        else:
            for i in range(min(len(result), len(lines))):
                result[i].append(lines[i][headers[target]]) # add the new file column

            # In case there are more lines in the file than the previous ones, adds the new lines
            if len(result) < len(lines):
                for i in range(len(result), len(lines)):
                    tab = [None] * len(result[-1]) # set all fields to none to align with current file column
                    tab[0] = lines[i][headers["TIME"]] # add the time for X axis
                    tab[-1] = lines[i][headers[target]] # add the actual column value

                    result.append(tab) # add line
            elif len(lines) < len(result): # if the file have less lines than previous one
                for i in range(len(lines), len(result)):
                    result[i].append(None) # add none to the column since it doest exist
            

out_filename = "concat_{}.csv".format(target)

with open(out_filename, "w") as csv_file:
    writer = csv.writer(csv_file)
    for row in result:
        writer.writerow(row)
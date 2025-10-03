#!/usr/bin/python3

import sys
import csv
import os
from datetime import datetime

all_stats = []
average_stats = []

# load all stats
for f in os.listdir():
    if f.startswith('.') or os.path.isdir(f) or not f.endswith('.csv'):
         continue
    
    with open(f, 'r') as csv_file:
        lines = [ line for line in csv.reader(csv_file, delimiter=',') ]
        all_stats.append(lines)

newheaders = []
# num_indicators = 6
num_indicators = 1

for header in all_stats[0][0]:
    newheaders.append(header)
    newheaders.append("1stQ")
    newheaders.append("Median")
    newheaders.append("3rdQ")
    newheaders.append("Min")
    newheaders.append("Max")

average_stats.append(newheaders) # add headers

# remove headers from all stats
for stat in all_stats:
    stat.pop(0)

repet = len(all_stats) # number of repetition
num_lines = min([len(stat) for stat in all_stats]) # number of rows in each file

# compute average
for i in range(num_lines):
    # create a line of zero, same size as number of headers
    # avg_line = [[]] * (len(average_stats[0]) // 6)
    avg_line = []
    for i in range(len(average_stats[0]) // num_indicators):
        avg_line.append([])

    for stat in all_stats:
        # get first file and remove it
        line = stat.pop(0)

        # print(len(all_stats), line)
        # print(avg_line[0])
        for j in range(len(line)):
            # print(len(line), len(avg_line), len(average_stats[0]))
            try:
                # sum value
                # avg_line[j] += float(line[j])
                avg_line[j].append(float(line[j]))
            except:
                avg_line[j].append(-1)
        # print(avg_line[0])
        # exit(0)
    
    # avg_line.sort()
    # print(avg_line)

    result = []
    for col in avg_line:
        if(len(col) == 0):
            continue

        col.sort()
        result.append(sum(col) / len(col))
        result.append(col[len(col) // 4])
        result.append(col[len(col) // 2])
        result.append(col[len(col) * 3 // 4])
        result.append(min(col))
        result.append(max(col))

    average_stats.append(result)

dir_name = os.getcwd().split('/')[-1] # get current directory name, strip absolute path and get only the dir name
date_str = datetime.today().strftime('%Y-%m-%d-%H-%M-%S') # get current date with time

# create filename for the average csv file
out_filename = "{dir}_{date}_average_{repet}.csv".format(dir=dir_name, date=date_str, repet=repet)

# open and write csv file
with open(out_filename, 'w') as csv_file:
    writer = csv.writer(csv_file)
    for row in average_stats:
        writer.writerow(row)


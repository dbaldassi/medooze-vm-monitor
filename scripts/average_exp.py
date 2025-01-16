#!/usr/bin/python3

import sys
import csv
import os
from datetime import datetime

all_stats = []
average_stats = []

# load all stats
for f in os.listdir():
    with open(f, 'r') as csv_file:
        lines = [ line for line in csv.reader(csv_file, delimiter=',') ]
        all_stats.append(lines)

average_stats.append(all_stats[0][0]) # add headers

# remove headers from all stats
for stat in all_stats:
    stat.pop(0)

repet = len(all_stats) # number of repetition
num_lines = min([len(stat) for stat in all_stats]) # number of rows in each file

# compute average
for i in range(num_lines):
    # create a line of zero, same size as number of headers
    avg_line = [0] * len(average_stats[0])
    for stat in all_stats:
        # get first file and remove it
        line = stat.pop(0)

        for j in range(len(line)):
            try:
                # sum value
                avg_line[j] += float(line[j])
            except:
                # if can not convert int or float
                continue
    
    # compute average and add line
    average_stats.append([ value / repet for value in avg_line ])

dir_name = os.getcwd().split('/')[-1] # get current directory name, strip absolute path and get only the dir name
date_str = datetime.today().strftime('%Y-%m-%d-%H-%M-%S') # get current date with time

# create filename for the average csv file
out_filename = "{dir}_{date}_average_{repet}.csv".format(dir=dir_name, date=date_str, repet=repet)

# open and write csv file
with open(out_filename, 'w') as csv_file:
    writer = csv.writer(csv_file)
    for row in average_stats:
        writer.writerow(row)


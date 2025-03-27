#!/usr/bin/python3

import sys
import csv
import os
from datetime import datetime

# csv headers
TIME = 0
ANON = 1
FILE = 2
KERNEL = 3
KERNEL_STACK = 4
PAGETABLES = 5
SEC_PAGETABLES = 6
PERCPU = 7
SOCK = 8
VMALLOC = 9
SHMEM = 10
ZSWAP = 11
ZSWAPPED = 12
FILE_MAPPED = 13
FILE_DIRTY = 14
FILE_WRITEBACK = 15
SWAPCACHED = 16
ANON_THP = 17
FILE_THP = 18
SHMEM_THP = 19
INACTIVE_ANON = 20
ACTIVE_ANON = 21
INACTIVE_FILE = 22
ACTIVE_FILE = 23
UNEVICTABLE = 24
SLAB_RECLAIMABLE = 25
SLAB_UNRECLAIMABLE = 26
SLAB = 27
WORKINGSET_REFAULT_ANON = 28
WORKINGSET_REFAULT_FILE = 29
WORKINGSET_ACTIVATE_ANON = 30
WORKINGSET_ACTIVATE_FILE = 31
WORKINGSET_RESTORE_ANON = 32
WORKINGSET_RESTORE_FILE = 33
WORKINGSET_NODERECLAIM = 34
PGDEMOTE_KSWAPD = 35
PGDEMOTE_DIRECT = 36
PGDEMOTE_KHUGEPAGED = 37
PGPROMOTE_SUCCESS = 38
PGSCAN = 39
PGSTEAL = 40
PGSCAN_KSWAPD = 41
PGSCAN_DIRECT = 42
PGSCAN_KHUGEPAGED = 43
PGSTEAL_KSWAPD = 44
PGSTEAL_DIRECT = 45
PGSTEAL_KHUGEPAGED = 46
PGFAULT = 47
PGMAJFAULT = 48
PGREFILL = 49
PGACTIVATE = 50
PGDEACTIVATE = 51
PGLAZYFREE = 52
PGLAZYFREED = 53
SWPIN_ZERO = 54
SWPOUT_ZERO = 55
ZSWPIN = 56
ZSWPOUT = 57
ZSWPWB = 58
THP_FAULT_ALLOC = 59
THP_COLLAPSE_ALLOC = 60
THP_SWPOUT = 61
THP_SWPOUT_FALLBACK = 62
NUMA_PAGES_MIGRATED = 63
NUMA_PTE_UPDATES = 64
NUMA_HINT_FAULTS = 65
RAM_USAGE = 66
SWAP_USAGE = 67
MAXRAM = 68
PRESSURE_AVG10 = 69
SUMMED_MEMORY = 70

# line index in new csv
# FIRST_ACTIVE=0
FIRST_INACTIVE=0
FIRST_SWAP=1
# ALL_ACTIVE=3
ALL_INACTIVE_TO_ACTIVE=2
ALL_INACTIVE_TO_SWAP=3
ALL_MEMORY_TO_SWAP=4
ALL_FREE=5

NUM_RESULT = ALL_FREE + 1

if __name__ == "__main__":
    all_stats = []
    average_stats = []

    # load all stats
    for f in os.listdir():
        if not f.endswith('.csv') or f.startswith('.') or not f.startswith('cgroups_cgroups'):
            continue
        
        with open(f, 'r') as csv_file:
            lines = [ line for line in csv.reader(csv_file, delimiter=',') ]
            all_stats.append(lines)

    for i in range(NUM_RESULT):
        average_stats.append([])

    i = 0
    for stat in all_stats:
        stat.pop(0)

        index = 1
        
        # print(initial_current_memory)

        while stat[index][INACTIVE_ANON] == stat[index-1][INACTIVE_ANON]:
            index += 1
        
        initial_current_memory = int(stat[index - 1][RAM_USAGE])
        initial_active_memory = int(stat[index - 1][ANON]) / 1024 / 1024
        # first reclaim
        first_index = index
        first_inactive_value = int(stat[index][INACTIVE_ANON]) / 1024 / 1024
        first_active_value = int(stat[index][ACTIVE_ANON]) / 1024 / 1024

        average_stats[FIRST_INACTIVE].append(first_inactive_value * 100 / initial_active_memory)

        while stat[index][SWAP_USAGE] == stat[index-1][SWAP_USAGE]:
            index += 1

        first_swap_value = int(stat[index][SWAP_USAGE])
        average_stats[FIRST_SWAP].append(first_swap_value * 100 / (initial_current_memory - int(stat[index][RAM_USAGE])))

        # print(initial_current_memory, int(stat[index][RAM_USAGE]), first_swap_value)

        inactive_to_active = 0
        inactive_to_swap = 0

        inactive_to_active_counter = 0
        inactive_to_swap_counter = 0

        ONE_MINUTE = (60 / 0.5) + first_index
        TEN_MINUTES = 10 * ONE_MINUTE

        inactive_to_active_tab = []
        inactive_to_swap_tab = []

        inactive_to_active_all_tab = []
        inactive_to_swap_all_tab = []
        
        index = first_index
        while index < len(stat):
            if index == ONE_MINUTE or index == TEN_MINUTES:             
                inactive_to_active_tab.append(inactive_to_active_counter * 100 / first_inactive_value)
                inactive_to_swap_tab.append(inactive_to_swap_counter * 100 / first_inactive_value)

                inactive_to_active_all_tab.append(inactive_to_active * 100 / first_inactive_value)
                inactive_to_swap_all_tab.append(inactive_to_swap * 100 / first_inactive_value)
    
                inactive_to_active_counter = 0
                inactive_to_swap_counter = 0
            
            if stat[index][INACTIVE_ANON] == stat[index-1][INACTIVE_ANON]:
                index += 1
                continue

            inactive_delta = int(stat[index - 1][INACTIVE_ANON]) - int(stat[index][INACTIVE_ANON])
            active_delta = int(stat[index - 1][ACTIVE_ANON]) - int(stat[index][ACTIVE_ANON])
            swap_delta = int(stat[index - 1][SWAP_USAGE]) - int(stat[index][SWAP_USAGE])

            if inactive_delta > 0 and active_delta < 0:
                inactive_to_active += min(inactive_delta, abs(active_delta)) / 1024 / 1024
                inactive_to_active_counter += min(inactive_delta, abs(active_delta)) / 1024 / 1024

            if inactive_delta > 0 and swap_delta < 0:
                inactive_to_swap += min(inactive_delta / 1024 / 1024, abs(swap_delta))
                inactive_to_swap_counter += min(inactive_delta / 1024 / 1024, abs(swap_delta))

            if inactive_delta < 0 :
                first_inactive_value += abs(inactive_delta) / 1024 / 1024
                           
            index += 1

        inactive_to_active_tab.append(inactive_to_active_counter * 100 / first_inactive_value)
        inactive_to_swap_tab.append(inactive_to_swap_counter * 100 / first_inactive_value)

        inactive_to_active_all_tab.append(inactive_to_active * 100 / first_inactive_value)
        inactive_to_swap_all_tab.append(inactive_to_swap * 100 / first_inactive_value)

        print(inactive_to_active_tab, inactive_to_swap_tab)
        print(inactive_to_active_all_tab, inactive_to_swap_all_tab)
            
        # print(inactive_to_swap, first_inactive_value, inactive_to_swap * 100 / first_inactive_value)
        average_stats[ALL_INACTIVE_TO_ACTIVE].append(inactive_to_active * 100 / first_inactive_value)
        average_stats[ALL_INACTIVE_TO_SWAP].append(inactive_to_swap * 100 / first_inactive_value)

        index -= 1
        memory_delta = initial_current_memory - int(stat[index][RAM_USAGE])
        average_stats[ALL_MEMORY_TO_SWAP].append(first_swap_value * 100 / memory_delta)

        inital_diff_current_anon = initial_current_memory - initial_active_memory
        diff_current_anon = int(stat[index][RAM_USAGE]) - ((int(stat[index][ACTIVE_ANON]) + int(stat[index][INACTIVE_ANON])) / (1024*1024) + int(stat[index][SWAP_USAGE]))

        average_stats[ALL_FREE].append(inital_diff_current_anon - diff_current_anon)

        current_anon = int(stat[index][INACTIVE_ANON]) / 1024 / 1024

        # print(current_anon, first_inactive_value, (first_inactive_value - current_anon) * 100 / first_inactive_value)

    out_filename = "percent_cgroups_step.csv"

    # open and write csv file
    with open(out_filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for row in average_stats:
            writer.writerow(row)


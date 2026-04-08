#!/usr/bin/env python3

import duckdb
import sys
import os
import re

main_cols = ["TIME",
             "MEMORY USED",
             "MEMORY FREE",
             "MEMORY MAX",
             "SWAP",
             "CGROUP CACHE FILES",
             "CGROUP SWAPPABLE",
             "MEMORY PRESSURE AVG10",
             "MEMORY PRESSURE AVG60",
             "MEMORY PRESSURE AVG300",
             "MEMORY PRESSURE TOTAL",
             "VIRSH ACTUAL",
             "VIRSH UNUSED",
             "VIRSH USABLE",
             "VIRSH AVAILABLE",
             "VIRSH SWAP IN",
             "VIRSH SWAP OUT",
             "VIRSH MINOR FAULT",
             "VIRSH MAJOR FAULT",
             "PUBLISHER BITRATE",
             "PUBLISHER FPS",
             "PUBLISHER RESOLUTION",
             "PUBLISHER RTT",
             "CONNECTION STATE",
             "VIEWER COUNT",
             "VM MEMORY USAGE",
             "VM MEMORY FREE",
             "VM CPU USAGE",
             "VM FREE TOTAL",
             "VM FREE USED",
             "VM FREE BUFCACHE",
             "MEDOOZE INCOMING LOST",
             "MEDOOZE INCOMING DROP",
             "MEDOOZE INCOMING BITRATE",
             "MEDOOZE INCOMING NACK",
             "MEDOOZE INCOMING PLI",
             "RX PACKET",
             "RX DROPPED",
             "RX ERRORS",
             "RX MISSED",
             "TX PACKET",
             "TX DROPPED",
             "TX ERRORS",
             "TX MISSED"
             ]

cgroup_cols = [
    "TIME",
    "ANON",
    "FILE",
    "KERNEL",
    "KERNEL STACK",
    "PAGETABLES",
    "SEC PAGETABLES",
    "PERCPU",
    "SOCK",
    "VMALLOC",
    "SHMEM",
    "ZSWAP",
    "ZSWAPPED",
    "FILE MAPPED",
    "FILE DIRTY",
    "FILE WRITEBACK",
    "SWAPCACHED",
    "ANON THP",
    "FILE THP",
    "SHMEM THP",
    "INACTIVE ANON",
    "ACTIVE ANON",
    "INACTIVE FILE",
    "ACTIVE FILE",
    "UNEVICTABLE",
    "SLAB RECLAIMABLE",
    "SLAB UNRECLAIMABLE",
    "SLAB",
    "WORKINGSET REFAULT ANON",
    "WORKINGSET REFAULT FILE",
    "WORKINGSET ACTIVATE ANON",
    "WORKINGSET ACTIVATE FILE",
    "WORKINGSET RESTORE ANON",
    "WORKINGSET RESTORE FILE",
    "WORKINGSET NODERECLAIM",
    "PGDEMOTE KSWAPD",
    "PGDEMOTE DIRECT",
    "PGDEMOTE KHUGEPAGED",
    "PGPROMOTE SUCCESS",
    "PGSCAN",
    "PGSTEAL",
    "PGSCAN KSWAPD",
    "PGSCAN DIRECT",
    "PGSCAN KHUGEPAGED",
    "PGSTEAL KSWAPD",
    "PGSTEAL DIRECT",
    "PGSTEAL KHUGEPAGED",
    "PGFAULT",
    "PGMAJFAULT",
    "PGREFILL",
    "PGACTIVATE",
    "PGDEACTIVATE",
    "PGLAZYFREE",
    "PGLAZYFREED",
    "SWPIN ZERO",
    "SWPOUT ZERO",
    "ZSWPIN",
    "ZSWPOUT",
    "ZSWPWB",
    "THP FAULT ALLOC",
    "THP COLLAPSE ALLOC",
    "THP SWPOUT",
    "THP SWPOUT FALLBACK",
    "NUMA PAGES MIGRATED",
    "NUMA PTE UPDATES",
    "NUMA HINT FAULTS",
    "MEMORY CURRENT",
    "SWAP CURRENT",
    "MEMORY MAX",
    "PRESSURE AVG10",
    "SUMMED MEMORY",
    "VM FREE USED",
    "VM FREE BUFCACHE",
    "SWAP IN",
    "SWAP OUT",
    "PGPG IN",
    "PGPG OUT",
    "HOST CPU",
    "LOAD AVERAGE"
]

def process_main_stats(stat_file, conn, exp_name):
    reg_match = re.search(fr'{exp_name}_(\d+-\d+-\d+-\d+-\d+-\d+).csv', stat_file)
    date = reg_match.group(1)

    conn.sql(f"CREATE OR REPLACE TEMP TABLE data AS SELECT * FROM read_csv('{stat_file}', header=true, null_padding=true)")

    try:
        conn.sql(f"CREATE TABLE stats AS SELECT '{exp_name}' as name, '{date}' as date, \"{"\",\"".join(main_cols)}\" FROM data")
    except:
        conn.sql(f"INSERT INTO stats (SELECT '{exp_name}' as name, '{date}' as date, \"{"\",\"".join(main_cols)}\" FROM data)")

    query = """
    CREATE TABLE IF NOT EXISTS viewers (
    exp_name VARCHAR,
    date VARCHAR,
    client_id INTEGER,
    time INTEGER,
    target INTEGER,
    bitrate INTEGER,
    rtt INTEGER,
    delay INTEGER,
    fps INTEGER,
    resolution VARCHAR,
    rid VARCHAR
    )
    """

    conn.sql(query)

    df = conn.execute("SELECT COUNT(*) AS numcols FROM (DESCRIBE data)").pl()

    num_viewers = (df["numcols"][0] - len(main_cols)) // 7

    client_id = 0
    i = 0
    while i < num_viewers:
        query = f"""INSERT INTO viewers
        SELECT '{exp_name}' as exp_name,
        '{date}' as date,
        '{client_id}' as client_id,
        TIME as time,
        "VM-VIEWER-{client_id} TARGET" AS target,
        "VM-VIEWER-{client_id} BITRATE" AS bitrate,
        "VM-VIEWER-{client_id} RTT" AS rtt,
        "VM-VIEWER-{client_id} E2E DELAY" AS delay,
        "VM-VIEWER-{client_id} FPS" AS fps,
        "VM-VIEWER-{client_id} RESOLUTION" AS resolution,
        "VM-VIEWER-{client_id} RID" AS rid,
        FROM data
        """

        try:
            conn.sql(query)
            i+= 1
            client_id += 1
        except:
            client_id += 1

def process_cgroup_stats(stat_file, conn, exp_name):
    reg_match = re.search(fr'cgroups_{exp_name}_(\d+-\d+-\d+-\d+-\d+-\d+).csv', stat_file)
    date = reg_match.group(1)

    conn.sql(f"CREATE OR REPLACE TEMP TABLE data AS SELECT * FROM read_csv('{stat_file}', header=true, null_padding=true)")

    try:
        conn.sql(f"CREATE TABLE cgroup_stats AS SELECT '{exp_name}' as name, '{date}' as date, \"{"\",\"".join(cgroup_cols)}\" FROM data")
    except:
        conn.sql(f"INSERT INTO cgroup_stats (SELECT '{exp_name}' as name, '{date}' as date, \"{"\",\"".join(cgroup_cols)}\" FROM data)")


if __name__ == "__main__":

    dbfile='results.db'
    conn = duckdb.connect(dbfile)
    conn.sql("SET temp_directory = '/tmp/'")

    exp_name = os.getcwd().split('/')[-1]

    for f in os.listdir():
        if f.startswith(f"{exp_name}-") and f.endswith('.csv') and not '_average_' in f:
            process_main_stats(f, conn, exp_name)
        elif f.startswith("cgroups_") and f.endswith('.csv') and not '_average_' in f:
            process_cgroup_stats(f, conn, exp_name)

    cgroup_dir = ['cgroup_stats', 'cgroups_stat', 'cgroup_stat', 'cgroups_stats']

    back = os.getcwd()

    for d in cgroup_dir:
        if d in os.listdir():
            os.chdir(d)
            break

    for f in os.listdir():
        if f.startswith("cgroups_") and f.endswith('.csv') and not '_average_' in f:
            process_cgroup_stats(f, conn, exp_name)

    os.chdir(back)

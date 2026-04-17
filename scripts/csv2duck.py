#!/usr/bin/env python3

import duckdb
import sys
import os
import re

EXCLUDE_EXPS=[
    "cgroups-reclaim-swappiness2-simulcast-vp8",
    "cgroups-reclaim-swappiness3-simulcast-vp8",
    "default",
    "naive-reduction-simulcast-vp8",
    "network-vp8-l1t1",
    "spawn-simulcast-vp8",
    "spawnfill-cgroup-reduction-simulcast-vp8",
    "traffic-ballooning-1h-2",
    "traffic-cgroup-reclaim-stdev60s-1h",
    "cgroups-max-reduction-viewers10-thresh50-increase0"
]

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

ROOM_FIXED_COLS = [ "TIME","PARTICIPANT_ID","NUM_PARTICIPANTS","SENT_RTT","SENT_BITRATE","SENT_FPS" ]

def create_tables(conn):
    query = """
    CREATE TABLE IF NOT EXISTS stats (
    exp_name                  VARCHAR,
    date                      VARCHAR,
    TIME                      BIGINT,
    "MEMORY USED"               BIGINT,
    "MEMORY FREE"               BIGINT,
    "MEMORY MAX"                BIGINT,
    SWAP                      BIGINT,
    "CGROUP CACHE FILES"        VARCHAR,
    "CGROUP SWAPPABLE"          VARCHAR,
    "MEMORY PRESSURE AVG10"     DOUBLE,
    "MEMORY PRESSURE AVG60"     DOUBLE,
    "MEMORY PRESSURE AVG300"    DOUBLE,
    "MEMORY PRESSURE TOTAL"     BIGINT,
    "VIRSH ACTUAL"              BIGINT,
    "VIRSH UNUSED"              BIGINT,
    "VIRSH USABLE"              BIGINT,
    "VIRSH AVAILABLE"           BIGINT,
    "VIRSH SWAP IN"             BIGINT,
    "VIRSH SWAP OUT"            BIGINT,
    "VIRSH MINOR FAULT"         BIGINT,
    "VIRSH MAJOR FAULT"         BIGINT,
    "PUBLISHER BITRATE"         BIGINT,
    "PUBLISHER FPS"             BIGINT,
    "PUBLISHER RESOLUTION"      VARCHAR,
    "PUBLISHER RTT"             BIGINT,
    "CONNECTION STATE"          BIGINT,
    "VIEWER COUNT"              BIGINT,
    "VM MEMORY USAGE"           BIGINT,
    "VM MEMORY FREE"            BIGINT,
    "VM CPU USAGE"              DOUBLE,
    "VM FREE TOTAL"             DOUBLE,
    "VM FREE USED"              DOUBLE,
    "VM FREE BUFCACHE"          DOUBLE,
    "MEDOOZE INCOMING LOST"     BIGINT,
    "MEDOOZE INCOMING DROP"     BIGINT,
    "MEDOOZE INCOMING BITRATE"  BIGINT,
    "MEDOOZE INCOMING NACK"     BIGINT,
    "MEDOOZE INCOMING PLI"      BIGINT,
    "RX PACKET"                 BIGINT,
    "RX DROPPED"                BIGINT,
    "RX ERRORS"                 BIGINT,
    "RX MISSED"                 BIGINT,
    "TX PACKET"                 BIGINT,
    "TX DROPPED"                BIGINT,
    "TX ERRORS"                 BIGINT,
    "TX MISSED"                 BIGINT,
    "VIEWERS TARGET AVERAGE"    BIGINT,
    "VIEWERS BITRATE AVERAGE"   BIGINT,
    "VIEWERS RTT AVG"           BIGINT,
    "VIEWERS E2E AVG"           BIGINT,
    "VIEWERS FPS AVERAGE"       BIGINT
    )
    """

    conn.sql(query)

    query = """
    CREATE TABLE IF NOT EXISTS cgroup_stats (
    exp_name                  VARCHAR,
    date                      VARCHAR,
    TIME                      BIGINT,
    ANON                      BIGINT,
    FILE                      BIGINT,
    KERNEL                    BIGINT,
    "KERNEL STACK"              BIGINT,
    PAGETABLES                BIGINT,
    "SEC PAGETABLES"            BIGINT,
    PERCPU                    BIGINT,
    SOCK                      BIGINT,
    VMALLOC                   BIGINT,
    SHMEM                     BIGINT,
    ZSWAP                     BIGINT,
    ZSWAPPED                  BIGINT,
    "FILE MAPPED"               BIGINT,
    "FILE DIRTY"                BIGINT,
    "FILE WRITEBACK"            BIGINT,
    SWAPCACHED                BIGINT,
    "ANON THP"                  BIGINT,
    "FILE THP"                  BIGINT,
    "SHMEM THP"                 BIGINT,
    "INACTIVE ANON"             BIGINT,
    "ACTIVE ANON"               BIGINT,
    "INACTIVE FILE"             BIGINT,
    "ACTIVE FILE"               BIGINT,
    UNEVICTABLE               BIGINT,
    "SLAB RECLAIMABLE"          BIGINT,
    "SLAB UNRECLAIMABLE"        BIGINT,
    SLAB                      BIGINT,
    "WORKINGSET REFAULT ANON"   BIGINT,
    "WORKINGSET REFAULT FILE"   BIGINT,
    "WORKINGSET ACTIVATE ANON"  BIGINT,
    "WORKINGSET ACTIVATE FILE"  BIGINT,
    "WORKINGSET RESTORE ANON"   BIGINT,
    "WORKINGSET RESTORE FILE"   BIGINT,
    "WORKINGSET NODERECLAIM"    BIGINT,
    "PGDEMOTE KSWAPD"           BIGINT,
    "PGDEMOTE DIRECT"           BIGINT,
    "PGDEMOTE KHUGEPAGED"       BIGINT,
    "PGPROMOTE SUCCESS"         BIGINT,
    PGSCAN                    BIGINT,
    PGSTEAL                   BIGINT,
    "PGSCAN KSWAPD"             BIGINT,
    "PGSCAN DIRECT"             BIGINT,
    "PGSCAN KHUGEPAGED"         BIGINT,
    "PGSTEAL KSWAPD"            BIGINT,
    "PGSTEAL DIRECT"            BIGINT,
    "PGSTEAL KHUGEPAGED"        BIGINT,
    PGFAULT                   BIGINT,
    PGMAJFAULT                BIGINT,
    PGREFILL                  BIGINT,
    PGACTIVATE                BIGINT,
    PGDEACTIVATE              BIGINT,
    PGLAZYFREE                BIGINT,
    PGLAZYFREED               BIGINT,
    "SWPIN ZERO"                BIGINT,
    "SWPOUT ZERO"               BIGINT,
    ZSWPIN                    BIGINT,
    ZSWPOUT                   BIGINT,
    ZSWPWB                    BIGINT,
    "THP FAULT ALLOC"           BIGINT,
    "THP COLLAPSE ALLOC"        BIGINT,
    "THP SWPOUT"                BIGINT,
    "THP SWPOUT FALLBACK"       BIGINT,
    "NUMA PAGES MIGRATED"       BIGINT,
    "NUMA PTE UPDATES"          BIGINT,
    "NUMA HINT FAULTS"          BIGINT,
    "MEMORY CURRENT"            BIGINT,
    "SWAP CURRENT"              BIGINT,
    "MEMORY MAX"                BIGINT,
    "PRESSURE AVG10"            DOUBLE,
    "SUMMED MEMORY"             BIGINT,
    "VM FREE USED"              DOUBLE,
    "VM FREE BUFCACHE"          DOUBLE,
    "SWAP IN"                   BIGINT,
    "SWAP OUT"                  BIGINT,
    "PGPG IN"                   BIGINT,
    "PGPG OUT"                  BIGINT,
    "HOST CPU"                  VARCHAR,
    "LOAD AVERAGE"              VARCHAR
    )
    """

    conn.sql(query)

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

    query = """
    CREATE TABLE IF NOT EXISTS room_receivers(
    exp_name VARCHAR,
    date VARCHAR,
    room_id VARCHAR,
    time BIGINT,
    participant_id VARCHAR,
    receiving_participant_id VARCHAR,
    BITRATE BIGINT,
    RTT BIGINT,
    FPS BIGINT
    )
    """

    conn.sql(query)

def process_main_stats(stat_file, conn, exp_name):
    reg_match = re.search(fr'{exp_name}_(\d+-\d+-\d+-\d+-\d+-\d+)(?:_average)?.csv', stat_file)
    if not reg_match:
        return

    date = reg_match.group(1)

    # check if already exists
    conn.execute(f"SELECT * FROM stats WHERE exp_name='{exp_name}' AND date='{date}'")
    if conn.fetchone():
        return

    conn.sql(f"CREATE OR REPLACE TEMP TABLE data AS SELECT * FROM read_csv('{stat_file}', header=true, null_padding=true, nullstr=['NaN', 'nan', 'NA', 'NULL', ''])")
    conn.sql(f"INSERT INTO stats BY NAME (SELECT '{exp_name}' as exp_name, '{date}' as date, COLUMNS(lambda c: c NOT LIKE 'VM-VIEWER-%' AND c NOT IN ['h','m','l']) FROM data)")

    df = conn.execute("SHOW data").pl()
    has_viewers = False

    for col in df["column_name"]:
        if col.startswith('VM-VIEWER'):
            has_viewers = True
            break

    if has_viewers:
        df = conn.execute("SELECT COUNT(*) AS numcols FROM (DESCRIBE data)").pl()

        num_viewers = (df["numcols"][0] - len(main_cols)) // 7

        client_id = 0
        i = 0
        while i < num_viewers and (client_id - i) < 50:
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
    reg_match = re.search(fr'cgroups_{exp_name}_(\d+-\d+-\d+-\d+-\d+-\d+)(?:_average)?.csv', stat_file)
    if not reg_match:
        return

    date = reg_match.group(1)

    # check if already exists
    conn.execute(f"SELECT * FROM cgroup_stats WHERE exp_name='{exp_name}' AND date='{date}'")
    if conn.fetchone():
        return

    conn.sql(f"CREATE OR REPLACE TEMP TABLE data AS SELECT * FROM read_csv('{stat_file}', header=true, null_padding=true, nullstr=['NaN', 'nan', 'NA', 'NULL', ''])")
    conn.sql(f"INSERT INTO cgroup_stats BY NAME (SELECT '{exp_name}' as exp_name, '{date}' as date, * FROM data)")

def process_rooms_stats(stat_file, conn, exp_name):
    reg_match = re.search(fr'room(\d+)_{exp_name}_(\d+-\d+-\d+-\d+-\d+-\d+).csv', stat_file)
    if not reg_match:
        return

    index = reg_match.group(1)
    date = reg_match.group(2)

    # check if already exists
    try:
        conn.execute(f"SELECT * FROM room_stats WHERE exp_name='{exp_name}' AND date='{date}'")
        if conn.fetchone():
            return
    except:
        pass

    print(stat_file)

    conn.sql(f"CREATE OR REPLACE TEMP TABLE data AS SELECT * FROM read_csv('{stat_file}', header=true, null_padding=true, nullstr=['NaN', 'nan', 'NA', 'NULL', ''],ignore_errors=true)")

    properties = ["BITRATE", "RTT", "FPS"]

    df = conn.execute("SELECT DISTINCT ON(PARTICIPANT_ID) TIME,PARTICIPANT_ID FROM data ORDER BY TIME,rowid").pl()
    participants = []
    headers = ROOM_FIXED_COLS[:]

    for participant in df['PARTICIPANT_ID']:
        for prop in properties:
            participants.append(f"{participant}")
            headers.append(f"{participant}_{prop}")

    df = conn.execute("SHOW TABLE data").pl()

    for i in range(len(headers)):
        if df['column_name'][i].startswith('column'):
            conn.sql(f"ALTER TABLE data RENAME \"{df['column_name'][i]}\" TO \"{headers[i]}\"")

    try:
        conn.sql(f"CREATE TABLE room_stats AS SELECT '{exp_name}' as exp_name, '{date}' as date, 'room{index}' as room_id, \"{"\",\"".join(ROOM_FIXED_COLS)}\" FROM data")
    except:
        conn.sql(f"INSERT INTO room_stats (SELECT '{exp_name}' as exp_name, '{date}' as date, 'room{index}' as room_id, \"{"\",\"".join(ROOM_FIXED_COLS)}\" FROM data)")

    for participant in participants:
        query = f"""
        INSERT INTO room_receivers
        SELECT '{exp_name}' as exp_name, '{date}' as date, 'room{index}' as room_id,
          TIME, participant_id, '{participant}' as sending_participant_id,
          "{participant}_BITRATE", "{participant}_RTT", "{participant}_FPS"
        FROM data
        """

        conn.sql(query)

def parse_exp(conn, exp_name):
    print(os.getcwd())
    for f in os.listdir():
        if f.startswith(f"{exp_name}") and f.endswith('.csv') and not '_average_' in f:
            process_main_stats(f, conn, exp_name)
        elif f.startswith("cgroups_") and f.endswith('.csv') and not '_average_' in f:
            process_cgroup_stats(f, conn, exp_name)
        elif f.startswith("room") and f.endswith('.csv') and not '_average_' in f:
            process_rooms_stats(f, conn, exp_name)

    cgroup_dir = ['cgroup_stats', 'cgroups_stat', 'cgroup_stat', 'cgroups_stats', 'cgroups', 'cgroup']

    back = os.getcwd()

    for d in cgroup_dir:
        if d in os.listdir():
            os.chdir(d)
            break

    for f in os.listdir():
        if f.startswith("cgroups_") and f.endswith('.csv') and not '_average_' in f:
            process_cgroup_stats(f, conn, exp_name)

    os.chdir(back)

    if 'rooms' in os.listdir():
        os.chdir('rooms')

        room_wd = os.getcwd()

        for d in os.listdir():
            if d.startswith('room') and os.path.isdir(d):
                os.chdir(d)
                for f in os.listdir():
                    if f.startswith("room") and f.endswith('.csv') and not '_average_' in f:
                        process_rooms_stats(f, conn, exp_name)

                os.chdir(room_wd)

        os.chdir(back)

def explore(conn):
    for d in os.listdir():
       if os.path.isdir(d):
           back = os.getcwd()
           os.chdir(d)
           exp_name = os.getcwd().split('/')[-1]

           if any([ f.startswith(exp_name) and f.endswith('.csv') for f in os.listdir() ]) and not exp_name in EXCLUDE_EXPS:
               #try:
               parse_exp(conn, exp_name)
               #except:
               #    print(exp_name)
           else:
               explore(conn)

           os.chdir(back)

if __name__ == "__main__":

    dbfile='results.db'
    conn = duckdb.connect(dbfile)
    conn.sql("SET temp_directory = '/tmp/'")

    create_tables(conn)

    os.chdir('results')

    print(os.getcwd())
    explore(conn)
    print(os.getcwd())

    # parse_exp(conn, 'visio-perf-maxroom2')
    # process_rooms_stats('room4_visio-perf-maxroom_02-06-2025-13-33-49.csv', conn, 'visio-perf-maxroom')

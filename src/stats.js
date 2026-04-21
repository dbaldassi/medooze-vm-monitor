
import FS from "fs";
import config from '../config/config.json' with { type: 'json' };
import { DuckDBInstance, DuckDBDataChunk, VARCHAR, INTEGER, DOUBLE } from '@duckdb/node-api';

class StatsLogger {
    constructor() {
        this.setup_duckdb();

        this.info = {
            // Not used, why not remove it ? I'll think about it
            last_modified: undefined,

            // time
            time: 0,
        
            // all purpose ingo
            viewer_count: 0,
            is_publisher_connected: false,
            is_medooze_connected: false,

            // publisher stats
            publisher_bitrate: undefined,
            publisher_fps: undefined,
            publisher_res: undefined,
            publisher_pc_state: undefined,
            publisher_rtt: undefined,

            // cgroup memory stats
            ram_usage: undefined,
            ram_free: undefined,
            swap_usage: undefined,
            maxram: config.initial_max_ram,
            pressure_avg10: 0,
            pressure_avg60: 0,
            pressure_avg300: 0,
            pressure_total: 0,
            anon: 0,
            file: 0,
            kernel_stack: 0,
            slab: 0,
            slab_reclaimable: 0,
            slab_unreclaimable: 0,
            sock: 0,
            shmem: 0,
            file_mapped: 0,
            file_dirty: 0,
            file_writeback: 0,
            anon_thp: 0,
            inactive_anon: 0,
            active_anon: 0,
            inactive_file: 0,
            active_file: 0,
            unevictable: 0,
            workingset_refault: 0,
            workingset_activate: 0,
            workingset_nodereclaim: 0,
            pgfault: 0,
            pgmajfault: 0,
            pglazyfree: 0,
            pglazyfreed: 0,
            
            // vm system stats
            vm_ram_usage: undefined,
            vm_ram_free: undefined,
            vm_cpu_usage: undefined,
        
            // medooze incoming
            medooze_incoming_lost: 0,
            medooze_incoming_drop: 0,
            medooze_incoming_bitrate: 0,
            medooze_incoming_nack: 0,
            medooze_incoming_pli: 0,
        
            //ip link stats
            rx_packet: 0,
            rx_dropped: 0,
            rx_missed: 0,
            rx_errors: 0,
            tx_packet: 0,
            tx_dropped: 0,
            tx_missed: 0,
            tx_errors: 0,

            // virsh dommeminfo
            virsh_actual: 0, // The actual memory size in KiB available with ballooning enabled
            virsh_unused: 0, //  That memory is available for immediate use as it is currently neither used by processes or the kernel
            virsh_usable: 0, // This consists of the free space plus the space, which can be easily reclaimed. This for example includes read caches, which contain data read from IO devices, from which the data can be read again if the need arises in the future.
            virsh_available: 0, // This is the maximum allowed memory, which is slightly less than the currently configured memory size
            virsh_swap_in: 0, // The number of swapped-in pages as reported by the guest OS since the start of the VM.
            virsh_swap_out: 0,  // The number of swapped-out pages as reported by the guest OS since the start of the VM.
            virsh_minor_fault: 0, // The number of page faults as reported by the guest OS since the start of the VM. Minor page faults happen quiet often, for example when first accessing newly allocated memory or on copy-on-write. 
            virsh_major_fault: 0, // The number of page faults as reported by the guest OS since the start of the VM. Major page faults on the other hand require disk IO as some data is accessed, which must be paged in from disk first.

            viewers: new Map(),
            rooms: new Map()
        };
    }

    set_exp_name(name) {
        this.exp_name = name;
        this.date = new Date().toLocaleString('fr-FR').replaceAll(' ', '-').replaceAll('/', '-').replaceAll(':', '-');
    }

    async setup_duckdb() {
        this.duck_promise = Promise.withResolvers();

        this.instance = await DuckDBInstance.create('results.db');
        this.connection = await this.instance.connect()

        await this.connection.run(`
    CREATE TABLE IF NOT EXISTS virsh_stats (
    exp_name                  VARCHAR,
    date                      VARCHAR,
    TIME                      BIGINT,
    "VIRSH ACTUAL"            BIGINT,
    "VIRSH UNUSED"            BIGINT,
    "VIRSH USABLE"            BIGINT,
    "VIRSH AVAILABLE"         BIGINT,
    "VIRSH SWAP IN"           BIGINT,
    "VIRSH SWAP OUT"          BIGINT,
    "VIRSH MINOR FAULT"       BIGINT,
    "VIRSH MAJOR FAULT"       BIGINT,
    );

    CREATE TABLE IF NOT EXISTS medooze_stats (
    exp_name                     VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "MEDOOZE INCOMING LOST"     BIGINT,
    "MEDOOZE INCOMING DROP"     BIGINT,
    "MEDOOZE INCOMING BITRATE"  BIGINT,
    "MEDOOZE INCOMING NACK"     BIGINT,
    "MEDOOZE INCOMING PLI"      BIGINT,
    );

    CREATE TABLE IF NOT EXISTS guest_stats (
    exp_name                    VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "VM MEMORY USAGE"           BIGINT,
    "VM MEMORY FREE"            BIGINT,
    "VM CPU USAGE"              DOUBLE,
    "VM FREE TOTAL"             DOUBLE,
    "VM FREE USED"              DOUBLE,
    "VM FREE BUFCACHE"          DOUBLE,
    "RX PACKET"                 BIGINT,
    "RX DROPPED"                BIGINT,
    "RX ERRORS"                 BIGINT,
    "RX MISSED"                 BIGINT,
    "TX PACKET"                 BIGINT,
    "TX DROPPED"                BIGINT,
    "TX ERRORS"                 BIGINT,
    "TX MISSED"                 BIGINT,
    );

    CREATE TABLE IF NOT EXISTS publisher_stats (
    exp_name                    VARCHAR,
    date                        VARCHAR,
    TIME                        BIGINT,
    "PUBLISHER BITRATE"         BIGINT,
    "PUBLISHER FPS"             BIGINT,
    "PUBLISHER RESOLUTION"      VARCHAR,
    "PUBLISHER RTT"             BIGINT,
    "CONNECTION STATE"          BIGINT,
    "VIEWER COUNT"              BIGINT,
    );

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
    );

    CREATE TABLE IF NOT EXISTS viewers_stats (
    exp_name VARCHAR,
    date VARCHAR,
    client_id VARCHAR,
    TIME INTEGER,
    target INTEGER,
    bitrate INTEGER,
    rtt INTEGER,
    delay INTEGER,
    fps INTEGER,
    resolution VARCHAR,
    rid VARCHAR
    );

    CREATE TABLE IF NOT EXISTS room_receivers(
    exp_name VARCHAR,
    date VARCHAR,
    room_id VARCHAR,
    TIME BIGINT,
    participant_id VARCHAR,
    receiving_participant_id VARCHAR,
    BITRATE BIGINT,
    RTT BIGINT,
    FPS BIGINT
    )
    `
                      );

        this.duck_promise.resolve();
    }

    async log_room() {
        const rooms = this.info.rooms;

        for (const [room_id, room] of rooms) {
            // Check if the CSV writer for this room already exists
            if (!room.csv || room.headers_modified) {
                // Create a new CSV writer for this room
                room.csv = createCsvWriter({
                    path: `${room_id}_stats.csv`,
                    header: room.csv_header,
                    append: room.headers_modified // Set to true if you want to append to the file
                });

                room.headers_modified = false; // Reset the flag after creating the writer
            }

            // Add the stats for each participant in the room
            for (const [participant_id, stats] of room.participants) {
                let line = {
                    time: this.info.time,
                    participant_id: participant_id,
                    num_participants: room.participants.size,
                };

                for(const stat of stats) {
                    if(stat.id === participant_id) {
                        // Add the stats to the line
                        line["sent_bitrate"] = stat.bitrate;
                        line["sent_rtt"] = stat.rtt;
                        line["sent_fps"] = stat.fps;
                    }
                    else {
                        // Add the stats to the line
                        line[`${stat.id}_bitrate`] = stat.bitrate;
                        line[`${stat.id}_rtt`] = stat.rtt;
                        line[`${stat.id}_fps`] = stat.fps;
                    }
                }

                // Write the line to the CSV file
                await room.csv.writeRecords([line]);
            }
        }
    }

    async append_to_table(table_config) {
        const appender = await this.connection.createAppender(table_config.name);
        const chunk = DuckDBDataChunk.create(table_config.types);
        chunk.setRows(table_config.values);

        appender.appendDataChunk(chunk);
        appender.flushSync();
    }

    async log_info() {
        await this.duck_promise.promise;

        this.append_to_table({
            name: 'virsh_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[this.exp_name, this.date, this.info.time,
             this.info.virsh_actual, this.info.virsh_unused, this.info.virsh_usable,
             this.info.virsh_available, this.info.virsh_swap_in, this.info.virsh_swap_out,
             this.info.virsh_minor_fault, this.info.virsh_major_fault]]
        });

        this.append_to_table({
            name: 'medooze_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[this.exp_name, this.date, this.info.time, this.info.medooze_incoming_lost, this.info.medooze_incoming_drop,
                     this.info.medooze_incoming_bitrate, this.info.medooze_incoming_nack, this.info.medooze_incoming_pli]]
        });

        this.append_to_table({
            name: 'guest_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, DOUBLE, DOUBLE, DOUBLE, DOUBLE, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER],
            values: [[this.exp_name, this.date, this.info.time, this.info.vm_ram_usage, this.info.vm_ram_free, this.info.vm_cpu_usage,
                     this.info.vm_free_total, this.info.vm_free_used, this.info.vm_free_bufcache,
                     this.info.rx_packet, this.info.rx_dropped, this.info.rx_missed, this.info.rx_errors,
                     this.info.tx_packet, this.info.tx_dropped, this.info.tx_missed, this.info.tx_errors
                    ]]
        });

        this.append_to_table({
            name: 'publisher_stats',
            types: [VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, VARCHAR, INTEGER, INTEGER, INTEGER],
            values: [[this.exp_name, this.date, this.info.time, this.info.publisher_bitrate, this.info.publisher_fps,
                     this.info.publisher_res, this.info.publisher_rtt, this.info.publisher_pc_state, this.info.viewer_count
                    ]]
        });

        this.append_to_table({
            name: 'cgroup_stats',
            types: [VARCHAR, VARCHAR, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER,
                    DOUBLE, INTEGER, DOUBLE, DOUBLE, INTEGER, INTEGER, INTEGER, INTEGER, VARCHAR, VARCHAR
                   ],
            values: [[this.exp_name, this.date, this.info.time,this.info.anon,this.info.file,this.info.kernel,this.info.kernel_stack,
                     this.info.pagetables,this.info.sec_pagetables,this.info.percpu,this.info.sock,this.info.vmalloc,this.info.shmem,
                     this.info.zswap,this.info.zswapped,this.info.file_mapped,this.info.file_dirty,this.info.file_writeback,
                     this.info.swapcached,this.info.anon_thp,this.info.file_thp,this.info.shmem_thp,this.info.inactive_anon,
                     this.info.active_anon,this.info.inactive_file,this.info.active_file,this.info.unevictable,this.info.slab_reclaimable,
                     this.info.slab_unreclaimable,this.info.slab,this.info.workingset_refault_anon,this.info.workingset_refault_file,
                     this.info.workingset_activate_anon,this.info.workingset_activate_file,this.info.workingset_restore_anon,
                     this.info.workingset_restore_file,this.info.workingset_nodereclaim,this.info.pgdemote_kswapd,
                     this.info.pgdemote_direct,this.info.pgdemote_khugepaged,this.info.pgpromote_success,this.info.pgscan,
                     this.info.pgsteal,this.info.pgscan_kswapd,this.info.pgscan_direct,this.info.pgscan_khugepaged,
                     this.info.pgsteal_kswapd,this.info.pgsteal_direct,this.info.pgsteal_khugepaged,this.info.pgfault,
                     this.info.pgmajfault,this.info.pgrefill,this.info.pgactivate,this.info.pgdeactivate,this.info.pglazyfree,
                     this.info.pglazyfreed,this.info.swpin_zero,this.info.swpout_zero,this.info.zswpin,this.info.zswpout,
                     this.info.zswpwb,this.info.thp_fault_alloc,this.info.thp_collapse_alloc,this.info.thp_swpout,
                     this.info.thp_swpout_fallback,this.info.numa_pages_migrated,this.info.numa_pte_updates,this.info.numa_hint_faults,
                     this.info.ram_usage,this.info.swap_usage,this.info.maxram,this.info.pressure_avg10,this.info.summed_memory,
                     this.info.vm_free_used,this.info.vm_free_bufcache,this.info.swapin,this.info.swapout,this.info.pgpgin,
                     this.info.pgpgout,this.info.host_cpu,this.info.load_average
                    ]]
        });

        let viewer_rows = [];
        this.info.viewers.forEach((v,k) => viewer_rows.push([this.exp_name, this.date, k, this.info.time, v.target, v.bitrate, v.rtt, v.e2e, v.fps, v.res, v.rid]));
        this.append_to_table({
            name: 'viewers_stats',
            types: [VARCHAR, VARCHAR, VARCHAR, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, INTEGER, VARCHAR, VARCHAR],
            values: viewer_rows
        })

        // this.log_room();
    }
}

// glogbal / singleton
export var logger = new StatsLogger;

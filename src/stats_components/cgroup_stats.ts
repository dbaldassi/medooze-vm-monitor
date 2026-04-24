
import { logger, StatsComponent, TableMetadata } from '../stats.js';
import { DuckDBConnection, DuckDBDataChunk, DuckDBMaterializedResult, VARCHAR, INTEGER, DOUBLE } from 'npm:@duckdb/node-api';

type CgroupStats = {
    anon: number;
    file: number;
    kernel: number;
    kernel_stack: number;
    pagetables: number;
    sec_pagetables: number;
    percpu: number;
    sock: number;
    vmalloc: number;
    shmem: number;
    zswap: number;
    zswapped: number;
    file_mapped: number;
    file_dirty: number;
    file_writeback: number;
    swapcached: number;
    anon_thp: number;
    file_thp: number;
    shmem_thp: number;
    inactive_anon: number;
    active_anon: number;
    inactive_file: number;
    active_file: number;
    unevictable: number;
    slab_reclaimable: number;
    slab_unreclaimable: number;
    slab: number;
    workingset_refault_anon: number;
    workingset_refault_file: number;
    workingset_activate_anon: number;
    workingset_activate_file: number;
    workingset_restore_anon: number;
    workingset_restore_file: number;
    workingset_nodereclaim: number;
    pgdemote_kswapd: number;
    pgdemote_direct: number;
    pgdemote_khugepaged: number;
    pgpromote_success: number;
    pgscan: number;
    pgsteal: number;
    pgscan_kswapd: number;
    pgscan_direct: number;
    pgscan_khugepaged: number;
    pgsteal_kswapd: number;
    pgsteal_direct: number;
    pgsteal_khugepaged: number;
    pgfault: number;
    pgmajfault: number;
    pgrefill: number;
    pgactivate: number;
    pgdeactivate: number;
    pglazyfree: number;
    pglazyfreed: number;
    swpin_zero: number;
    swpout_zero: number;
    zswpin: number;
    zswpout: number;
    zswpwb: number;
    thp_fault_alloc: number;
    thp_collapse_alloc: number;
    thp_swpout: number;
    thp_swpout_fallback: number;
    numa_pages_migrated: number;
    numa_pte_updates: number;
    numa_hint_faults: number;
    ram_usage: number;
    ram_free: number;
    swap_usage: number;
    maxram: number;
    pressure_avg10: number;
    summed_memory: number;
    vm_free_used: number;
    vm_free_bufcache: number;
    swapin: number;
    swapout: number;
    pgpgin: number;
    pgpgout: number;
    host_cpu: number;
    load_average: number;
}

export interface StatsListener {
    fetch(): void;
}

export class CgroupStatsComponent implements StatsComponent {
    public info: CgroupStats;
    private listener: StatsListener;

    constructor(listener: StatsListener) {
        this.info = new CgroupStats;
        this.listener = listener;
    }

    public fetch(): void {
        this.listener.fetch();
    }

    public create_table(conn: DuckDBConnection): Promise<DuckDBMaterializedResult> {
        return conn.run(`
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
    "HOST CPU"                  BIGINT,
    "LOAD AVERAGE"              BIGINT
    );
`);
    }

    public drop_table(conn: DuckDBConnection): void {

    }

    public update_table(metadata: TableMetadata): void {
        logger.append_to_table({
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
            values: [[metadata.exp_name, metadata.date, metadata.time,this.info.anon,this.info.file,this.info.kernel,this.info.kernel_stack,
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
    }
    
}

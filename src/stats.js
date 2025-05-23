
const FS = require("fs");

const config = require('../config/config.json');
const { title } = require("process");
// Create csv logger to log all stats
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

class StatsLogger {
    constructor() {
        this.csv_name = 'stats.csv';
        this.csvWriter = undefined;
        
        // csv stats headers
        this.headers = [
            {id: 'time', title: 'TIME'},
            {id: 'ram_usage', title: 'MEMORY USED'},
            {id: 'ram_free', title: 'MEMORY FREE'},
            {id: 'maxram', title: 'MEMORY MAX'},
            {id: 'swap_usage', title: 'SWAP'},
            {id: 'cgroup_cache', title: 'CGROUP CACHE FILES'},
            {id: 'cgroup_swappable', title: 'CGROUP SWAPPABLE'},
            {id: 'pressure_avg10', title: 'MEMORY PRESSURE AVG10'},
            {id: 'pressure_avg60', title: 'MEMORY PRESSURE AVG60'},
            {id: 'pressure_avg300', title: 'MEMORY PRESSURE AVG300'},
            {id: 'pressure_total', title: 'MEMORY PRESSURE TOTAL'},
            {id: 'virsh_actual', title: 'VIRSH ACTUAL'},
            {id: 'virsh_unused', title: 'VIRSH UNUSED'},
            {id: 'virsh_usable', title: 'VIRSH USABLE'},
            {id: 'virsh_available', title: 'VIRSH AVAILABLE'},
            {id: 'virsh_swap_in', title: 'VIRSH SWAP IN'},
            {id: 'virsh_swap_out', title: 'VIRSH SWAP OUT'},
            {id: 'virsh_minor_fault', title: 'VIRSH MINOR FAULT'},
            {id: 'virsh_major_fault', title: 'VIRSH MAJOR FAULT'},
            {id: 'publisher_bitrate', title: 'PUBLISHER BITRATE'},
            {id: 'publisher_fps', title: 'PUBLISHER FPS'},
            {id: 'publisher_res', title: 'PUBLISHER RESOLUTION'},
            {id: 'publisher_rtt', title: 'PUBLISHER RTT'},
            {id: 'publisher_pc_state', title: 'CONNECTION STATE'},
            {id: 'viewer_count', title: 'VIEWER COUNT'},
            {id: 'vm_ram_usage', title: 'VM MEMORY USAGE'},
            {id: 'vm_ram_free', title: 'VM MEMORY FREE'},
            {id: 'vm_cpu_usage', title: 'VM CPU USAGE'},
            {id: 'vm_free_total', title: 'VM FREE TOTAL'},
            {id: 'vm_free_used', title: 'VM FREE USED'},
            {id: 'vm_free_bufcache', title: 'VM FREE BUFCACHE'},
            {id: 'medooze_incoming_lost', title: 'MEDOOZE INCOMING LOST'},
            {id: 'medooze_incoming_drop', title: 'MEDOOZE INCOMING DROP'},
            {id: 'medooze_incoming_bitrate', title: 'MEDOOZE INCOMING BITRATE'},
            {id: 'medooze_incoming_nack', title: 'MEDOOZE INCOMING NACK'},
            {id: 'medooze_incoming_pli', title: 'MEDOOZE INCOMING PLI'},
            {id: 'rx_packet', title: 'RX PACKET'},
            {id: 'rx_dropped', title: 'RX DROPPED'},
            {id: 'rx_errors', title: 'RX ERRORS'},
            {id: 'rx_missed', title: 'RX MISSED'},
            {id: 'tx_packet', title: 'TX PACKET'},
            {id: 'tx_dropped', title: 'TX DROPPED'},
            {id: 'tx_errors', title: 'TX ERRORS'},
            {id: 'tx_missed', title: 'TX MISSED'},
        ];

        // Headers spécifiques pour les stats cgroup
        this.cgroup_headers = [
            { id: 'time', title: 'TIME' },
            { id: 'anon', title: 'ANON' },
            { id: 'file', title: 'FILE' },
            { id: 'kernel', title: 'KERNEL' },
            { id: 'kernel_stack', title: 'KERNEL STACK' },
            { id: 'pagetables', title: 'PAGETABLES' },
            { id: 'sec_pagetables', title: 'SEC PAGETABLES' },
            { id: 'percpu', title: 'PERCPU' },
            { id: 'sock', title: 'SOCK' },
            { id: 'vmalloc', title: 'VMALLOC' },
            { id: 'shmem', title: 'SHMEM' },
            { id: 'zswap', title: 'ZSWAP' },
            { id: 'zswapped', title: 'ZSWAPPED' },
            { id: 'file_mapped', title: 'FILE MAPPED' },
            { id: 'file_dirty', title: 'FILE DIRTY' },
            { id: 'file_writeback', title: 'FILE WRITEBACK' },
            { id: 'swapcached', title: 'SWAPCACHED' },
            { id: 'anon_thp', title: 'ANON THP' },
            { id: 'file_thp', title: 'FILE THP' },
            { id: 'shmem_thp', title: 'SHMEM THP' },
            { id: 'inactive_anon', title: 'INACTIVE ANON' },
            { id: 'active_anon', title: 'ACTIVE ANON' },
            { id: 'inactive_file', title: 'INACTIVE FILE' },
            { id: 'active_file', title: 'ACTIVE FILE' },
            { id: 'unevictable', title: 'UNEVICTABLE' },
            { id: 'slab_reclaimable', title: 'SLAB RECLAIMABLE' },
            { id: 'slab_unreclaimable', title: 'SLAB UNRECLAIMABLE' },
            { id: 'slab', title: 'SLAB' },
            { id: 'workingset_refault_anon', title: 'WORKINGSET REFAULT ANON' },
            { id: 'workingset_refault_file', title: 'WORKINGSET REFAULT FILE' },
            { id: 'workingset_activate_anon', title: 'WORKINGSET ACTIVATE ANON' },
            { id: 'workingset_activate_file', title: 'WORKINGSET ACTIVATE FILE' },
            { id: 'workingset_restore_anon', title: 'WORKINGSET RESTORE ANON' },
            { id: 'workingset_restore_file', title: 'WORKINGSET RESTORE FILE' },
            { id: 'workingset_nodereclaim', title: 'WORKINGSET NODERECLAIM' },
            { id: 'pgdemote_kswapd', title: 'PGDEMOTE KSWAPD' },
            { id: 'pgdemote_direct', title: 'PGDEMOTE DIRECT' },
            { id: 'pgdemote_khugepaged', title: 'PGDEMOTE KHUGEPAGED' },
            { id: 'pgpromote_success', title: 'PGPROMOTE SUCCESS' },
            { id: 'pgscan', title: 'PGSCAN' },
            { id: 'pgsteal', title: 'PGSTEAL' },
            { id: 'pgscan_kswapd', title: 'PGSCAN KSWAPD' },
            { id: 'pgscan_direct', title: 'PGSCAN DIRECT' },
            { id: 'pgscan_khugepaged', title: 'PGSCAN KHUGEPAGED' },
            { id: 'pgsteal_kswapd', title: 'PGSTEAL KSWAPD' },
            { id: 'pgsteal_direct', title: 'PGSTEAL DIRECT' },
            { id: 'pgsteal_khugepaged', title: 'PGSTEAL KHUGEPAGED' },
            { id: 'pgfault', title: 'PGFAULT' },
            { id: 'pgmajfault', title: 'PGMAJFAULT' },
            { id: 'pgrefill', title: 'PGREFILL' },
            { id: 'pgactivate', title: 'PGACTIVATE' },
            { id: 'pgdeactivate', title: 'PGDEACTIVATE' },
            { id: 'pglazyfree', title: 'PGLAZYFREE' },
            { id: 'pglazyfreed', title: 'PGLAZYFREED' },
            { id: 'swpin_zero', title: 'SWPIN ZERO' },
            { id: 'swpout_zero', title: 'SWPOUT ZERO' },
            { id: 'zswpin', title: 'ZSWPIN' },
            { id: 'zswpout', title: 'ZSWPOUT' },
            { id: 'zswpwb', title: 'ZSWPWB' },
            { id: 'thp_fault_alloc', title: 'THP FAULT ALLOC' },
            { id: 'thp_collapse_alloc', title: 'THP COLLAPSE ALLOC' },
            { id: 'thp_swpout', title: 'THP SWPOUT' },
            { id: 'thp_swpout_fallback', title: 'THP SWPOUT FALLBACK' },
            { id: 'numa_pages_migrated', title: 'NUMA PAGES MIGRATED' },
            { id: 'numa_pte_updates', title: 'NUMA PTE UPDATES' },
            { id: 'numa_hint_faults', title: 'NUMA HINT FAULTS' },
            { id: 'ram_usage', title: 'MEMORY CURRENT' },
            { id: 'swap_usage', title: 'SWAP CURRENT' },
            { id: 'maxram', title: 'MEMORY MAX' },
            { id: 'pressure_avg10', title: 'PRESSURE AVG10' },
            { id: 'summed_memory', title: 'SUMMED MEMORY' },
            { id: 'vm_free_used', title: 'VM FREE USED'},
            { id: 'vm_free_bufcache', title: 'VM FREE BUFCACHE'},
            { id: 'swapin', title: 'SWAP IN'},
            { id: 'swapout', title: 'SWAP OUT'},
            { id: 'pgpgin', title: 'PGPG IN'},
            { id: 'pgpgout', title: 'PGPG OUT'},
            { id: 'host_cpu', title: 'HOST CPU'},
            { id: 'load_average', title: 'LOAD AVERAGE'},
        ];

        this.headers_init_len = this.headers.length;

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

            rooms: new Map()
        };

        this.create_writer(false);

        this.cgroupCsvWriter = createCsvWriter({
            path: "cgroups_stats.csv",
            header: this.cgroup_headers,
            append: false
        });
    }

    add_header(id, title) {
        this.headers.push({id : id, title : title});
    }

    sync_headers_sync(file) {
        // If no viewers added, nothing to do
        if(this.headers.length === this.headers_init_len) return;

        // Else rewrite csv headers
        const data =  FS.readFileSync(file, 'utf8');
        const new_headers = this.headers.map((e) => e.title).join(",");
        console.log(new_headers);
        const newData = data.replace(/.*/, new_headers);
        FS.writeFileSync(file, newData);
    }

    create_writer(append) {
        this.csvWriter = createCsvWriter({
            path: this.csv_name,
            header: this.headers,
            append: append
        }); 
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
    
    async log_info() {
        // write a new line into the csv file
        const records = [this.info];
        await this.csvWriter.writeRecords(records);

        const memoryComponents = [
            'anon',
            'file',
            'kernel_stack',
            'pagetables',
            'sec_pagetables',
            'shmem',
            'slab_reclaimable',
            'slab_unreclaimable',
            'sock',
            'zswap',
            'zswapped',
            'percpu'
        ];

        // Calcul de la somme des composantes de la mémoire
        let summedMemory = 0;
        memoryComponents.forEach(component => {
            if (this.info[component] !== undefined) {
                summedMemory += this.info[component];
            }
        });

        // Ajout de la valeur calculée à l'objet info
        this.info.summed_memory = summedMemory;

        const cgroup_records = [this.info];
        await this.cgroupCsvWriter.writeRecords(cgroup_records);

        this.log_room();
    }
}

// glogbal / singleton
var logger = new StatsLogger;

module.exports = logger;
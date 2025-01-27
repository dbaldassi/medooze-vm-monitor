const Path     = require("path");
const FS       = require("fs");
const Inotify  = require("node-inotify").Inotify;

const { exec, execSync } = require('node:child_process')

// Get logger
const logger = require('./stats.js');
// Get config
const config = require('./config.json');
const { readFileSync } = require("node:fs");

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

// Inotify
var inotify = new Inotify();

class SystemManager {
    constructor() {
        this.ram_usage_path  = Path.join(config.memory_stats_path, config.ram_usage_file);
        this.ram_total_path  = Path.join(config.memory_stats_path, config.ram_total_file);
        this.swap_usage_path = Path.join(config.memory_stats_path, config.swap_usage_file);
        this.swap_event_path = Path.join(config.memory_stats_path, config.swap_event_file);
        this.memory_event_path = Path.join(config.memory_stats_path, config.memory_event_file);
        this.memory_pressure_path = Path.join(config.memory_stats_path, config.memory_pressure_file);
        this.memory_reclaim_path = Path.join(config.memory_stats_path, config.memory_reclaim_file);

        this.swappiness = 0;
        
        // inotify.addWatch({ path: this.swap_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.swapevent_callback(event) });
        // inotify.addWatch({ path: this.memory_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.memoryevents_callback(event) });
        // inotify.addWatch({ path: this.memory_pressure_path, watch_for: Inotify.IN_MODIFY, callback: event => this.pressure_callback(event) });
    }

    fetch_ram_usage() {
        // Read current memory usage from cgroup file
        const data = FS.readFileSync(this.ram_usage_path);
        // Log it in csv file
        logger.info.ram_usage = parseInt(parseInt(data) / MEGA);
    }
    
    fetch_ram_free() {
        const data = FS.readFileSync(this.ram_total_path);
        // Log it into csv
        logger.info.ram_free = parseInt(parseInt(data) / (MEGA)) - logger.info.ram_usage;
    }
    
    fetch_swap_usage() {
        const data = FS.readFileSync(this.swap_usage_path);
        // Log it into csv
        logger.info.swap_usage = parseInt(parseInt(data) / MEGA);
    }

    fetch_memory_pressure() {
        const data = FS.readFileSync(this.memory_pressure_path);
        const some = data.toString().split('\n')[0];
        const pressure = some.split(' ');

        for(let p of pressure) {
            const fields = p.split('=');
            if(fields.length === 2) {
                logger.info[`pressure_${fields[0]}`] = parseFloat(fields[1]);
            }

        }
    }
    
    fetch_virsh_info() {
        exec("virsh dommemstat --domain medooze", (err, output) => {
            if(err) {
                console.error(err);
                return;
            }
            
            let lines = output.split('\n');
            for(let line of lines) {
                let splitted = line.split(' ');
                if(splitted.length === 2) {
                    logger.info[`virsh_${splitted[0]}`] = splitted[1];
                    // console.log(logger.info);
                }
            }
        });
    }

    pressure_callback(event) {
        if(event.mask & Inotify.IN_MODIFY) {
            console.log("Pressure has been modified");
        }
    }

    swapevent_callback(event) {
        if(event.mask & Inotify.IN_MODIFY) {
            console.log("swapevent has been modified");
            // const data = FS.readFileSync(this.swap_event_path);
            // console.log(data.toString());
        }
    }

    memoryevents_callback(event) {
        if(event.mask & Inotify.IN_MODIFY) {
            console.log("memory events has been modified");
            // const data = FS.readFileSync(this.memory_event_path);
            // console.log(data.toString());
        }
    }

    fetch_memory() {
        // console.log("fetch memory");
        this.fetch_ram_usage();
        this.fetch_ram_free();
        this.fetch_swap_usage();
        this.fetch_memory_pressure();
        this.fetch_virsh_info();
    }
    
    // Max in MiB
    set_max_ram(max) {
        // todo write max to memory.max
        console.log(max);
        // log in csv stats new max
        logger.info.maxram = max;
        // Write new max in the file
        FS.writeFileSync(this.ram_total_path, String(max * MEGA));
    }

    reclaim_memory(mem, swappiness) {
        try {
            let cmd = `${mem*1024*1024}`
            if(swappiness !== undefined) {
                cmd = `${cmd} swappiness=${swappiness}`;
            }

            console.log("Reclaiming", mem);

            FS.writeFileSync(this.memory_reclaim_path, cmd);
        } catch(error) {
            console.error(error);
            return false
        }

        return true
    }

    start_collecting(interval, callback) {
        // Set time interval
        this.time_interval = interval;
        // Start interval and keep ref to delete it
        this.fetch_memory_timeout = setInterval(() => {
            this.fetch_memory();
            if(callback) callback(logger.info.time);
        }, interval);
    }

    stop_collecting() {
        // Clear timeout that fetch memory
	    clearInterval(this.fetch_memory_timeout[Symbol.toPrimitive]());
    }

    memory_reduction() {
        const increment = 100;
        const threshold = increment / 2;
        const vm_mem = (logger.info.virsh_available - logger.info.virsh_usable) / 1024;

        console.log(logger.info.ram_usage, (vm_mem + 2 * increment));
        if(logger.info.swap_usage == 0 && logger.info.ram_free > threshold) {
            this.set_max_ram(logger.info.ram_usage + increment); // remove all free memory at the beginning
        }
        else if(logger.info.ram_usage > vm_mem + threshold) {
            this.set_max_ram(logger.info.maxram - increment); // Progressively decrease max memory
        }
        else if(logger.info.ram_usage <  (vm_mem + threshold / 10)) {
            this.set_max_ram(logger.info.maxram + 2 * increment);
        }
    }

    memory_reclaim() {
        const increment = 100; // 100 MiB
        const threshold = increment / 2;
        const vm_mem = (logger.info.virsh_available - logger.info.virsh_usable) / 1024;
    
        console.log(logger.info.ram_usage, vm_mem + threshold);
        if(logger.info.ram_usage > vm_mem + threshold) {
            let ret = false;
            while(!ret && this.swappiness < 100) {
                ret = this.reclaim_memory(increment, this.swappiness);
                if(!ret) {
                    this.swappiness += 10;
                    console.log(`Swappiness = ${this.swappiness}`);
                }
            }
        }
    }

    memory_reduction_ballon() {
        const increment = 100 * 1024; // 100M MiB
        const threshold = increment / 2;

        console.log(logger.info.virsh_usable / 1024, logger.info.virsh_available / 1024, logger.info.virsh_actual / 1024)

        if(logger.info.virsh_usable > threshold) {
            let new_vm_size = logger.info.virsh_actual - increment;
            SystemManager.quick_exec(`virsh setmem --domain medooze --size ${new_vm_size}K --current`);
        }
        else if(logger.info.virsh_usable < threshold / 10) {
            let new_vm_size = logger.info.virsh_actual + 2 * increment; // deflate
            SystemManager.quick_exec(`virsh setmem --domain medooze --size ${new_vm_size}K --current`);
        }
    }

    static quick_exec(cmd, opts) {
        exec(cmd, opts, (err, output) => {
            if(err) console.error(err);
            else console.log(output);
        });
    }

    static quick_exec_sync(cmd, opts) {
        execSync(cmd, opts, (err, output) => {
            if(err) console.error(err);
            else console.log(output);
        });
    }
}

module.exports = SystemManager;
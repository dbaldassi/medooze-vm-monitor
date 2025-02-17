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
        this.memory_stat_file = Path.join(config.memory_stats_path, config.memory_stat_file);

        this.swappiness = 0;
        this.mem_stat = {};

        this.pid = {
            kp : 1/10, // to be tuned
            ki : 1/200, // to be tuned
            kd : 1/10, // to be tuned
            
            prevError : 0,
            integrator : 0,

            dt : 10 // 10sec
        }
        
        // inotify.addWatch({ path: this.swap_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.swapevent_callback(event) });
        // inotify.addWatch({ path: this.memory_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.memoryevents_callback(event) });
        // inotify.addWatch({ path: this.memory_pressure_path, watch_for: Inotify.IN_MODIFY, callback: event => this.pressure_callback(event) });
    }

    fetch_ram_usage() {
        try {
            // Read current memory usage from cgroup file
            const data = FS.readFileSync(this.ram_usage_path);
            // Log it in csv file
            logger.info.ram_usage = parseInt(parseInt(data) / MEGA);
        } catch(e) {
            logger.info.ram_usage = 0;
        }
    }
    
    fetch_ram_free() {
        try {
            const data = FS.readFileSync(this.ram_total_path);
            // Log it into csv
            logger.info.ram_free = parseInt(parseInt(data) / (MEGA)) - logger.info.ram_usage;
        } catch(e) {
            logger.info.ram_free = 0;
        }
    }
    
    fetch_swap_usage() {
        try {
            const data = FS.readFileSync(this.swap_usage_path);
            // Log it into csv
            logger.info.swap_usage = parseInt(parseInt(data) / MEGA);
        } catch(e) {
            logger.info.swap_usage = 0;
        }
    }

    fetch_mem_stat() {
        try {
            const data = FS.readFileSync(this.memory_stat_file);

            for(let line of data.toString().split('\n')) {
                const split = line.split(' ');
                this.mem_stat[split[0]] = parseInt(split[1]);
            }
        } catch(e) {
        
        }
    }

    get_reclaimable_bytes() {
        this.fetch_mem_stat();

        let active_file = this.mem_stat["active_file"];
        let inactive_file = this.mem_stat["inactive_file"];
        logger.info.cgroup_cache = active_file + inactive_file;

        let active_anon = this.mem_stat["active_anon"];
        let inactive_anon = this.mem_stat["inactive_anon"];
        let anon = active_anon + inactive_anon;

        logger.info.cgroup_swappable = anon; // facebok OOM algo actually take the min of anon and swap free
        logger.info.cgroup_reclaimable = logger.info.cgroup_cache + logger.info.cgroup_swappable;

        return logger.info.cgroup_reclaimable;
    }

    fetch_memory_pressure() {
        try {
            const data = FS.readFileSync(this.memory_pressure_path);
            const some = data.toString().split('\n')[0];
            const pressure = some.split(' ');

            for(let p of pressure) {
                const fields = p.split('=');
                if(fields.length === 2) {
                    logger.info[`pressure_${fields[0]}`] = parseFloat(fields[1]);
                }
            }
        } catch(e) {}
    }
    
    fetch_virsh_info() {
        exec("virsh dommemstat --domain medooze", (err, output) => {
            if(err) {
                logger.info.virsh_actual = 0;
                console.error(err);
                return;
            }
            
            let lines = output.split('\n');
            for(let line of lines) {
                let splitted = line.split(' ');
                if(splitted.length === 2) {
                    logger.info[`virsh_${splitted[0]}`] = parseInt(splitted[1]);
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
        this.get_reclaimable_bytes();
    }

    pid_regul(target, measured) {
        let error = target - measured;
        console.log(target, measured);


        this.pid.integrator += error * this.pid.dt;
        
        let p = this.pid.kp * error;
        let i = this.pid.ki * this.pid.integrator;
        let d = this.pid.kd * (this.pid.prevError - error) / this.pid.dt;

        let out = p + i + d;

        console.log("pid : ", p, i, d, out);

        this.pid.prevError = error;

        return out;
    }
    
    // Max in MiB
    set_max_ram(max) {
        // todo write max to memory.max
        console.log(max);

        max = Math.max(max, 0); // don't write negative value 
        // log in csv stats new max
        logger.info.maxram = max;
        // Write new max in the file

        try {
            // let before = new Date();
            FS.writeFile(this.ram_total_path, String(max * MEGA), (err) => {
                if(err) console.error(err);
                else console.log("Wrote ", max);
            });
            // let after = new Date();
        } catch(error) {
            console.error(error);
        }
    }

    reclaim_memory(mem, swappiness) {

        try {
            let cmd = `${mem*1024*1024}`
            if(swappiness !== undefined) {
                // cmd = `${cmd} swappiness=${swappiness}`;
            }

            console.log("Reclaiming", mem);
            
            logger.info.maxram += 100; // mark to find where we begin reclaim when boxing plot

            // let before = new Date();
            FS.writeFile(this.memory_reclaim_path, cmd, (err) => {
                if(err) console.error(err);
                logger.info.maxram -= 100;
            });
            // let after = new Date();

            // console.log(after-before);
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

    memory_reduction(increment, threshold, increase) {
        const vm_mem = (logger.info.virsh_available - logger.info.virsh_usable) / 1024;

        console.log(logger.info.ram_usage, (vm_mem + 2 * increment));
        if(logger.info.swap_usage == 0 && logger.info.ram_free > threshold) {
            this.set_max_ram(logger.info.ram_usage + threshold / 2); // remove all free memory at the beginning
        }
        
        if(logger.info.ram_usage > vm_mem + threshold) {
            this.set_max_ram(logger.info.maxram - increment); // Progressively decrease max memory
        }
        else if(!!increase && logger.info.ram_usage <  (vm_mem + threshold / 10)) {
            this.set_max_ram(logger.info.maxram + increase);
        }
    }

    cgroup_max_regul(increment, threshold, increase) {

        if(logger.info.maxram > 150 + logger.info.ram_usage) {
            this.set_max_ram(logger.info.ram_usage + 100);
        }

        const vm_mem = (logger.info.virsh_available - logger.info.virsh_usable) / 1024;

        // let target = vm_mem + threshold + logger.info.swap_usage;
        let target = vm_mem + threshold + logger.info.swap_usage;


        let out = this.pid_regul(target, logger.info.ram_usage);

        console.log(logger.info.maxram, out, Math.floor(out));
        this.set_max_ram(logger.info.maxram + Math.floor(out));
    }

    ballon_regul(threshold) {
        threshold *= 1024;

        const target = threshold + (logger.info.virsh_swap_out - logger.info.virsh_swap_in);
        let out = this.pid_regul(target, logger.info.virsh_usable);

        out = ((logger.info.virsh_usable + out < 0) ? target - logger.info.virsh_usable : Math.floor(out));

        let new_vm_size = logger.info.virsh_actual + out;

        console.log("Out : ", out, new_vm_size);

        SystemManager.quick_exec(`virsh setmem --domain medooze --size ${new_vm_size}K --current`);
    }

    memory_reclaim(increment, threshold, increase) {
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

    memory_reduction_ballon(increment, threshold, increase) {
        increment *= 1024; // MEGA !!
        threshold *= 1024;
        increase  *= 1024;

        console.log(logger.info.virsh_usable / 1024, logger.info.virsh_available / 1024, logger.info.virsh_actual / 1024)

        if(logger.info.virsh_usable > threshold) {
            let new_vm_size = logger.info.virsh_actual - increment;
            SystemManager.quick_exec(`virsh setmem --domain medooze --size ${new_vm_size}K --current`);
        }
        else if(!!increase && logger.info.virsh_usable < threshold / 10) {
            let new_vm_size = logger.info.virsh_actual + increase; // deflate
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
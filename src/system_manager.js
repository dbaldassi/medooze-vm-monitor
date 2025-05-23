const Path     = require("path");
const FS       = require("fs");
const Inotify  = require("node-inotify").Inotify;
const os = require('os-utils');

const { exec, execSync } = require('node:child_process')

// Get logger
const logger = require('./stats.js');
// Get config
const config = require('../config/config.json');
const { readFileSync } = require("node:fs");
const { log } = require("node:console");

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

// Inotify
var inotify = new Inotify();

function clamp(value, lower, upper) {
    return Math.min(Math.max(value, lower), upper);
}

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
            kp : 3/10, // to be tuned
            ki : 1/10, // to be tuned
            kd : 2/11, // to be tuned
            
            prevError : 0,
            integrator : 0,

            dt : 10 // 10sec
        }

        this.window_size = 30;
        this.threshold_percentage = 1;
        
        // inotify.addWatch({ path: this.swap_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.swapevent_callback(event) });
        // inotify.addWatch({ path: this.memory_event_path, watch_for: Inotify.IN_MODIFY, callback: event => this.memoryevents_callback(event) });
        // inotify.addWatch({ path: this.memory_pressure_path, watch_for: Inotify.IN_MODIFY, callback: event => this.pressure_callback(event) });
    }

    fetch_swap_stats() {
        try {
            const data = FS.readFileSync('/proc/vmstat', 'utf8');
            const lines = data.split('\n');
            for (const line of lines) {
                const [key, value] = line.split(/\s+/);
                if (key === 'pswpin') {
                    logger.info.swapin = parseInt(value);
                } else if (key === 'pswpout') {
                    logger.info.swapout = parseInt(value);
                } else if (key === 'pgpgin') {
                    logger.info.pgpgin = parseInt(value);
                } else if (key === 'pgpgout') {
                    logger.info.pgpgout = parseInt(value);
                }
            }
        } catch (e) {
            console.error("Error reading /proc/vmstat:", e);
            logger.info.swapin = 0;
            logger.info.swapout = 0;
        }
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
                logger.info[split[0]] = parseInt(split[1]);
            }
        } catch(e) {
        
        }
    }

    fetch_cpu_and_load() {
        try {
            // Récupérer le load average
            const loadAverage = os.loadavg(1); // Load average sur 1 minute
            logger.info.load_average = loadAverage;

            // Récupérer l'utilisation du CPU
            os.cpuUsage((cpuUsage) => {
                logger.info.host_cpu = cpuUsage * 100; // Convertir en pourcentage
                console.log(`Load Average: ${loadAverage}, CPU Usage: ${cpuUsage * 100}%`);
            });
        } catch (e) {
            console.error("Error fetching CPU and Load Average:", e);
            logger.info.load_average = 0;
            logger.info.host_cpu = 0;
        }
    }

    get_reclaimable_bytes() {
        logger.info.cgroup_reclaimable = (logger.info.slab_reclaimable + logger.info.inactive_file) / (1024 * 1024);

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
        this.fetch_mem_stat();
        this.fetch_swap_stats();
        // this.fetch_cpu_and_load();
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
                cmd = `${cmd} swappiness=${swappiness}`;
            }

            console.log("Reclaiming", cmd);
            
            logger.info.maxram += 100; // mark to find where we begin reclaim when boxing plot

            // let before = new Date();
            FS.writeFile(this.memory_reclaim_path, cmd, (err) => {
                if(err) console.error(err);
                // else logger.info.maxram -= 100;
            });
            // let after = new Date();

            // console.log(after-before);
        } catch(error) {
            console.error(error);
            return false;
        }

        return true;
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

    /*cgroups_regul(threshold, dt) {
        this.set_max_ram(logger.info.ram_usage + threshold);
        
        const step = 100;
        const wait_time = 3;

        if(logger.info.pressure_avg10 >= 1) {
            console.log("waiting ", logger.info.pressure_avg10);
            return logger.info.pressure_avg10; // wait for that amount of time, let it recover
        }

        // if still above threshold
        if(logger.info.ram_usage > logger.info.vm_ram_usage + threshold) {
            this.reclaim_memory(step);
        }

        console.log("waiting ", wait_time);
        return wait_time;
    }*/

    cgroups_regul_pid(threshold, dt) {
        if(logger.info.pressure_avg10 > 1) {
            return logger.info.pressure_avg10;
        }


        const default_wait_time = 3;
        let target = logger.info.vm_ram_usage + threshold;

        // if the memory is under the target, we can't increase
        // so we change the target to the current memory value to make the pid error converge to 0
        // since we can't increase
        if(logger.info.ram_usage - target < 0) {
            target = logger.info.ram_usage;
        }

        this.pid.dt = dt;
        this.pid.kd = 0;
        this.pid.ki = 0;

        this.set_max_ram(logger.info.ram_usage + threshold);

        let out = this.pid_regul(logger.info.ram_usage, target); // invert to invert the sign

        console.log({out, target, usage:logger.info.ram_usage, vm:logger.info.vm_ram_usage})

        out = Math.min(Math.floor(out), logger.info.ram_usage - target);

        console.log({out, target, usage:logger.info.ram_usage})

        if(out <= 0) {
            return default_wait_time; // wait 10sec
        }

        out = Math.min(out, 150);
        this.reclaim_memory(out);

        let time = (7/499) * out + 492/499;
        time = Math.max(time * 2, 1);

        // console.log({out, target, usage:logger.info.ram_usage, time})

        return time;        
    }

    update_anon_window() {
        if(this.inactive_anon_values === undefined) {
            console.log("create anon array");
            this.inactive_anon_values = [];
        }

        if(logger.info.inactive_anon === undefined) {
            return; // no data
        }

        this.inactive_anon_values.push(logger.info.inactive_anon);

        if(this.inactive_anon_values.length < this.window_size) {
            console.log("not enough values");
            return; // window not filled yet, considered not stabilized
        }
        else if(this.inactive_anon_values.length > this.window_size) {
            this.inactive_anon_values.shift(); // we want only the last minute not one second more
        }
    }

    calculate_standard_seviation(values) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    cgroups_regul(threshold, dt) {
        this.update_anon_window();

        const unused = logger.info.ram_usage - (logger.info.vm_free_used + logger.info.vm_free_bufcache);

        console.log("estimated unused : ", unused);

        if(unused === undefined || Number.isNaN(unused) || unused < threshold) {
            console.log("unused is NaN or greater than threshold");
            return;
        }

        const inactive_anon = logger.info.inactive_anon / (1024 * 1024);
        console.log("inactive anon : ", inactive_anon);

        if(inactive_anon === 0) {
            console.log("anon is 0, reclaiming 100");
            this.reclaim_memory(15); // to be adjusted in function of reclaimable bytes
            return;
        }
        
        if(this.inactive_anon_values.length < this.window_size) {   
            console.log("Not enough values yet");
            return; // not enough values yet
        }

        console.log("Checking stabilization");
        const std_dev = this.calculate_standard_seviation(this.inactive_anon_values);

        // Vérifier si l'écart type est inférieur à un seuil
        if (std_dev >= 1) {
            console.log("Not stabilized (stdDev too high):", std_dev);
            return; // Pas encore stabilisé
        }

        console.log("Stabilized");
        this.inactive_anon_values = [];

        console.log("reclaiming : ", unused - threshold);
        this.reclaim_memory(Math.min(100,unused - threshold));
    }

    create_balloon_pid() {
        this.pid = {
            kp : 3/10, // to be tuned
            ki : 1/10, // to be tuned
            kd : 2/11, // to be tuned
            
            prevError : 0,
            integrator : 0,

            dt : 10 // 10sec
        }
    }

    ballon_regul(threshold, dt) {
        threshold *= 1024;

        const max = 4 * 1024 * 1024 - (logger.info.virsh_available - logger.info.virsh_usable); // max ram is 4GB
        const min = 0;
        this.pid.dt = dt;

        const target = clamp(threshold + (logger.info.virsh_swap_out - logger.info.virsh_swap_in), min, max);

        console.log({target : target / 1024, min : min / 1024 , max : max / 1024});

        let out = this.pid_regul(target, logger.info.virsh_usable);

        out = ((logger.info.virsh_usable + out < 0) ? target - logger.info.virsh_usable : Math.floor(out));

        let new_vm_size = logger.info.virsh_actual + out;
        console.log({ out, new_vm_size, actual: logger.info.virsh_actual });

        let time = 3;
        if(out < 0) {
            time = (1 / 250) * (out / -1024) + 1/2; // found by interpolation
            time = Math.max(time, 1); // min 1 sec because virsh report stats every second
            console.log("Time until next : ", time)
        }

        SystemManager.quick_exec(`virsh setmem --domain medooze --size ${new_vm_size}K --current`);

        return time;
    }

    memory_reclaim(increment, threshold, swappiness) {
        const vm_mem = (logger.info.virsh_available - logger.info.virsh_usable) / 1024;
        
        // const bytes = this.get_reclaimable_bytes();
        // console.log("Reclaimable bytes : ", bytes, increment, increment + bytes);

        console.log(logger.info.ram_usage, vm_mem + threshold);
        if(logger.info.ram_usage > vm_mem + threshold) {
            this.reclaim_memory(increment, swappiness);
        }
    }

    memory_reduction_ballon(increment, threshold, increase) {
        increment *= 1024; // MEGA !!
        threshold *= 1024;
        increase  *= 1024;

        console.log(logger.info.virsh_usable / 1024, logger.info.virsh_available / 1024, logger.info.virsh_actual / 1024);

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

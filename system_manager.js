const Path     = require("path");
const FS       = require("fs");

const { exec } = require('node:child_process')

// Get logger
const logger = require('./stats.js');
// Get config
const config = require('./config.json');

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

class SystemManager {
    constructor() {
        this.ram_usage_path  = Path.join(config.memory_stats_path, config.ram_usage_file);
        this.ram_total_path  = Path.join(config.memory_stats_path, config.ram_total_file);
        this.swap_usage_path = Path.join(config.memory_stats_path, config.swap_usage_file);
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
    
    fetch_memory() {
        this.fetch_ram_usage();
        this.fetch_ram_free();
        this.fetch_swap_usage();
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
    
        if(logger.info.ram_free > increment) {
            // Set the new max as the current ram usage (removing all free memory)
            this.set_max_ram(logger.info.ram_usage);
        }
        else {
            if(logger.info.ram_usage > logger.info.vm_ram_usage) {
                // Removing ${increment}MiB of memory from current usage
                this.set_max_ram(logger.info.ram_usage - increment);
            }
        }
    }

     static quick_exec(cmd) {
        exec(cmd, (err, output) => {
            if(err) console.error(err);
            else console.log(output);
        });
    }
}

module.exports = SystemManager;
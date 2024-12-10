// Get config
const config = require('./config.json');
// Get logger
const logger = require('./stats.js');
// Get system manager
const SystemManager = require('./system_manager.js');
// Get Update listener function
const update_listener = require('./lib/receivers.js').update_listener;

class Monitor {
    constructor() {
        // Create system manager
        this.sys_manager = new SystemManager;
        // Client that runs publisher on demand
        this.publisher_launchers = require('./lib/publisher_launcher.js').launchers;
        // Client that runs viewers on demand
        this.viewer_launchers = require('./lib/viewer_launcher.js').launchers;
    }

    set_max_ram(max) {
        this.sys_manager.set_max_ram(max);
    }

    medooze_connected() {
        // Set up max memory as the current max of the vm
        // This is to avoid having 'inf' in the cgroup file
        this.sys_manager.set_max_ram(config.initial_max_ram);
        // Start collecting cgroup stats
        this.sys_manager.start_collecting(config.time_interval, (time) => update_listener());
        // Time to publish a video to medooze
        this.publisher_launchers.forEach(p => p.sendUTF(JSON.stringify({"cmd":"run"})));
    }
    
    medooze_disconnected() {
        // Stop collecting memory stats
        this.sys_manager.stop_collecting();
        // Update all listeners
        update_listener();
    }
    
    publisher_connected() {
        // Start algorithm to reduce memory
        // const timeout = setInterval(sys_manager.memory_reduction, 10 * SECONDS);
        console.log("publisher_connected");
    }
    
    publisher_disconnected() {
        // Update all listeners
        update_listener();
    
        // Clear interval running the memory reduction algo
        // clearInterval(timeout[Symbol.toPrimitive]());
    }
    
    start_medooze() {
        SystemManager.quick_exec(config.medooze_server.exec_start);
    }
    
    stop_medooze() {
        if(config.exec_stop) {
            SystemManager.quick_exec(config.medooze_server.exec_stop);
        }
    }
    
    search_and_run(ids, component, cmd) {
        for(let id of ids) {
            let launcher = config[component].find(elt => elt.id === id);
            SystemManager.quick_exec(launcher[cmd]);
        }
    }
    
    start_viewer_launchers(ids) {
        this.search_and_run(ids, "viewer_launchers", "exec_start");
    }
    
    start_publisher_launchers(ids) {
        this.search_and_run(ids, "publisher_launchers", "exec_start");
    }
    
    stop_viewer_launchers(ids) {
        this.search_and_run(ids, "viewer_launchers", "exec_stop");
    }
    
    stop_publisher_launchers(ids) {
        this.search_and_run(ids, "publisher_launchers", "exec_stop");
    }
    
    run() {
        this.start_publisher_launchers(["mac"]);
        this.start_viewer_launchers(["baleze"]);
        this.start_medooze();
    }
}

var monitor = new Monitor;
module.exports = monitor;
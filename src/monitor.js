const FS   = require('fs');
const Path = require('path');

// Get config
const config = require('../config/config.json');
// Get logger
const logger = require('./stats.js');
// Get system manager
const SystemManager = require('./system_manager.js');
// Get Update listener function
const update_listener = require('../lib/receivers.js').update_listener;

const WebSocketClient = require('websocket').client;

const SECONDS = 1000;

class Monitor {
    constructor() {
        // Create system manager
        this.sys_manager = new SystemManager;
        // Client that runs publisher on demand
        this.publisher_launchers = require('../lib/publisher_launcher.js').launchers;
        // Client that runs viewers on demand
        this.viewer_launchers = require('../lib/viewer_launcher.js').launchers;
        // Client that runs visio on demand
        this.visio_launchers = require('../lib/visio_launcher.js').launchers;

        // default medooze
        this.medooze_server = config.medooze_server.find(elt => elt.id === "vm");

	this.current_viewer_count = 0;
    }

    set_max_ram(max) {
        this.sys_manager.set_max_ram(max);
    }

    medooze_connected(ws) {
	    console.log("Medooze connected");
        this.medooze_ws = ws;

        // Set up max memory as the current max of the vm
        // This is to avoid having 'inf' in the cgroup file
        this.sys_manager.set_max_ram(config.initial_max_ram);
        // Start collecting cgroup stats
        this.sys_manager.start_collecting(config.time_interval, (time) => {
            logger.info.time += config.time_interval;

            update_listener();
            logger.log_info();
        });

        this.medooze_connected_promise.resolve();
    }
    
    medooze_disconnected() {
        // Stop collecting memory stats
        this.sys_manager.stop_collecting();
        // Update all listeners
        update_listener();
    }
    
    publisher_connected() {
        console.log("publisher_connected");
        this.publisher_connected_promise.resolve();
    }
    
    publisher_disconnected() {
        // Update all listeners
        update_listener();
    }

    get_medooze_info() {
        return this.medooze_server;
    }

    start_naive_memory_reduction(opts) {
        // Start algorithm to reduce memory
        this.memory_timeout = setInterval(() => this.sys_manager.memory_reduction(opts.increment, opts.threshold, opts.increase), 
                                         opts.timeout * SECONDS);
    }

    stop_naive_memory_reduction() {
        // Clear interval running the memory reduction algo
        clearInterval(this.memory_timeout[Symbol.toPrimitive]());
    }

    start_cgroups_regul(opts) {
        let time = opts.timeout;

        let callback = () => {
            // time = this.sys_manager.cgroups_regul(opts.threshold, time);
            this.sys_manager.cgroups_regul(opts.threshold, time);
            this.pid_cgroups_timeout = setTimeout(callback, Math.floor(time * SECONDS));
        };

        this.pid_max_timeout = setTimeout(callback, time * SECONDS);
    }

    stop_cgroups_regul() {
        clearTimeout(this.pid_max_timeout[Symbol.toPrimitive]());
    }

    start_balloon_regul(opts) {
        let time = opts.timeout;
        let callback = () => {
            time = this.sys_manager.ballon_regul(opts.threshold, time);
            this.pid_balloon_timeout = setTimeout(callback, Math.floor(time * SECONDS));
        };

        this.pid_balloon_timeout = setTimeout(callback, time * SECONDS);
    }

    stop_balloon_regul() {
        clearTimeout(this.pid_balloon_timeout[Symbol.toPrimitive]());
    }

    start_reclaim_reduction(opts) {
        // Start algorithm to reduce memory
        this.reclaim_timeout = setInterval(() => this.sys_manager.memory_reclaim(opts.increment, opts.threshold, opts.swappiness), 
        opts.timeout * SECONDS);
    }

    stop_reclaim_reduction() {
        // Clear interval running the memory reduction algo
        clearInterval(this.reclaim_timeout[Symbol.toPrimitive]());
    }
    
    start_balloon_reduction(opts) {
        console.log(opts);
        this.balloon_timeout = setInterval(() => this.sys_manager.memory_reduction_ballon(opts.increment, opts.threshold, opts.increase), 
        opts.timeout * SECONDS);
    }

    stop_balloon_reduction() {
        console.log("Le ballon éclate");
        clearInterval(this.balloon_timeout[Symbol.toPrimitive]());
    }

    start_medooze(id) {
        console.log("Starting medooze", id);

        this.medooze_server = config.medooze_server.find(elt => elt.id === id);

        if(this.medooze_server.exec_start) {
            SystemManager.quick_exec(this.medooze_server.exec_start);
        }

        // Create promised to be resolved when medooze connects
        this.medooze_connected_promise = Promise.withResolvers();
    }
    
    stop_medooze(id) {
        if(this.medooze_server.exec_stop) {
            SystemManager.quick_exec(this.medooze_server.exec_stop);
        }
    }
    
    start_spawning_process() {
        this.process_promise = Promise.withResolvers();
        this.num_process = 0;

        this.spawn_timeout = setInterval(() => {
            console.log("ram free ", logger.info.ram_free, logger.info.vm_ram_free);
            // if(!logger.info.vm_ram_free) return;
            // if(Math.min(logger.info.ram_free, logger.info.vm_ram_free) > 300) {
            if(Math.min(logger.info.ram_free) > 300) {
                this.medooze_ws.sendUTF(JSON.stringify({"cmd" : "spawn"}));
                this.num_process += 1;
            } else this.stop_spawning_process();
        }, 5000);
    }

    kill_process(percent) {
        this.medooze_ws.sendUTF(JSON.stringify({ "cmd": "kill", count : parseInt(this.num_process * percent / 100) }));
    }

    stop_spawning_process() {
        // Clear interval running spawning processus
        clearInterval(this.spawn_timeout[Symbol.toPrimitive]());

        if(this.process_promise) this.process_promise.resolve();
    }

    search_and_run(ids, component, cmd) {
        for(let id of ids) {
            let launcher = config[component].find(elt => elt.id === id);
            console.log(launcher[cmd]);
            SystemManager.quick_exec(launcher[cmd]);
        }
    }

    search_and_run_sync(ids, component, cmd) {
        for(let id of ids) {
            let launcher = config[component].find(elt => elt.id === id);
            SystemManager.quick_exec_sync(launcher[cmd]);
        }
    }
    
    start_viewer_launchers(ids) {
        this.stop_viewer_launchers(ids); // first stop any remaining viewers otherwise it breaks everything if previous exps crashed
        this.search_and_run(ids, "viewer_launchers", "exec_start");
    }
    
    start_publisher_launchers(ids) {
        this.search_and_run(ids, "publisher_launchers", "exec_start");
    }
    
    stop_viewer_launchers(ids) {
        this.search_and_run_sync(ids, "viewer_launchers", "exec_stop");
    }
    
    stop_publisher_launchers(ids) {
        this.search_and_run(ids, "publisher_launchers", "exec_stop");
    }

    start_visio_launchers(ids) {
        this.stop_visio_launchers(ids); // first stop any remaining viewers otherwise it breaks everything if previous exps crashed
        this.search_and_run(ids, "visio_launchers", "exec_start");
    }
    stop_visio_launchers(ids) {
        this.search_and_run_sync(ids, "visio_launchers", "exec_stop");
    }

    reclaim() {
        let mem = logger.info.ram_usage - logger.info.vm_ram_usage;
        if(mem > 0) this.sys_manager.reclaim_memory(mem);
    }

    add_publisher(opts) {
        for(let opt of opts) {
            // Get publisher by id
            let launcher = this.publisher_launchers.find(e => e.id === opt.id);
            // Run a publisher and publish video
            let obj = {
                "cmd": "run",
                "host": `${this.medooze_server.host}:${this.medooze_server.port}`,
                "codec": opt.codec,
                "scenar": opt.scenar
            };
            launcher.ws.sendUTF(JSON.stringify(obj));

            // Create promise to be resolved when publisher is connected
            this.publisher_connected_promise = Promise.withResolvers();
        }
    }

    add_viewer(opts) {
        for(let opt of opts) {
	    console.log(`Adding ${opt.count} viewers`);
            // get launcher by id
            let launcher = this.viewer_launchers.find(e => e.id === opt.id);
            // Run  the specified amount of viewer
            let obj = {
                "cmd": "run",
                "count": opt.count,
                "network": opt.network ?? "none"
            };

            if(opt.viewerid) obj.viewerid = opt.viewerid;
            
            launcher.ws.sendUTF(JSON.stringify(obj));

	    this.current_viewer_count += opt.count;
        };
    }

    create_room(opts) {
        console.log("create room");

        let client = new WebSocketClient({ tlsOptions: { rejectUnauthorized: false }});
        
        client.on('connect', (connection) => {
            console.log("connected to medooze visio");

            connection.on('message', (message) => {
                let msg = JSON.parse(message.utf8Data);
                if(msg.cmd === "create" && msg.success) {
                    console.log("Room created", msg.roomId);
                    this.room_created_promise.resolve();
                }
            });

            for(let opt of opts) {
                let obj = {
                    "cmd": "create",
                    "roomId": opt.roomId
                };
                connection.send(JSON.stringify(obj));

                console.log("Send create command", obj);
            }
        });

        client.on('connectFailed', (error) => {
            console.log('Connect Error: ' + error.toString());
        });

        this.room_created_promise = Promise.withResolvers();

        client.connect(`wss://${this.medooze_server.host}:${this.medooze_server.port}`, "vm-visio");
    }

    delete_room(opts) {
        let client = new WebSocketClient({ tlsOptions: { rejectUnauthorized: false }});
        client.on('connect', (connection) => {
            for(let opt of opts) {
                let obj = {
                    "cmd": "delete",
                    "roomId": opt.roomId
                };
                connection.send(JSON.stringify(obj));
            }
        }
        );
        client.connect(`wss://${this.medooze_server.host}:${this.medooze_server.port}`, "vm-visio");
    }

    add_visio_client(opts) {
        console.log("Adding visio client");
        for(let opt of opts) {
            // Get visio by id
            let launcher = this.visio_launchers.find(e => e.id === opt.id);
            // Run a publisher and publish video
            let obj = {
                "cmd": "run",
                "medooze_host": this.medooze_server.host,
                "medooze_port": this.medooze_server.port,
                "monitor_host": config.host,
                "monitor_port": config.port,
                "roomId": opt.roomId,
                "count": opt.count,
            };
            launcher.ws.sendUTF(JSON.stringify(obj));
        }
    }

    remove_viewer(opts) {
	for(let opt of opts) {
	    console.log(`Removing ${opt.count} viewers`);
	    
	    let launcher = this.viewer_launchers.find(e => e.id === opt.id);

	    let obj = {
		"cmd": "kill",
		"count": opt.count
	    };

	    launcher.ws.sendUTF(JSON.stringify(obj));

	    this.current_viewer_count -= opt.count;
	}
    }
    
    random(min, max) {
	return Math.floor(Math.random() * (max + 1 - min)) + min;
    }

    start_viewer_traffic(opts) {
	const ADD = 0;
	const REMOVE = 1;
	
	const time = this.random(opts.time_min, opts.time_max);
	console.log("traffic wait time : ", time);
	
	this.viewers_timeout = setTimeout(() => {
	    const count = this.random(opts.viewers_min, opts.viewers_max);
	    const op = this.random(0,1);

	    console.log({count});
	    
	    if(op === ADD) {		
		let obj = {
		    id: opts.id,
		    count: Math.min(count, opts.max - this.current_viewer_count)
		};

		console.log(obj);
		
		this.add_viewer([obj]);
	    }
	    else if(op === REMOVE) {
		let obj = {
		    id: opts.id,
		    count: Math.min(count, this.current_viewer_count)
		};

		console.log(obj);
		
		this.remove_viewer([obj]);
	    }
	    
	    this.start_viewer_traffic(opts);
	}, time * SECONDS);
    }

    stop_viewer_traffic(opts) {
	    clearInterval(this.viewers_timeout[Symbol.toPrimitive]());
    }

    save(opt) {
        // Get dest dir
        const dest_dir = Path.join('results', this.exp_name);

        console.log("save ", dest_dir);

        // Check if folder exists
        if(!FS.existsSync(dest_dir)) {
            // If not create it
            FS.mkdirSync(dest_dir, { recursive: true });
        }

        // Setup final name : expname_date;
        const date = new Date().toLocaleString('fr-FR').replaceAll(' ', '-').replaceAll('/', '-').replaceAll(':', '-');
        const name = `${this.exp_name}_${date}.csv`;

        // Get dest path
        const dest_path = Path.join(dest_dir, name);
        const cgroups_dest_path = Path.join(dest_dir, `cgroups_${name}`);

        // Copy stats.csv to dest path
        FS.cpSync(logger.csv_name, dest_path);
        FS.cpSync("cgroups_stats.csv", cgroups_dest_path);
        // Copy rooms csv to dest dir
        for(let [room_id, _] of logger.info.rooms) {
            const room_path = Path.join(dest_dir, `${room_id}_${name}`);
            FS.cpSync(`${room_id}_stats.csv`, room_path);
        }

        // Add viewers csv headers
        logger.sync_headers_sync(dest_path);

        if(opt === "average_viewer") {
            console.log("Run average_viewer.py");
            // Run average viewer script
            SystemManager.quick_exec_sync(`../../scripts/average_viewer.py ${name}`, { cwd : dest_dir });
            // remove original file
            FS.rmSync(dest_path);
        }
    }

    exit() {
        process.exit(0);
    }

    async run_scenar(scenar) {
        // Save the name in class member
        this.exp_name = scenar.name;

        for(let step of scenar.steps) {
            // Await for requirement to be fullfilled before performing the step
            if(step.require) { 
                // Wait for medooze to be connected
                if(step.require === "medooze_connected") {
                    // Create promise in case monitor is not starting medooze by himself
                    if(!this.medooze_connected_promise) 
                        this.medooze_connected_promise = Promise.withResolvers();

		    console.log("await medooze promise");
                    await this.medooze_connected_promise.promise;
		    console.log("Medooze PROMISE OK");
                }
                // Wait for a publisher to be connected
                else if(step.require === "publisher_connected") await this.publisher_connected_promise.promise;
                else if(step.require === "memory_filled") await this.process_promise.promise;
                else if(step.require === "room_created") await this.room_created_promise.promise;
            }

            // Number of times to repeat this step
            let repeat = step.repeat ?? 1;
            for(let i = 0; i < repeat; ++i) {
                // Perform all actions contained in this step
                step.actions.forEach(action => this[action](step[action]));

                // If the step speficieda wait time before going to next step
                if(step.wait) {
                    // Create promise with timout to wait
                    const promise = new Promise((resolve, reject) => {
                        setTimeout(() => { resolve(); }, step.wait);
                      });
                    // Wait for timout to expire
                    await promise;
                }
            }
        }
    }
    
    run(scenar) {
        // Make sure medooze promise is not set
        this.medooze_connected_promise = undefined;
        // RUN !!
        this.run_scenar(scenar);
    }
}

var monitor = new Monitor;
module.exports = monitor;

// Node modules
const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const Path              = require("path");
const WebSocketServer = require ("websocket").server;

const { exec } = require('node:child_process')

// Get config
const config = require('./config.json');
// Get logger
const logger = require('./stats.js');
// Get Update listener function
const update_listener = require('./lib/receivers.js').update_listener;

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

// Client that runs publisher on demand
const publisher_launchers = require('./lib/publisher_launcher.js').launchers;
// Client that runs viewers on demand
const viewer_launchers = require('./lib/viewer_launcher.js').launchers;

function fetch_ram_usage() {
	// Read current memory usage from cgroup file
    const path = Path.join(config.memory_stats_path, config.ram_usage_file);
    const data = FS.readFileSync(path);

	// Log it in csv file
    logger.info.ram_usage = parseInt(parseInt(data) / MEGA);
}

function fetch_ram_free() {
    const path = Path.join(config.memory_stats_path, config.ram_total_file);
    const data = FS.readFileSync(path);
    
    logger.info.ram_free = parseInt(parseInt(data) / (MEGA)) - logger.info.ram_usage;
    // console.log(parseInt(data), info.ram_free);
}

function fetch_swap_usage() {
	const path = Path.join(config.memory_stats_path, config.swap_usage_file);
	const data = FS.readFileSync(path);

	logger.info.swap_usage = parseInt(parseInt(data) / MEGA);
}

function fetch_memory() {
	fetch_ram_usage();
	fetch_ram_free();
	fetch_swap_usage();

	logger.info.time += config.time_interval;
	logger.log_info();

	update_listener()
}

// Max in MiB
function set_max_ram(max) {
	// todo write max to memory.max
	console.log(max);
	// log in csv stats new max
	logger.info.maxram = max;
	// Get path to the cgroup file
	const path = Path.join(config.memory_stats_path, config.ram_total_file);
	// Write new max in the file
	FS.writeFileSync(path, String(max * MEGA));
}

var fetch_memory_timeout;

function medooze_connected() {
	// Set up max memory as the current max of the vm
	// This is to avoid having 'inf' in the cgroup file
    set_max_ram(config.initial_max_ram);

	// Setup timout to gather memory stats
    fetch_memory_timeout = setInterval(fetch_memory, config.time_interval);

	// Time to publish a video to medooze
    publisher_launchers.forEach(p => p.sendUTF(JSON.stringify({"cmd":"run"})));
}

function medooze_disconnected() {
	// Clear timeout that fetch memory
	clearInterval(fetch_memory_timeout[Symbol.toPrimitive]());
	// Update all listeners
	update_listener();
}

function memory_reduction() {
	const increment = 100;

	if(logger.info.ram_free > increment) {
		// Set the new max as the current ram usage (removing all free memory)
		set_max_ram(logger.info.ram_usage);
	}
	else {
		if(info.ram_usage > logger.info.vm_ram_usage) {
			// Removing ${increment}MiB of memory from current usage
			set_max_ram(logger.info.ram_usage - increment);
		}
	}
}

function publisher_connected() {
	// Start algorithm to reduce memory
	// const timeout = setInterval(memory_reduction, 10 * SECONDS);

	console.log("publisher_connected");

	// Running viewers
	let obj = {
		cmd: "run",
		count: 1	
	};

	// First viewer after 5sec
	setTimeout(() => {
		viewer_launchers[0].sendUTF(JSON.stringify(obj));
	}, 5 * SECONDS);

	// 2 more after 10sec later
	setTimeout(() => {
		obj.count = 2;
		viewer_launchers[0].sendUTF(JSON.stringify(obj));
	}, 15 * SECONDS);

	// sotp everythin after 1mn
	setTimeout(() => {
		stop_viewer_launchers(["baleze"]);
		stop_publisher_launchers(["mac"]);
		stop_medooze();

		process.exit(0);
	}, 75 * SECONDS);
}

function publisher_disconnected() {
	// Update all listeners
	update_listener();

	// Clear interval running the memory reduction algo
	// clearInterval(timeout[Symbol.toPrimitive]());
}

function quick_exec(cmd) {
	exec(cmd, (err, output) => {
		if(err) console.error(err);
		else console.log(output);
	});
}

function start_medooze() {
	quick_exec(config.medooze_server.exec_start);
}

function start_viewer_launchers(ids) {
	for(let id of ids) {
		let launcher = config.viewer_launchers.find(elt => elt.id === id);
		quick_exec(launcher.exec_start);
	}
}

function start_publisher_launchers(ids) {
	for(let id of ids) {
		let launcher = config.publisher_launchers.find(elt => elt.id === id);
		quick_exec(launcher.exec_start);
	}
}

function stop_medooze() {
	if(config.exec_stop) {
		quick_exec(config.medooze_server.exec_stop);
	}
}

function stop_viewer_launchers(ids) {
	for(let id of ids) {
		let launcher = config.viewer_launchers.find(elt => elt.id === id);
		quick_exec(launcher.exec_stop);
	}
}

function stop_publisher_launchers(ids) {
	for(let id of ids) {
		let launcher = config.publisher_launchers.find(elt => elt.id === id);
		quick_exec(launcher.exec_stop);
	}	
}

function run() {
	start_publisher_launchers(["mac"]);
	start_viewer_launchers(["baleze"]);
	start_medooze();
}

//Load certs
const options = {
	key     : FS.readFileSync ("server.key"),
	cert	: FS.readFileSync ("server.cert")
};

//Manualy starty server
const server = createServer(options, rest);
server.listen(config.port);

const handlers = {
	"publisher"          : require('./lib/publisher.js'),
	"medooze"            : require('./lib/medooze.js'),
	"publisher_launcher" : require('./lib/publisher_launcher.js').handler,
	"viewer_launcher"    : require('./lib/viewer_launcher.js').handler,
	"viewer"             : require('./lib/viewers.js'),
	"receiver"           : require('./lib/receivers.js').handler
};

let callbacks = {
	medooze_connected: medooze_connected,
	medooze_disconnected: medooze_disconnected,
	publisher_connected: publisher_connected,
	publisher_disconnected: publisher_disconnected,
	set_max_ram: set_max_ram
}

//Launch wss server
//Create websocket server
console.log("Starting ws server");
const wss = new WebSocketServer ({ httpServer: server, autoAcceptConnections: false });

wss.on("request", (request) => {
	let protocol = request.requestedProtocols[0];
	console.log("-Got request for: "+ protocol);

	//If not found
	if (!handlers.hasOwnProperty (protocol))
		//Reject connection
		return request.reject();

	// Process it
	handlers[protocol](request, protocol, callbacks);

	update_listener();
});

run();
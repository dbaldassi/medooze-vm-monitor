// Node modules
const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const WebSocketServer = require ("websocket").server;

// Get config
const config = require('./config.json');
// Get logger
const logger = require('./stats.js');
// Get system manager
const SystemManager = require('./system_manager.js');
const sys_manager = new SystemManager;

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

function medooze_connected() {
	// Set up max memory as the current max of the vm
	// This is to avoid having 'inf' in the cgroup file
    sys_manager.set_max_ram(config.initial_max_ram);
	// Start collecting cgroup stats
    sys_manager.start_collecting(config.time_interval, (time) => update_listener());
	// Time to publish a video to medooze
    publisher_launchers.forEach(p => p.sendUTF(JSON.stringify({"cmd":"run"})));
}

function medooze_disconnected() {
	// Stop collecting memory stats
	sys_manager.stop_collecting();
	// Update all listeners
	update_listener();
}

function publisher_connected() {
	// Start algorithm to reduce memory
	// const timeout = setInterval(sys_manager.memory_reduction, 10 * SECONDS);
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

function start_medooze() {
	SystemManager.quick_exec(config.medooze_server.exec_start);
}

function stop_medooze() {
	if(config.exec_stop) {
		SystemManager.quick_exec(config.medooze_server.exec_stop);
	}
}

function search_and_run(ids, component, cmd) {
	for(let id of ids) {
		let launcher = config[component].find(elt => elt.id === id);
		SystemManager.quick_exec(launcher[cmd]);
	}
}

function start_viewer_launchers(ids) {
	search_and_run(ids, "viewer_launchers", "exec_start");
}

function start_publisher_launchers(ids) {
	search_and_run(ids, "publisher_launchers", "exec_start");
}

function stop_viewer_launchers(ids) {
	search_and_run(ids, "viewer_launchers", "exec_stop");
}

function stop_publisher_launchers(ids) {
	search_and_run(ids, "publisher_launchers", "exec_stop");
}

function run() {
	start_publisher_launchers(["mac"]);
	start_viewer_launchers(["baleze"]);
	start_medooze();
}

// Load certs
const options = {
	key     : FS.readFileSync ("server.key"),
	cert	: FS.readFileSync ("server.cert")
};

// Manualy start server
const server = createServer(options, rest);
server.listen(config.port);

// Subprotocols handler
const handlers = {
	"publisher"          : require('./lib/publisher.js'),
	"medooze"            : require('./lib/medooze.js'),
	"publisher_launcher" : require('./lib/publisher_launcher.js').handler,
	"viewer_launcher"    : require('./lib/viewer_launcher.js').handler,
	"viewer"             : require('./lib/viewers.js'),
	"receiver"           : require('./lib/receivers.js').handler
};

// Callback object to be passed to subprotocol handler
let callbacks = {
	medooze_connected: medooze_connected,
	medooze_disconnected: medooze_disconnected,
	publisher_connected: publisher_connected,
	publisher_disconnected: publisher_disconnected,
	set_max_ram: sys_manager.set_max_ram
}

//Launch wss server
//Create websocket server
console.log("Starting ws server");
const wss = new WebSocketServer ({ httpServer: server, autoAcceptConnections: false });

wss.on("request", (request) => {
	// Get protocol
	let protocol = request.requestedProtocols[0];
	console.log("-Got request for: " + protocol);

	//If not found
	if (!handlers.hasOwnProperty (protocol))
		//Reject connection
		return request.reject();

	// Process it
	handlers[protocol](request, protocol, callbacks);

	// Update all listener
	update_listener();
});

// RUN !!
run();
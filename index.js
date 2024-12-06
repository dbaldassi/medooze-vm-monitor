// Node modules
const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const Path              = require("path");
const {WebSocketServer} = require ("ws");

// csv stats headers
const headers = [
	{id: 'time', title: 'TIME'},
	{id: 'ram_usage', title: 'MEMORY USED'},
	{id: 'ram_free', title: 'MEMORY FREE'},
	{id: 'maxram', title: 'MEMORY MAX'},
	{id: 'swap_usage', title: 'SWAP'},
	{id: 'publisher_bitrate', title: 'PUBLISHER BITRATE'},
	{id: 'publisher_pc_state', title: 'CONNECTION STATE'},
	{id: 'viewer_count', title: 'VIEWER COUNT'},
	{id: 'vm_ram_usage', title: 'VM MEMORY USAGE'},
	{id: 'vm_ram_free', title: 'VM MEMORY FREE'},
	{id: 'vm_cpu_usage', title: 'VM CPU USAGE'},
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

// Peerconnection state map to write number in stat.csv
const connection_state_map = new Map();
connection_state_map.set('disconnected', 1);
connection_state_map.set('closed', 0);
connection_state_map.set('connecting', 2);
connection_state_map.set('new', 2);
connection_state_map.set('connected', 3);
connection_state_map.set('failed', 4);
connection_state_map.set('checking', 5);
connection_state_map.set('completed', 6);

// Create csv logger to log all stats
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
var csvWriter = createCsvWriter({
    path: 'stats.csv',
    header: headers,
	append: false
}); 

// Get config
const config = require('./config.json');

// HTTP port
const PORT = 9000;
const ip = config.host;

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

// Viewers that conencted to monitor
var receivers = [];
// Client that runs publisher on demand
var publisher_launchers = [];
// Client that runs viewers on demand
var viewer_launchers = [];

var info = {
	last_modified: undefined,
	time: 0,

 	viewer_count: 0,
	is_publisher_connected: false,
	is_medooze_connected: false,
	publisher_bitrate: undefined,
	publisher_pc_state: 0,
	ram_usage: undefined,
	ram_free: undefined,
	swap_usage: undefined,
	maxram: config.initial_max_ram,
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
};

async function log_info() {
	// write a new line into the csv file
	const records = [info];
	await csvWriter.writeRecords(records);
}

function handle_new_receiver(ws) {
	// Keep ref on the new viewer
	receivers.push(ws);
	// Send current info so it init itself
	ws.send(JSON.stringify(info));
	ws.on('close', () => {
		// remove the ref now that the viewer is off
		const index = receivers.indexOf(ws);
		if(index > -1) receivers.splice(index, 1);
	});
}

function update_listener() {
	// Send info object to all listeners so they know whats going on
	receivers.forEach(elt => elt.send(JSON.stringify(info)));
}

function update_viewer_bitrate(msg) {

	update_listener();
}

function fetch_ram_usage() {
	// Read current memory usage from cgroup file
    const path = Path.join(config.memory_stats_path, config.ram_usage_file);
    const data = FS.readFileSync(path);

	// Log it in csv file
    info.ram_usage = parseInt(parseInt(data) / MEGA);
}

function fetch_ram_free() {
    const path = Path.join(config.memory_stats_path, config.ram_total_file);
    const data = FS.readFileSync(path);
    
    info.ram_free = parseInt(parseInt(data) / (MEGA)) - info.ram_usage;
    // console.log(parseInt(data), info.ram_free);
}

function fetch_swap_usage() {
	const path = Path.join(config.memory_stats_path, config.swap_usage_file);
	const data = FS.readFileSync(path);

	info.swap_usage = parseInt(parseInt(data) / MEGA);
}

function fetch_memory() {
	fetch_ram_usage();
	fetch_ram_free();
	fetch_swap_usage();

	info.time += config.time_interval;
	log_info();

	update_listener()
}

// Max in MiB
function set_max_ram(max) {
	// todo write max to memory.max
	console.log(max);
	// log in csv stats new max
	info.maxram = max;
	// Get path to the cgroup file
	const path = Path.join(config.memory_stats_path, config.ram_total_file);
	// Write new max in the file
	FS.writeFileSync(path, String(max * MEGA));
}

function medooze_connected(ws) {
	// Update medooze connection state
    info.is_medooze_connected = true;

	// Set up max memory as the current max of the vm
	// This is to avoid having 'inf' in the cgroup file
    set_max_ram(config.initial_max_ram);

	// Setup timout to gather memory stats
    const timeout = setInterval(fetch_memory, config.time_interval);

    ws.on('close', () => {
		console.log("Medooze_close");
		// update medooze connection state
		info.is_medooze_connected = false
		// Clear timeout that fetch memory
		clearInterval(timeout[Symbol.toPrimitive]());
		// Update all listeners
		update_listener();
    });

	// Time to publish a video to medooze
    publisher_launchers.forEach(p => p.send(JSON.stringify({"cmd":"launch"})));
}

function memory_reduction() {
	const increment = 100;

	if(info.ram_free > increment) {
		// Set the new max as the current ram usage (removing all free memory)
		set_max_ram(info.ram_usage);
	}
	else {
		if(info.ram_usage > info.vm_ram_usage) {
			// Removing ${increment}MiB of memory from current usage
			set_max_ram(info.ram_usage - increment);
		}
	}
}

function publisher_connected(ws) {
	// Update publisher connection state
	info.is_publisher_connected = true;

	// Start algorithm to reduce memory
	// const timeout = setInterval(memory_reduction, 10 * SECONDS);

	ws.on('close', () => {
		// Update publisher connection state
		info.is_medooze_connected = false
		// Update all listeners
		update_listener();

		// Clear interval running the memory reduction algo
		// clearInterval(timeout[Symbol.toPrimitive]());
	});

	// Running viewers
	let obj = {
		cmd: "run",
		count: 1	
	};

	// First viewer after 5sec
	setTimeout(() => {
		viewer_launchers[0].send(JSON.stringify(obj));
	}, 5000);

	// 10 more after 10sec later
	setTimeout(() => {
		obj.count = 10;
		viewer_launchers[0].send(JSON.stringify(obj));
	}, 15000);
}

function handle_vm_stats(stats) {
	// Update VM memory and cpu usage
	info.vm_ram_free = parseInt(stats.freemem / MEGA);
	info.vm_ram_usage = parseInt((stats.totalmem - stats.freemem) / MEGA);
	info.vm_cpu_usage = stats.cpu;
}

function handle_new_viewer(name) {
	console.log("new viewer", name);

	// Create new stats IDs for this viewer stats 
	let target_id = name + "_target";
	let bitrate_id = name + "_bitrate";
	let fps_id = name + "_fps";

	// Add new IDs to the csv header
	headers.push({ id: target_id, title: target_id.toUpperCase() });
	headers.push({ id: bitrate_id, title: bitrate_id.toUpperCase() });
	headers.push({ id: fps_id, title: fps_id.toUpperCase() });

	// Re-create the csv writer to write stats for the new viewer
	csvWriter = createCsvWriter({
		path: 'stats.csv',
		header: headers,
		append: true
	}); 

	// Set default values
	info[target_id] = 0;
	info[bitrate_id] = 0;
	info[fps_id] = 0;
}

function handle_viewer_target(msg) {	
	// Retrieve csv header id
	let target_id = msg.name + "_target";
	// Update stats
	info[target_id] = parseInt(msg.target);
}

function handle_viewer_bitrate(msg) {
	// Retrieve csv header id
	let bitrate_id = msg.name + "_bitrate";
	let fps_id = msg.name + "_fps";

	// Update stats 
	info[bitrate_id] = parseInt(msg.bitrate);
	info[fps_id] = parseInt(msg.fps);
}

function handle_medooze_incoming(msg) {
	// console.log(msg);

	// Incoming medooze stats (stats from publisher side)
	info.medooze_incoming_bitrate = msg.stats.bitrate;
	info.medooze_incoming_lost = msg.stats.lost;
	info.medooze_incoming_drop = msg.stats.drop;
	info.medooze_incoming_pli = msg.stats.pli;
	info.medooze_incoming_nack = msg.stats.nack;
}

function handle_iplink_stats(msg) {
	// Received kernel packets stats
	info.rx_packet = msg.rx.packet;
	info.rx_dropped = msg.rx.dropped;
	info.rx_errors = msg.rx.errors;
	info.rx_missed = msg.rx.missed;

	// Sent kernel packets stats
	info.tx_packet = msg.tx.packet;
	info.tx_dropped = msg.tx.dropped;
	info.tx_errors = msg.tx.errors;
	info.tx_missed = msg.tx.missed;
}

function handle_publisher_launchers(ws) {
	console.log("New publisher launcher");
    // keep ref on ws to notify it
    publisher_launchers.push(ws);
}

function handle_viewer_launchers(ws) {
	console.log("New viewer launcher");
	// keep ref on ws to notify it
	viewer_launchers.push(ws);

	// environment variable for viewer launcher
	let obj = {
		"cmd": "env",
		"medooze_port": 8084,
		"medooze_host": "134.59.133.76",
		"monitor_port": 9000,
		"monitor_host": "134.59.133.57"
	};

	// Send to viewer launcher to setup its environment
	ws.send(JSON.stringify(obj));
}

//Load certs
const options = {
	key     : FS.readFileSync ("server.key"),
	cert	: FS.readFileSync ("server.cert")
};

//Manualy starty server
const server = createServer(options, rest);

//Launch wss server
//Create websocket server
console.log("Starting ws server");
const wss = new WebSocketServer ({ server });

wss.on("connection", (ws) => {
	ws.on('error', console.error);
	ws.on('message', (message) => {
	    // console.log(`received ${message}`);

		let msg = "";
		try {
			// parse json
			msg = JSON.parse(message);
		} catch(err) {
			// return if not json
			console.error(err)
			return
		}

		// Parse and run cmd in json message
		if(msg.cmd === "receiver") {
			handle_new_receiver(ws);
			return;
		}
		else if(msg.cmd === "new_publisher")      publisher_connected(ws);
		else if(msg.cmd === "publisher_bitrate")  info.publisher_bitrate = msg.bitrate;
		else if(msg.cmd === "viewer_count")       info.viewer_count = msg.count;
		else if(msg.cmd === "iammedooze")         medooze_connected(ws);
		else if(msg.cmd === "maxram")             set_max_ram(msg.max);
		else if(msg.cmd === "viewer_bitrate")     update_viewer_bitrate(msg);
		else if(msg.cmd === "vm_stats")           handle_vm_stats(msg.stats);
		else if(msg.cmd === "new_viewer")         handle_new_viewer(msg.name);
		else if(msg.cmd === "viewertarget")       handle_viewer_target(msg);
		else if(msg.cmd === "viewerbitrate")      handle_viewer_bitrate(msg);
		else if(msg.cmd === "medooze_incoming")   handle_medooze_incoming(msg);
		else if(msg.cmd === "iplink_stats")       handle_iplink_stats(msg);
	    else if(msg.cmd === "publisher_pc_state") info.publisher_pc_state = connection_state_map.get(msg.state);
	    else if(msg.cmd === "publisher_launcher") handle_publisher_launchers(ws);
		else if(msg.cmd === "viewer_launcher")      handle_viewer_launchers(ws);
		else return;

		update_listener();
	});
});

// HTTP server listen
server.listen(PORT);

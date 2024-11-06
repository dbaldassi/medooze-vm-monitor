const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const Path              = require("path");
const {WebSocketServer} = require ("ws");

const headers = [
	{id: 'time', title: 'TIME'},
	{id: 'ram_usage', title: 'MEMORY USED'},
	{id: 'ram_free', title: 'MEMORY FREE'},
	{id: 'maxram', title: 'MEMORY MAX'},
	{id: 'swap_usage', title: 'SWAP'},
	{id: 'publisher_bitrate', title: 'PUBLISHER BITRATE'},
	{id: 'viewer_count', title: 'VIEWER COUNT'},
	{id: 'vm_ram_usage', title: 'VM MEMORY USAGE'},
	{id: 'vm_ram_free', title: 'VM MEMORY FREE'}
];

const createCsvWriter = require('csv-writer').createObjectCsvWriter;
var csvWriter = createCsvWriter({
    path: 'stats.csv',
    header: headers,
	append: false
}); 

const config = require('./config.json');

const PORT = 9000;
const KILO = 1024;
const MEGA = 1024 * KILO;
const GIGA = 1024 * MEGA;
const SECONDS = 1000;

const ip = config.host;

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

let receivers = [];

let info = {
	last_modified: undefined,
	time: 0,

 	viewer_count: 0,
	is_publisher_connected: false,
	is_medooze_connected: false,
	viewer_bitrate: [],
	publisher_bitrate: undefined,
	ram_usage: undefined,
	ram_free: undefined,
	swap_usage: undefined,
	maxram: config.initial_max_ram,
	vm_ram_usage: undefined,
	vm_ram_free: undefined,
};

async function log_info() {
	const records = [info];
	await csvWriter.writeRecords(records);
}

function handle_new_receiver(ws) {
	receivers.push(ws);
	ws.send(JSON.stringify(info));
	ws.on('close', () => {
		const index = receivers.indexOf(ws);
		if(index > -1) receivers.splice(index, 1);
	});
}

function update_listener() {
	receivers.forEach(elt => elt.send(JSON.stringify(info)));
}

function update_viewer_bitrate(msg) {

	update_listener();
}

function fetch_ram_usage() {
    const path = Path.join(config.memory_stats_path, config.ram_usage_file);
    const data = FS.readFileSync(path);

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
	info.maxram = max;
	const path = Path.join(config.memory_stats_path, config.ram_total_file);
	FS.writeFileSync(path, String(max * MEGA));
}

function medooze_connected(ws) {
    info.is_medooze_connected = true;

	// console.log("medooze_connected");
    set_max_ram(config.initial_max_ram);
	// console.log("Max ram set");
    const timeout = setInterval(fetch_memory, config.time_interval);

    ws.on('close', () => {
		console.log("Nedooze_close");
		info.is_medooze_connected = false
		clearInterval(timeout[Symbol.toPrimitive]());
		update_listener();
    });
}

function memory_reduction() {
	const increment = 100;

	if(info.ram_free > increment) {
		set_max_ram(info.ram_usage);
	}
	else {
		if(info.ram_usage > info.vm_ram_usage) {
			set_max_ram(info.ram_usage - increment);
		}
	}
}

function publisher_connected(ws) {
	info.is_publisher_connected = true;

	const timeout = setInterval(memory_reduction, 10 * SECONDS);

	ws.on('close', () => {
		info.is_medooze_connected = false
		update_listener();

		clearInterval(timeout[Symbol.toPrimitive]());
	});
}

function handle_vm_stats(stats) {
	info.vm_ram_free = parseInt(stats.freemem / MEGA);
	info.vm_ram_usage = parseInt((stats.totalmem - stats.freemem) / MEGA);
}

function handle_new_viewer(name) {
	console.log("new viewer", name);

	let target_id = name + "_target";
	let bitrate_id = name + "_bitrate";
	let fps_id = name + "_fps";

	headers.push({ id: target_id, title: target_id.toUpperCase() });
	headers.push({ id: bitrate_id, title: bitrate_id.toUpperCase() });
	headers.push({ id: fps_id, title: fps_id.toUpperCase() });

	csvWriter = createCsvWriter({
		path: 'stats.csv',
		header: headers,
		append: true
	}); 

	info[target_id] = 0;
	info[bitrate_id] = 0;
	info[fps_id] = 0;
}

function handle_viewer_target(msg) {	
	let target_id = msg.name + "_target";
	info[target_id] = parseInt(msg.target);

	// console.log(info);
}

function handle_viewer_bitrate(msg) {
	let bitrate_id = msg.name + "_bitrate";
	let fps_id = msg.name + "_fps";

	info[bitrate_id] = parseInt(msg.bitrate);
	info[fps_id] = parseInt(msg.fps);

	// console.log(bitrate_id, msg.bitrate);
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
		// console.log('message');
		let msg = JSON.parse(message);

		// console.log(msg.cmd);

		if(msg.cmd === "receiver") {
			handle_new_receiver(ws);
			return;
		}
		else if(msg.cmd === "new_publisher")     publisher_connected(ws);
		else if(msg.cmd === "publisher_bitrate") info.publisher_bitrate = msg.bitrate;
		else if(msg.cmd === "viewer_count")      info.viewer_count = msg.count;
		else if(msg.cmd === "iammedooze")        medooze_connected(ws);
		else if(msg.cmd === "maxram")            set_max_ram(msg.max);
		else if(msg.cmd === "viewer_bitrate")    update_viewer_bitrate(msg);
		else if(msg.cmd === "vm_stats")          handle_vm_stats(msg.stats);
		else if(msg.cmd === "new_viewer")        handle_new_viewer(msg.name);
		else if(msg.cmd === "viewertarget")      handle_viewer_target(msg);
		else if(msg.cmd === "viewerbitrate")     handle_viewer_bitrate(msg);
		else return;

		update_listener();
	});
});

server.listen(PORT);

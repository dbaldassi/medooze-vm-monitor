const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const Path              = require("path");
const {WebSocketServer} = require ("ws");

const config = require('./config.json');

const PORT = 9000;

//Check 
if (process.argv.length!=3)
	 throw new Error("Missing IP address\nUsage: node index.js <ip>");
//Get ip
const ip = process.argv[2];

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

let receivers = [];

let info = {
	last_modified: undefined,

 	viewer_count: 0,
	is_publisher_connected: false,
	is_medooze_connected: false,
	viewer_bitrate: [],
	publisher_bitrate: undefined,
	ram_usage: undefined,
	ram_free: undefined,
	swap_usage: undefined,
};

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

    info.ram_usage = parseInt(parseInt(data) / (1024*1024));
}

function fetch_ram_free() {
    const path = Path.join(config.memory_stats_path, config.ram_total_file);
    const data = FS.readFileSync(path);
    
    info.ram_free = parseInt(parseInt(data) / (1024*1024)) - info.ram_usage;
    // console.log(parseInt(data), info.ram_free);
}

function fetch_swap_usage() {
	const path = Path.join(config.memory_stats_path, config.swap_usage_file);
	const data = FS.readFileSync(path);

	info.swap_usage = parseInt(data);
}

function fetch_memory() {
	fetch_ram_usage();
	fetch_ram_free();
	fetch_swap_usage();

	update_listener()
}

function set_max_ram(max) {
	// todo write max to memory.max
	const path = Path.join(config.memory_stats_path, config.ram_total_file);
	FS.writeFileSync(path, String(max));
}

function medooze_connected(ws) {
    info.is_medooze_connected = true;

    set_max_ram(3*1024*1024*1024);
    setInterval(fetch_memory, config.time_interval);

    ws.on('close', () => {
	info.is_medooze_connected = false
	clearInterval();
	update_listener();
    });
}

function publisher_connected(ws) {
	info.is_publisher_connected = true;
	ws.on('close', () => {
		info.is_medooze_connected = false
		update_listener();
	});
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
		console.log('message');
		let msg = JSON.parse(message);

		if(msg.cmd === "receiver") {
			handle_new_receiver(ws);
			return;
		}
		else if(msg.cmd === "new_publisher")     publisher_connected(ws);
		else if(msg.cmd === "publisher_bitrate") info.publisher_bitrate = msg.bitrate;
		else if(msg.cmd === "viewer_count")      info.viewer_count = msg.count;
		else if(msg.cmd === "iammedooze")        medooze_connected(ws);
		else if(msg.cmd === "viewer_bitrate")    update_viewer_bitrate(msg);
		else if(msg.cmd === "maxram")            set_max_ram(msg.max);
		else return;

		update_listener();
	});
});

server.listen(PORT);

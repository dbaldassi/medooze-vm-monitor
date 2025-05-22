// Node modules
const Express           = require("express");
const CORS              = require("cors");
const FS                = require("fs");
const { createServer }  = require("https");
const parse             = require('json-templates');
const WebSocketServer   = require ("websocket").server;

// Get config
const config = require('./config.json');
// Get Update listener function
const update_listener = require('./lib/receivers.js').update_listener;
// Get Monitor
const monitor = require('./monitor.js');

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

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
	"visio"             : require('./lib/visio.js'),
	"receiver"           : require('./lib/receivers.js').handler,
	"visio_launcher"     : require('./lib/visio_launcher.js').handler,	
};

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
	handlers[protocol](request, protocol, monitor);

	// Update all listener
	update_listener();
});

// Check if scenario provided
if (process.argv.length >= 3) {
	// Get file name
	const scenar_name = process.argv[2];
	const scenar = require(`./scenario/${scenar_name}.json`);
	
	const template = parse(scenar);

	let args = process.argv.slice(3);
	const obj = {};
	console.log(args, template.parameters);

	for(let param of template.parameters) {
		if(param.defaultValue) {
			let value = parseInt(param.defaultValue);
			if(!Number.isNaN(value)) param.defaultValue = value;
		}
	}

	for(let arg of args) {
		let split = arg.split(":");

		let param = template.parameters.find(e => e.key === split[0]);
	
		if(param) obj[`${split[0]}`] = Number.isNaN(parseInt(split[1])) ? split[1] : parseInt(split[1]);
	}

    console.log(JSON.stringify(template(obj)));

	// RUN !!
	monitor.run(template(obj));
}
else {
	// Get default scenario (max2500, don't start launcher and medooze)
	const scenar = require(`./scenario/default.json`);
	// RUN !!
	monitor.run(scenar);
}

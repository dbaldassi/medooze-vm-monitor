import Express from 'npm:express';
import CORS from 'npm:cors';
import fs from 'node:fs';
import process from 'node:process';
import { createServer } from 'node:https';
import { server as WebSocketServer } from 'npm:websocket';
import config from './config/config.json' with { type: 'json' };
// import { update_listener } from './lib/receivers.js';
import { MonitorConfig } from './src/monitor.ts';
import { MonitorFactory } from './src/monitor_factory.ts';

//Create rest api
const rest = Express();
rest.use(CORS());
rest.use(Express.static("www"));

// Load certs
const options = {
    key: fs.readFileSync ("config/server.key"),
    cert: fs.readFileSync ("config/server.cert")
};

// Manualy start server
const server = createServer(options, rest);
server.listen(config.port);

console.log("Starting ws server");
const wss = new WebSocketServer({ httpServer: server, autoAcceptConnections: false });

wss.on("request", (request: any) => {
    // // Get protocol
    // let protocol = request.requestedProtocols[0];
    // console.log("-Got request for: " + protocol);

    // //If not found
    // if (!handlers.hasOwnProperty (protocol))
    //     //Reject connection
    //     return request.reject();

    // // Process it
    // handlers[protocol](request, protocol, monitor);

    // // Update all listener
    // update_listener();
});

if (process.argv.length >= 3) {
    const data = fs.readFileSync(process.argv[2], 'utf8');
    const monitor_config: MonitorConfig = JSON.parse(data);
    const monitor = MonitorFactory.create(monitor_config);

    if(monitor) monitor.run().then(() => exit());
}
else {
    console.error("No config provided for monitor");
}

function exit() {
    console.log("Exiting");
    server.closeAllConnections();
    process.exit(0);
}

// Get config
const config = require('../config.json');

var launchers = [];

function handler(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    console.log("New viewer launcher");
    launchers.push(connection);

    connection.on('message', (message) => {});
    connection.on('close', () => {});

    // environment variable for viewer launcher
	let obj = {
		"cmd": "env",
		"medooze_port": config.medooze_server.port,
		"medooze_host": config.medooze_server.host,
		"monitor_port": config.port,
		"monitor_host": config.host
	};

	// Send to viewer launcher to setup its environment
	connection.sendUTF(JSON.stringify(obj));
}

module.exports = {
    handler: handler,
    launchers: launchers
}
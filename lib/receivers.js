// Get logger
const logger = require('../stats.js');

var receivers = [];

function update_listener() {
	// Send info object to all listeners so they know whats going on
	receivers.forEach(elt => elt.sendUTF(JSON.stringify(logger.info)));
}

function handler(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    // Keep ref on the new viewer
    receivers.push(ws);
    // Send current info so it init itself
    ws.sendUTF(JSON.stringify(info));

    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);
        if(msg.cmd === "maxram")  callbacks.set_max_ram(msg.max);
    });
    connection.on('close', () => {
        const index = receivers.indexOf(ws);
		if(index > -1) receivers.splice(index, 1);
    });
}

module.exports = {
    handler: handler,
    update_listener: update_listener
}
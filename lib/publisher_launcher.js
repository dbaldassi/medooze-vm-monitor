// Get logger
const logger = require('../stats.js');

var launchers = [];

function handler(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    console.log("New publisher launcher");
    // launchers.push(connection);

    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);

        if(msg.cmd === "id") launchers.push({ id : msg.id, ws : connection });
    });
    connection.on('close', () => {});
}

module.exports = {
    handler: handler,
    launchers: launchers
}


var launchers = [];

function handler(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    console.log("New visio launcher");

    connection.on('message', (message) => {
		let msg = JSON.parse(message.utf8Data);

        console.log(msg);
        if(msg.cmd === "id") launchers.push({ id : msg.id, ws : connection });
	});
    connection.on('close', () => {});
}

module.exports = {
    handler: handler,
    launchers: launchers
}
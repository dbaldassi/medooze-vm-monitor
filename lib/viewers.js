// Get logger
const { logger } = require('../src/stats.js');

function handle_new_viewer(name) {
    if(logger.viewers.has(name)) {
        console.log("Viewer already exists");
        return;
    }

    console.log("Adding new viewer", name);

    logger.info.viewers.set(name, {
        target: 0,
        bitrate: 0,
        rtt: 0,
        e2e: 0,
        fps: 0,
        res: undefined,
        rid: undefined
    });
}

function handle_viewer_target(msg) {
    let viewer = logger.viewers.get(name);
    viewer.target = parseInt(msg.target);
    viewer.rid = msg.rid;
}

function endsWith_array(str, array) {
    for(let s of array) {
        if(str.endsWith(s) && !str.startsWith("publisher")) return true;
    }

    return false;
}

function reset_logger(name) {
    logger.viewer.delete(name);
}

function handle_viewer_bitrate(msg) {
    let viewer = logger.viewers.get(name);

    viewer.bitrate = parseInt(msg.bitrate);
    viewer.rtt = parseInt(msg.rtt);
    viewer.e2e = parseInt(msg.delay);
    viewer.fps = parseInt(msg.fps);
    viewer.res = msg.res;
}

module.exports = function(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);

        if(msg.cmd === "bitrate")      handle_viewer_bitrate(msg);
        else if(msg.cmd === "target")  handle_viewer_target(msg);
        else if(msg.cmd === "id") {
			handle_new_viewer(msg.name);
			connection.viewer_id = msg.name;
		}
    });

    connection.on('close', () => {
		console.log("Closing : ", connection.viewer_id);
		// Reset the stats for the viewer
		if(connection.viewer_id) reset_logger(connection.viewer_id);
		
	});
}

// Get logger
const logger = require('../stats.js');

function handle_new_viewer(name) {
	console.log("new viewer", name);

	// Create new stats IDs for this viewer stats 
	let target_id = name + "_target";
	let bitrate_id = name + "_bitrate";
	let fps_id = name + "_fps";

	// Add new IDs to the csv header
	logger.add_header(target_id,target_id.toUpperCase());
	logger.add_header(bitrate_id, bitrate_id.toUpperCase());
	logger.add_header(fps_id, fps_id.toUpperCase());

	// Re-create the csv writer to write stats for the new viewer
    logger.create_writer(true);

	// Set default values
	logger.info[target_id] = 0;
	logger.info[bitrate_id] = 0;
	logger.info[fps_id] = 0;
}

function handle_viewer_target(msg) {	
	// Retrieve csv header id
	let target_id = msg.name + "_target";
	// Update stats
	logger.info[target_id] = parseInt(msg.target);
}

function handle_viewer_bitrate(msg) {
	// Retrieve csv header id
	let bitrate_id = msg.name + "_bitrate";
	let fps_id = msg.name + "_fps";

	// Update stats 
	logger.info[bitrate_id] = parseInt(msg.bitrate);
	logger.info[fps_id] = parseInt(msg.fps);
}

module.exports = function(request, protocol, callbacks) {
    const connection = request.accept(protocol);

    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);

        if(msg.cmd === "bitrate")      handle_viewer_bitrate(msg);
        else if(msg.cmd === "target")  handle_viewer_target(msg);
        else if(msg.cmd === "id")      handle_new_viewer(msg.name);
    });

    connection.on('close', () => {});
}
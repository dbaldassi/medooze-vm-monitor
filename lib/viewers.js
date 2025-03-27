// Get logger
const logger = require('../stats.js');

function handle_new_viewer(name) {
	console.log("new viewer", name);

	// Create new stats IDs for this viewer stats 
	let target_id = `${name}_target`;
	let bitrate_id = `${name}_bitrate`;
	let rtt_id = `${name}_rtt`;
	let e2e_id = `${name}_e2edelay`;
	let fps_id = `${name}_fps`;
	let res_id = `${name}_res`;
	let rid_id = `${name}_rid`;
	// Create header name
	let target_name = `${name} target`;
	let bitrate_name = `${name} bitrate`;
	let rtt_name = `${name} rtt`;
	let e2e_name = `${name} E2E DELAY`;
	let fps_name = `${name} fps`;
	let res_name = `${name} RESOLUTION`;
	let rid_name = `${name} rid`;

	if(logger.headers.includes(target_id)) return;
	
	// Add new IDs to the csv header
	logger.add_header(target_id,target_name.toUpperCase());
	logger.add_header(bitrate_id, bitrate_name.toUpperCase());
	logger.add_header(rtt_id, rtt_name.toUpperCase());
	logger.add_header(e2e_id, e2e_name.toUpperCase());
	logger.add_header(fps_id, fps_name.toUpperCase());
	logger.add_header(res_id, res_name.toUpperCase());
	logger.add_header(rid_id, rid_name.toUpperCase());
	
	// Re-create the csv writer to write stats for the new viewer
    logger.create_writer(true);

	// Set default values
	logger.info[target_id] = 0;
	logger.info[bitrate_id] = 0;
	logger.info[rtt_id] = 0;
	logger.info[e2e_id] = 0;
	logger.info[fps_id] = 0;
	logger.info[res_id] = "0x0";
	logger.info[rid_id] = '0';
}

function handle_viewer_target(msg) {	
	// console.log(msg);
	// Retrieve csv header id
	let target_id = msg.name + "_target";
	let rid_id = msg.name + "_rid";
	// Update stats
	logger.info[target_id] = parseInt(msg.target);
	logger.info[rid_id] = msg.rid;
}

function endsWith_array(str, array) {
	for(let s of array) {
		if(str.endsWith(s) && !str.startsWith("publisher")) return true;
	}

	return false;
}

function reset_logger(name) {
	let target_id = `${name}_target`;
	let bitrate_id = `${name}_bitrate`;
	let rtt_id = `${name}_rtt`;
	let e2e_id = `${name}_e2edelay`;
	let fps_id = `${name}_fps`;
	let res_id = `${name}_res`;
	let rid_id = `${name}_rid`;

	logger.info[target_id] = undefined;
	logger.info[bitrate_id] = undefined;
	logger.info[rtt_id] = undefined;
	logger.info[e2e_id] = undefined;
	logger.info[fps_id] = undefined;
	logger.info[res_id] = undefined;
	logger.info[rid_id] = undefined;
}

function handle_viewer_bitrate(msg) {
	// Retrieve csv header id
	let bitrate_id = msg.name + "_bitrate";
	let rtt_id = msg.name + "_rtt";
	let e2e_id = msg.name + "_e2edelay";
	let fps_id = msg.name + "_fps";
	let res_id = msg.name + "_res";
	// Update stats 
	logger.info[bitrate_id] = parseInt(msg.bitrate);
	logger.info[rtt_id] = parseInt(msg.rtt);
	logger.info[e2e_id] = parseInt(msg.delay);
	logger.info[fps_id] = parseInt(msg.fps);
	logger.info[res_id] = msg.res;
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
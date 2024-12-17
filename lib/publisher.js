// Get logger
const logger = require('../stats.js');

// Peerconnection state map to write number in stat.csv
const connection_state_map = new Map();
connection_state_map.set('disconnected', 1);
connection_state_map.set('closed', 0);
connection_state_map.set('connecting', 2);
connection_state_map.set('new', 2);
connection_state_map.set('connected', 3);
connection_state_map.set('failed', 4);
connection_state_map.set('checking', 5);
connection_state_map.set('completed', 6);

function handle_bitrate(msg) {
    logger.info.publisher_bitrate = msg.bitrate;
    logger.info.publisher_fps = msg.fps;
    logger.info.publisher_res = msg.res;
}

module.exports = function(request, protocol, callbacks) {
    const connection = request.accept(protocol);
    console.log("publisher accept");
    
    // Update publisher connection state
    logger.info.is_publisher_connected = true;
    callbacks.publisher_connected();

    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);

        if(msg.cmd === "bitrate")           handle_bitrate(msg);
        else if(msg.cmd === "pc_state")     logger.info.publisher_pc_state = connection_state_map.get(msg.state);
        else if(msg.cmd === "viewer_count") logger.info.viewer_count = msg.count;
    });

    connection.on('close', () => {
        logger.info.is_publisher_connected = false
        callbacks.publisher_disconnected();
    });
};
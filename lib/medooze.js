
// Get logger
const logger = require('../stats.js');

// Units
const KILO = 1024;
const MEGA = 1024 * KILO;

function handle_medooze_incoming(msg) {
	// console.log(msg);

	// Incoming medooze stats (stats from publisher side)
	logger.info.medooze_incoming_bitrate = msg.stats.bitrate;
	logger.info.medooze_incoming_lost = msg.stats.lost;
	logger.info.medooze_incoming_drop = msg.stats.drop;
	logger.info.medooze_incoming_pli = msg.stats.pli;
	logger.info.medooze_incoming_nack = msg.stats.nack;
}

function handle_iplink_stats(msg) {
	// Received kernel packets stats
	logger.info.rx_packet = msg.rx.packet;
	logger.info.rx_dropped = msg.rx.dropped;
	logger.info.rx_errors = msg.rx.errors;
	logger.info.rx_missed = msg.rx.missed;

	// Sent kernel packets stats
	logger.info.tx_packet = msg.tx.packet;
	logger.info.tx_dropped = msg.tx.dropped;
	logger.info.tx_errors = msg.tx.errors;
	logger.info.tx_missed = msg.tx.missed;
}

function handle_vm_stats(stats) {
	// Update VM memory and cpu usage
	logger.info.vm_ram_free = parseInt(stats.freemem / MEGA);
	logger.info.vm_ram_usage = parseInt((stats.totalmem - stats.freemem) / MEGA);
	logger.info.vm_cpu_usage = stats.cpu;
}

function reset_logger(stats) {
	// Set every medooze stats to 0
	logger.info.medooze_incoming_bitrate = undefined;
	logger.info.medooze_incoming_lost = undefined;
	logger.info.medooze_incoming_drop = undefined;
	logger.info.medooze_incoming_pli = undefined;
	logger.info.medooze_incoming_nack = undefined;
	// Received kernel packets stats
	logger.info.rx_packet = undefined;
	logger.info.rx_dropped = undefined;
	logger.info.rx_errors = undefined;
	logger.info.rx_missed = undefined;
	// Sent kernel packets stats
	logger.info.tx_packet = undefined;
	logger.info.tx_dropped = undefined;
	logger.info.tx_errors = undefined;
	logger.info.tx_missed = undefined;
	// Update VM memory and cpu usage
	logger.info.vm_ram_free = undefined;
	logger.info.vm_ram_usage = undefined;
	logger.info.vm_cpu_usage = undefined;
}

module.exports = function(request, protocol, callbacks) {
    const connection = request.accept(protocol);
 
    console.log("medooze connected");

    logger.info.is_medooze_connected = true;
    callbacks.medooze_connected(connection);

    connection.on('message', (message) => {
		// console.log("medooze sent : ", message);
        let msg = JSON.parse(message.utf8Data);

        if(msg.cmd === "iplink_stats")            handle_iplink_stats(msg);
        else if(msg.cmd === "medooze_incoming")   handle_medooze_incoming(msg);
        else if(msg.cmd === "vm_stats")           handle_vm_stats(msg.stats);
    });

    connection.on('close', () => {
        console.log("Medooze close");
        logger.info.is_medooze_connected = false
		callbacks.medooze_disconnected();

		reset_logger();
    });
}
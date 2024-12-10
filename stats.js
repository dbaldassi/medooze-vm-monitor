
const config = require('./config.json');
// Create csv logger to log all stats
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

class StatsLogger {
    constructor() {
        this.csvWriter = undefined;
        
        // csv stats headers
        this.headers = [
            {id: 'time', title: 'TIME'},
            {id: 'ram_usage', title: 'MEMORY USED'},
            {id: 'ram_free', title: 'MEMORY FREE'},
            {id: 'maxram', title: 'MEMORY MAX'},
            {id: 'swap_usage', title: 'SWAP'},
            {id: 'publisher_bitrate', title: 'PUBLISHER BITRATE'},
            {id: 'publisher_pc_state', title: 'CONNECTION STATE'},
            {id: 'viewer_count', title: 'VIEWER COUNT'},
            {id: 'vm_ram_usage', title: 'VM MEMORY USAGE'},
            {id: 'vm_ram_free', title: 'VM MEMORY FREE'},
            {id: 'vm_cpu_usage', title: 'VM CPU USAGE'},
            {id: 'medooze_incoming_lost', title: 'MEDOOZE INCOMING LOST'},
            {id: 'medooze_incoming_drop', title: 'MEDOOZE INCOMING DROP'},
            {id: 'medooze_incoming_bitrate', title: 'MEDOOZE INCOMING BITRATE'},
            {id: 'medooze_incoming_nack', title: 'MEDOOZE INCOMING NACK'},
            {id: 'medooze_incoming_pli', title: 'MEDOOZE INCOMING PLI'},
            {id: 'rx_packet', title: 'RX PACKET'},
            {id: 'rx_dropped', title: 'RX DROPPED'},
            {id: 'rx_errors', title: 'RX ERRORS'},
            {id: 'rx_missed', title: 'RX MISSED'},
            {id: 'tx_packet', title: 'TX PACKET'},
            {id: 'tx_dropped', title: 'TX DROPPED'},
            {id: 'tx_errors', title: 'TX ERRORS'},
            {id: 'tx_missed', title: 'TX MISSED'},
        ];

        this.info = {
            last_modified: undefined,
            time: 0,
        
             viewer_count: 0,
            is_publisher_connected: false,
            is_medooze_connected: false,
            publisher_bitrate: undefined,
            publisher_pc_state: 0,
            ram_usage: undefined,
            ram_free: undefined,
            swap_usage: undefined,
            maxram: config.initial_max_ram,
            vm_ram_usage: undefined,
            vm_ram_free: undefined,
            vm_cpu_usage: undefined,
        
            // medooze incoming
            medooze_incoming_lost: 0,
            medooze_incoming_drop: 0,
            medooze_incoming_bitrate: 0,
            medooze_incoming_nack: 0,
            medooze_incoming_pli: 0,
        
            //ip link stats
            rx_packet: 0,
            rx_dropped: 0,
            rx_missed: 0,
            rx_errors: 0,
            tx_packet: 0,
            tx_dropped: 0,
            tx_missed: 0,
            tx_errors: 0,
        };

        this.create_writer(false);
    }

    add_header(id, title) {
        this.headers.push({id : id, title : title});
    }

    create_writer(append) {
        this.csvWriter = createCsvWriter({
            path: 'stats.csv',
            header: this.headers,
            append: append
        }); 
    }
    
    async log_info() {
        // write a new line into the csv file
        const records = [this.info];
        await this.csvWriter.writeRecords(records);
    }
}

// glogbal / singleton
var logger = new StatsLogger;

module.exports = logger;
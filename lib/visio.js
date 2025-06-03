// Get logger
const logger = require('../src/stats.js');

function handle_report(msg) {
    const report = msg.reports;

    for(let stat of report) {
        // console.log(stat.room, stat.id, stat.peer);

        const room = logger.info.rooms.get(stat.room);
        if(!room) continue;

        const participant = room.participants.get(stat.id);
        if(!participant) continue;

        // find peer in participant
        let peer = participant.find(e => e.id === stat.peer);
        if(!peer) {
            participant.push({
                bitrate: stat.bitrate,
                delay: stat.delay,
                fps: stat.fps,
                id: stat.peer,
                rtt: stat.rtt,
            });
        } 
        else {
            peer.bitrate = stat.bitrate;
            peer.delay = stat.delay;
            peer.fps = stat.fps;
            peer.rtt = stat.rtt;
        }
    }
}

function handle_new_participant(id, room_id) {
    console.log("Hey new participant", {id, room_id});
    if(!logger.info.rooms.has(room_id)) {  
        console.log("Creating new room");
        logger.info.rooms.set(room_id, {
            participants: new Map(),
            csv: undefined,
            headers_modified: false,
            csv_header: [
                {id: "time", title: "TIME"},
                {id: "participant_id", title: "PARTICIPANT_ID"},
                {id: "num_participants", title: "NUM_PARTICIPANTS"},
                {id: "sent_rtt", title: "SENT_RTT"},
                {id: "sent_bitrate", title: "SENT_BITRATE"},
                {id: "sent_fps", title: "SENT_FPS"},
            ],
        });
    }

    const room = logger.info.rooms.get(room_id);
    room.participants.set(id, []);
    room.csv_header.push({id: id + "_bitrate", title: id + "_BITRATE"});
    room.csv_header.push({id: id + "_rtt", title: id + "_RTT"});
    room.csv_header.push({id: id + "_fps", title: id + "_FPS"});
    room.headers_modified = !!room.csv;
}

function handle_participant_left(id, room_id) {
    const room = logger.info.rooms.get(room_id);
    /*if(room) {
        room.participants.delete(id);
        // delete participant from other partipants
        for(let [key, value] of room.participants) {
            let index = value.findIndex(e => e.id === id);
            if(index !== -1) {
                value.splice(index, 1);
            }
        }
    }*/
    if(!room) return;
    if(!room.participants.has(id)) return;

    const participant = room.participants.get(id);
    participant.forEach(peer => {
        peer.bitrate = 0;
        peer.delay = 0;
        peer.fps = 0;
        peer.rtt = 0;
    });
}

module.exports = function(request, protocol, _) {
    const connection = request.accept(protocol);
    console.log("visio accept");
    
    connection.on('message', (message) => {
        let msg = JSON.parse(message.utf8Data);
        // console.log(msg);
        if(msg.cmd === "report")  handle_report(msg);
        else if(msg.cmd === "hey") {
            handle_new_participant(msg.id, msg.room);
            connection.participant_id = msg.id;
            connection.room_id = msg.room_id;
        }
    });

    connection.on('close', () => {
        handle_participant_left(connection.participant_id, connection.room_id);
    });
};
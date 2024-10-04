const url = "wss://" + window.location.hostname + ":" + window.location.port;

var opts = {
    lines: 12, // The number of lines to draw
    angle: 0.15, // The length of each line
    lineWidth: 0.44, // 0.44 The line thickness
    pointer: {
	length: 0.8, // 0.9 The radius of the inner circle
	strokeWidth: 0.035, // The rotation offset
	color: '#A0A0A0'     // Fill color
    },
    limitMax: true,
    colorStart: '#28c1d1', // Colors
    colorStop: '#28c1d1', // just experiment with them
    strokeColor: '#F0F0F0', // to see which ones work best for you
    generateGradient: false,
    gradientType: 0
};

var targets = document.querySelectorAll('.gaugeChart'); // your canvas element
var gauges = [];
for (var i=0;i<targets.length;++i)
{
    gauges[i] = new Gauge(targets[i]).setOptions (opts); // create sexy gauge!
    gauges[i].animationSpeed = 10000; // set animation speed (32 is default value)
    gauges[i].set (0); // set actual value
}

function update_info(data) {
    let publisher_state = document.getElementById("publisherstate");
    publisher_state.innerHTML = "Publisher: " + (data.is_publisher_connected ? "Connected": "Not Connected");

    let medooze_state = document.getElementById("medoozestate");
    medooze_state.innerHTML = "Medooze: " + (data.is_medooze_connected ? "Connected": "Not Connected");

    let viewer_count = document.getElementById("viewercount");
    viewer_count.innerHTML = "Viewer: " + data.viewer_count;

    gauges[0].set(data.ram_usage ?? 0);
    gauges[1].set(data.ram_free ?? 0);
    gauges[2].set(data.swap_usage ?? 0);
}

(function () {
    const ws = new WebSocket(url);

    ws.onopen = async () => {
        // console.log("Websocket is open");
        ws.send(JSON.stringify({cmd: "receiver"}));
    }

    ws.onmessage = async (message) => {
        let msg = JSON.parse(message.data);
        update_info(msg);
    }
})()
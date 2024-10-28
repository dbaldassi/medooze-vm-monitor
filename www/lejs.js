const url = "wss://" + window.location.hostname + ":" + window.location.port;

const MEGA = 1024 * 1024;

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
for (var i=0; i < targets.length; ++i)
{
    gauges[i] = new Gauge(targets[i]).setOptions (opts); // create sexy gauge!
    gauges[i].animationSpeed = 32; // set animation speed (32 is default value)
    gauges[i].set (0); // set actual value
    gauges[i].maxValue = 0;
}

var texts = document.querySelectorAll('.gaugeChartLabel');
var max_texts = document.querySelectorAll('.gaugeChartMax');

function update_info(data) {
    let publisher_state = document.getElementById("publisherstate");
    publisher_state.innerHTML = "Publisher: " + (data.is_publisher_connected ? "Connected": "Not Connected");

    let medooze_state = document.getElementById("medoozestate");
    medooze_state.innerHTML = "Medooze: " + (data.is_medooze_connected ? "Connected": "Not Connected");

    let viewer_count = document.getElementById("viewercount");
    viewer_count.innerHTML = "Viewer: " + data.viewer_count;

    let ram = data.ram_usage ?? 0;
    let free = data.ram_free ?? 0;
    let swap = data.swap_usage ?? 0;
    let publisher_bitrate = data.publisher_bitrate ?? 0;
    let vm_ram_usage = data.vm_ram_usage ?? 0;
    let vm_ram_free = data.vm_ram_free ?? 0;
    
    gauges[0].maxValue = data.maxram;
    gauges[1].maxValue = data.maxram;
    gauges[3].maxValue = data.maxram;
    gauges[4].maxValue = data.maxram;
    gauges[5].maxValue = Math.max(publisher_bitrate, gauges[3].maxValue);

    max_texts[0].innerText = data.maxram;
    max_texts[1].innerText = data.maxram;
    max_texts[3].innerText = data.maxram;
    max_texts[4].innerText = data.maxram;

    gauges[0].set(ram);
    gauges[1].set(free);
    gauges[2].set(swap);
    gauges[3].set(vm_ram_usage);
    gauges[4].set(vm_ram_free);
    gauges[5].set(publisher_bitrate);

    texts[0].innerText = ram;
    texts[1].innerText = free;
    texts[2].innerText = swap;
    texts[3].innerText = vm_ram_usage;
    texts[4].innerText = vm_ram_free;
    texts[5].innerText = publisher_bitrate;
}

(function () {
    const ws = new WebSocket(url);

    ws.onopen = async () => {
        // console.log("Websocket is open");
        ws.send(JSON.stringify({cmd: "receiver"}));
    }

    let setup_slider = false;
    let slider = document.getElementById("slider");
    let slider_text = document.getElementById("slidertext");

    ws.onmessage = async (message) => {
        let data = JSON.parse(message.data);
        update_info(data);

        if(!setup_slider) {
            console.log(data)

            slider.max = data.maxram;
            slider.value = slider.max;
            slider_text.innerHTML = slider.value;

            setup_slider = true;
        }
    }

    slider.oninput = () => {
        slider_text.innerHTML = slider.value;
        ws.send(JSON.stringify({ cmd: "maxram", max: slider.value }));
    };
})()

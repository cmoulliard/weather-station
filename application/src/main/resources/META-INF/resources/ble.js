var Charts = window.Charts || window['@carbon/charts'];
var LineChart = Charts.LineChart;

var MAX_POINTS = 100;
var history = [];
var chart = null;
var ws;

function initChart() {
    var el = document.getElementById('ble-history-chart');
    if (!el) return;

    var colorScale = {};
    colorScale['Sensor Value'] = '#0f62fe';

    chart = new LineChart(el, {
        data: [],
        options: {
            title: 'Sensor readings over time',
            resizable: true,
            height: '300px',
            axes: {
                bottom: { mapsTo: 'date', scaleType: 'time' },
                left: { mapsTo: 'value' }
            },
            curve: 'curveMonotoneX',
            toolbar: { enabled: false },
            legend: { enabled: false },
            tooltip: { showTotal: false },
            points: { radius: 3 },
            color: { scale: colorScale }
        }
    });
}

function connect() {
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(proto + '//' + location.host + '/ws/ble');

    ws.onmessage = function(e) {
        var msg = JSON.parse(e.data);
        if (msg.type === 'sensor') onSensor(msg);
        else if (msg.type === 'status') onStatus(msg);
        else if (msg.type === 'led') onLed(msg);
    };

    ws.onclose = function() {
        setTimeout(connect, 2000);
    };

    ws.onerror = function() {
        // onclose will fire after this
    };
}

function onSensor(msg) {
    document.getElementById('ble-sensor-value').textContent = msg.value;
    var d = new Date(msg.ts * 1000);
    document.getElementById('ble-last-update').textContent = d.toLocaleTimeString();

    var num = parseFloat(msg.value);
    if (!isNaN(num)) {
        history.push({ group: 'Sensor Value', date: new Date(msg.ts * 1000), value: num });
        if (history.length > MAX_POINTS) history.shift();
        if (chart) {
            chart.model.setData(history.slice());
        }
    }
    addLog('Sensor: ' + msg.value);
}

function onStatus(msg) {
    var dot = document.getElementById('ble-status-dot');
    var txt = document.getElementById('ble-status-text');
    var addr = document.getElementById('ble-address');

    dot.className = 'ble-dot ble-dot--' + msg.state;

    var labels = {
        disabled: 'Disabled',
        scanning: 'Scanning…',
        connecting: 'Connecting…',
        connected: 'Connected',
        disconnected: 'Disconnected',
        not_found: 'Device not found',
        error: 'Error'
    };
    txt.textContent = labels[msg.state] || msg.state;
    addr.textContent = msg.address || '';

    addLog('Status: ' + (labels[msg.state] || msg.state) +
        (msg.address ? ' (' + msg.address + ')' : ''));
}

function onLed(msg) {
    var onBtn = document.getElementById('led-on-btn');
    var offBtn = document.getElementById('led-off-btn');

    if (msg.state === 1) {
        onBtn.classList.add('ble-led-btn--active');
        offBtn.classList.remove('ble-led-btn--active');
    } else {
        offBtn.classList.add('ble-led-btn--active');
        onBtn.classList.remove('ble-led-btn--active');
    }
    addLog('LED: ' + (msg.state ? 'ON' : 'OFF'));
}

function sendLed(state) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ cmd: 'led', state: state }));
    }
}

function addLog(text) {
    var el = document.getElementById('ble-log');
    var t = new Date().toLocaleTimeString();
    var entry = document.createElement('div');
    entry.className = 'ble-log-entry';
    entry.textContent = t + ' — ' + text;
    el.appendChild(entry);
    el.scrollTop = el.scrollHeight;

    // Keep log bounded
    while (el.children.length > 200) {
        el.removeChild(el.firstChild);
    }
}

// Fetch initial status via REST (in case WebSocket replays are missed)
function fetchInitialStatus() {
    fetch('/api/ble')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(data) {
            if (!data) return;
            onStatus({ state: data.state, address: data.address });
            if (data.latestValue) {
                document.getElementById('ble-sensor-value').textContent = data.latestValue;
            }
            if (data.latestTimestamp) {
                var d = new Date(data.latestTimestamp);
                document.getElementById('ble-last-update').textContent = d.toLocaleTimeString();
            }
        })
        .catch(function(e) { console.error('Failed to fetch BLE status', e); });
}

document.addEventListener('DOMContentLoaded', function() {
    initChart();
    fetchInitialStatus();
    connect();
});

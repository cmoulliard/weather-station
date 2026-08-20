var Charts = window.Charts || window['@carbon/charts'];
var LineChart = Charts.LineChart;

var VALUE_FIELDS = ['temperature', 'humidity', 'pressure', 'windSpeed', 'rainfall'];

var HISTORY_CONFIGS = [
    { field: 'temperature', label: 'Temperature (°C)', color: '#da1e28' },
    { field: 'humidity',    label: 'Humidity (%)',      color: '#0043ce' },
    { field: 'pressure',    label: 'Pressure (hPa)',   color: '#198038' },
    { field: 'windSpeed',   label: 'Wind Speed (km/h)', color: '#8a3ffc' },
    { field: 'rainfall',    label: 'Rainfall (mm)',    color: '#005d5d' },
];

var historyCharts = {};

function createHistoryCharts() {
    HISTORY_CONFIGS.forEach(function(cfg) {
        var el = document.getElementById('history-' + cfg.field);
        if (!el) return;
        var colorScale = {};
        colorScale[cfg.label] = cfg.color;
        historyCharts[cfg.field] = new LineChart(el, {
            data: [],
            options: {
                title: cfg.label,
                resizable: true,
                height: '250px',
                axes: {
                    bottom: { mapsTo: 'date', scaleType: 'time' },
                    left: { mapsTo: 'value' },
                },
                curve: 'curveMonotoneX',
                toolbar: { enabled: false },
                legend: { enabled: false },
                tooltip: { showTotal: false },
                points: { radius: 2 },
                color: { scale: colorScale },
            },
        });
    });
}

function refreshCurrent() {
    fetch('/api/weather')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(data) {
            if (!data) return;
            VALUE_FIELDS.forEach(function(field) {
                var el = document.getElementById('val-' + field);
                if (el) {
                    var v = data[field];
                    el.textContent = (v != null) ? v.toFixed(1) : '--';
                }
            });
            document.getElementById('last-updated').textContent =
                'Last updated: ' + new Date(data.timestamp).toLocaleTimeString();
        })
        .catch(function(e) { console.error('Failed to fetch current weather', e); });
}

function refreshHistory() {
    var range = document.getElementById('range-select').value || '-1h';
    fetch('/api/weather/history?range=' + range)
        .then(function(res) { return res.ok ? res.json() : []; })
        .then(function(data) {
            HISTORY_CONFIGS.forEach(function(cfg) {
                var chartData = [];
                data.forEach(function(r) {
                    chartData.push({ group: cfg.label, date: new Date(r.timestamp), value: r[cfg.field] });
                });
                if (historyCharts[cfg.field]) {
                    historyCharts[cfg.field].model.setData(chartData);
                }
            });
        })
        .catch(function(e) { console.error('Failed to fetch history', e); });
}

function loadMap() {
    fetch('/api/weather/location')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(loc) {
            if (!loc || (!loc.latitude && !loc.longitude)) return;
            var mapEl = document.getElementById('station-map');
            if (!mapEl || mapEl.dataset.loaded) return;
            mapEl.dataset.loaded = 'true';

            var titleEl = document.getElementById('map-title');
            if (titleEl) titleEl.textContent = 'Station: ' + loc.name;

            var map = L.map('station-map').setView([loc.latitude, loc.longitude], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 18,
            }).addTo(map);
            L.marker([loc.latitude, loc.longitude])
                .addTo(map)
                .bindPopup(loc.name)
                .openPopup();
        })
        .catch(function(e) { console.error('Failed to load location', e); });
}

function refreshStatus() {
    fetch('/api/weather/status')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(status) {
            if (!status) return;
            var el = document.getElementById('data-source');
            if (el) {
                el.textContent = status.influxdb ? 'InfluxDB connected' : 'In-memory only';
                el.className = 'status-tag ' + (status.influxdb ? 'status-connected' : 'status-disconnected');
            }
        })
        .catch(function(e) { console.error('Failed to fetch status', e); });
}

document.addEventListener('DOMContentLoaded', function() {
    createHistoryCharts();
    refreshCurrent();
    refreshHistory();
    refreshStatus();
    loadMap();

    setInterval(refreshCurrent, 30000);
    setInterval(refreshHistory, 60000);

    document.getElementById('range-select').addEventListener('change', refreshHistory);
});

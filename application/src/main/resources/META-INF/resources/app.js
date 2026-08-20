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
var leafletMap = null;
var leafletMarker = null;
var windDirByTimestamp = {};

var CARDINALS = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];

function degreesToCardinal(deg) {
    var idx = Math.round(((deg % 360) + 360) % 360 / 22.5) % 16;
    return CARDINALS[idx];
}

function owmIconUrl(icon, size) {
    return 'https://openweathermap.org/img/wn/' + icon + (size || '@2x') + '.png';
}

/* ── History charts ─────────────────────────────── */

function createHistoryCharts() {
    HISTORY_CONFIGS.forEach(function(cfg) {
        var el = document.getElementById('history-' + cfg.field);
        if (!el) return;
        var colorScale = {};
        colorScale[cfg.label] = cfg.color;

        var chartOpts = {
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
        };

        // Wind Speed chart: larger points for arrows, custom tooltip
        if (cfg.field === 'windSpeed') {
            chartOpts.points = { radius: 3, enabled: true };
            chartOpts.tooltip = {
                showTotal: false,
                customHTML: function(dataSlice) {
                    if (!dataSlice || !dataSlice.length) return '';
                    var item = dataSlice[0];
                    var ts = item.date instanceof Date ? item.date.getTime() : new Date(item.date).getTime();
                    var dir = windDirByTimestamp[ts];
                    var cardinal = dir != null ? ' from ' + degreesToCardinal(dir) : '';
                    var time = new Date(ts).toLocaleString(undefined, { weekday: 'short', hour: '2-digit', minute: '2-digit' });
                    return '<div class="cds--tooltip" style="padding:8px">' +
                        '<p style="font-weight:600;margin:0 0 4px">' + time + '</p>' +
                        '<p style="margin:0;color:#8a3ffc">Wind Speed: ' + item.value.toFixed(1) + ' km/h' + cardinal + '</p>' +
                    '</div>';
                }
            };
        }

        historyCharts[cfg.field] = new LineChart(el, {
            data: [],
            options: chartOpts,
        });
    });
}

/* ── Current weather ────────────────────────────── */

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
            var dirEl = document.getElementById('val-windDirection');
            if (dirEl && data.windDirection != null) {
                dirEl.textContent = Math.round(data.windDirection) + '° ' + degreesToCardinal(data.windDirection);
            }
            var arrowEl = document.getElementById('compass-arrow');
            if (arrowEl && data.windDirection != null) {
                // Arrow points towards the direction the wind is blowing to (from + 180°)
                arrowEl.style.transform = 'rotate(' + (data.windDirection + 180) + 'deg)';
            }
            document.getElementById('last-updated').textContent =
                'Last updated: ' + new Date(data.timestamp).toLocaleTimeString();
        })
        .catch(function(e) { console.error('Failed to fetch current weather', e); });
}

/* ── History ────────────────────────────────────── */

function refreshHistory() {
    var range = document.getElementById('range-select').value || '-1h';
    fetch('/api/weather/history?range=' + range)
        .then(function(res) { return res.ok ? res.json() : []; })
        .then(function(data) {
            // Store wind directions keyed by timestamp for tooltip and arrows
            windDirByTimestamp = {};
            var windDirOrdered = [];
            data.forEach(function(r) {
                var ts = new Date(r.timestamp).getTime();
                windDirByTimestamp[ts] = r.windDirection;
                windDirOrdered.push(r.windDirection);
            });

            HISTORY_CONFIGS.forEach(function(cfg) {
                var chartData = [];
                data.forEach(function(r) {
                    chartData.push({ group: cfg.label, date: new Date(r.timestamp), value: r[cfg.field] });
                });
                if (historyCharts[cfg.field]) {
                    historyCharts[cfg.field].model.setData(chartData);
                }
            });

            // Overlay wind direction arrows after chart renders
            setTimeout(function() { addWindArrows(windDirOrdered); }, 600);
        })
        .catch(function(e) { console.error('Failed to fetch history', e); });
}

function addWindArrows(directions) {
    var container = document.getElementById('history-windSpeed');
    if (!container || !directions.length) return;

    var svg = container.querySelector('svg');
    if (!svg) return;

    // Remove previous arrows
    var old = svg.querySelector('.wind-arrows');
    if (old) old.remove();

    // Find data point circles (Carbon Charts renders them as <circle> in a scatter/dot group)
    var circles = svg.querySelectorAll('circle.dot');
    if (!circles.length) return;

    var arrowGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    arrowGroup.setAttribute('class', 'wind-arrows');

    // Sample every Nth point to avoid visual clutter
    var step = Math.max(1, Math.floor(circles.length / 30));

    circles.forEach(function(circle, i) {
        if (i >= directions.length) return;
        // Show arrow on every step-th point
        if (i % step !== 0 && i !== circles.length - 1) return;

        var cx = parseFloat(circle.getAttribute('cx'));
        var cy = parseFloat(circle.getAttribute('cy'));
        if (isNaN(cx) || isNaN(cy)) return;

        var dir = directions[i];
        // Arrow points in "towards" direction (from + 180)
        var rotation = (dir + 180) % 360;

        var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('transform', 'translate(' + cx + ',' + cy + ') rotate(' + rotation + ')');

        // Small arrow triangle
        var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M0,-8 L3,0 L0,-2 L-3,0 Z');
        path.setAttribute('fill', '#8a3ffc');
        path.setAttribute('opacity', '0.85');

        g.appendChild(path);
        arrowGroup.appendChild(g);
    });

    // Insert arrows before tooltip layer so they don't block hover
    var firstG = svg.querySelector('g');
    if (firstG) {
        svg.insertBefore(arrowGroup, null);
    }
}

/* ── Map + conditions icon ──────────────────────── */

function loadMap() {
    fetch('/api/weather/location')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(loc) {
            if (!loc) return;

            // Update current condition icon and description
            var iconEl = document.getElementById('current-icon');
            if (iconEl && loc.icon) {
                iconEl.src = owmIconUrl(loc.icon, '@2x');
                iconEl.alt = loc.description || 'Weather';
            }
            var descEl = document.getElementById('current-description');
            if (descEl && loc.description) {
                descEl.textContent = loc.description.charAt(0).toUpperCase() + loc.description.slice(1);
            }

            // Update station label
            var stationLabel = document.getElementById('station-label');
            if (stationLabel && loc.name) {
                stationLabel.textContent = 'Station: ' + loc.name;
            }

            if (!loc.latitude && !loc.longitude) return;

            var mapEl = document.getElementById('station-map');
            if (!mapEl) return;

            var titleEl = document.getElementById('map-title');
            if (titleEl) titleEl.textContent = 'Station: ' + loc.name;

            if (leafletMap) {
                // Map already exists, just update view and marker
                leafletMap.setView([loc.latitude, loc.longitude], 12);
                if (leafletMarker) {
                    leafletMarker.setLatLng([loc.latitude, loc.longitude])
                        .setPopupContent(loc.name)
                        .openPopup();
                }
            } else {
                // First load
                leafletMap = L.map('station-map').setView([loc.latitude, loc.longitude], 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors',
                    maxZoom: 18,
                }).addTo(leafletMap);
                leafletMarker = L.marker([loc.latitude, loc.longitude])
                    .addTo(leafletMap)
                    .bindPopup(loc.name)
                    .openPopup();
            }
        })
        .catch(function(e) { console.error('Failed to load location', e); });
}

/* ── City selector ──────────────────────────────── */

function loadCities() {
    fetch('/api/weather/cities')
        .then(function(res) { return res.ok ? res.json() : null; })
        .then(function(data) {
            if (!data) return;
            var select = document.getElementById('city-select');
            if (!select) return;
            select.innerHTML = '';
            data.cities.forEach(function(city) {
                var opt = document.createElement('option');
                opt.value = city;
                opt.textContent = city;
                if (city === data.active) opt.selected = true;
                select.appendChild(opt);
            });
        })
        .catch(function(e) { console.error('Failed to load cities', e); });
}

function onCityChange(e) {
    var newCity = e.target.value;
    if (!newCity) return;
    fetch('/api/weather/city', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: newCity }),
    })
    .then(function() {
        // Refresh everything for the new city
        refreshCurrent();
        refreshForecast();
        loadMap();
    })
    .catch(function(e) { console.error('Failed to change city', e); });
}

/* ── Forecast ───────────────────────────────────── */

var forecastData = [];

function refreshForecast() {
    fetch('/api/weather/forecast')
        .then(function(res) { return res.ok ? res.json() : []; })
        .then(function(data) {
            forecastData = data;
            renderHourlyForecast(data);
            render5DayForecast(data);
        })
        .catch(function(e) { console.error('Failed to fetch forecast', e); });
}

function renderHourlyForecast(data) {
    var container = document.getElementById('forecast-hourly');
    if (!container || !data.length) return;
    container.innerHTML = '';

    data.forEach(function(entry) {
        var card = document.createElement('div');
        card.className = 'forecast-card';

        var dt = new Date(entry.timestamp);
        var dayName = dt.toLocaleDateString(undefined, { weekday: 'short' });
        var time = dt.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

        card.innerHTML =
            '<div class="forecast-card__time">' +
                '<span class="forecast-card__day">' + dayName + '</span>' +
                '<span class="forecast-card__hour">' + time + '</span>' +
            '</div>' +
            '<img class="forecast-card__icon" src="' + owmIconUrl(entry.icon) + '" alt="' + entry.description + '">' +
            '<div class="forecast-card__temp">' + entry.temperature.toFixed(1) + '&deg;</div>' +
            '<div class="forecast-card__desc">' + entry.description + '</div>' +
            '<div class="forecast-card__details">' +
                '<span>' + entry.humidity.toFixed(0) + '%</span>' +
                '<span>' + entry.rainfall.toFixed(1) + ' mm</span>' +
                '<span>' + entry.windSpeed.toFixed(0) + ' km/h</span>' +
            '</div>';

        container.appendChild(card);
    });
}

function render5DayForecast(data) {
    var container = document.getElementById('forecast-5day');
    if (!container || !data.length) return;
    container.innerHTML = '';

    // Group by day
    var days = {};
    data.forEach(function(entry) {
        var dt = new Date(entry.timestamp);
        var dayKey = dt.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
        if (!days[dayKey]) {
            days[dayKey] = { entries: [], high: -Infinity, low: Infinity, icon: entry.icon, description: entry.description };
        }
        days[dayKey].entries.push(entry);
        if (entry.temperature > days[dayKey].high) {
            days[dayKey].high = entry.temperature;
            // Use the icon from the warmest reading as the "main" condition
            days[dayKey].icon = entry.icon;
            days[dayKey].description = entry.description;
        }
        if (entry.temperature < days[dayKey].low) {
            days[dayKey].low = entry.temperature;
        }
    });

    Object.keys(days).forEach(function(dayKey) {
        var day = days[dayKey];
        var card = document.createElement('div');
        card.className = 'forecast-card forecast-card--daily';

        var avgHumidity = day.entries.reduce(function(s, e) { return s + e.humidity; }, 0) / day.entries.length;
        var totalRain = day.entries.reduce(function(s, e) { return s + e.rainfall; }, 0);
        var avgWind = day.entries.reduce(function(s, e) { return s + e.windSpeed; }, 0) / day.entries.length;

        card.innerHTML =
            '<div class="forecast-card__time">' +
                '<span class="forecast-card__day">' + dayKey + '</span>' +
            '</div>' +
            '<img class="forecast-card__icon" src="' + owmIconUrl(day.icon) + '" alt="' + day.description + '">' +
            '<div class="forecast-card__temp-range">' +
                '<span class="temp-high">' + day.high.toFixed(0) + '&deg;</span>' +
                '<span class="temp-sep"> | </span>' +
                '<span class="temp-low">' + day.low.toFixed(0) + '&deg;</span>' +
            '</div>' +
            '<div class="forecast-card__desc">' + day.description + '</div>' +
            '<div class="forecast-card__details">' +
                '<span>' + avgHumidity.toFixed(0) + '%</span>' +
                '<span>' + totalRain.toFixed(1) + ' mm</span>' +
                '<span>' + avgWind.toFixed(0) + ' km/h</span>' +
            '</div>';

        container.appendChild(card);
    });
}

/* ── Tabs ───────────────────────────────────────── */

function initTabs() {
    var buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var tab = btn.dataset.tab;
            // Toggle active button
            buttons.forEach(function(b) {
                b.classList.remove('tab-btn--active');
                b.setAttribute('aria-selected', 'false');
            });
            btn.classList.add('tab-btn--active');
            btn.setAttribute('aria-selected', 'true');

            // Toggle panels
            document.getElementById('forecast-hourly').style.display = (tab === 'hourly') ? '' : 'none';
            document.getElementById('forecast-5day').style.display = (tab === '5day') ? '' : 'none';
        });
    });
}

/* ── Status ─────────────────────────────────────── */

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

/* ── Init ───────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function() {
    createHistoryCharts();
    initTabs();
    loadCities();
    refreshCurrent();
    refreshHistory();
    refreshForecast();
    refreshStatus();
    loadMap();

    setInterval(refreshCurrent, 30000);
    setInterval(refreshHistory, 60000);
    setInterval(function() { refreshForecast(); loadMap(); }, 300000);

    document.getElementById('range-select').addEventListener('change', refreshHistory);
    document.getElementById('city-select').addEventListener('change', onCityChange);
});

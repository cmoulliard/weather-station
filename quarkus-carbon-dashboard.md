# Quarkus Weather Dashboard with IBM Carbon Design System

Build a weather station dashboard using Quarkus, IBM Carbon Web Components, and Carbon Charts. The dashboard reads historical sensor data from InfluxDB and displays live readings via a REST API -- all served from a single native binary.

Based on the [Quarkus + Carbon Design System tutorial](https://www.the-main-thread.com/p/quarkus-carbon-design-system-dashboard-tutorial).

## Why InfluxDB on the Pi?

| Storage | Time-series queries | Aggregation (mean, max over 1h/1d) | ARM64 support | RAM usage | Verdict |
|---------|--------------------|------------------------------------|---------------|-----------|---------|
| **InfluxDB 2.x** | Native (Flux language) | Built-in (`aggregateWindow`, `mean`, `max`) | Official ARM64 package | ~100 MB | Best fit for sensor data |
| SQLite | Manual (SQL `GROUP BY` + date functions) | Possible but verbose | Built-in | ~5 MB | Simpler but no time-series features |
| PostgreSQL + TimescaleDB | Excellent | Built-in (`time_bucket`) | ARM64 available | ~200 MB | Overkill for a Pi weather station |

**InfluxDB is the right choice** for this use case: it handles time-series data natively, supports efficient downsampling queries (e.g., hourly averages over 7 days), and runs well on Pi 4/5 with 2 GB+ RAM. The Quarkus app writes data points via the InfluxDB Java client, and the dashboard reads them back using Flux queries.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Quarkus Native App                            │
│                                                                  │
│  ┌────────────┐   ┌─────────────────┐   ┌────────────────────┐  │
│  │ Scheduler  │──►│ InfluxDB Writer │──►│ InfluxDB 2.x       │  │
│  │ (30s)      │   └─────────────────┘   │ (weather bucket)   │  │
│  └─────┬──────┘                         └────────┬───────────┘  │
│        │                                         │              │
│  ┌─────▼──────────────────────────────┐   ┌──────▼───────────┐  │
│  │ DashboardResource                  │   │ InfluxDB Reader  │  │
│  │ GET /              → index.html    │◄──│ (Flux queries)   │  │
│  │ GET /api/weather   → JSON current  │   └──────────────────┘  │
│  │ GET /api/weather/history → JSON    │                         │
│  └────────────────────────────────────┘                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Web Bundler (build-time)                                   │  │
│  │ Carbon Web Components + Carbon Charts + Carbon Styles      │  │
│  │ → fingerprinted JS/CSS bundles served as static assets     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 1. Dependencies

### Maven Dependencies (pom.xml)

Add the mvnpm repository and Carbon packages:

```xml
<profiles>
    <profile>
        <id>mvnpm-repo</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <repositories>
            <repository>
                <id>central</id>
                <url>https://repo.maven.apache.org/maven2</url>
            </repository>
            <repository>
                <id>mvnpm.org</id>
                <url>https://repo.mvnpm.org/maven2</url>
            </repository>
        </repositories>
    </profile>
</profiles>
```

```xml
<dependencies>
    <!-- Carbon Web Components -->
    <dependency>
        <groupId>org.mvnpm.at.carbon</groupId>
        <artifactId>web-components</artifactId>
        <version>2.43.0</version>
        <scope>provided</scope>
    </dependency>

    <!-- Carbon Styles -->
    <dependency>
        <groupId>org.mvnpm.at.carbon</groupId>
        <artifactId>styles</artifactId>
        <version>1.95.0</version>
        <scope>provided</scope>
    </dependency>

    <!-- Carbon Charts (for gauges and line charts) -->
    <dependency>
        <groupId>org.mvnpm.at.carbon</groupId>
        <artifactId>charts</artifactId>
        <version>1.22.1</version>
        <scope>provided</scope>
    </dependency>

    <!-- Carbon Icons -->
    <dependency>
        <groupId>org.mvnpm.at.carbon</groupId>
        <artifactId>icons</artifactId>
        <version>11.70.0</version>
        <scope>provided</scope>
    </dependency>

    <!-- Carbon Grid -->
    <dependency>
        <groupId>org.mvnpm.at.carbon</groupId>
        <artifactId>grid</artifactId>
        <version>11.45.0</version>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

The `provided` scope ensures the npm packages are resolved at build time by the Web Bundler and bundled into static assets -- they are not shipped as JARs.

### Quarkus Configuration

Add to `application.properties`:

```properties
quarkus.web-bundler.bundle.main=true
```

## 2. InfluxDB Reader Service

This service queries InfluxDB for historical weather data using Flux:

```java
package com.example.weather.storage;

import com.example.weather.model.WeatherReading;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.QueryApi;
import com.influxdb.query.FluxRecord;
import com.influxdb.query.FluxTable;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@ApplicationScoped
public class InfluxDbReader {

    @ConfigProperty(name = "influxdb.url", defaultValue = "http://localhost:8086")
    String url;

    @ConfigProperty(name = "influxdb.token")
    String token;

    @ConfigProperty(name = "influxdb.org", defaultValue = "home")
    String org;

    @ConfigProperty(name = "influxdb.bucket", defaultValue = "weather")
    String bucket;

    private InfluxDBClient client;

    @PostConstruct
    void init() {
        client = InfluxDBClientFactory.create(url, token.toCharArray(), org, bucket);
    }

    public WeatherReading getLatest() {
        String flux = """
            from(bucket: "%s")
              |> range(start: -5m)
              |> filter(fn: (r) => r._measurement == "weather")
              |> last()
              |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
            """.formatted(bucket);

        List<FluxTable> tables = client.getQueryApi().query(flux, org);
        if (tables.isEmpty() || tables.get(0).getRecords().isEmpty()) return null;

        FluxRecord record = tables.get(0).getRecords().get(0);
        return new WeatherReading(
            getDouble(record, "temperature"),
            getDouble(record, "humidity"),
            getDouble(record, "pressure"),
            getDouble(record, "wind_speed"),
            getDouble(record, "wind_direction"),
            getDouble(record, "rainfall"),
            record.getTime()
        );
    }

    public List<WeatherReading> getHistory(String range) {
        String flux = """
            from(bucket: "%s")
              |> range(start: %s)
              |> filter(fn: (r) => r._measurement == "weather")
              |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
              |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
              |> sort(columns: ["_time"])
            """.formatted(bucket, range);

        List<FluxTable> tables = client.getQueryApi().query(flux, org);
        List<WeatherReading> readings = new ArrayList<>();

        for (FluxTable table : tables) {
            for (FluxRecord record : table.getRecords()) {
                readings.add(new WeatherReading(
                    getDouble(record, "temperature"),
                    getDouble(record, "humidity"),
                    getDouble(record, "pressure"),
                    getDouble(record, "wind_speed"),
                    getDouble(record, "wind_direction"),
                    getDouble(record, "rainfall"),
                    record.getTime()
                ));
            }
        }
        return readings;
    }

    private double getDouble(FluxRecord record, String field) {
        Object value = record.getValueByKey(field);
        return value instanceof Number n ? n.doubleValue() : 0.0;
    }

    @PreDestroy
    void shutdown() {
        if (client != null) client.close();
    }
}
```

## 3. Dashboard REST Endpoint

```java
package com.example.weather.dashboard;

import com.example.weather.model.WeatherReading;
import com.example.weather.storage.InfluxDbReader;
import io.quarkus.qute.Template;
import io.quarkus.qute.TemplateInstance;
import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import java.util.List;

@Path("/")
public class DashboardResource {

    @Inject InfluxDbReader influxDbReader;

    @GET
    @Produces(MediaType.TEXT_HTML)
    public TemplateInstance index() {
        return Template.of("index").instance();
    }

    @GET
    @Path("/api/weather")
    @Produces(MediaType.APPLICATION_JSON)
    public WeatherReading current() {
        return influxDbReader.getLatest();
    }

    @GET
    @Path("/api/weather/history")
    @Produces(MediaType.APPLICATION_JSON)
    public List<WeatherReading> history(@QueryParam("range") String range) {
        return influxDbReader.getHistory(range != null ? range : "-1h");
    }
}
```

## 4. JavaScript Entry Point

`src/main/resources/web/app/index.js`:

```javascript
// Carbon Web Components
import '@carbon/web-components/es/components/ui-shell/index.js';
import '@carbon/web-components/es/components/tile/index.js';
import '@carbon/web-components/es/components/button/index.js';
import '@carbon/web-components/es/components/inline-loading/index.js';
import '@carbon/web-components/es/components/heading/index.js';
import '@carbon/web-components/es/components/tag/index.js';
import '@carbon/web-components/es/components/tabs/index.js';
import '@carbon/web-components/es/components/dropdown/index.js';

// Carbon Charts
import { GaugeChart, LineChart } from '@carbon/charts';
import '@carbon/charts/dist/styles.css';

// Carbon Styles
import '@carbon/styles/css/styles.css';

// App styles
import './app.css';

const GAUGE_CONFIGS = [
    { id: 'gauge-temp',     field: 'temperature',    label: 'Temperature',  unit: '°C',  min: -10, max: 50   },
    { id: 'gauge-humidity', field: 'humidity',        label: 'Humidity',     unit: '%',   min: 0,   max: 100  },
    { id: 'gauge-pressure', field: 'pressure',       label: 'Pressure',     unit: 'hPa', min: 950, max: 1050 },
    { id: 'gauge-wind',     field: 'windSpeed',      label: 'Wind Speed',   unit: 'km/h',min: 0,   max: 120  },
    { id: 'gauge-rain',     field: 'rainfall',       label: 'Rainfall',     unit: 'mm',  min: 0,   max: 50   },
];

const gauges = {};
let historyChart;

function createGauges() {
    GAUGE_CONFIGS.forEach(cfg => {
        const el = document.getElementById(cfg.id);
        if (!el) return;
        gauges[cfg.field] = new GaugeChart(el, {
            data: [{ group: cfg.label, value: 0 }],
            options: {
                title: cfg.label,
                resizable: true,
                height: '180px',
                gauge: {
                    type: 'semi',
                    arcWidth: 16,
                    numberFormatter: v => `${v.toFixed(1)} ${cfg.unit}`,
                },
                color: {
                    scale: { [cfg.label]: '#0f62fe' },
                },
                toolbar: { enabled: false },
            },
        });
    });
}

function createHistoryChart() {
    const el = document.getElementById('history-chart');
    if (!el) return;
    historyChart = new LineChart(el, {
        data: [],
        options: {
            title: 'Sensor History',
            resizable: true,
            height: '400px',
            axes: {
                bottom: { mapsTo: 'date', scaleType: 'time', title: 'Time' },
                left: { mapsTo: 'value', title: 'Value' },
            },
            curve: 'curveMonotoneX',
            toolbar: { enabled: true },
            legend: { position: 'top' },
            tooltip: { showTotal: false },
            color: {
                scale: {
                    'Temperature (°C)': '#da1e28',
                    'Humidity (%)': '#0043ce',
                    'Pressure (hPa)': '#198038',
                    'Wind (km/h)': '#8a3ffc',
                    'Rainfall (mm)': '#005d5d',
                },
            },
        },
    });
}

async function refreshCurrent() {
    try {
        const res = await fetch('/api/weather');
        if (!res.ok) return;
        const data = await res.json();
        if (!data) return;

        GAUGE_CONFIGS.forEach(cfg => {
            if (gauges[cfg.field]) {
                gauges[cfg.field].model.setData([{
                    group: cfg.label,
                    value: data[cfg.field] || 0,
                }]);
            }
        });

        document.getElementById('last-updated').textContent =
            `Last updated: ${new Date(data.timestamp).toLocaleTimeString()}`;
    } catch (e) {
        console.error('Failed to fetch current weather', e);
    }
}

async function refreshHistory() {
    const range = document.getElementById('range-select')?.value || '-1h';
    try {
        const res = await fetch(`/api/weather/history?range=${range}`);
        if (!res.ok) return;
        const data = await res.json();

        const chartData = data.flatMap(r => [
            { group: 'Temperature (°C)', date: new Date(r.timestamp), value: r.temperature },
            { group: 'Humidity (%)',      date: new Date(r.timestamp), value: r.humidity },
            { group: 'Pressure (hPa)',    date: new Date(r.timestamp), value: r.pressure },
            { group: 'Wind (km/h)',       date: new Date(r.timestamp), value: r.windSpeed },
            { group: 'Rainfall (mm)',     date: new Date(r.timestamp), value: r.rainfall },
        ]);

        if (historyChart) {
            historyChart.model.setData(chartData);
        }
    } catch (e) {
        console.error('Failed to fetch history', e);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    createGauges();
    createHistoryChart();
    refreshCurrent();
    refreshHistory();

    setInterval(refreshCurrent, 30000);
    setInterval(refreshHistory, 60000);

    const rangeSelect = document.getElementById('range-select');
    if (rangeSelect) {
        rangeSelect.addEventListener('change', refreshHistory);
    }
});
```

## 5. App Stylesheet

`src/main/resources/web/app/app.css`:

```css
.app-content {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.gauge-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.gauge-tile {
    min-height: 220px;
}

.status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 0.5rem 0;
}

.status-bar span {
    font-size: 0.875rem;
    color: var(--cds-text-secondary);
}

.history-section {
    margin-top: 2rem;
}

.history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.history-chart-container {
    min-height: 420px;
}
```

## 6. HTML Page

`src/main/resources/web/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Weather Station Dashboard</title>
    {#bundle /}
</head>
<body class="cds-theme-zone-g10">

    <!-- Carbon UI Shell Header -->
    <cds-header aria-label="Weather Station">
        <cds-header-name href="/" prefix="Pi">
            Weather Station
        </cds-header-name>
    </cds-header>

    <main class="app-content">

        <!-- Status bar -->
        <div class="status-bar">
            <cds-heading>Current Conditions</cds-heading>
            <span id="last-updated">Loading...</span>
        </div>

        <!-- Gauge tiles -->
        <div class="gauge-grid">
            <cds-tile class="gauge-tile">
                <div id="gauge-temp"></div>
            </cds-tile>
            <cds-tile class="gauge-tile">
                <div id="gauge-humidity"></div>
            </cds-tile>
            <cds-tile class="gauge-tile">
                <div id="gauge-pressure"></div>
            </cds-tile>
            <cds-tile class="gauge-tile">
                <div id="gauge-wind"></div>
            </cds-tile>
            <cds-tile class="gauge-tile">
                <div id="gauge-rain"></div>
            </cds-tile>
        </div>

        <!-- History chart -->
        <section class="history-section">
            <div class="history-header">
                <cds-heading>Sensor History</cds-heading>
                <select id="range-select">
                    <option value="-1h">Last 1 hour</option>
                    <option value="-6h">Last 6 hours</option>
                    <option value="-24h">Last 24 hours</option>
                    <option value="-7d">Last 7 days</option>
                    <option value="-30d">Last 30 days</option>
                </select>
            </div>
            <cds-tile>
                <div id="history-chart" class="history-chart-container"></div>
            </cds-tile>
        </section>

    </main>

</body>
</html>
```

## 7. How It All Fits Together

1. **Build time:** The Quarkus Web Bundler resolves `@carbon/web-components`, `@carbon/charts`, and `@carbon/styles` from mvnpm (no Node.js toolchain needed). It bundles the JS/CSS into fingerprinted static assets and injects `<script>` and `<link>` tags via the `{#bundle /}` directive.

2. **Runtime:** The Quarkus native binary serves the HTML page and the bundled assets. JavaScript initializes Carbon gauge charts and a Carbon line chart. Every 30 seconds, it fetches `/api/weather` for current readings and updates the gauges. Every 60 seconds (or on range change), it fetches `/api/weather/history` for time-series data from InfluxDB and updates the line chart.

3. **Data flow:**
   - **Write path:** Scheduler → SensorService → InfluxDbWriter → InfluxDB `weather` bucket (unchanged from the main app)
   - **Read path:** Dashboard JS → `/api/weather/history` → `InfluxDbReader` → Flux query with `aggregateWindow` → JSON response → Carbon Charts

4. **No MQTT needed for the dashboard.** The dashboard reads from InfluxDB (the persistent store), not from MQTT (the live stream). MQTT is used for real-time sensor-to-app communication; InfluxDB is queried for historical views with proper downsampling.

## 8. Carbon Components Used

| Component | Carbon Element | Purpose |
|-----------|---------------|---------|
| Header bar | `cds-header`, `cds-header-name` | Top navigation with app title |
| Metric tiles | `cds-tile` | Card container for each gauge |
| Section headings | `cds-heading` | Section titles |
| Gauges | `GaugeChart` (Carbon Charts) | Semi-circular gauge for each sensor value |
| History chart | `LineChart` (Carbon Charts) | Multi-series time-series line chart |

## 9. Useful Flux Queries

Query examples you can use via the InfluxDB Reader or directly in the InfluxDB UI:

```flux
// Daily min/max temperature for the last 30 days
from(bucket: "weather")
  |> range(start: -30d)
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: min, createEmpty: false)
  |> yield(name: "min")

from(bucket: "weather")
  |> range(start: -30d)
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: 1d, fn: max, createEmpty: false)
  |> yield(name: "max")

// Total rainfall per day
from(bucket: "weather")
  |> range(start: -30d)
  |> filter(fn: (r) => r._field == "rainfall")
  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)

// Average wind speed per hour
from(bucket: "weather")
  |> range(start: -7d)
  |> filter(fn: (r) => r._field == "wind_speed")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
```

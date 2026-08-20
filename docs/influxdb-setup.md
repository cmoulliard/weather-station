# InfluxDB 3 Core - Local Setup

Run InfluxDB 3 Core locally and feed it with weather data from the Quarkus application.

## 1. Install InfluxDB 3 Core

**Quick install (macOS and Linux):**

```bash
curl -O https://www.influxdata.com/d/install_influxdb3.sh && sh install_influxdb3.sh
```

**macOS (Apple Silicon) - manual download:**

```bash
curl -O https://dl.influxdata.com/influxdb/releases/influxdb3-core-latest_darwin_arm64.tar.gz
tar xzf influxdb3-core-latest_darwin_arm64.tar.gz
sudo mv influxdb3 /usr/local/bin/
```

**Linux (DEB-based - Ubuntu/Debian):**

```bash
curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key
echo '24C975CBA61A024EE1B631787C3D57159FC2F927' | gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 | grep -q '^fpr:' && \
  cat influxdata-archive.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdata-archive.gpg > /dev/null && \
  echo 'deb [signed-by=/usr/share/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' | \
  sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install influxdb3-core
```

**Docker:**

```bash
docker pull influxdb:3-core
```

Verify the installation:

```bash
influxdb3 --version
```

## 2. Start the Server

**Quick-start (development):**

```bash
influxdb3
```

This auto-generates a node ID (`node0`) and stores data in `~/.influxdb/data`. The server binds to `0.0.0.0:8181` by default:

```
Starting InfluxDB (Quick Start)
├─ Node ID: node0
├─ Storage: ~/.influxdb/data
├─ Plugins: ~/.influxdb/plugins
├─ Logs: ~/.influxdb/logs/<timestamp>.log
└─ Command:
    influxdb3 serve \
     --node-id=node0 \
     --http-bind=0.0.0.0:8181 \
     --object-store=file --data-dir ~/.influxdb/data --plugin-dir ~/.influxdb/plugins
```

**With explicit options:**

```bash
influxdb3 serve \
  --node-id local-dev \
  --http-bind 0.0.0.0:8181 \
  --object-store file \
  --data-dir ~/.influxdb3/data
```

**Docker:**

```bash
docker run -d \
  --name influxdb3 \
  -p 8181:8181 \
  -v influxdb3-data:/data \
  influxdb:3-core influxdb3 serve \
  --node-id local-dev \
  --object-store file \
  --data-dir /data
```

## 3. Create an Auth Token

```bash
influxdb3 create token --admin
```

**Save this token** — it cannot be retrieved later. Set it as an environment variable for convenience:

```bash
export INFLUXDB3_AUTH_TOKEN=<your-token>
```

## 4. Create the Weather Database

```bash
influxdb3 create database weather --token $INFLUXDB3_AUTH_TOKEN
```

## 5. Configure the Quarkus Application

Edit `application/.env`:

```bash
# Switch data source to the OpenWeatherMap API
WEATHER_DATASOURCE=api
WEATHER_CITY=Brussels

# Set your OpenWeatherMap API key (get one free at https://openweathermap.org/api)
OPENWEATHERMAP_API_KEY=89f75483c9c6531e7808466bc1cba6b6

# Enable InfluxDB and configure connection
INFLUXDB_ENABLED=true
INFLUXDB_URL=http://localhost:8181
INFLUXDB_TOKEN=apiv3_WyGQnzPYzf31wz3tWcmNtM8rGCNIjGCGQQADSMVtMOQn30l-fs8eMKyll0ZZoO45dHUveTQ-toARYHDHlgdKWw
INFLUXDB_DATABASE=weather
```

## 6. Start the Quarkus Application

```bash
cd application
./mvnw quarkus:dev
```

The app will:
- Fetch weather data from OpenWeatherMap every 30 seconds
- Write each reading to InfluxDB as a `weather` measurement
- Serve the dashboard at http://localhost:8080/

Logs will show:

```
T=18.5°C H=72.0% P=1015.0hPa W=12.6km/h R=0.00mm [source=api]
```

## 7. Verify Data in InfluxDB

**Query the latest reading:**

```bash
influxdb3 query \
  --database weather \
  "SELECT * FROM weather ORDER BY time DESC LIMIT 5"
```

**Query with time range:**

```bash
influxdb3 query \
  --database weather \
  "SELECT * FROM weather WHERE time >= now() - INTERVAL '1 hour' ORDER BY time"
```

**Aggregated averages (5-minute windows):**

```bash
influxdb3 query \
  --database weather \
  "SELECT
     date_bin(INTERVAL '5 minutes', time) AS time_bucket,
     avg(temperature) AS avg_temp,
     avg(humidity) AS avg_hum,
     avg(pressure) AS avg_press
   FROM weather
   WHERE time >= now() - INTERVAL '1 hour'
   GROUP BY 1
   ORDER BY 1"
```

**Via HTTP API (curl):**

```bash
curl -G "http://localhost:8181/api/v3/query_sql" \
  --header "Authorization: Bearer $INFLUXDB3_AUTH_TOKEN" \
  --data-urlencode "db=weather" \
  --data-urlencode "q=SELECT * FROM weather ORDER BY time DESC LIMIT 5"
```

**Write a test point manually (line protocol):**

```bash
influxdb3 write \
  --database weather \
  --precision s \
  'weather temperature=22.5,humidity=65.0,pressure=1013.0,wind_speed=8.0,wind_direction=180.0,rainfall=0.0'
```

## 8. OpenWeatherMap API Key

1. Go to https://openweathermap.org/api and create a free account
2. Navigate to **API keys** in your account dashboard
3. Copy the default key or create a new one
4. The free tier allows **1,000 API calls/day** — at 30-second intervals, the app makes ~2,880 calls/day, so increase the interval or upgrade to the paid tier if needed

To adjust the collection interval:

```properties
# application.properties or as env var
weather.collect.interval=60s
```

## 9. Running on Raspberry Pi (Production)

If you installed InfluxDB 3 Core via the DEB package, a systemd service is already available:

```bash
sudo systemctl enable --now influxdb3
sudo journalctl -u influxdb3 -f    # check logs
```

If you installed from the tarball, create a systemd service manually:

```bash
sudo tee /etc/systemd/system/influxdb3.service > /dev/null <<EOF
[Unit]
Description=InfluxDB 3 Core
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/influxdb3 serve --node-id pi-weather --object-store file --data-dir /var/lib/influxdb3
Restart=always
RestartSec=5
User=pi
StateDirectory=influxdb3

[Install]
WantedBy=multi-user.target
EOF

sudo mkdir -p /var/lib/influxdb3
sudo chown pi:pi /var/lib/influxdb3
sudo systemctl daemon-reload
sudo systemctl enable --now influxdb3
```

Then create the token and database:

```bash
influxdb3 create token --admin
influxdb3 create database weather --token <your-token>
```

The Quarkus weather station app can run alongside InfluxDB on the same Pi — see the main [README](../README.md) for the systemd service setup for the Quarkus binary.

## Notes

- InfluxDB 3 Core limits query time ranges to **~72 hours** by default. For longer history (7d, 30d), consider InfluxDB 3 Enterprise or adjust the dashboard range options.
- The `influxdb3-java` client uses **FlightSQL (gRPC)** for queries and **HTTP** for writes. Ensure both port 8181 (HTTP) and the gRPC port are accessible.
- Data is stored in Apache Parquet format on disk. The `--data-dir` path contains all persisted data.
- On Pi 4 (2 GB), expect InfluxDB 3 to use ~200-400 MB RAM. Monitor with `htop` and consider adding swap if needed.

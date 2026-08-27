# Raspberry Pi Weather Station Guide

Build a complete weather station using a Raspberry Pi, environmental sensors, and software to collect and publish data to Weather Underground or OpenWeatherMap.

## References

### Tutorials

- Pi vs ESP32: https://www.raspberrypi-france.fr/station-meteo-diy-comparatif-et-tutoriel/
- Pi:
    - With [Adafruit HAT Pi](https://www.adafruit.com/product/2310) + sensors:
      - archived project but really helpful: https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/0
      - Another interesting project: https://core-electronics.com.au/projects/diy-weather-station-raspberry-pi/
    - With Weather board:
        - Standard: https://thepihut.com/products/weather-board-for-raspberry-pi with BME280 & soldiers: https://thepihut.com/products/weather-hat-pro-assembled-for-raspberry-pi
        - Tuto: part [1](https://bc-robotics.com/tutorials/raspberry-pi-weather-station-part-1/), [2](https://bc-robotics.com/tutorials/raspberry-pi-weather-station-part-2/) & [3](https://bc-robotics.com/tutorials/raspberry-pi-weather-station-part-3/)
- BME280 wiring & Python:
    - Sensor plugged on Pi: https://randomnerdtutorials.com/raspberry-pi-bme280-python/
- ESP32 Board:
    - ESPHome & hardware + blog/tuto: https://esphome.io/components/esp32/
    - https://www.haraldkreuzer.net/en/news/esp32-weather-station-weather-forecast-wireless-sensors-and-air-quality-measurement
    - https://www.instructables.com/DIY-Weather-Station-With-ESP32/
    - https://www.makerguides.com/fr/simple-esp32-internet-weather-station-fr/

- Seller:
    - ESP32:
        - https://www.gotronic.fr/cat-cartes-esp32.htm
        - Carte ESP32 française: https://www.upesy.fr/
    - Weather components bc-robotics: https://bc-robotics.com/?product_cat=&s=weather&post_type=product
    - Sparkfun meter kit (rain gauge, wind vane, anemometer): https://thepihut.com/products/sparkfun-weather-meter-kit
    - All: https://www.kiwi-electronics.com/en

- Forum: https://forums.raspberrypi.com/viewforum.php?f=112&sid=e893b51c323da761164dc232a929f962



### Software & Data

| Topic | Link |
|-------|------|
| InfluxDB 3 Core documentation | https://docs.influxdata.com/influxdb3/core/ |
| InfluxDB 3 Core install guide | https://docs.influxdata.com/influxdb3/core/install/ |
| influxdb3-java client library | https://github.com/InfluxCommunity/influxdb3-java |
| OpenWeatherMap API (free tier) | https://openweathermap.org/api |
| Weather Underground Pi uploader example | https://github.com/garnathan/wunderground-killi/tree/main/pi |
| WeeWX source code and documentation | https://github.com/weewx/weewx |
| WeeWX architecture and developer notes | https://www.weewx.com/docs/5.5/devnotes/ |
| WeeWX daemon (`weewxd`) reference | https://www.weewx.com/docs/5.5/utilities/weewxd/ |
| WeeWX CLI (`weectl`) reference | https://www.weewx.com/docs/5.5/utilities/weectl-about/ |
| Node-RED flow-based IoT platform | https://nodered.org/ |
| Node-RED Dashboard 2.0 (FlowFuse) | https://dashboard.flowfuse.com/ |

### Dashboard & Visualization

| Topic | Link |
|-------|------|
| Quarkus + IBM Carbon Design dashboard tutorial | https://www.the-main-thread.com/p/quarkus-carbon-design-system-dashboard-tutorial |
| IBM Carbon Design System | https://carbondesignsystem.com/ |
| Carbon Charts (D3-based, 26 chart types) | https://github.com/carbon-design-system/carbon-charts |

## Hardware & Wiring

See the full hardware selection guide, wiring diagrams, and Raspberry Pi configuration instructions in [docs/hardware-setup.md](docs/hardware-setup.md).

## Software Options

Two approaches are available: a **Quarkus native application** (Java, lightweight binary) or **WeeWX** (Python, batteries-included).

### Feature Comparison

| Feature | Quarkus Native (Java) | WeeWX (Python) |
|---------|----------------------|----------------|
| Sensor data collection | Pi4J library for I2C/GPIO | Built-in drivers for 50+ station types (Davis, Fine Offset, LaCrosse, Oregon Scientific, AcuRite, SDR, etc.) |
| Data archiving | InfluxDB time-series database | SQLite or MySQL with daily summaries for fast queries |
| Weather API upload | REST client to Weather Underground and OpenWeatherMap | Weather Underground, CWOP, PWSweather, WOW, AWEKAS, Windy, OpenWeatherMap, WeatherBug, WeatherCloud |
| MQTT publishing | Built-in Quarkus MQTT client (SmallRye Reactive Messaging) | Via extension (`weewx-mqtt`) |
| Web dashboard | IBM Carbon Design (built-in), Node-RED Dashboard 2.0, or Grafana via InfluxDB | Built-in Cheetah template engine with skins |
| Report generation | Grafana dashboards | Charts, HTML pages, almanac data |
| Extensibility | Full Java/Quarkus ecosystem | Python extensions, large 3rd-party ecosystem |
| Resource usage | ~30 MB RAM (native binary) | ~50-100 MB RAM (Python runtime) |
| Startup time | Sub-second | Several seconds |
| Installation | Single binary, no JVM needed | `apt-get install weewx` |

### Option A: Quarkus Native Application (Java)

A custom Java application built with Quarkus and compiled to a native executable using GraalVM. This approach gives you full control over the data pipeline with minimal resource usage (~30 MB RAM, sub-second startup).

**Stack:** Pi4J (sensors) + Quarkus Scheduler + REST Client (weather APIs) + SmallRye Reactive Messaging (MQTT) + InfluxDB.

**Dashboard options:**

| Option | Description | Extra dependencies |
|--------|-------------|--------------------|
| **Built-in (IBM Carbon Design)** | Enterprise-grade dashboard with Carbon Web Components + Carbon Charts, served from the Quarkus binary | None (Web Bundler resolves Carbon at build time) |
| **Node-RED Dashboard 2.0** | External Node-RED process subscribes to MQTT, drag-and-drop widgets | Node.js + Node-RED |
| **Grafana** | Queries InfluxDB directly, advanced analytics and alerting | Grafana server |

See the full development guide: [application/quarkus-weather-app.md](application/quarkus-weather-app.md), and the Carbon dashboard guide: [application/quarkus-carbon-dashboard.md](application/quarkus-carbon-dashboard.md)

**Local setup (macOS/Linux):**

See [docs/influxdb-setup.md](docs/influxdb-setup.md) for the complete InfluxDB 3 + Weather API setup guide.

```bash
# Install InfluxDB 3 Core
curl -O https://www.influxdata.com/d/install_influxdb3.sh && sh install_influxdb3.sh

# Start InfluxDB 3 (listens on port 8181)
influxdb3

# Create admin token and database
influxdb3 create token --admin
influxdb3 create database weather --token <your-token>

# Configure application/.env with your token and OpenWeatherMap API key
# Then start the Quarkus app
cd application && ./mvnw quarkus:dev
```

**Prerequisites on the Pi:**

```bash
# Install InfluxDB 3 Core
sudo apt-get update && sudo apt-get install influxdb3-core

# (Optional) Install Mosquitto MQTT broker
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto

# (Optional) Install Node-RED if using Node-RED Dashboard
sudo apt-get install nodejs npm
sudo npm install -g --unsafe-perm node-red
cd ~/.node-red && npm install @flowfuse/node-red-dashboard
```

**Install the pre-built native binary:**

```bash
# Copy the native binary to the Pi
scp target/quarkus-weather-station-1.0-runner pi@raspberrypi:~/

# On the Pi: make executable and install as a systemd service
ssh pi@raspberrypi
chmod +x ~/quarkus-weather-station-1.0-runner
sudo mv ~/quarkus-weather-station-1.0-runner /usr/local/bin/quarkus-weather-station

# Create systemd service
sudo tee /etc/systemd/system/quarkus-weather.service > /dev/null <<EOF
[Unit]
Description=Quarkus Weather Station
After=network-online.target mosquitto.service influxdb.service
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/quarkus-weather-station
Restart=always
RestartSec=5
User=pi
Environment=QUARKUS_PROFILE=prod

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now quarkus-weather.service
sudo journalctl -u quarkus-weather -f    # check logs
```

**Built-in dashboard:** No extra services needed -- the Quarkus binary serves the dashboard at `http://raspberrypi:8080/`. See [application/quarkus-weather-app.md](application/quarkus-weather-app.md) for the full implementation.

**Start Node-RED (only if using Node-RED Dashboard):**

```bash
# Run as a systemd service
sudo tee /etc/systemd/system/nodered.service > /dev/null <<EOF
[Unit]
Description=Node-RED
After=network-online.target mosquitto.service
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node-red
Restart=always
User=pi
Environment=NODE_RED_ENABLE_SAFE_MODE=false

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now nodered.service
```

Access the Node-RED editor at `http://raspberrypi:1880` and the dashboard at `http://raspberrypi:1880/dashboard`.

### Option B: WeeWX (Python)

[WeeWX](https://weewx.com/) is the most widely used open-source weather station software (GPLv3). It handles the full pipeline: data collection, quality control, unit conversion, archiving, report generation, and upload to external services. Requires Python 3.7+.

**Architecture:**

WeeWX uses a **micro-kernel design** where the engine loads and runs pluggable *services* at runtime:

- **`weewxd`** -- The main daemon. Collects data from hardware, processes it, archives to database, and generates reports. Can run in foreground (useful for debugging) or as a background daemon (`--daemon` flag). All database writes are transaction-safe -- you can kill the process at any time without corrupting data.
- **`weectl`** -- Command-line utility for managing stations, databases, devices, extensions, reports, and diagnostics.
- **Data flow:** Hardware driver → LOOP packets → accumulator → ARCHIVE records → database → report engine.
- **Single-threaded** data collection isolated from report generation (separate thread). Stateless design with no semaphores.
- **Daily summaries:** Each observation type gets a dedicated table with daily min/max/sum/count, enabling fast queries over long periods without scanning all archive records.
- All timestamps stored as Unix epoch (UTC), converted to local time only for display.

**Install WeeWX:**

```bash
sudo apt-get update
sudo apt-get install weewx
```

During installation, follow the prompts to set your station location, altitude, and units.

**Push data to Weather Underground:**

1. Create an account at [wunderground.com](https://www.wunderground.com/) and register a Personal Weather Station (PWS) to get a **Station ID** and **Station Key**.

2. Edit `/etc/weewx/weewx.conf` in the `[StdRESTful]` section:

```ini
[[Wunderground]]
    enable = true
    station = YOUR_STATION_ID
    password = YOUR_STATION_KEY
```

**Push data to OpenWeatherMap:**

1. Create an account at [openweathermap.org](https://openweathermap.org/) and generate an **API Key**.

2. Install the WeeWX OpenWeatherMap extension:

```bash
sudo weectl extension install https://github.com/matthewwall/weewx-owm/archive/master.zip
```

3. Edit `/etc/weewx/weewx.conf` and add your API key and station ID under the `[[OpenWeatherMap]]` block.

**Enable MQTT publishing (optional):**

```bash
sudo weectl extension install https://github.com/matthewwall/weewx-mqtt/archive/master.zip
```

Configure the MQTT broker in `weewx.conf` under `[StdRESTful]` -> `[[MQTT]]`.

**Start the service:**

```bash
sudo systemctl restart weewx
sudo systemctl enable weewx
sudo journalctl -u weewx -f    # check logs
```

**Useful `weectl` commands:**

| Command | Purpose |
|---------|---------|
| `weectl station create` | Create or reconfigure a station |
| `weectl device` | Manage connected hardware |
| `weectl extension list` | List installed extensions |
| `weectl extension install <url>` | Install a new extension |
| `weectl report list` | List available report skins |
| `weectl report run` | Manually run reports |
| `weectl import` | Import data from CSV, Weather Underground, Cumulus, Weather Display, or WeatherCat |
| `weectl database` | Manage WeeWX databases |
| `weectl debug` | Generate diagnostic info for troubleshooting |

**Run `weewxd` in foreground (debugging):**

```bash
weewxd --config /etc/weewx/weewx.conf
```

Useful options: `--exit` (terminate on I/O or database errors), `--loop-on-init` (retry device initialization at startup).

## Recommendation Summary

| Goal | Recommended Setup |
|------|-------------------|
| **Full control, minimal footprint** | Raspberry Pi 4/5 + BME280 + RJ11 kit + Quarkus native app + built-in Carbon dashboard |
| **Best drag-and-drop dashboards** | Quarkus or WeeWX + Node-RED Dashboard 2.0 |
| **Quickest to get running** | Raspberry Pi 4/5 + Pimoroni Weather HAT + WeeWX |
| **Best analytics dashboards** | Either option + InfluxDB + Grafana |

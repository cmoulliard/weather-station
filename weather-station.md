# Raspberry Pi Weather Station Guide

Build a complete weather station using a Raspberry Pi, environmental sensors, and software to collect and publish data to Weather Underground or OpenWeatherMap.

## References

| Topic | Link |
|-------|------|
| Pi weather station build guide | https://pcbsync.com/raspberry-pi-weather-station/ |
| Pi weather station with sensors tutorial | https://www.tme.eu/en/news/library-articles/page/68616/build-your-own-weather-station-with-raspberry-pi/ |
| Weather Underground Pi uploader example | https://github.com/garnathan/wunderground-killi/tree/main/pi |
| BMP280 vs BME280 vs BME680 comparison | https://www.flywing-tech.com/blog/bmp280-bme280-bme680-best-barometric-sensor-for-weather-stations/ |
| Wind/rain sensor kit (anemometer, vane, rain bucket) | https://thepihut.com/products/weather-station-kit-with-anemometer-wind-vane-rain-bucket |
| WeeWX source code and documentation | https://github.com/weewx/weewx |
| WeeWX architecture and developer notes | https://www.weewx.com/docs/5.5/devnotes/ |
| WeeWX daemon (`weewxd`) reference | https://www.weewx.com/docs/5.5/utilities/weewxd/ |
| WeeWX CLI (`weectl`) reference | https://www.weewx.com/docs/5.5/utilities/weectl-about/ |
| Node-RED flow-based IoT platform | https://nodered.org/ |
| Node-RED Dashboard 2.0 (FlowFuse) | https://dashboard.flowfuse.com/ |
| Quarkus + IBM Carbon Design dashboard tutorial | https://www.the-main-thread.com/p/quarkus-carbon-design-system-dashboard-tutorial |
| IBM Carbon Design System | https://carbondesignsystem.com/ |
| Carbon Charts (D3-based, 26 chart types) | https://github.com/carbon-design-system/carbon-charts |

## 1. Hardware Selection

### Raspberry Pi

| Model | RAM | GPIO | Notes |
|-------|-----|------|-------|
| **Raspberry Pi 4 Model B** | 2/4/8 GB | 40-pin (I2C, SPI, UART) | Mature, widely available, large community. Broadcom BCM2711 (quad-core Cortex-A72 @ 1.8 GHz). Sufficient for headless data collection. |
| **Raspberry Pi 5** | 4/8 GB | 40-pin (I2C, SPI, UART) | Broadcom BCM2712 (quad-core Cortex-A76 @ 2.4 GHz). PCIe 2.0 x1, dedicated RP1 I/O controller for improved GPIO/I2C timing. Better suited when running dashboards (Node-RED, Grafana) alongside data collection. |

**Recommendation:** A Pi 4 with 2 GB is sufficient for headless data collection with WeeWX. Choose a Pi 5 or 4 GB+ RAM if you plan to run a local web dashboard, InfluxDB, and/or Node-RED on the same device.

**OS:** Use Raspberry Pi OS Lite (64-bit, Debian Bookworm-based) for headless setups. See [Pi setup guide](../setup/pi4.md) for initial OS installation, SSH access, and network configuration.

### Sensors

**Temperature, Humidity & Pressure:**

| Sensor | Measures | Accuracy | Price (approx.) | Links                                                                                                                                                                                                         |
|--------|----------|----------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **BME280** (I2C/SPI) | Temperature (-40 to +85 °C), Humidity (0-100% RH), Pressure (300-1100 hPa) | ±1.0 °C, ±3% RH, ±1 hPa | ~€15 (breakout board) | [Adafruit](https://www.adafruit.com/product/2652), [Mouser BE](https://www.mouser.be/fr/c/?q=BME280), [TME](https://www.tme.eu/be/fr/details/df-sen0335/capteurs-environnementaux/dfrobot/sen0335/), [Kiwi](https://www.kiwi-electronics.com/en/bme280-sensor-board-with-i2c-and-spi-for-temperature-humidity-and-pressure-stemma-qt-2112?search=BME280) |
| **BME680** (I2C/SPI) | Same as BME280 + VOC gas (air quality) | ±1.0 °C, ±3% RH, ±1 hPa | ~€19 (breakout board) | [Adafruit](https://www.adafruit.com/product/3660), [Mouser BE](https://www.mouser.be/), [TME](https://www.tme.eu/)                                                                                            |

The BME280 is the go-to choice for weather stations. The BME680 adds a metal oxide VOC gas sensor (48h burn-in required) -- useful if indoor air quality matters. Both are available as STEMMA QT / Qwiic breakout boards for solderless I2C wiring.

**Belgium / EU suppliers:** [Mouser Belgium](https://www.mouser.be/), [TME](https://www.tme.eu/) (Poland, ships to BE), [Kiwi Electronics](https://www.kiwi-electronics.com/) (Netherlands, ships to BE), [SOS Solutions](https://www.sossolutions.nl/) (Netherlands).

**Wind & Rain:**

| Sensor | Function | Interface | Price (approx.) | Links |
|--------|----------|-----------|-----------------|-------|
| **Rain gauge** (tipping bucket) | Precipitation measurement | Reed switch pulse → GPIO | Part of kit (~€160) | [The Pi Hut](https://thepihut.com/products/weather-station-kit-with-anemometer-wind-vane-rain-bucket), [DFRobot](https://www.dfrobot.com/) |
| **Anemometer** | Wind speed (rotation pulses/sec) | Reed switch pulse → GPIO | Part of kit | Same kit |
| **Wind vane** | Wind direction (resistor network) | Analog → ADC (MCP3008/ADS1115) | Part of kit | Same kit |

These are typically sold as a single **RJ11 Weather Sensor Kit** (anemometer + wind vane + rain bucket + mounting mast). DFRobot, Pimoroni, and SparkFun all sell compatible kits.

### Ready-Made Options

| Product | Includes | Price (approx.) | Links |
|---------|----------|-----------------|-------|
| **Pimoroni Weather HAT** | BME280, LTR-559 light sensor, 1.54" LCD, RJ11 connectors for wind/rain kits | ~£30 (HAT only) | [Pimoroni](https://shop.pimoroni.com/) |
| **SparkFun MicroMod Weather Carrier Board** | RJ11 wind/rain connectors, Qwiic I2C sensor ports | ~$45 | [SparkFun](https://www.sparkfun.com/catalogsearch/result/?q=weather), [Mouser BE](https://www.mouser.be/fr/ProductDetail/DFRobot/SEN0186?qs=kE1vTINknaUaWz5cQFgJUA%3D%3D) |

## 2. Wiring

### BME280 (I2C)

| BME280 Pin | Raspberry Pi Pin |
|------------|------------------|
| VCC        | 3.3V (pin 1)     |
| GND        | Ground (pin 6)   |
| SDA        | GPIO 2 (pin 3)   |
| SCL        | GPIO 3 (pin 5)   |

### Rain Gauge / Anemometer

Connect one wire of each sensor to GND and the other to a free GPIO pin (e.g., GPIO 5 for the rain gauge, GPIO 6 for the anemometer). These sensors use simple pulse-counting via their internal Reed switches.

### Wind Vane

The wind vane outputs a variable resistance. Connect it through an ADC (MCP3008 or ADS1115) if your board lacks analog inputs, or use the RJ11 breakout board provided with the sensor kit.

## 3. Raspberry Pi Configuration

Enable the I2C bus:

```bash
sudo raspi-config
# Navigate to "Interface Options" -> "I2C" -> Enable
```

Verify the BME280 is detected:

```bash
sudo apt-get install i2c-tools
i2cdetect -y 1
# The BME280 should appear at address 0x76 or 0x77
```

## 4. Software Options

Two approaches are available: **WeeWX** (Python, batteries-included) or a **Quarkus native application** (Java, lightweight binary).

### Feature Comparison

| Feature | WeeWX (Python) | Quarkus Native (Java) |
|---------|----------------|----------------------|
| Sensor data collection | Built-in drivers for 50+ station types (Davis, Fine Offset, LaCrosse, Oregon Scientific, AcuRite, SDR, etc.) | Pi4J library for I2C/GPIO |
| Data archiving | SQLite or MySQL with daily summaries for fast queries | InfluxDB time-series database |
| Weather API upload | Weather Underground, CWOP, PWSweather, WOW, AWEKAS, Windy, OpenWeatherMap, WeatherBug, WeatherCloud | REST client to Weather Underground and OpenWeatherMap |
| MQTT publishing | Via extension (`weewx-mqtt`) | Built-in Quarkus MQTT client (SmallRye Reactive Messaging) |
| Web dashboard | Built-in Cheetah template engine with skins | Node-RED Dashboard 2.0 or Grafana via InfluxDB |
| Report generation | Charts, HTML pages, almanac data | Grafana dashboards |
| Extensibility | Python extensions, large 3rd-party ecosystem | Full Java/Quarkus ecosystem |
| Resource usage | ~50-100 MB RAM (Python runtime) | ~30 MB RAM (native binary) |
| Startup time | Several seconds | Sub-second |
| Installation | `apt-get install weewx` | Single binary, no JVM needed |

### Option A: WeeWX (Python)

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

### Option B: Quarkus Native Application (Java)

A custom Java application built with Quarkus and compiled to a native executable using GraalVM. This approach gives you full control over the data pipeline with minimal resource usage (~30 MB RAM, sub-second startup).

**Stack:** Pi4J (sensors) + Quarkus Scheduler + REST Client (weather APIs) + SmallRye Reactive Messaging (MQTT) + InfluxDB.

**Dashboard options:**

| Option | Description | Extra dependencies |
|--------|-------------|--------------------|
| **Built-in (IBM Carbon Design)** | Enterprise-grade dashboard with Carbon Web Components + Carbon Charts, served from the Quarkus binary | None (Web Bundler resolves Carbon at build time) |
| **Node-RED Dashboard 2.0** | External Node-RED process subscribes to MQTT, drag-and-drop widgets | Node.js + Node-RED |
| **Grafana** | Queries InfluxDB directly, advanced analytics and alerting | Grafana server |

See the full development guide: [quarkus-weather-app.md](quarkus-weather-app.md), and the Carbon dashboard guide: [quarkus-carbon-dashboard.md](quarkus-carbon-dashboard.md)

**Prerequisites on the Pi:**

```bash
# Install Mosquitto MQTT broker
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto

# Install InfluxDB 2.x
curl -s https://repos.influxdata.com/influxdata-archive.key | sudo gpg --dearmor -o /usr/share/keyrings/influxdb-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update
sudo apt-get install influxdb2
sudo systemctl enable --now influxdb

# (Optional) Install Node-RED if using Dashboard Option A
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

**Start Node-RED (only if using Dashboard Option A):**

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

**Built-in dashboard (Option B):** No extra services needed -- the Quarkus binary serves the dashboard at `http://raspberrypi:8080/`. See [quarkus-weather-app.md](quarkus-weather-app.md#option-b-built-in-quarkus-dashboard-qute--htmx--chartjs) for the full implementation.

## 5. Recommendation Summary

| Goal | Recommended Setup |
|------|-------------------|
| **Quickest to get running** | Raspberry Pi 4/5 + Pimoroni Weather HAT + WeeWX |
| **Full control, minimal footprint** | Raspberry Pi 4/5 + BME280 + RJ11 kit + Quarkus native app + built-in Qute dashboard |
| **Best drag-and-drop dashboards** | Quarkus or WeeWX + Node-RED Dashboard 2.0 |
| **Best analytics dashboards** | Either option + InfluxDB + Grafana |

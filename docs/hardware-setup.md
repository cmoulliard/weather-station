# Hardware Selection, Wiring & Pi Configuration

## To be reviewed
- https://www.lextronic.fr/station-meteo-girouette-anemometre-pluviometre-2640.html
- https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all
- https://learn.sparkfun.com/tutorials/arduino-weather-shield-hookup-guide-v12
- https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide

Arduino:
- La bible des tuto en français: https://newbiely.fr/tutorials/arduino-uno-r4/ et anglais: https://arduinogetstarted.com/arduino-tutorials
- Official doc: https://docs.arduino.cc/tutorials/ and https://projecthub.arduino.cc
- https://www.makerguides.com/arduino-weather-station-kit-dfrobot-tutorial/ 
- https://docs.arduino.cc/tutorials/uno-r4-minima/shield-guide/
- Reseller (Adafruit, Sparkfun):
  - https://www.digikey.be/, https://www.gotron.be, https://www.antratek.be
  - https://shop.mchobby.be/fr/

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

Investigate from SparkFun guides, how we can integrate the different pieces together : https://www.sparkfun.com/catalog/product/view/id/7790/s/sparkfun-arduino-iot-weather-station/ !

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

## 4. Dual-Pi Setup (Sensor Node + Hub)

An alternative topology uses two Raspberry Pi 3 boards: one as a sensor node collecting data, and the other as a hub running a Wi-Fi hotspot and MQTT broker. This creates a self-contained weather station with no internet dependency.

### Pi 3 Model Comparison

| Spec | Pi 3 Model B | Pi 3 Model B+ |
|------|-------------|----------------|
| CPU | 1.2 GHz quad-core | 1.4 GHz quad-core |
| Wi-Fi | 2.4 GHz (BCM43438) | 2.4 + 5 GHz (BCM43455) |
| Ethernet | 100 Mbps | 300 Mbps (USB 2.0 bound) |
| RAM | 1 GB | 1 GB |
| PoE | No | Yes (with HAT) |
| GPIO | 40-pin | 40-pin |

### Recommended Assignment

**Pi 3 B+ as sensor node** (with Weather HAT on GPIO):
- Better Wi-Fi chip (dual-band, better antenna) provides more reliable connection to the hotspot, especially outdoors
- Same 40-pin GPIO, fully compatible with Weather HAT
- Lower workload — runs only a lightweight Python publisher

**Pi 3 B as hub / server** (hotspot + MQTT + Quarkus):
- Runs `hostapd` (AP mode), Mosquitto MQTT broker, and the Quarkus app
- 1 GB RAM is sufficient (Mosquitto ~5 MB, Quarkus native ~30 MB, InfluxDB3 ~100-200 MB)
- Doesn't need the better Wi-Fi since it creates the network rather than reaching for one

### Architecture

```
┌──────────────────────┐        Wi-Fi (hotspot)        ┌──────────────────────┐
│    Pi 3 B+           │ ────────────────────────────── │    Pi 3 B            │
│    (sensor node)     │                                │    (hub / server)    │
│                      │   MQTT publish                 │                      │
│  Weather HAT (GPIO)  │ ───────────────────────────►   │  Mosquitto broker    │
│  BME280 + wind/rain  │   topic: weather/readings      │  Quarkus app         │
│  Built-in Wi-Fi      │                                │  InfluxDB3 (opt.)    │
│  Python publisher    │                                │  Wi-Fi AP (hostapd)  │
└──────────────────────┘                                └──────────────────────┘
```

### Constraints

| Concern | Detail |
|---------|--------|
| **RAM** | 1 GB on the hub Pi — monitor memory if running Quarkus + InfluxDB3 together |
| **Wi-Fi throughput** | ~20-30 Mbps in AP mode — more than enough for sensor telemetry (a few KB/s) |
| **Power** | Both Pis need stable 5V/2.5A supplies, especially the sensor node with the Weather HAT |
| **Range** | Pi 3 B's built-in Wi-Fi has limited range (~10-15m indoors); position accordingly or add an external antenna |

### Mosquitto Bridge (Message Resilience)

When the sensor Pi loses connectivity to the hub Pi (Wi-Fi dropout, broker restart, hotspot issue), sensor readings are lost unless buffered locally. Running Mosquitto on **both** Pis with a bridge solves this — the sensor Pi publishes to its local broker, which queues messages and forwards them to the hub when the connection is restored.

#### Architecture with Bridge

```
┌──────────────────────────┐        Wi-Fi (hotspot)        ┌──────────────────────┐
│    Pi 3 B+               │ ────────────────────────────── │    Pi 3 B            │
│    (sensor node)          │                                │    (hub / server)    │
│                          │                                │                      │
│  Weather HAT (GPIO)      │                                │  Mosquitto broker    │
│  Python publisher        │   MQTT bridge (QoS 1)         │  (main broker)       │
│    → localhost:1883      │ ───────────────────────────►   │  persistence: true   │
│  Mosquitto (local)       │   topic: weather/#             │  Quarkus app         │
│    persistence: true     │                                │  InfluxDB3 (opt.)    │
│    bridge → hub Pi       │                                │  Wi-Fi AP (hostapd)  │
└──────────────────────────┘                                └──────────────────────┘
```

#### Sensor Pi — Mosquitto Configuration

Install Mosquitto on the sensor Pi:

```bash
sudo apt-get install mosquitto
```

Edit `/etc/mosquitto/conf.d/bridge.conf`:

```
# Local broker settings
listener 1883 localhost
persistence true
persistence_location /var/lib/mosquitto/

# Bridge to hub Pi
connection bridge-to-hub
address <hub-pi-ip>:1883
topic weather/# out 1
cleansession false
restart_timeout 5
notifications false
```

Key settings:
- `topic weather/# out 1` — forwards all `weather/` topics with QoS 1 (at-least-once delivery)
- `cleansession false` — the hub broker remembers the bridge subscription across reconnects
- `persistence true` — queued messages survive a sensor Pi reboot
- `restart_timeout 5` — retry connection every 5 seconds when the hub is unreachable

#### Python Publisher Change

The sensor publisher connects to `localhost` instead of the remote hub:

```python
client.connect("localhost", 1883)
```

#### References

- [Eclipse Mosquitto Bridge Documentation](https://mosquitto.org/man/mosquitto-conf-5.html) — official `mosquitto.conf` reference covering all bridge options
- [Bridging Two Mosquitto Brokers (HiveMQ)](https://www.hivemq.com/blog/mqtt-bridge-mosquitto/) — step-by-step tutorial on configuring Mosquitto bridges
- [Steve's Internet Guide — Mosquitto Bridge](http://www.steves-internet-guide.com/mosquitto-bridge-configuration/) — practical guide with examples for multi-broker setups
- [MQTT Bridge Explained (Cedalo)](https://cedalo.com/blog/mqtt-bridge-mosquitto/) — covers bridge architecture, QoS handling, and failure scenarios

## 5. Arduino Sensor Node (BME280 + RJ11 Wind/Rain)

An alternative to the dual-Pi topology: use an **Arduino Uno R4 WiFi** as the outdoor sensor node. It reads the BME280 and wind/rain sensors, publishes readings over Wi-Fi to the Raspberry Pi hub via MQTT. Compared to a Pi sensor node, the Arduino draws ~20× less power, boots instantly, and has built-in analog inputs (no external ADC needed for the wind vane).

### Why Arduino Uno R4 WiFi

| Spec | Arduino Uno R4 WiFi |
|------|---------------------|
| MCU | Renesas RA4M1 (Arm Cortex-M4, 48 MHz, 256 KB flash, 32 KB SRAM) |
| Wi-Fi | ESP32-S3 module (802.11 b/g/n, 2.4 GHz) |
| Analog inputs | 6 (A0–A5), 14-bit ADC |
| Digital I/O | 14 (D0–D13), including 2 hardware interrupts (D2, D3) |
| I2C | A4 (SDA) / A5 (SCL) |
| Operating voltage | 5V |
| Input voltage | 6–24V via VIN pin, or 5V via USB-C |
| Current draw | ~100 mA active with Wi-Fi, ~30 mA with Wi-Fi off |
| Price | ~€25 |

Links: [Arduino Store](https://store.arduino.cc/products/uno-r4-wifi), [Mouser BE](https://www.mouser.be/)

### Architecture

```
┌─────────────────────────────┐       Wi-Fi        ┌──────────────────────┐
│  Arduino Uno R4 WiFi        │ ──────────────────► │  Raspberry Pi        │
│  (outdoor sensor node)      │   MQTT publish      │  (hub / server)      │
│                             │   topic: weather/#  │                      │
│  BME280 (I2C)               │                     │  Mosquitto broker    │
│  Rain gauge (D2, interrupt) │                     │  Quarkus app         │
│  Anemometer (D3, interrupt) │                     │  InfluxDB3 (opt.)    │
│  Wind vane (A0, analog)     │                     │                      │
│                             │                     │                      │
│  Power: solar + LiPo        │                     │                      │
└─────────────────────────────┘                     └──────────────────────┘
```

### Wiring

#### BME280 → Arduino (I2C)

| BME280 Pin | Arduino Pin | Notes |
|------------|-------------|-------|
| VCC | 3.3V | BME280 runs at 3.3V; Uno R4 WiFi has a 3.3V output pin |
| GND | GND | |
| SDA | A4 (SDA) | Shared I2C bus |
| SCL | A5 (SCL) | Shared I2C bus |

If using a STEMMA QT / Qwiic breakout board, connect directly via the Qwiic connector — no soldering needed.

#### RJ11 Weather Sensors → Arduino

The SparkFun Weather Meter Kit (SEN-15901) or equivalent RJ11 sensor kit includes three sensors. Connect them via RJ11 breakout boards or by cutting the cables:

**Rain gauge** (tipping-bucket reed switch):

| Wire | Arduino Pin | Notes |
|------|-------------|-------|
| Wire 1 | D2 (INT0) | Hardware interrupt for pulse counting |
| Wire 2 | GND | |

Each tip of the bucket closes the reed switch for ~100 ms. One tip = 0.2794 mm of rain.

**Anemometer** (reed switch, 1 pulse per rotation):

| Wire | Arduino Pin | Notes |
|------|-------------|-------|
| Wire 1 | D3 (INT1) | Hardware interrupt for pulse counting |
| Wire 2 | GND | |

Wind speed = (pulses / time) × 2.4 km/h (per SparkFun datasheet).

**Wind vane** (resistor ladder producing variable voltage):

| Wire | Arduino Pin | Notes |
|------|-------------|-------|
| Wire 1 | A0 | Analog read — the 14-bit ADC maps resistance to direction |
| Wire 2 | GND through a 10 kΩ pull-down resistor | Forms a voltage divider with the internal vane resistors |

The vane has 8 resistors producing 16 possible directions. Read the analog value and map it to a compass bearing using a lookup table.

#### Wiring Diagram Summary

```
                    Arduino Uno R4 WiFi
                   ┌───────────────────┐
  BME280 SDA ──────┤ A4 (SDA)          │
  BME280 SCL ──────┤ A5 (SCL)          │
  BME280 VCC ──────┤ 3.3V              │
  BME280 GND ──────┤ GND               │
                   │                   │
  Rain gauge ──────┤ D2 (INT0)         │
  Rain GND ────────┤ GND               │
                   │                   │
  Anemometer ──────┤ D3 (INT1)         │
  Anemo GND ───────┤ GND               │
                   │                   │
  Wind vane ───────┤ A0                │
  Vane GND ────┬───┤ GND               │
               │   │                   │
            10kΩ   │   VIN ────── power │
               │   └───────────────────┘
              GND
```

### Arduino Sketch (MQTT Client)

Libraries required (install via Arduino Library Manager):
- **WiFiS3** (built-in with Uno R4 WiFi board package)
- **ArduinoMqttClient** (Arduino official MQTT library)
- **Adafruit BME280** + **Adafruit Unified Sensor**

```cpp
#include <WiFiS3.h>
#include <ArduinoMqttClient.h>
#include <Adafruit_BME280.h>

// Wi-Fi credentials
const char* ssid     = "weather-hub";
const char* password = "your-password";

// MQTT broker (Pi hub IP)
const char* broker   = "192.168.4.1";
const int   port     = 1883;

// Sensor objects
Adafruit_BME280 bme;
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// Wind/rain pulse counters (updated by ISR)
volatile unsigned long rainPulses = 0;
volatile unsigned long windPulses = 0;

// Publish interval
const unsigned long INTERVAL_MS = 30000; // 30 seconds
unsigned long lastPublish = 0;
unsigned long lastWindCheck = 0;

// Wind vane direction lookup (ADC value → degrees)
// Values depend on your specific vane + pull-down resistor combo
struct VaneEntry { int adcMin; int adcMax; float degrees; };
const VaneEntry VANE_TABLE[] = {
  {  150,  250, 112.5}, // ESE
  {  250,  400,  67.5}, // ENE
  {  400,  600,  90.0}, // E
  {  600,  900, 157.5}, // SSE
  {  900, 1200, 135.0}, // SE
  { 1200, 1600, 202.5}, // SSW
  { 1600, 2000, 180.0}, // S
  { 2000, 2500,  22.5}, // NNE
  { 2500, 3200,  45.0}, // NE
  { 3200, 3800, 247.5}, // WSW
  { 3800, 4500, 225.0}, // SW
  { 4500, 5500, 337.5}, // NNW
  { 5500, 6500,   0.0}, // N
  { 6500, 8000, 292.5}, // WNW
  { 8000, 9500, 315.0}, // NW
  { 9500,11000, 270.0}, // W
};

void rainISR() { rainPulses++; }
void windISR() { windPulses++; }

float readWindDirection() {
  int adc = analogRead(A0);
  for (auto& entry : VANE_TABLE) {
    if (adc >= entry.adcMin && adc < entry.adcMax) return entry.degrees;
  }
  return -1; // unknown
}

void connectWiFi() {
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    delay(5000);
  }
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    mqttClient.connect(broker, port);
    delay(2000);
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(14); // Uno R4 supports 14-bit ADC

  // BME280
  if (!bme.begin(0x76)) {
    Serial.println("BME280 not found!");
    while (1) delay(1000);
  }

  // Rain & wind interrupts
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(2), rainISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(3), windISR, FALLING);

  connectWiFi();
  connectMQTT();

  lastWindCheck = millis();
}

void loop() {
  mqttClient.poll();

  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (!mqttClient.connected()) connectMQTT();

  unsigned long now = millis();
  if (now - lastPublish >= INTERVAL_MS) {
    // Read BME280
    float temperature = bme.readTemperature();
    float humidity    = bme.readHumidity();
    float pressure    = bme.readPressure() / 100.0; // hPa

    // Calculate wind speed (km/h)
    unsigned long elapsed = now - lastWindCheck;
    noInterrupts();
    unsigned long pulses = windPulses;
    windPulses = 0;
    interrupts();
    float windSpeed = (pulses / (elapsed / 1000.0)) * 2.4;
    lastWindCheck = now;

    // Rain since last publish (mm)
    noInterrupts();
    unsigned long rain = rainPulses;
    rainPulses = 0;
    interrupts();
    float rainMM = rain * 0.2794;

    // Wind direction
    float windDir = readWindDirection();

    // Build JSON payload
    char payload[256];
    snprintf(payload, sizeof(payload),
      "{\"temperature\":%.1f,\"humidity\":%.1f,\"pressure\":%.1f,"
      "\"wind_speed_kmh\":%.1f,\"wind_dir_deg\":%.1f,\"rain_mm\":%.2f}",
      temperature, humidity, pressure, windSpeed, windDir, rainMM);

    // Publish
    mqttClient.beginMessage("weather/readings");
    mqttClient.print(payload);
    mqttClient.endMessage();

    Serial.println(payload);
    lastPublish = now;
  }
}
```

### Powering the Outdoor Arduino

The Arduino Uno R4 WiFi draws ~100 mA when active with Wi-Fi. The key challenge is providing reliable outdoor power. Here are the options ranked by suitability:

#### Option A: Solar Panel + LiPo Battery (Recommended for Off-Grid)

Best for a fully autonomous outdoor station with no access to mains power.

| Component | Spec | Price (approx.) | Purpose |
|-----------|------|-----------------|---------|
| Solar panel | 6V, 3.5W (or higher) | ~€12 | Charges the battery during daylight |
| LiPo battery | 3.7V, 6000 mAh (18650 × 2 in parallel, or flat pouch) | ~€10 | Powers the Arduino overnight and during cloudy days |
| Charge controller | TP4056 module with DW01 protection | ~€2 | Manages solar charging, prevents over-charge/over-discharge |
| Boost converter | MT3608 or similar, output set to 5V | ~€3 | Steps up 3.7V LiPo to 5V for the Arduino VIN |
| Weatherproof enclosure | IP65 junction box, ~150×100×70 mm | ~€8 | Protects electronics from rain and moisture |

**Wiring:**

```
Solar panel (6V)
    │
    ▼
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ TP4056   │────►│ 3.7V LiPo    │────►│ MT3608 boost │──► Arduino VIN (5V)
│ charger  │     │ 6000 mAh     │     │ set to 5V    │
└──────────┘     └──────────────┘     └──────────────┘
```

**Runtime estimate:**
- Arduino active draw: ~100 mA at 5V ≈ ~135 mA from 3.7V LiPo
- 6000 mAh battery: ~44 hours without any solar input
- With a 3.5W panel and 5+ hours of sunlight per day, the station runs indefinitely in summer; may need a larger panel (6W) or battery (10000 mAh) for winter at northern latitudes

**With deep sleep (extends battery life dramatically):**
- Wake every 60s, read sensors, publish MQTT, sleep again
- Active time per cycle: ~3 seconds (~100 mA) + sleep: ~5 mA
- Average draw: ~10 mA → battery lasts ~25 days without sun

To enable deep sleep on the Uno R4 WiFi, use the RTC peripheral:

```cpp
#include <RTC.h>

void setup() {
  RTC.begin();
  // ... sensor setup, one-shot publish ...
  // Sleep for 60 seconds
  RTCTime alarmTime;
  alarmTime.setSecond(0);
  AlarmMatch match;
  match.addMatchMinute(); // wake every minute
  RTC.setAlarmCallback([](){}, alarmTime, match);
  // Enter low-power mode (board-specific)
}
```

> **Note:** Deep sleep on the Uno R4 WiFi requires reconnecting Wi-Fi on each wake cycle, which adds ~2–3 seconds. For sub-minute intervals, keep Wi-Fi on and use `delay()` instead.

#### Option B: Weatherproof USB Power Supply (Near Mains Power)

Simplest option if the station is within reach of an outdoor outlet.

| Component | Spec | Price | Notes |
|-----------|------|-------|-------|
| Outdoor-rated USB-C charger | 5V / 2A, IP44+ | ~€15 | Must be rated for outdoor/wet locations |
| USB-C cable | Outdoor-rated, UV-resistant | ~€8 | Standard cables degrade in sunlight |
| Weatherproof enclosure | IP65 box | ~€8 | Mount the Arduino inside |

**Pros:** No battery management, no charge controller, always-on.
**Cons:** Requires proximity to an outlet; power outage = data gap.

#### Option C: PoE Splitter (Near Ethernet)

If you already have Ethernet cable running to the sensor location:

| Component | Spec | Price |
|-----------|------|-------|
| PoE injector | 802.3af, at the router/switch end | ~€15 |
| PoE splitter | 5V output, at the Arduino end | ~€10 |

The PoE splitter extracts power from the Ethernet cable and outputs 5V for the Arduino. The Ethernet data lines go unused (the Arduino uses Wi-Fi), but this avoids running a separate power cable.

#### Option D: 12V DC with Buck Converter (Shared with Other Outdoor Equipment)

If you have a 12V source (e.g., garden lighting transformer, CCTV power supply):

| Component | Spec | Price |
|-----------|------|-------|
| Buck converter | LM2596 module, output set to 7–9V | ~€3 |

Feed the buck converter output into the Arduino's VIN pin (accepts 6–24V). The onboard regulator steps it down to 5V.

### Power Comparison Summary

| Option | Best For | Cost | Autonomy | Complexity |
|--------|----------|------|----------|------------|
| **A: Solar + LiPo** | Remote / off-grid locations | ~€35 | Indefinite (with sun) | Medium — charge controller + boost converter |
| **B: USB mains** | Near outdoor outlet | ~€25 | Unlimited (mains) | Low — plug and play |
| **C: PoE splitter** | Near Ethernet run | ~€25 | Unlimited (PoE) | Low — injector + splitter |
| **D: 12V buck** | Shared 12V supply nearby | ~€5 | Unlimited (12V source) | Low — one module |

**Recommendation:** For a truly outdoor, self-contained weather station, **Option A (solar + LiPo)** is the standard choice. Use a 6V/3.5W panel and a 6000 mAh LiPo as the baseline. If deep sleep is enabled (wake every 60s), a smaller panel (2W) suffices. If the station is near the house, **Option B (USB mains)** is simpler and more reliable.

### Weatherproofing

| Concern | Solution |
|---------|----------|
| **Electronics** | Mount Arduino, charge controller, and battery in an IP65 junction box. Use cable glands for sensor wires. |
| **BME280** | Must be exposed to ambient air — mount it in a ventilated radiation shield (Stevenson screen) or under a louvered cover to avoid direct sun heating. |
| **RJ11 cables** | Weather sensor kits come with outdoor-rated cables. Seal the entry point into the enclosure with silicone or cable glands. |
| **Solar panel** | Mount at a ~30–45° angle facing south (northern hemisphere). Most panels are IP65+ rated. |
| **Connectors** | Use weatherproof RJ11 connectors or seal with self-amalgamating tape. |

### Arduino vs Pi Sensor Node Comparison

| Aspect | Arduino Uno R4 WiFi | Raspberry Pi 3 B+ |
|--------|--------------------|--------------------|
| Power draw (active) | ~100 mA (0.5 W) | ~700 mA (3.5 W) |
| Power draw (idle/sleep) | ~5 mA (deep sleep) | ~300 mA (idle, no deep sleep) |
| Boot time | Instant (<1 s) | ~30 s |
| Analog inputs | 6 (built-in, 14-bit) | None (needs external ADC) |
| Local buffering | No (publishes or loses data) | Yes (local Mosquitto bridge) |
| OS complexity | None (bare-metal sketch) | Full Linux OS |
| Cost | ~€25 | ~€40 |
| Solar feasible? | Yes (small panel) | Difficult (needs large panel + high-capacity battery) |
| OTA updates | Yes (via ESP32-S3 OTA) | Yes (SSH + apt/git) |

**Trade-off:** The Arduino wins on power, cost, and simplicity. The Pi wins on local buffering (Mosquitto bridge queues messages during Wi-Fi outages) and flexibility. If data loss during brief Wi-Fi dropouts is acceptable, the Arduino is the better sensor node.

### References

- [Arduino Uno R4 WiFi Documentation](https://docs.arduino.cc/hardware/uno-r4-wifi/) — official pinout, specs, and getting started
- [ArduinoMqttClient Library](https://github.com/arduino-libraries/ArduinoMqttClient) — official MQTT client for Arduino
- [SparkFun Weather Meter Kit Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all) — wiring and calibration for the RJ11 wind/rain sensors
- [Adafruit BME280 Arduino Guide](https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout/arduino-test) — library setup and wiring
- [Solar-Powered Arduino Weather Station (Instructables)](https://www.instructables.com/Solar-Powered-WiFi-Weather-Station-V4-0/) — detailed solar power design for outdoor Arduino stations

## 6. Arduino Ethernet Sensor Node (Indoor — Closed Wooden Shelter)

An alternative to the Wi-Fi-based Arduino setup in section 5: use an **Arduino Uno R4 Minima** with a **W5500 Ethernet Shield** for a wired connection to the Raspberry Pi hub. The Arduino is installed **inside a room of a closed wooden shelter** (garden cabin, shed, or outbuilding), protected from weather. All sensors are mounted **outside** the shelter, connected via **Qwiic cables** (I2C: BME280) and **RJ11 cables** (weather meter: rain, wind, vane) running 2–3 m through the wall back to the board.

### Why Ethernet Over Wi-Fi

| Concern | Wi-Fi (section 5) | Ethernet (this section) |
|---------|-------------------|------------------------|
| Reliability | Subject to interference, signal drops outdoors | Rock-solid wired link |
| Latency | Variable | Consistent, low |
| Power | ESP32-S3 radio draws ~70 mA continuously | W5500 draws ~130 mA but no reconnect cycles |
| Range | Limited to ~15 m from AP | Up to 100 m Cat5 cable |
| Security | Encrypted but attackable over the air | Physical access required |
| Setup | SSID/password config | Plug and play (DHCP) |

**Trade-off:** Ethernet requires running a Cat5/Cat6 cable from the shelter to the Pi hub. If the cable run is feasible, Ethernet is more reliable. If not, use the Wi-Fi setup from section 5.

### RJ45 Ethernet Shield — Which One?

The **W5500 Ethernet Shield** is the standard choice. It uses the WIZnet W5500 chip and is fully supported by the built-in Arduino `Ethernet` library.

| Product | Chip | Notes | Price (approx.) |
|---------|------|-------|-----------------|
| **Arduino Ethernet Shield 2** (A000024) | W5500 | Official Arduino product, includes microSD slot. May be discontinued in some markets — check availability | ~€25 |
| **W5500 Ethernet Shield V2 (clone)** | W5500 | Pin-compatible with Uno R4, widely available from HanRun, Keyestudio, DFRobot. Same functionality at lower cost | ~€8–12 |
| **WIZnet W5100S Shield** | W5100S | Older chip, fewer simultaneous sockets (4 vs 8). Works but W5500 is preferred | ~€10 |

**Recommendation:** Any **W5500-based shield** works. The clones are functionally identical to the official shield. The W5500 uses SPI (pins D10–D13) and leaves I2C (A4/A5) and interrupts (D2/D3) free for sensors.

Links: [Arduino Store](https://store.arduino.cc/products/arduino-ethernet-shield-2), [Mouser BE](https://www.mouser.be/), [Amazon](https://www.amazon.com/s?k=W5500+ethernet+shield+arduino)

### Connecting Sensors at 2–3 m Distance

#### I2C Sensors (BME280) — via Qwiic

Standard Qwiic (JST SH 4-pin) cables max out at 500 mm. For 2–3 m runs, I2C needs signal conditioning:

| Approach | Product | How it works | Price |
|----------|---------|-------------|-------|
| **Active I2C extender (recommended)** | Adafruit LTC4311 (#4756) | Single board — boosts I2C drive strength with active pull-ups. STEMMA QT on both sides for daisy-chaining. Proven at 3 m (phone wire, 400 kHz) and up to 30 m (Cat5, 100 kHz). Only **one** board needed (not a pair). | ~€10 |
| **Differential I2C** | SparkFun PCA9615 Breakout (×2, one at each end) | Converts I2C to differential signaling over Cat5/RJ45 cable — reliable up to 20 m. No Adafruit equivalent. Overkill for 2–3 m but necessary beyond ~5 m. | ~€7 each |
| **Lower bus speed** | Software config (`Wire.setClock(10000)`) | Drop I2C clock from 100 kHz to 10 kHz to tolerate capacitance on long cables — no extra hardware, but slower | Free |

Links: [Adafruit LTC4311](https://www.adafruit.com/product/4756), [SparkFun PCA9615](https://www.sparkfun.com/products/14589)

**Qwiic daisy-chain from Arduino:** Since the Ethernet shield sits on top of the Uno R4, use a **Qwiic adapter cable with breadboard jumpers** (SparkFun PRT-14425 or Adafruit 4209) to tap the I2C lines from the shield's pass-through headers. The full chain:

```
Arduino A4/A5 ──► Qwiic Adapter Cable ──► LTC4311 (STEMMA QT in/out) ──► long cable (2–3 m, through wall) ──► BME280
    (indoor)          (indoor)                (indoor)                        cable gland              (outdoor, in
                                                                              at wall                  Stevenson screen)
```

All connections are solderless Qwiic/STEMMA QT plug-and-play. For the 2–3 m segment, use a standard 4-wire cable (or Cat5 using 4 of 8 wires) with JST SH connectors crimped or soldered at each end.

#### Weather Sensors (Rain, Wind, Vane) — via RJ11

The **SparkFun Weather Meter Kit** (SEN-15901) ships with RJ11 cables that are 3–5 m long — already sufficient for a 2–3 m run. To connect the RJ11 plugs to Arduino pins, use breakout boards:

| Product | Purpose | Price |
|---------|---------|-------|
| **SparkFun RJ11 Breakout** (BOB-14021) | Breaks out the RJ11 wires to screw terminals or header pins — one per sensor pair | ~€2 each |
| **SparkFun Weather Meter Kit** (SEN-15901) | Anemometer + wind vane + rain gauge with RJ11 cables | ~€80 |

The rain gauge and anemometer connect to D2 (INT0) and D3 (INT1) for interrupt-based pulse counting. The wind vane connects to A0 for analog reading (voltage divider via internal resistor ladder).

### Component List

| # | Component | Purpose | Price (approx.) |
|---|-----------|---------|-----------------|
| 1 | Arduino Uno R4 Minima | MCU — no WiFi needed (Ethernet instead) | ~€20 |
| 2 | W5500 Ethernet Shield (clone) | Wired network to Pi hub | ~€10 |
| 3 | BME280 Qwiic breakout (Adafruit 2652 or SparkFun SEN-15440) | Temperature, humidity, pressure sensor | ~€15 |
| 4 | SparkFun Weather Meter Kit (SEN-15901) | Rain gauge, anemometer, wind vane with RJ11 cables | ~€80 |
| 5 | SparkFun RJ11 Breakout (BOB-14021) ×2 | Connect weather sensor RJ11 plugs to Arduino pins | ~€4 |
| 6 | Qwiic adapter cable — JST SH to jumper (PRT-14425) | Connect Qwiic BME280 to Arduino I2C headers | ~€2 |
| 7 | Adafruit LTC4311 I2C Extender (#4756) | Active I2C pull-up for reliable 2–3 m Qwiic cable run. STEMMA QT connectors. Single board. | ~€10 |
| 8 | Cat5e Ethernet cable (5–10 m) | Arduino to RJ45 hub | ~€5 |
| 9 | 10 kΩ resistor | Pull-down for wind vane voltage divider | ~€0.10 |
| 10 | Cable glands (IP68, 3–5 mm) ×4 | Weatherproof wall pass-throughs for sensor cables | ~€5 |
| | | **Total** | **~€151** |

### Indoor Installation (Closed Wooden Shelter)

The Arduino and electronics are installed **inside a room of a closed wooden shelter** (garden cabin, shed, workshop). The room provides natural protection from weather — no IP-rated enclosure is needed for the board. All sensors are mounted **outside**, with cables routed through the wall.

| Concern | Detail |
|---------|--------|
| **Arduino placement** | Mount on a shelf, DIN rail, or directly on the wall inside the room. Keep away from heat sources (radiators, direct window sun) to avoid warming the board unnecessarily |
| **Cable pass-through** | Drill holes through the exterior wall for RJ11 (sensors), Qwiic/Cat5 (BME280), and Cat5 (Ethernet to Pi hub). Use IP68 cable glands to seal each hole against rain and drafts |
| **BME280 placement** | Must be mounted **outside** in a Stevenson screen — the closed room's temperature and humidity do not reflect outdoor conditions. See [outdoor weatherproofing](#outdoor-weatherproofing-bme280) below for conformal coating and alternative sensors |
| **Weather sensors** | Mount rain gauge, anemometer, and wind vane on a mast or post 2–3 m from the wall, in an open area free from obstructions |
| **Ethernet cable** | Route the Cat5 cable from the Arduino through the wall (or existing conduit) to the Pi hub indoors, or to another building |
| **Power** | USB-C from an indoor outlet (simplest), or any of the power options from section 5 |
| **Moisture** | Even indoors, unheated wooden shelters can be damp — consider a small silica gel pack near the Arduino in humid climates |

### Wiring Diagram (SVG)

See the full-color wiring diagram: [arduino-ethernet-wiring.svg](arduino-ethernet-wiring.svg)

### Architecture Diagram

```
  Closed Wooden Shelter (indoor room)             OUTSIDE (2–3 m from wall)
 ┌────────────────────────────────────┐
 │                                    │
 │  Arduino Uno R4 Minima             │
 │  ┌──────────────────────┐          │      Qwiic + PCA9615       ┌────────────────┐
 │  │                      │          │    (I2C over Cat5, 2–3 m)  │ BME280         │
 │  │  W5500 Ethernet      │  A4/A5 ──┼──────────────────────────► │ (Qwiic)        │
 │  │  Shield (stacked)    │          │                            │ Temp/Hum/Press │
 │  │                      │          │                            │ in Stevenson   │
 │  └──┬───────────────────┘          │                            │ screen         │
 │     │                              │                            └────────────────┘
 │     │  D2 ─────────────────────────┼──── RJ11, 2–3 m ────────► Rain Gauge
 │     │  D3 ─────────────────────────┼──── RJ11, 2–3 m ────────► Anemometer
 │     │  A0 ─────────────────────────┼──── RJ11, 2–3 m ────────► Wind Vane
 │     │                              │      (cable glands
 │     │  RJ45 (Ethernet)             │       at wall)
 │     │                              │
 │  USB-C ← power (indoor outlet)    │
 │                                    │
 │  ┌──────────────────┐              │
 │  │ RJ45 Ethernet    │              │     Weather sensors mounted
 │  │ Hub / Switch     │              │     on mast/post in open area:
 │  │ 10/100 Mbps      │              │
 │  │ ┌──┐┌──┐┌──┐┌──┐│              │     ┌──────────┐ ┌──────────┐ ┌──────────┐
 │  │ │P1││P2││P3││P4││              │     │Rain Gauge│ │Anemometer│ │Wind Vane │
 │  │ └──┘└──┘└──┘└──┘│              │     │(tipping  │ │(reed     │ │(resistor │
 │  └───┬──┬───────────┘              │     │ bucket)  │ │ switch)  │ │ ladder)  │
 │      │  │                          │     └──────────┘ └──────────┘ └──────────┘
 │      │  └──► to indoor network     │
 │      │      (Pi, router, etc.)     │
 └──────┼─────────────────────────────┘
        │
     Arduino
     Ethernet
     (Cat5e)

Pin mapping:
  D2  (INT0)  ← Rain gauge (pulse interrupt)
  D3  (INT1)  ← Anemometer (pulse interrupt)
  A0          ← Wind vane (analog, 14-bit ADC + 10 kΩ pull-down)
  A4  (SDA)   ← BME280 via Qwiic / PCA9615
  A5  (SCL)   ← BME280 via Qwiic / PCA9615
  D10–D13     ← W5500 Ethernet Shield (SPI)
```

### Shelter Wall Cross-Section

```
      INSIDE (room)                    OUTSIDE
 ┌───────────────────┐  wall  ┌──────────────────────────────────────┐
 │                   │ ┌────┐ │                                      │
 │  ┌─────────────┐  │ │    │ │   ┌──────────┐                      │
 │  │ Arduino     │  │ │    │ │   │ BME280 in│  2–3 m    ┌────────┐ │
 │  │ + Ethernet  │──┼─┤gland├─┼──►│ Stevenson│           │ mast   │ │
 │  │ shield      │  │ │    │ │   │ screen   │           │ with   │ │
 │  └─────────────┘  │ │    │ │   └──────────┘           │ rain/  │ │
 │        │          │ │    │ │                           │ wind/  │ │
 │     USB-C power   │ ├────┤ │   RJ11 cables ──────────►│ vane   │ │
 │     (from outlet) │ │gland│ │   (rain, wind, vane)     │        │ │
 │                   │ │    │ │                           └────────┘ │
 │  Cat5 to Pi ◄─────┼─┤gland├─┘                                    │
 │                   │ └────┘                                        │
 └───────────────────┘        └──────────────────────────────────────┘
    cable glands (IP68) seal each wall penetration
```

### Outdoor Weatherproofing (BME280)

The BME280 chip is rated for -40 to +85 °C and 0-100% RH, but the breakout board (PCB, traces, pads) has **no weatherproofing**. In a Stevenson screen, the board is sheltered from direct rain but still exposed to ambient humidity, condensation, and freeze-thaw cycles.

**The #1 failure mode is condensation + freeze cycles** — the humidity sensor saturates, reads 100% permanently, and pressure drifts. Reported lifespan outdoors: 1-3 years depending on climate.

#### Protection: Conformal Coating

Apply a silicone conformal coating spray to the entire breakout board, but **mask the BME280 sensor port** (the small metal-lid component) with tape before spraying. This protects traces and pads from corrosion while keeping the humidity measurement functional.

| Product | Type | Availability | Notes |
|---------|------|-------------|-------|
| **MG Chemicals 422B** | Silicone conformal spray | Worldwide (Mouser, Digikey) | Flexible, moisture-resistant, widely recommended for weather station PCBs |
| **Kontakt Chemie Plastik 70** | Acrylic conformal spray | EU (Conrad, Reichelt) | Good alternative for European suppliers |

Additional tips:
- **Mount the sensor pointing down** to prevent rain pooling on the sensor port
- **Ensure multiple ventilation openings** in the Stevenson screen — sealed boxes trap moisture and cause faster drift
- **Budget for periodic replacement** (~€15/board every 1-3 years)

#### Alternative: Adafruit SHT31-D + BMP280

For harsher climates (frequent frost, coastal salt air, prolonged high humidity), consider replacing the BME280 with a pair of sensors purpose-built for outdoor use:

| Sensor | Measures | Outdoor Advantage | STEMMA QT | Price |
|--------|----------|------------------|-----------|-------|
| **Adafruit SHT31-D** (#2857) | Temperature + Humidity | Built-in **PTFE membrane filter** (blocks liquid water, passes vapor) + **on-board heater** to burn off condensation | Yes | ~$14 |
| **BMP280** (Adafruit #2651) | Pressure only | No humidity sensor to degrade; pressure measurement is inherently robust | Yes | ~$10 |

The SHT31-D + BMP280 pair costs ~$24 (vs ~$15 for one BME280) but lasts significantly longer outdoors. Both have STEMMA QT connectors and work with the same Qwiic daisy-chain (LTC4311 → long cable → sensors).

**Trade-off:** Two boards instead of one, slightly higher cost, two I2C addresses to read in code. But no conformal coating needed and much longer outdoor lifespan.

### References

**Ethernet Shield:**
- [Arduino Ethernet Shield 2 Documentation](https://docs.arduino.cc/retired/shields/arduino-ethernet-shield-2/) — official wiring, pinout, and library reference
- [W5500 Datasheet (WIZnet)](https://www.wiznet.io/product-item/w5500/) — chip specs and SPI interface details
- [Arduino Ethernet Library Reference](https://www.arduino.cc/reference/en/libraries/ethernet/) — API docs for `Ethernet`, `EthernetClient`, `EthernetServer`

**I2C over Long Cables:**
- [Adafruit LTC4311 Guide](https://learn.adafruit.com/adafruit-ltc4311-i2c-extender-active-terminator) — active I2C extender with STEMMA QT; single board, proven at 3 m (400 kHz) and up to 30 m (100 kHz)
- [SparkFun PCA9615 Hookup Guide](https://learn.sparkfun.com/tutorials/qwiic-differential-i2c-bus-extender-pca9615-hookup-guide) — differential I2C for cable runs beyond ~5 m (requires a pair of boards)
- [I2C Bus Specification (NXP)](https://www.nxp.com/docs/en/user-guide/UM10204.pdf) — electrical limits, capacitance budgets, and maximum cable length

**Qwiic / STEMMA QT Ecosystem:**
- [SparkFun Qwiic System Overview](https://www.sparkfun.com/qwiic) — connector pinout, daisy-chaining, and compatible boards
- [Adafruit STEMMA QT Guide](https://learn.adafruit.com/introducing-adafruit-stemma-qt) — Adafruit's compatible I2C connector system

**Weather Sensors & RJ11:**
- [SparkFun Weather Meter Kit Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all) — wiring, calibration, and RJ11 pinout for rain/wind/vane sensors
- [SparkFun RJ11 Breakout Guide](https://learn.sparkfun.com/tutorials/rj11-breakout-hookup-guide) — connecting RJ11 plugs to breadboard/Arduino pins

**Sensors Outdoor Weatherproofing & Alternatives:**

3D-printable Stevenson screens with internal sensor mount (for BME280/SHT31 — rain gauge and wind sensors are mounted separately):

[3D-Printable Stevenson Screen (Thingiverse)](https://www.thingiverse.com/search?q=stevenson+screen&type=things) — compact louvered enclosures for outdoor temperature/humidity sensors
 
| Design | Platform | Sensor Mount | Outdoor Tested | Link |
|--------|----------|-------------|----------------|------|
| **Stevenson Screen** (ImaRH 3D) | MakerWorld | BME280 internal mount, waterproof-tested | Several months | [makerworld.com/model/1922952](https://makerworld.com/en/models/1922952-stevenson-screen-for-weather-station) |
| **ESP32 + BME280 Stevenson Screen** (mariusbach) | Thingiverse | BME280 PCB holder + pipe clamp | 12+ months (cold/rain) | [thingiverse.com/thing:4459925](https://www.thingiverse.com/thing:4459925) |
| **Radiation Shield** (MakerMeik) | Thingiverse + Printables | BME280/DHT, 6mm cable holes, stackable | 12+ months | [thingiverse.com/thing:3793535](https://www.thingiverse.com/thing:3793535) |
| **Radiation Shield for SHT31** (SanglierLab) | Thingiverse | SHT31 specific, PVC pipe mount | Yes | [thingiverse.com/thing:4120452](https://www.thingiverse.com/thing:4120452) |

Print in **ASA or PETG** (UV-resistant) in **white**. PLA works short-term but may warp above ~50 °C in direct sun.

Forum discussion:
- [MySensors Forum — BME280 Outdoor Use](https://forum.mysensors.org/topic/4917/bme280-how-to-use-it-outdoors) — RTV silicone, PTFE tape, ventilation tips; 1+ year outdoor report

Silicone coating:
- [MG Chemicals 422B Silicone Conformal Coating](https://www.mgchemicals.com/products/conformal-coatings/silicone-conformal-coating-422b/) — recommended spray coating for weather station PCBs

Alternative sensors:
- [Adafruit SHT31-D (#2857)](https://www.adafruit.com/product/2857) — outdoor-rated alternative with PTFE membrane + heater (STEMMA QT)
- [Adafruit BMP280 (#2651)](https://www.adafruit.com/product/2651) — pressure-only companion to SHT31-D (STEMMA QT)

**Arduino Uno R4 Minima:**
- [Arduino Uno R4 Minima Documentation](https://docs.arduino.cc/hardware/uno-r4-minima/) — pinout, specs, shield compatibility
- [Arduino Uno R4 Shield Compatibility Guide](https://docs.arduino.cc/tutorials/uno-r4-minima/shield-guide/) — which R3 shields work with R4

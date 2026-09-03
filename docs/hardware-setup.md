# Hardware Selection, Wiring & Pi Configuration

## To be reviewed
- https://www.lextronic.fr/station-meteo-girouette-anemometre-pluviometre-2640.html
- https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all
- https://learn.sparkfun.com/tutorials/arduino-weather-shield-hookup-guide-v12
- https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide

Arduino:
- Tutorial's bible: 
  - FR: https://newbiely.fr/tutorials/arduino-uno-r4/
  - EN: https://newbiely.com/tutorials/arduino-uno-r4-tutorial
- Official doc: https://docs.arduino.cc/tutorials/ and https://projecthub.arduino.cc
- https://www.makerguides.com/arduino-weather-station-kit-dfrobot-tutorial/ 
- https://docs.arduino.cc/tutorials/uno-r4-minima/shield-guide/
- Reseller (Adafruit, Sparkfun):
  - https://www.digikey.be/, https://www.gotron.be, https://www.antratek.be
  - https://shop.mchobby.be/fr/

## 1. Hardware Selection

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
| **Wind vane** | Wind direction (resistor network) | Analog → ADC (ESP32-C3 built-in) | Part of kit | Same kit |

These are typically sold as a single **RJ11 Weather Sensor Kit** (anemometer + wind vane + rain bucket + mounting mast). DFRobot, Pimoroni, and SparkFun all sell compatible kits.

**Ready-Made Options**

| Product | Includes | Price (approx.) | Links |
|---------|----------|-----------------|-------|
| **Pimoroni Weather HAT** | BME280, LTR-559 light sensor, 1.54" LCD, RJ11 connectors for wind/rain kits | ~£30 (HAT only) | [Pimoroni](https://shop.pimoroni.com/) |
| **SparkFun MicroMod Weather Carrier Board** | RJ11 wind/rain connectors, Qwiic I2C sensor ports | ~$45 | [SparkFun](https://www.sparkfun.com/catalogsearch/result/?q=weather), [Mouser BE](https://www.mouser.be/fr/ProductDetail/DFRobot/SEN0186?qs=kE1vTINknaUaWz5cQFgJUA%3D%3D) |

## 2. Architecture

### Raspberry Pi HotSpot

We use a Raspberry Pi 3B+  acting as a hub running a Wi-Fi hotspot and MQTT broker.

**Pi 3 B+ as hub / server** (hotspot + MQTT + Quarkus):
- Runs `hostapd` (AP mode), Mosquitto MQTT broker, and the Quarkus app
- 1 GB RAM is sufficient (Mosquitto ~5 MB, Quarkus native ~30 MB, InfluxDB3 ~100-200 MB)
- Doesn't need the better Wi-Fi since it creates the network rather than reaching for one

### Message Resilience (Wi-Fi Dropout)

When the ESP32-C3 loses Wi-Fi connectivity (dropout, broker restart, hotspot issue), sensor readings are lost unless handled. Unlike a Raspberry Pi, the ESP32-C3 runs bare-metal firmware — it cannot run a local Mosquitto broker or use a broker bridge.

**Strategies for the ESP32-C3 sensor node:**

| Strategy | How it works | Trade-off |
|----------|-------------|-----------|
| **MQTT QoS 1** | Broker acknowledges each message; ESP32 retransmits on reconnect | Only works if the connection drops briefly — PubSubClient doesn't queue across reboots |
| **Local flash buffering** | Store readings in SPIFFS/LittleFS when Wi-Fi is down, publish batch on reconnect | Adds complexity; flash has limited write cycles (~100k) |
| **Accept data loss** | Publish at QoS 0, accept gaps during disconnection | Simplest; acceptable if readings are frequent (every 30–60s) |

For most garden weather stations where the Pi hotspot and ESP32 are within 10–20 m, Wi-Fi dropouts are rare. **QoS 0 with frequent readings** is the pragmatic choice — a missed 30-second reading has no meaningful impact on weather data.

#### References

- [Eclipse Mosquitto Bridge Documentation](https://mosquitto.org/man/mosquitto-conf-5.html) — broker bridge configuration (Pi-to-Pi setups)
- [Steve's Internet Guide — Mosquitto Bridge](http://www.steves-internet-guide.com/mosquitto-bridge-configuration/) — practical guide with examples for multi-broker setups
- [ESP32 MQTT Reconnect Strategies](https://randomnerdtutorials.com/esp32-mqtt-publish-subscribe-arduino-ide/) — handling connection loss in ESP32 MQTT clients

## 3. ESP32-C3 WiFi Sensor Node

The **ESP32-C3 DevKIT** serves as the outdoor sensor node. It has built-in Wi-Fi, draws very little power, costs ~€5, and has analog inputs for the wind vane — no external ADC, Ethernet shield, or Wi-Fi co-processor needed. It communicates with the Raspberry Pi 3B+ hub over Wi-Fi (the Pi runs `hostapd` as a local hotspot), publishing sensor data via MQTT.

### ESP32-C3 Specifications

| Spec | Value |
|------|-------|
| MCU | RISC-V single-core, 160 MHz |
| Wi-Fi | Built-in 802.11 b/g/n (2.4 GHz) |
| Bluetooth | BLE 5.0 |
| ADC | 12-bit, 6 channels (ADC1: GPIO0–4) |
| GPIO interrupts | Any GPIO |
| I2C | Any GPIO (default: GPIO8=SDA, GPIO9=SCL) |
| Operating voltage | 3.3V |
| Power draw (active + Wi-Fi) | ~35 mA |
| Deep sleep | ~5 µA |
| Flash / SRAM | 4 MB flash, 400 KB SRAM |
| Price | ~€5–8 |
| Framework | Arduino or ESP-IDF |

### ESP32-C3 Board Options

#### Recommended: Generic 30-pin DevKIT

A **30-pin ESP32-C3 DevKIT** (~€5) is the best choice for this project. All pins are accessible via standard 0.1" headers — easy to wire RJ11 breakout boards for the weather sensors. I2C for the BME280 uses **GPIO8 (SDA) and GPIO9 (SCL)**, which avoids any conflict with the rain gauge (GPIO5) and anemometer (GPIO6) interrupt pins. Add a **Qwiic adapter cable** (SparkFun PRT-14425, ~€2) to connect to the STEMMA QT / I2C chain.

| Board | Module | Form Factor | Price (approx.) | Links |
|-------|--------|-------------|-----------------|-------|
| **Ai-Thinker NodeMCU ESP-C3-32S-Kit** | ESP-C3-32S | 30 pins (breadboard-friendly) | ~€5 | [AliExpress](https://www.aliexpress.com/), [Amazon FR](https://www.amazon.fr/) |
| **WeAct Studio ESP32-C3** | ESP32-C3FH4 | 30 pins, USB-C | ~€4 | [AliExpress](https://www.aliexpress.com/) |
| **Espressif ESP32-C3-DevKitC-02** | ESP32-C3-WROOM-02 | 20 pins (official reference design) | ~€8 | [Mouser BE](https://www.mouser.be/), [DigiKey BE](https://www.digikey.be/) |

**Pin assignments used in this project:**

| Pin | Function | Notes |
|-----|----------|-------|
| GPIO8 (SDA) | I2C data | Via Qwiic adapter cable (PRT-14425) |
| GPIO9 (SCL) | I2C clock | Via Qwiic adapter cable (PRT-14425) |
| GPIO4 | Wind vane (analog) | ADC1_CH4, with 10 kΩ pull-down |
| GPIO5 | Rain gauge (interrupt) | INPUT_PULLUP, FALLING edge |
| GPIO6 | Anemometer (interrupt) | INPUT_PULLUP, FALLING edge |

All boards use the same ESP32-C3 chip and are programmed identically.

#### Alternative: SparkFun Thing Plus ESP32-C3

The **SparkFun Thing Plus ESP32-C3** (WRL-18168, ~€20) has a built-in Qwiic connector, but it uses **GPIO5 (SDA) and GPIO6 (SCL)** for I2C — which conflicts with the rain gauge and anemometer pins. If you use this board, you must reassign the weather sensor interrupts to other GPIOs and update the sketch.

#### Not Recommended: Adafruit QT Py ESP32-C3

The **QT Py** (#5405) has a built-in STEMMA QT but is physically too small (17.8 × 17.8 mm) with castellated pads — impractical for connecting RJ11 breakout boards. Its Qwiic port also uses GPIO5/6, creating the same pin conflict as the SparkFun board.

Links: [GoTronic (ESP32 boards)](https://www.gotronic.fr/cat-cartes-esp32.htm), [uPesy (French ESP32 boards)](https://www.upesy.fr/), [Espressif ESP32-C3 Product Page](https://www.espressif.com/en/products/socs/esp32-c3)

### Architecture

```
                                Wi-Fi (hotspot)
┌──────────────────────────┐ ◄──────────────────────── ┌───────────────────────────┐
│  Raspberry Pi 3B+        │                            │  ESP32-C3 DevKIT (30 pins)│
│  (hub / server)          │   MQTT publish             │  (sensor node)            │
│                          │ ◄─────────────────────     │                           │
│  Wi-Fi AP (hostapd)      │   topic: weather/#         │  GPIO8/9 → Qwiic adapter  │
│  Mosquitto broker        │                            │   └─► LTC4311 → BME280    │
│  Quarkus app             │                            │  Rain gauge (GPIO5)       │
│  InfluxDB3 (opt.)        │                            │  Anemometer (GPIO6)       │
│                          │                            │  Wind vane (GPIO4)        │
│  Powered by:             │                            │                           │
│  - PoE HAT + PoE switch  │                            │  Powered by:              │
│  - or standard 5V PSU    │                            │  - PoE splitter           │
│                          │                            │  - or USB / Solar         │
└──────────────────────────┘                            └───────────────────────────┘
```

### Wiring

#### BME280 → ESP32-C3 (I2C via STEMMA QT)

The **Adafruit BME280** (#2652) has a built-in STEMMA QT connector that carries both **power (3V3 + GND) and data (SDA + SCL)** — a single cable handles everything. No separate power wiring needed.

The BME280 is mounted **outside in a Stevenson screen**, 3–4 m from the ESP32-C3 inside the shed. Standard STEMMA QT cables max out at 500 mm, so the long segment uses **Cat5 cable** with an **LTC4311 I2C extender** to boost the signal.

##### Full STEMMA QT Cable Chain

```
Garden Shed (indoor)                                              Stevenson Screen (outdoor)
┌────────────────────────────────────────────────────────┐       ┌──────────────────────┐
│                                                        │       │                      │
│  ESP32-C3     Qwiic         LTC4311        splice     │ Cat5  │  splice   STEMMA QT  │
│  DevKIT   ──► adapter    ──► I2C        ──► terminal ──┼─ 3–4m─┼► terminal  100 mm    │
│  (30 pins)    cable          Extender       block      │(wall, │  block    ──────►    │
│  GPIO8=SDA    PRT-14425      #4756                     │cable  │           BME280     │
│  GPIO9=SCL    to GPIO8/9     STEMMA IN  STEMMA OUT     │gland) │           Adafruit   │
│                                                        │       │           #2652      │
│                                                        │       │                      │
│  ①             ②             ③            splice       │  ④    │  splice    ⑤         │
└────────────────────────────────────────────────────────┘       └──────────────────────┘
```

##### Cable Segments

| Step | Segment | Cable Type | Length | Connector |
|------|---------|-----------|--------|-----------|
| ① | DevKIT GPIO8/9 → Qwiic adapter | Qwiic adapter cable (SparkFun PRT-14425) soldered to GPIO8/9 | — | Female JST SH on adapter end |
| ② | Qwiic adapter → LTC4311 | STEMMA QT cable (e.g., Adafruit #4210) | 100 mm | JST SH → JST SH (plug-and-play) |
| ③ | LTC4311 STEMMA QT OUT → splice (indoor) | STEMMA QT pigtail (cut a 100 mm cable in half) | 50 mm | Solder or screw terminal block |
| ④ | Splice → splice (through wall) | **Cat5 cable** (4 of 8 wires, twisted pairs) | **3–4 m** | Through IP68 cable gland |
| ⑤ | Splice → BME280 (outdoor) | STEMMA QT pigtail (other half) | 50 mm | Screw terminal block → JST SH plug into BME280 |

##### Cat5 Wire Mapping

Use twisted pairs to reduce noise:

| Cat5 Wire | I2C Signal | Color (T568B) |
|-----------|-----------|----------------|
| Orange solid | SDA | orange |
| Orange/white striped | SCL | orange/white |
| Blue solid | 3V3 | blue |
| Blue/white striped | GND | blue/white |

##### Splicing at Each End

At the **indoor splice** (LTC4311 → Cat5) and **outdoor splice** (Cat5 → BME280), join the 4 wires using either:
- **Screw terminal blocks** (4-position, ~€1) — easiest, no soldering
- **Solder + heat-shrink tubing** — more permanent

##### Important: Reduce I2C Clock Speed

At 3–4 m, reduce the I2C clock from the default 400 kHz to **100 kHz** for reliable communication. Set `Wire.setClock(100000)` in the sketch setup.

The LTC4311 is tested at 3 m (400 kHz, phone wire) and up to 30 m (100 kHz, Cat5). At 3–4 m with Cat5 at 100 kHz, it works reliably.

##### Outdoor Cable Tips

- **Drip loop:** Let the cable sag below the Stevenson screen entry point so rain drips off instead of following the cable inside
- **UV protection:** Use conduit or UV-rated cable trunking for exposed Cat5 runs — bare jacket degrades in 1–2 years
- **Stevenson screen mounting:** Screw the BME280 board to the internal mount plate with M2.5 standoffs, sensor-side facing down. Route the STEMMA QT cable out the bottom

##### Pin-Level Reference (Generic DevKIT Only)

If using a generic DevKIT without built-in STEMMA QT, connect via the Qwiic adapter cable (PRT-14425):

| BME280 Pin | ESP32-C3 Pin | Notes |
|------------|--------------|-------|
| VCC | 3V3 | 3.3V native — no level shifter needed |
| GND | GND | |
| SDA | GPIO8 | Default I2C SDA |
| SCL | GPIO9 | Default I2C SCL |

#### RJ11 Weather Sensors → ESP32-C3

The SparkFun Weather Meter Kit (SEN-15901) sensors connect via RJ11 breakout boards (SparkFun BOB-14021 + PRT-00132).

**Important:** The ESP32-C3 is a **3.3V device**. The RJ11 weather sensors are passive components (reed switches and resistor ladder), so they work natively at 3.3V — no level shifting required. Enable internal pull-ups on the interrupt pins.

**Rain gauge** (tipping-bucket reed switch):

| Wire | ESP32-C3 Pin | Notes |
|------|--------------|-------|
| Wire 1 | GPIO5 | Interrupt for pulse counting (`INPUT_PULLUP`) |
| Wire 2 | GND | |

Each tip of the bucket closes the reed switch for ~100 ms. One tip = 0.2794 mm of rain.

**Anemometer** (reed switch, 1 pulse per rotation):

| Wire | ESP32-C3 Pin | Notes |
|------|--------------|-------|
| Wire 1 | GPIO6 | Interrupt for pulse counting (`INPUT_PULLUP`) |
| Wire 2 | GND | |

Wind speed = (pulses / time) × 2.4 km/h (per SparkFun datasheet).

**Wind vane** (resistor ladder producing variable voltage):

| Wire | ESP32-C3 Pin | Notes |
|------|--------------|-------|
| Wire 1 | GPIO4 | ADC1_CH4 — 12-bit analog read (0–4095) |
| Wire 2 | GND through a 10 kΩ pull-down resistor | Forms a voltage divider with the internal vane resistors |

**Note on ADC:** The ESP32-C3's ADC1 channels (GPIO0–4) remain fully functional when Wi-Fi is active. ADC2 channels are unavailable during Wi-Fi transmission — always use ADC1 pins for analog reads. GPIO4 (ADC1_CH4) is safe.

#### RJ11 Pin Mapping

```
Weather Meter RJ11 cables          RJ11 Breakout PCBs          ESP32-C3 DevKIT
─────────────────────              ──────────────────          ───────────────

Rain gauge RJ11 ──────────►  Breakout #1  ──► pin 2 (inner) ──► GPIO5 (interrupt)
                                           ──► pin 5 (inner) ──► GND

Anemometer + Vane RJ11 ──►  Breakout #2  ──► pin 3 (anemometer) ──► GPIO6 (interrupt)
                                           ──► pin 4 (anemometer) ──► GND
                                           ──► pin 1 (wind vane)  ──► GPIO4 (ADC1_CH4)
                                           ──► pin 6 (wind vane)  ──► GND
                                                                      │
                                                              10 kΩ resistor
                                                              between GPIO4 and GND
                                                              (pull-down for
                                                               voltage divider)
```

#### Wiring Diagram Summary

```
  ESP32-C3 DevKIT (30 pins)                                    Stevenson Screen
  + Qwiic adapter cable (PRT-14425)                            (3–4 m away)
 ┌───────────────────┐                                       ┌──────────────┐
 │                   │  Qwiic       ┌─────────┐  Cat5 3-4m  │              │
 │  GPIO8=SDA ───────┼── adapter ──►│ LTC4311 ├══════════════┼──► [BME280]  │
 │  GPIO9=SCL        │  PRT-14425  └─────────┘  (splice +   │   STEMMA QT  │
 │                   │                           wall gland) │   #2652      │
 │                   │                                       └──────────────┘
 │                   │
 │  GPIO5 ───────────┼──── RJ11 ─────► Rain gauge
 │  GPIO6 ───────────┼──── RJ11 ─────► Anemometer
 │  GPIO4 ───────────┼──── RJ11 ─────► Wind vane (ADC)
 │  GND ─────────────┼──── (common)     + 10 kΩ pull-down
 │                   │
 │  USB-C ◄── PoE splitter ◄── Cat5 PoE
 └───────────────────┘
```

#### Wiring Diagram (SVG)

See the full-color wiring diagram: [esp32c3-wifi-wiring.svg](diagrams/esp32c3-wifi-wiring.svg)

### Powering the ESP32-C3

The ESP32-C3 DevKIT draws ~35 mA with Wi-Fi active (~0.12 W), making it extremely easy to power compared to the Arduino options.

#### Option A: PoE Switch + Splitter (Recommended for Shelter Installations)

If the ESP32-C3 is installed inside a shelter (garden cabin, shed) and you can run an Ethernet cable from the house, a PoE setup provides power over the cable — no outlet needed at the sensor location. The Ethernet cable carries **only power** here — the ESP32 uses Wi-Fi for data.

**Components:**

| Component | Spec                                                                                                                       | Price (approx.) | Purpose |
|-----------|----------------------------------------------------------------------------------------------------------------------------|-----------------|---------|
| PoE switch | 5-port, 802.3af/at (e.g., [TP-Link TL-SG1005P](https://www.amazon.fr/TP-Link-sg1005p-Ports-Gigabit-Desktop/dp/B0763TGBTS)) | ~€35 | Sources PoE power on all ports |
| PoE splitter | 5V micro-USB or USB-C output (e.g., UCTRONICS PoE splitter)                                                                | ~€10 | Extracts 5V from Ethernet cable at ESP32 end |
| PoE HAT for Pi 3B+ (optional) | Official Raspberry Pi PoE+ HAT                                                                                             | ~€20 | Powers the Pi from the same PoE switch |
| Cat5e cable | Length as needed (up to 100 m)                                                                                             | ~€5–10 | Carries PoE power to ESP32 location |

**Setup:**

```
   House / Indoor                              Shelter / Outdoor
┌────────────────────────┐              ┌─────────────────────────────┐
│                        │   Cat5e      │                             │
│  PoE Switch            │ ──(PoE)────► │  PoE Splitter → 5V → ESP32 │
│  (e.g., TL-SG1005P)   │   up to      │  (data lines unused —      │
│     │                  │   100 m      │   ESP32 uses Wi-Fi)        │
│     │ port 1: Pi 3B+   │              │                             │
│     │ port 2: → ESP32  │              │  Sensors (BME280, RJ11)    │
│     │                  │              │                             │
│  Router / Internet     │              └─────────────────────────────┘
└────────────────────────┘
```

**Note:** The Raspberry Pi 3B+ can be **powered by** PoE (with the PoE HAT) but **cannot source** PoE. A dedicated PoE switch or PoE injector is required to send power to the ESP32 over an Ethernet cable.

#### Option B: USB Power (Near Outlet)

Simplest option if the ESP32 is within reach of an outlet.

| Component | Spec | Price (approx.) | Notes |
|-----------|------|-----------------|-------|
| USB-C cable + charger | 5V / 1A | ~€8 | Any USB charger works — the ESP32-C3 draws only ~0.12 W |

#### Option C: Solar + LiPo (Off-Grid)

The ESP32-C3's low power draw allows a small solar panel and battery:

| Component | Spec | Price (approx.) |
|-----------|------|-----------------|
| Solar panel | 5V, 1W | ~€5 |
| LiPo battery | 3.7V, 2000 mAh | ~€6 |
| TP4056 charger | With DW01 protection circuit | ~€2 |

With deep sleep (wake every 60s), average draw is ~0.5 mA → battery lasts ~166 days without sun. Even a 1W panel keeps it running year-round at most latitudes.

### Pi 3B+ as Wi-Fi Hotspot

The Raspberry Pi 3B+ runs `hostapd` to create a local Wi-Fi network (SSID: `weather-hub`). The ESP32-C3 connects to this network and publishes MQTT messages to the Mosquitto broker running on the Pi. The ESP32-C3 receives an IP in the 192.168.4.x range via `dnsmasq` DHCP.

### Component List

| # | Component | Purpose | Price (approx.) | Buy |
|---|-----------|---------|-----------------|-----|
| 1 | ESP32-C3 DevKIT (30 pins) | MCU with built-in Wi-Fi, breadboard-friendly headers | ~€5 | [AliExpress](https://www.aliexpress.com/), [Amazon FR](https://www.amazon.fr/) |
| 1b | SparkFun Qwiic adapter cable (PRT-14425) | Adds JST SH (STEMMA QT) connector to GPIO8/9 | ~€2 | [Kiwi Electronics](https://www.kiwi-electronics.com/), [SparkFun](https://www.sparkfun.com/products/14425) |
| 2 | Adafruit BME280 (#2652) | Temperature, humidity, pressure sensor with STEMMA QT | ~€15 | [MCHobby](https://shop.mchobby.be/en/breakout/684-bme280-temphumiditypressure-sensor-i2c-spi-stemmaqtqwiic--3232100006843-adafruit.html) |
| 3 | SparkFun Weather Meter Kit (SEN-15901) | Rain gauge, anemometer, wind vane with RJ11 cables | ~€80 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/weather-meters-2931) |
| 4 | SparkFun RJ11 Breakout (BOB-14021) | Breaks out RJ11 wires to header pins (includes 2 PCBs) | ~€2 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/sparkfun-rj11-breakout-2925) |
| 5 | SparkFun RJ11 6-Pin Connector (PRT-00132) ×2 | Through-hole RJ11 sockets — solder onto each breakout PCB | ~€4 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/brand-sparkfun-electronics/rj11-6-pin-connector-2926) |
| 6 | STEMMA QT cable 100 mm (Adafruit #4210) ×2 | Qwiic adapter → LTC4311, and pigtails for Cat5 splices | ~€3 | [Adafruit](https://www.adafruit.com/product/4210), [MCHobby](https://shop.mchobby.be) |
| 7 | Adafruit LTC4311 I2C Extender (#4756) | Active I2C pull-up for reliable 3–4 m Cat5 cable run | ~€10 | [MCHobby](https://shop.mchobby.be/en/breakout/2058-extension-terminaison-bus-i2c-ltc4311-3232100020580-adafruit.html) |
| 8 | 4-pos screw terminal blocks ×2 | Splice STEMMA QT pigtails to Cat5 wires (indoor + outdoor) | ~€2 | [Gotron](https://www.gotron.be) |
| 9 | 10 kΩ resistor | Pull-down for wind vane voltage divider | ~€0.10 | [Gotron](https://www.gotron.be) |
| 10 | Cat5e cable (3–4 m + PoE run) | I2C signal to BME280 + PoE power delivery | ~€5 | [Gotron](https://www.gotron.be) |
| 11 | PoE switch (5-port, 802.3af) | Sources PoE power for ESP32 and Pi | ~€35 | [Amazon FR](https://www.amazon.fr/), [Alternate BE](https://www.alternate.be/) |
| 12 | PoE splitter (5V USB-C output) | Extracts 5V from Ethernet cable at ESP32 end | ~€10 | [Amazon FR](https://www.amazon.fr/), [UCTRONICS](https://www.uctronics.com/) |
| 13 | Cable glands (IP68, 3–5 mm) ×3 | Weatherproof wall pass-throughs for sensor cables | ~€4 | [Gotron](https://www.gotron.be/kabelwartel-zwart-pg7.html) |
| | | **Total (with PoE)** | **~€172** | |
| | | **Total (without PoE, USB power)** | **~€122** | |

### References

**ESP32-C3:**
- [Espressif ESP32-C3 Product Page](https://www.espressif.com/en/products/socs/esp32-c3) — official specs, features, and technical documents
- [ESP32-C3-DevKitC-02 Getting Started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/hw-reference/esp32c3/user-guide-devkitc-02.html) — official development board guide with pinout diagram
- [Arduino-ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/) — Arduino framework for all ESP32 variants including C3
- [ESP32-C3 Arduino GPIO Reference](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html) — GPIO, ADC, I2C, and interrupt configuration
- [Random Nerd Tutorials — Getting Started with ESP32](https://randomnerdtutorials.com/getting-started-with-esp32/) — beginner-friendly tutorials for ESP32 boards

**Books & Courses:**
- [ESP32-C3 Wireless Adventure (Espressif, free)](https://github.com/niceBoy0929/book-esp32c3-iot-projects) — official Espressif book covering IoT development with ESP32-C3 from basics to cloud integration (Wi-Fi, BLE, ESP RainMaker, OTA). Covers both ESP-IDF and Arduino. Highly regarded by the community.
- [Learn ESP32 with Arduino IDE (Random Nerd Tutorials)](https://randomnerdtutorials.com/learn-esp32-with-arduino-ide/) — paid ebook/course by Sara & Rui Santos. Covers 60+ projects including weather stations, MQTT, deep sleep, web servers. The most popular hands-on ESP32 resource.

**MQTT on ESP32:**
- [PubSubClient Library (Nick O'Leary)](https://github.com/knolleary/pubsubclient) — lightweight MQTT client for Arduino and ESP32
- [ESP32 MQTT Publish/Subscribe Tutorial](https://randomnerdtutorials.com/esp32-mqtt-publish-subscribe-arduino-ide/) — step-by-step MQTT setup with ESP32

**BME280 on ESP32:**
- [ESP32 BME280 Weather Station Tutorial](https://randomnerdtutorials.com/esp32-bme280-arduino-ide-pressure-temperature-humidity/) — wiring and code for ESP32 + BME280

**PoE:**
- [Raspberry Pi PoE+ HAT](https://www.raspberrypi.com/products/poe-plus-hat/) — official PoE HAT for Pi 3B+/4 (802.3af/at input, 5V/5A output)
- [TP-Link TL-SG1005P](https://www.tp-link.com/en/business-networking/poe-switch/tl-sg1005p/) — 5-port Gigabit PoE switch (4 PoE ports, 56W total budget)
- [UCTRONICS PoE Splitter](https://www.uctronics.com/) — compact 802.3af/at PoE splitter with 5V USB-C output for microcontrollers

**Weather Sensors & RJ11:**
- [SparkFun Weather Meter Kit Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all) — wiring, calibration, and RJ11 pinout for rain/wind/vane sensors
- [SparkFun RJ11 Breakout Hookup Guide](https://learn.sparkfun.com/tutorials/rj11-breakout-hookup-guide) — connecting RJ11 plugs to breadboard or MCU pins
- [SparkFun MicroClimate Kit Guide](https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide) — complete weather station experiment guide
- [Lextronic Weather Station Kit](https://www.lextronic.fr/station-meteo-girouette-anemometre-pluviometre-2640.html) — anemometer + wind vane + rain gauge kit (French reseller)

**Suppliers:**
- [DigiKey BE](https://www.digikey.be/), [Gotron](https://www.gotron.be), [Antratek](https://www.antratek.be) — electronics components (Belgium)
- [MCHobby](https://shop.mchobby.be/fr/) — Adafruit / SparkFun reseller (Belgium, French-speaking)

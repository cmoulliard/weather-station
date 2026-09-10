# Architecture and hardware

## To be reviewed and sorted
- https://www.lextronic.fr/station-meteo-girouette-anemometre-pluviometre-2640.html
- https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all
- https://learn.sparkfun.com/tutorials/arduino-weather-shield-hookup-guide-v12
- https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide

- !!!! EXCELLENT: https://learn.sparkfun.com/tutorials/esp32-environment-sensor-shield-hookup-guide and https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide

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

## References

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

**Weather Sensors & RJ11:**
- [SparkFun Weather Meter Kit Hookup Guide](https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide/all) — wiring, calibration, and RJ11 pinout for rain/wind/vane sensors
- [SparkFun RJ11 Breakout Hookup Guide](https://learn.sparkfun.com/tutorials/rj11-breakout-hookup-guide) — connecting RJ11 plugs to breadboard or MCU pins
- [SparkFun MicroClimate Kit Guide](https://learn.sparkfun.com/tutorials/microclimate-kit-experiment-guide) — complete weather station experiment guide
- [Lextronic Weather Station Kit](https://www.lextronic.fr/station-meteo-girouette-anemometre-pluviometre-2640.html) — anemometer + wind vane + rain gauge kit (French reseller)

**Suppliers:**
- [DigiKey BE](https://www.digikey.be/), [Gotron](https://www.gotron.be), [Antratek](https://www.antratek.be) — electronics components (Belgium)
- [MCHobby](https://shop.mchobby.be/fr/) — Adafruit / SparkFun reseller (Belgium, French-speaking)


## Hardware

### Sensors

**Temperature, Humidity & Pressure:**

| Sensor | Measures | Accuracy | Price (approx.) | Links                                                                                                                                                                                                         |
|--------|----------|----------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **BME280** (I2C/SPI) | Temperature (-40 to +85 °C), Humidity (0-100% RH), Pressure (300-1100 hPa) | ±1.0 °C, ±3% RH, ±1 hPa | ~€15 (breakout board) | [Adafruit](https://www.adafruit.com/product/2652), [Mouser BE](https://www.mouser.be/fr/c/?q=BME280), [TME](https://www.tme.eu/be/fr/details/df-sen0335/capteurs-environnementaux/dfrobot/sen0335/), [Kiwi](https://www.kiwi-electronics.com/en/bme280-sensor-board-with-i2c-and-spi-for-temperature-humidity-and-pressure-stemma-qt-2112?search=BME280) |
| **BME680** (I2C/SPI) | Same as BME280 + VOC gas (air quality) | ±1.0 °C, ±3% RH, ±1 hPa | ~€19 (breakout board) | [Adafruit](https://www.adafruit.com/product/3660), [Mouser BE](https://www.mouser.be/), [TME](https://www.tme.eu/)                                                                                            |

The BME280 is the go-to choice for weather stations. The BME680 adds a metal oxide VOC gas sensor (48h burn-in required) -- useful if indoor air quality matters. Both are available as STEMMA QT / Qwiic breakout boards for solderless I2C wiring.

**UV:**

| Sensor | Measures | Accuracy | Price (approx.) | Links |
|--------|----------|----------|-----------------|-------|
| **LTR390-UV** (I2C) | UV Index (UVI), raw UVS counts, ambient light (ALS) | ±1 UVI | ~€8 (breakout board) | [Adafruit](https://www.adafruit.com/product/4831), [MCHobby](https://shop.mchobby.be) |
| **VEML6075** (I2C) | UVA, UVB irradiance | ±1 UVI (calculated) | ~€7 (breakout board) | [Adafruit](https://www.adafruit.com/product/3964), [Mouser BE](https://www.mouser.be) |

The LTR390-UV is the recommended choice — available as a STEMMA QT breakout from Adafruit (#4831), it connects directly to the I2C chain alongside the BME280 and provides a calibrated UV Index reading. Unlike the BME280 (shaded in a Stevenson screen), the UV sensor must be mounted with a clear view of the sky.

**Wind & Rain:**

| Sensor | Function | Interface | Price (approx.) | Links |
|--------|----------|-----------|-----------------|-------|
| **Rain gauge** (tipping bucket) | Precipitation measurement | Reed switch pulse → GPIO | Part of kit (~€160) | [The Pi Hut](https://thepihut.com/products/weather-station-kit-with-anemometer-wind-vane-rain-bucket), [DFRobot](https://www.dfrobot.com/) |
| **Anemometer** | Wind speed (rotation pulses/sec) | Reed switch pulse → GPIO | Part of kit | Same kit |
| **Wind vane** | Wind direction (resistor network) | Analog → ADC (ESP32 built-in) | Part of kit | Same kit |

These are typically sold as a single **RJ11 Weather Sensor Kit** (anemometer + wind vane + rain bucket + mounting mast). DFRobot, Pimoroni, and SparkFun all sell compatible kits.

**Ready-Made Options**

| Product | Includes | Price (approx.) | Links |
|---------|----------|-----------------|-------|
| ~~**Pimoroni Weather HAT**~~ | ~~BME280, LTR-559 light sensor, 1.54" LCD, RJ11 connectors for wind/rain kits~~ | ~~£30 (HAT only)~~ | ~~[Pimoroni](https://shop.pimoroni.com/)~~ |
| **SparkFun MicroMod Weather Carrier Board** | RJ11 wind/rain connectors, Qwiic I2C sensor ports | ~$45 | [SparkFun](https://www.sparkfun.com/catalogsearch/result/?q=weather), [Mouser BE](https://www.mouser.be/fr/ProductDetail/DFRobot/SEN0186?qs=kE1vTINknaUaWz5cQFgJUA%3D%3D) |

## 2. Architecture

### Raspberry Pi HotSpot

We use a Raspberry Pi 3B+ acting as a hub running:
- a Wi-Fi hotspot,
- MQTT broker to collect the data from the IoT ESP32 board
- Weather Quarkus application (optional)

### Message Resilience (Wi-Fi Dropout)

When the ESP32 loses Wi-Fi connectivity (dropout, broker restart, hotspot issue), sensor readings are lost unless handled. Unlike a Raspberry Pi, the ESP32 runs bare-metal firmware — it cannot run a local Mosquitto broker or use a broker bridge.

**Strategies for the ESP32 sensor node:**

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

## 3. ESP32 WiFi Sensor Node

The **ESP32** serves as the outdoor sensor node. It has built-in Wi-Fi, draws very little power, and has analog inputs for the wind vane — no external ADC or Wi-Fi co-processor needed. It communicates with the Raspberry Pi 3B+ hub over Wi-Fi (the Pi runs `hostapd` as a local hotspot), publishing sensor data via MQTT.

The specific ESP32 variant will be selected based on project requirements. See the [ESP32 board catalog](https://www.espboards.dev/esp32/) for available options.

**Sensors connected to the ESP32 board:**

| Sensor | Measurement | Interface |
|--------|-------------|-----------|
| BME280 | Temperature, Humidity, Pressure | I2C (STEMMA QT) |
| LTR390-UV | UV Index | I2C (STEMMA QT) |
| Rain gauge | Precipitation | GPIO interrupt |
| Anemometer | Wind speed | GPIO interrupt |
| Wind vane | Wind direction | ADC (analog) |

**Power supply:** Solar panel and/or LiPo battery (see [Powering the ESP32](#powering-the-esp32)).

> **Note:** The pin assignments below are based on a typical ESP32 development board. Specific GPIO numbers will be confirmed once the board variant is selected.

**Planned pin assignments:**

| Pin | Function | Notes |
|-----|----------|-------|
| SDA (e.g. GPIO8) | I2C data | Via Qwiic adapter cable — serves BME280 and LTR390 |
| SCL (e.g. GPIO9) | I2C clock | Via Qwiic adapter cable |
| ADC pin (e.g. GPIO4) | Wind vane (analog) | ADC channel, with 10 kΩ pull-down |
| GPIO (e.g. GPIO5) | Rain gauge (interrupt) | INPUT_PULLUP, FALLING edge |
| GPIO (e.g. GPIO6) | Anemometer (interrupt) | INPUT_PULLUP, FALLING edge |

### Architecture

```
                                Wi-Fi (hotspot)
┌──────────────────────────┐ ◄──────────────────────── ┌───────────────────────────┐
│  Raspberry Pi 3B+        │                            │  ESP32 DevKIT             │
│  (hub / server)          │   MQTT publish             │  (sensor node)            │
│                          │ ◄─────────────────────     │                           │
│  Wi-Fi AP (hostapd)      │   topic: weather/#         │  I2C (STEMMA QT):         │
│  Mosquitto broker        │                            │   └─► BME280 (T/H/P)      │
│  Quarkus app (opt.)      │                            │   └─► LTR390 (UV Index)   │
│                          │                            │  Rain gauge (GPIO INT)    │
│  Powered by:             │                            │  Anemometer (GPIO INT)    │
│  - Standard 5V PSU       │                            │  Wind vane (ADC)          │
│                          │                            │                           │
│                          │                            │  Powered by:              │
│                          │                            │  - Solar panel + LiPo     │
└──────────────────────────┘                            └───────────────────────────┘
```

### Wiring

#### BME280 → ESP32 (I2C via STEMMA QT)

The **Adafruit BME280** (#2652) has a built-in STEMMA QT connector that carries both **power (3V3 + GND) and data (SDA + SCL)** — a single cable handles everything. No separate power wiring needed.

The BME280 is mounted **outside in a Stevenson screen**, 3–4 m from the ESP32 inside the shed. Standard STEMMA QT cables max out at 500 mm, so the long segment uses **Cat5 cable** with an **LTC4311 I2C extender** to boost the signal.

The **LTR390-UV** sensor connects to the same I2C bus via a STEMMA QT daisy-chain from the BME280 breakout board. It must be mounted with a clear view of the sky (not inside the Stevenson screen).

##### Full STEMMA QT Cable Chain

```
Garden Shed (indoor)                                              Stevenson Screen (outdoor)
┌────────────────────────────────────────────────────────┐       ┌──────────────────────┐
│                                                        │       │                      │
│  ESP32       Qwiic         LTC4311        splice      │ Cat5  │  splice   STEMMA QT  │
│  DevKIT   ──► adapter    ──► I2C        ──► terminal ──┼─ 3–4m─┼► terminal  100 mm    │
│               cable          Extender       block      │(wall, │  block    ──────►    │
│  SDA          PRT-14425      #4756                     │cable  │           BME280     │
│  SCL          to SDA/SCL     STEMMA IN  STEMMA OUT     │gland) │      ──► LTR390-UV   │
│                                                        │       │          (sky-facing) │
│                                                        │       │                      │
│  ①             ②             ③            splice       │  ④    │  splice    ⑤         │
└────────────────────────────────────────────────────────┘       └──────────────────────┘
```

##### Cable Segments

| Step | Segment | Cable Type | Length | Connector |
|------|---------|-----------|--------|-----------|
| ① | DevKIT SDA/SCL → Qwiic adapter | Qwiic adapter cable (SparkFun PRT-14425) soldered to SDA/SCL pins | — | Female JST SH on adapter end |
| ② | Qwiic adapter → LTC4311 | STEMMA QT cable (e.g., Adafruit #4210) | 100 mm | JST SH → JST SH (plug-and-play) |
| ③ | LTC4311 STEMMA QT OUT → splice (indoor) | STEMMA QT pigtail (cut a 100 mm cable in half) | 50 mm | Solder or screw terminal block |
| ④ | Splice → splice (through wall) | **Cat5 cable** (4 of 8 wires, twisted pairs) | **3–4 m** | Through IP68 cable gland |
| ⑤ | Splice → BME280 → LTR390 (outdoor) | STEMMA QT pigtail (other half) + short daisy-chain cable | 50 mm + 100 mm | Screw terminal block → JST SH plug into BME280 → LTR390 |

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
- **UV sensor mounting:** Mount the LTR390 outside the Stevenson screen in a clear enclosure facing upward, with a short STEMMA QT cable from the BME280's second connector

##### Pin-Level Reference

Connect via the Qwiic adapter cable (PRT-14425):

| BME280 / LTR390 Pin | ESP32 Pin | Notes |
|----------------------|-----------|-------|
| VCC | 3V3 | 3.3V native — no level shifter needed |
| GND | GND | |
| SDA | SDA (e.g. GPIO8) | Default I2C SDA |
| SCL | SCL (e.g. GPIO9) | Default I2C SCL |

#### RJ11 Weather Sensors → ESP32

The SparkFun Weather Meter Kit (SEN-15901) sensors connect via RJ11 breakout boards (SparkFun BOB-14021 + PRT-00132).

**Important:** The ESP32 is a **3.3V device**. The RJ11 weather sensors are passive components (reed switches and resistor ladder), so they work natively at 3.3V — no level shifting required. Enable internal pull-ups on the interrupt pins.

**Rain gauge** (tipping-bucket reed switch):

| Wire | ESP32 Pin | Notes |
|------|-----------|-------|
| Wire 1 | Rain GPIO (e.g. GPIO5) | Interrupt for pulse counting (`INPUT_PULLUP`) |
| Wire 2 | GND | |

Each tip of the bucket closes the reed switch for ~100 ms. One tip = 0.2794 mm of rain.

**Anemometer** (reed switch, 1 pulse per rotation):

| Wire | ESP32 Pin | Notes |
|------|-----------|-------|
| Wire 1 | Anemometer GPIO (e.g. GPIO6) | Interrupt for pulse counting (`INPUT_PULLUP`) |
| Wire 2 | GND | |

Wind speed = (pulses / time) × 2.4 km/h (per SparkFun datasheet).

**Wind vane** (resistor ladder producing variable voltage):

| Wire | ESP32 Pin | Notes |
|------|-----------|-------|
| Wire 1 | ADC pin (e.g. GPIO4) | 12-bit analog read (0–4095) |
| Wire 2 | GND through a 10 kΩ pull-down resistor | Forms a voltage divider with the internal vane resistors |

**Note on ADC:** On most ESP32 variants, ADC2 channels are unavailable during Wi-Fi transmission — always use ADC1 pins for analog reads. Check your board's datasheet for the ADC1 channel mapping.

#### RJ11 Pin Mapping

```
Weather Meter RJ11 cables          RJ11 Breakout PCBs          ESP32 DevKIT
─────────────────────              ──────────────────          ───────────

Rain gauge RJ11 ──────────►  Breakout #1  ──► pin 2 (inner) ──► Rain GPIO (interrupt)
                                           ──► pin 5 (inner) ──► GND

Anemometer + Vane RJ11 ──►  Breakout #2  ──► pin 3 (anemometer) ──► Anemometer GPIO (interrupt)
                                           ──► pin 4 (anemometer) ──► GND
                                           ──► pin 1 (wind vane)  ──► ADC pin
                                           ──► pin 6 (wind vane)  ──► GND
                                                                      │
                                                              10 kΩ resistor
                                                              between ADC pin and GND
                                                              (pull-down for
                                                               voltage divider)
```

#### Wiring Diagram Summary

```
  ESP32 DevKIT                                                  Stevenson Screen
  + Qwiic adapter cable (PRT-14425)                            (3–4 m away)
 ┌───────────────────┐                                       ┌──────────────┐
 │                   │  Qwiic       ┌─────────┐  Cat5 3-4m  │              │
 │  SDA ─────────────┼── adapter ──►│ LTC4311 ├══════════════┼──► [BME280]  │
 │  SCL              │  PRT-14425  └─────────┘  (splice +   │  ──► [LTR390]│
 │                   │                           wall gland) │   STEMMA QT  │
 │                   │                                       └──────────────┘
 │                   │
 │  GPIO ────────────┼──── RJ11 ─────► Rain gauge
 │  GPIO ────────────┼──── RJ11 ─────► Anemometer
 │  ADC  ────────────┼──── RJ11 ─────► Wind vane (analog)
 │  GND ─────────────┼──── (common)     + 10 kΩ pull-down
 │                   │
 │  Solar + LiPo ◄── TP4056 charger
 └───────────────────┘
```

#### Wiring Diagram (SVG)

See the full-color wiring diagram: [esp32c3-wifi-wiring.svg](diagrams/esp32c3-wifi-wiring.svg)

### Powering the ESP32

The ESP32 DevKIT draws very little power with Wi-Fi active, making it easy to power with a small solar panel and LiPo battery.

#### Option A: Solar + LiPo (Recommended for Outdoor Installations)

The ESP32's low power draw allows a small solar panel and battery for fully off-grid operation:

| Component | Spec | Price (approx.) |
|-----------|------|-----------------|
| Solar panel | 5V, 1W | ~€5 |
| LiPo battery | 3.7V, 2000 mAh | ~€6 |
| TP4056 charger | With DW01 protection circuit | ~€2 |

With deep sleep (wake every 60s), average draw is ~0.5 mA → battery lasts ~166 days without sun. Even a 1W panel keeps it running year-round at most latitudes.

#### Option B: USB Power (Near Outlet)

Simplest option if the ESP32 is within reach of an outlet.

| Component | Spec | Price (approx.) | Notes |
|-----------|------|-----------------|-------|
| USB-C cable + charger | 5V / 1A | ~€8 | Any USB charger works |

### Pi 3B+ as Wi-Fi Hotspot

The Raspberry Pi 3B+ runs `hostapd` to create a local Wi-Fi network (SSID: `weather-hub`). The ESP32 connects to this network and publishes MQTT messages to the Mosquitto broker running on the Pi. The ESP32 receives an IP in the 192.168.4.x range via `dnsmasq` DHCP.

### Component List

| # | Component | Purpose | Price (approx.) | Buy |
|---|-----------|---------|-----------------|-----|
| 1 | ESP32 DevKIT | MCU with built-in Wi-Fi | ~€5 | [espboards.dev](https://www.espboards.dev/esp32/), [AliExpress](https://www.aliexpress.com/) |
| 1b | SparkFun Qwiic adapter cable (PRT-14425) | Adds JST SH (STEMMA QT) connector to SDA/SCL pins | ~€2 | [Kiwi Electronics](https://www.kiwi-electronics.com/), [SparkFun](https://www.sparkfun.com/products/14425) |
| 2 | Adafruit BME280 (#2652) | Temperature, humidity, pressure sensor with STEMMA QT | ~€15 | [MCHobby](https://shop.mchobby.be/en/breakout/684-bme280-temphumiditypressure-sensor-i2c-spi-stemmaqtqwiic--3232100006843-adafruit.html) |
| 3 | Adafruit LTR390-UV (#4831) | UV Index sensor with STEMMA QT | ~€8 | [Adafruit](https://www.adafruit.com/product/4831), [MCHobby](https://shop.mchobby.be) |
| 4 | SparkFun Weather Meter Kit (SEN-15901) | Rain gauge, anemometer, wind vane with RJ11 cables | ~€80 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/weather-meters-2931) |
| 5 | SparkFun RJ11 Breakout (BOB-14021) | Breaks out RJ11 wires to header pins (includes 2 PCBs) | ~€2 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/sparkfun-rj11-breakout-2925) |
| 6 | SparkFun RJ11 6-Pin Connector (PRT-00132) ×2 | Through-hole RJ11 sockets — solder onto each breakout PCB | ~€4 | [Kiwi Electronics](https://www.kiwi-electronics.com/en/brand-sparkfun-electronics/rj11-6-pin-connector-2926) |
| 7 | STEMMA QT cable 100 mm (Adafruit #4210) ×3 | Qwiic adapter → LTC4311, splices, and BME280 → LTR390 daisy-chain | ~€5 | [Adafruit](https://www.adafruit.com/product/4210), [MCHobby](https://shop.mchobby.be) |
| 8 | Adafruit LTC4311 I2C Extender (#4756) | Active I2C pull-up for reliable 3–4 m Cat5 cable run | ~€10 | [MCHobby](https://shop.mchobby.be/en/breakout/2058-extension-terminaison-bus-i2c-ltc4311-3232100020580-adafruit.html) |
| 9 | 4-pos screw terminal blocks ×2 | Splice STEMMA QT pigtails to Cat5 wires (indoor + outdoor) | ~€2 | [Gotron](https://www.gotron.be) |
| 10 | 10 kΩ resistor | Pull-down for wind vane voltage divider | ~€0.10 | [Gotron](https://www.gotron.be) |
| 11 | Cat5e cable (3–4 m) | I2C signal run from shed to Stevenson screen | ~€3 | [Gotron](https://www.gotron.be) |
| 12 | Solar panel (5V, 1W) | Primary power source for ESP32 | ~€5 | [AliExpress](https://www.aliexpress.com/), [Amazon FR](https://www.amazon.fr/) |
| 13 | LiPo battery (3.7V, 2000 mAh) | Battery backup for ESP32 | ~€6 | [AliExpress](https://www.aliexpress.com/), [Amazon FR](https://www.amazon.fr/) |
| 14 | TP4056 charger module | Solar charge controller with battery protection (DW01) | ~€2 | [AliExpress](https://www.aliexpress.com/) |
| 15 | Cable glands (IP68, 3–5 mm) ×3 | Weatherproof wall pass-throughs for sensor cables | ~€4 | [Gotron](https://www.gotron.be/kabelwartel-zwart-pg7.html) |
| | | **Total** | **~€153** | |
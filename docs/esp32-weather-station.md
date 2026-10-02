# Solar-powered ESP32 Weather Station

> TODO

## Table of contents

1. [Bill of materials](#bill-of-materials)
2. [References](#references)
---

## Bill of materials

### Sensors

| Category | Sensor | Key Specifications / Details | Link |
| --- | --- | --- | --- |
| **Environmental** | **BME280 Sensor Module** | Temperature (-40 to +85 °C, ±1.0 °C), Humidity (0–100% RH, ±3%), Barometric Pressure (300–1100 hPa, ±1 hPa). I2C / SPI, 3.3V compatible, STEMMA QT connector. | [TinyTronics](https://www.tinytronics.nl/en/sensors/temperature-air-humidity/bme280-digital-barometer-pressure-and-humidity-sensor-module) |
| **UV Index** | **DFRobot Gravity LTR390-UV** | UV Index (UVI), ambient light (ALS). I2C/UART, 3.3V. Mount with clear sky view (not inside Stevenson screen). | [TinyTronics](https://www.tinytronics.nl/en/sensors/optical/light-and-color/dfrobot-gravity-ltr390-uv-light-sensor-module-i2c-uart) |
| **Rain Gauge** | **Tipping Bucket Rain Gauge** (part of weather meter kit) | Reed switch pulse per tip → GPIO interrupt. One tip = 0.2794 mm of rain. RJ11 connector. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |
| **Wind Speed** | **Anemometer** (part of weather meter kit) | Reed switch, 1 pulse per rotation → GPIO interrupt. Speed = pulses/sec × 2.4 km/h. RJ11 connector. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |
| **Wind Direction** | **Wind Vane** (part of weather meter kit) | Resistor ladder producing variable voltage → ADC analog read. 16 directions. RJ11 connector. Requires 10 kΩ pull-down resistor. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |

### ESP32

| Category | Recommended Product Reference | Key Specifications / Details | Tinytronics Link |
| --- | --- | --- | --- |
| **Microcontroller** | **DFRobot FireBeetle 2 ESP32-C6** - https://www.dfrobot.com/product-2771.html | RISC-V 160MHz, BLE 5.3 + Wi-Fi 6, onboard solar MPPT charge controller & JST-PH battery jack. | [View ESP32-C6 Boards](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/dfrobot-firebeetle-2-esp32-c6-development-board-seperate-headers) |
| **Rechargeable Battery** | **LiPo Battery 3.7V (1200mAh – 2000mAh)** | Single-cell 3.7V Lithium-Polymer battery with standard **JST-PH 2.0mm** connector. | [TinyTronics](https://www.tinytronics.nl/en/power/batteries/li-po/pkcell-li-po-battery-3.7v-2000mah-jst-ph-lp803860) |
| **Solar Panel** | **Mini Solar Panel 5V or 6V (1W – 2W)** | Monocrystalline / Polycrystalline panel outputting 5V–6V DC (approx. 150mA–300mA in sun). | [TinyTronics](https://www.tinytronics.nl/en/power/solar-energy/solar-panels) |
| **Battery Connector** | **JST-PH 2.0mm 2-Pin Cable** | Plug extension/lead for solar panel or custom battery connections. | [TinyTronics](https://tinytronics.nl/shop/en/cables/jst/jst-2.0mm-connector-with-cable-ph2.0-2-pins) |
| **Sensor Wiring** | **Dupont Female-to-Female Jumper Wires** | 10cm or 20cm wires to connect the BME280 sensor to the FireBeetle I2C pins (`SDA` / `SCL`). | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/prototyping-wires/dupont-compatible-and-jumper/dupont-jumper-wire-female-female-10cm-10-wires) |
| **18650 Battery Holder** | **1x 18650 Battery Holder** (leaf spring contacts, wires per cell) | Holds one 18650 Li-Ion cell. Bare wires — solder a JST-PH cable for plug connection. | [TinyTronics](https://www.tinytronics.nl/en/power/battery-holders-and-clips/18650/1x-18650-battery-holder-leaf-spring-contacts-wires-per-cell) |
| **18650 Battery Module** | **LilyGO TTGO T-Bat** (CN3065 solar charger) | 18650 holder with solar panel input, DC-DC converter, stable output voltage. €5.50. | [TinyTronics](https://www.tinytronics.nl/en/power/power-banks-and-battery-modules/lilygo-ttgo-t-bat-with-18650-battery-holder-cn3065) |

**Optional**

| Category | Recommended Product Reference | Key Specifications / Details | Tinytronics Link |
| --- | --- | --- | --- |
| **Crimping Tool** | **SN-2549 Crimping Tool** (28-18AWG, 0.1-1.0mm²) | Crimps JST-XH and Dupont connectors. Steel jaws with plastic handle. | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/tools/pliers-and-cutters/crimping-tools/sn-2549-crimping-tool-28-18awg-0.1-1.0mm2) |
| **JST-PH Connector Set** | **JST-PH Compatible Crimp Connector and Housing Set** | Crimp pins + housings (2.0mm pitch) for making custom JST-PH cables. | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible/jst-ph-compatible-crimp-connector-and-housing-set) |
| **Multimeter** | **UNI-T UT133B Multimeter** | Compact handheld multimeter with test probes included. €20.25. | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/tools/measuring/lcr-and-multimeters/uni-t-ut133b-multimeter) |

### Pico 2 WH

| # | Part | Price | Link |
|---|---|---|---|
| 1 | **TP4056 USB-C with protection** (5V 1A, DW01A) | €2.50 | [TinyTronics](https://www.tinytronics.nl/en/power/bms-and-chargers/li-ion-and-li-po/with-protection-circuit/tp4056-usb-c-li-ion-charger-1a-with-li-ion-protection-circuit) |
| 2 | **Solar Panel 5V 1A with USB** (275×170mm, monocrystalline, DC-DC converter) | €11.50 | [TinyTronics](https://www.tinytronics.nl/shop/en/power-supplies/solar-panels/solar-panel-with-dc-dc-converter-and-usb-5v-1a) |
| 3 | **PKCELL Li-Po 3.7V 2500mAh** (JST-PH, PCB protection) | €8.50 | [TinyTronics](https://www.tinytronics.nl/en/power/batteries/li-po/pkcell-li-po-battery-3.7v-2500mah-jst-ph-lp785060) |
| 4 | **2× HC-12 SI4438 433MHz** (wireless serial, UART, 1000m range) | €11.00 | [TinyTronics](https://www.tinytronics.nl/en/communication-and-signals/wireless/rf/modules/hc-12-si4438-wireless-serial-port-module-433mhz) |
| 5 | **2× Female header 20-pin** (2.54mm, socket for Pico) | €0.72 | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/female/20-pins-header-female) |
| 6 | **Perfboard double-sided 5×7cm** | €0.80 | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/prototyping-supplies/experiment-pcbs) |
| 7 | **c** (RP2350, no WiFi, headers not soldered) | €7.25 | [TinyTronics](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/others/raspberry-pi-pico-2-rp2350) |
| | **Subtotal** | **~€42.27** | |
| | **Shipping to Belgium** (PostNL) | **~€7** | |
| | **TinyTronics total** | **~€49** | |


## References

### Weather station projects

**Harald Kreuzer**

The blog of Harald contains a lot of valuable blog posts

- https://www.haraldkreuzer.net/en/news/build-guide-esp32-weather-station-and-environmental-monitor
- https://www.haraldkreuzer.net/en/news/firebeetle-2-esp32-c6-low-cost-sensor-esp32-weather-station

**Harald Schlangmann**

Code repository and circuits: https://github.com/HarrysLapTimer/WeatherStationOne

- https://www.printables.com/model/61709-weather-station-one-part-1-the-central-station
- https://www.printables.com/model/61719-weather-station-one-part-2-the-base-station
- https://www.printables.com/model/61766-weather-station-one-part-3-the-temperature-humidit
- https://www.printables.com/model/61720-weather-station-one-part-4-the-rain-gauge
- https://www.printables.com/model/61764-weather-station-one-part-5-the-wind-vane-and-anemo/files
- https://www.printables.com/model/61859-weather-station-one-part-7-optional-battery-pack
- https://www.printables.com/model/109429-weather-station-one-part-9-the-solar-panel-mount


### Pico 2

The following blog posts rely on Pico 2 but contains information applicable too to ESP32 !

https://stfn.pl/blog/34-pico-power-consumption-solar-panels/
https://stfn.pl/blog/02-pico-weather-station/
https://stfn.pl/blog/04-pico-weather-station2/
https://stfn.pl/blog/06-pico-aa-batteries/
https://stfn.pl/blog/09-pico-solar-panels/

**Arduino**

- Tutorial's bible:
    - FR: https://newbiely.fr/tutorials/arduino-uno-r4/
    - EN: https://newbiely.com/tutorials/arduino-uno-r4-tutorial
- Official doc: https://docs.arduino.cc/tutorials/ and https://projecthub.arduino.cc
- https://www.makerguides.com/arduino-weather-station-kit-dfrobot-tutorial/
- https://docs.arduino.cc/tutorials/uno-r4-minima/shield-guide/

**ESP32-C3:**
- [Espressif ESP32-C3 Product Page](https://www.espressif.com/en/products/socs/esp32-c3) — official specs, features, and technical documents
- [ESP32-C3-DevKitC-02 Getting Started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/hw-reference/esp32c3/user-guide-devkitc-02.html) — official development board guide with pinout diagram
- [Arduino-ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/) — Arduino framework for all ESP32 variants including C3
- [ESP32-C3 Arduino GPIO Reference](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html) — GPIO, ADC, I2C, and interrupt configuration
- [Random Nerd Tutorials — Getting Started with ESP32](https://randomnerdtutorials.com/getting-started-with-esp32/) — beginner-friendly tutorials for ESP32 boards

**Books**

| Title | Author | Publisher | Edition | Link |
|---|---|---|---|---|
| **L'électronique en pratique : 30 expériences ludiques** | Charles Platt | Eyrolles | 3rd (2022) | [Eyrolles](https://www.eyrolles.com/Informatique/Livre/l-electronique-en-pratique-9782416006999/) |
| **L'Électronique pour les Nuls** | Cathleen Shamieh | First Interactive | 4th (2024) | [Eyrolles](https://www.eyrolles.com/Sciences/Livre/electronique-pour-les-nuls-4e-edition-9782412102886/) |
| **Devenez makers : Guide pratique** | Paolo Aliverti | Eyrolles | | [Eyrolles](https://www.eyrolles.com/Informatique/Livre/devenez-maker--9782100762934/) |

**Note**: The list of the electronic components needed is listed [here](make-electronics-components.md)


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

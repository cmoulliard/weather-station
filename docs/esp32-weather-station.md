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
| **Environmental** | BME280 Sensor Module | Temperature (-40 to +85 °C, ±1.0 °C), Humidity (0–100% RH, ±3%), Barometric Pressure (300–1100 hPa, ±1 hPa). I2C / SPI, 3.3V compatible, STEMMA QT connector. | [TinyTronics](https://www.tinytronics.nl/en/sensors/temperature-air-humidity/bme280-digital-barometer-pressure-and-humidity-sensor-module) |
| **UV Index** | DFRobot Gravity LTR390-UV | UV Index (UVI), ambient light (ALS). I2C/UART, 3.3V. Mount with clear sky view (not inside Stevenson screen). | [TinyTronics](https://www.tinytronics.nl/en/sensors/optical/light-and-color/dfrobot-gravity-ltr390-uv-light-sensor-module-i2c-uart) |
| **Rain Gauge** | Tipping Bucket Rain Gauge (part of weather meter kit) | Reed switch pulse per tip → GPIO interrupt. One tip = 0.2794 mm of rain. RJ11 connector. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |
| **Wind Speed** | Anemometer (part of weather meter kit) | Reed switch, 1 pulse per rotation → GPIO interrupt. Speed = pulses/sec × 2.4 km/h. RJ11 connector. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |
| **Wind Direction** | Wind Vane (part of weather meter kit) | Resistor ladder producing variable voltage → ADC analog read. 16 directions. RJ11 connector. Requires 10 kΩ pull-down resistor. | [SparkFun SEN-15901](https://www.sparkfun.com/products/15901) |

### ESP32

![firebeetle-v2-solar-panels](https://www.haraldkreuzer.net/application/files/6017/1905/6635/Firebeetle_2_ESP32_C6_PXL_20240622_094806785.jpg)

| Category | Recommended Product Reference | Key Specifications / Details | Tinytronics Link |
| --- | --- | --- | --- |
| **Microcontroller** | DFRobot FireBeetle 2 ESP32-C6 - https://www.dfrobot.com/product-2771.html | RISC-V 160MHz, BLE 5.3 + Wi-Fi 6, onboard solar MPPT charge controller & JST-PH battery jack. | [View ESP32-C6 Boards](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/dfrobot-firebeetle-2-esp32-c6-development-board-seperate-headers) |
| **Rechargeable Battery** | Li-Ion Battery 3.6V (3350mAh – 6700mAh) | Panasonic 18650 Li-ion Battery - 3350mAh - 6.7A | [TinyTronics](https://www.tinytronics.nl/en/power/batteries/18650/panasonic-18650-li-ion-battery-3350mah-6.7a-ncr18650b) |
| **18650 Battery Holder** | 1x 18650 Battery Holder (leaf spring contacts, wires per cell) | Holds one 18650 Li-Ion cell. Bare wires — solder a JST-PH cable for plug connection. | [TinyTronics](https://www.tinytronics.nl/en/power/battery-holders-and-clips/18650/1x-18650-battery-holder-leaf-spring-contacts-wires-per-cell) |
| **18650 Battery Module** | LilyGO TTGO T-Bat (CN3065 solar charger) | 18650 holder with solar panel input, DC-DC converter, stable output voltage. €5.50. | [TinyTronics](https://www.tinytronics.nl/en/power/power-banks-and-battery-modules/lilygo-ttgo-t-bat-with-18650-battery-holder-cn3065) |
| **Rechargeable Battery** | Li-Polymer Battery 3.7V (1200mAh – 2000mAh) | Single-cell 3.7V Lithium-Polymer battery with standard JST-PH 2.0mm connector. | [TinyTronics](https://www.tinytronics.nl/en/power/batteries/li-po/pkcell-li-po-battery-3.7v-2000mah-jst-ph-lp803860) |
| **Solar Panel** | Mini Solar Panel 5V or 6V (1W – 2W) | Monocrystalline / Polycrystalline panel outputting 5V–6V DC (approx. 150mA–300mA in sun). | [TinyTronics](https://www.tinytronics.nl/en/power/solar-energy/solar-panels) |

**Optional**

| Category | Recommended Product Reference | Key Specifications / Details | Tinytronics Link |
| --- | --- | --- | --- |
| **Battery Connector** | JST-PH 2.0mm 2-Pin Cable | Plug extension/lead for solar panel or custom battery connections. | [TinyTronics](https://tinytronics.nl/shop/en/cables/jst/jst-2.0mm-connector-with-cable-ph2.0-2-pins) |
| **Sensor Wiring** | Dupont Female-to-Female Jumper Wires | 10cm or 20cm wires to connect the BME280 sensor to the FireBeetle I2C pins (`SDA` / `SCL`). | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/prototyping-wires/dupont-compatible-and-jumper/dupont-jumper-wire-female-female-10cm-10-wires) |
| **Crimping Tool** | SN-2549 Crimping Tool (28-18AWG, 0.1-1.0mm²) | Crimps JST-XH and Dupont connectors. Steel jaws with plastic handle. | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/tools/pliers-and-cutters/crimping-tools/sn-2549-crimping-tool-28-18awg-0.1-1.0mm2) |
| **JST-PH Connector Set** | JST-PH Compatible Crimp Connector and Housing Set | Crimp pins + housings (2.0mm pitch) for making custom JST-PH cables. | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible/jst-ph-compatible-crimp-connector-and-housing-set) |
| **Multimeter** | UNI-T UT139A Multimeter | Allow to test too batteries. €40. | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/tools/measuring/lcr-and-multimeters/uni-t-ut139a-multimeter) |

TODO: 
- Add alligator clips - https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/alligator-clip/goobay-alligator-clip-cable-set-50cm-10-pieces
- battery with loose wires: https://www.tinytronics.nl/en/power/battery-holders-and-clips/aa/2x-aa-battery-holder-with-loose-wires
- resistors: https://www.tinytronics.nl/en/components/resistors/resistors/10%CF%89-1m%CF%89-resistor-set

| Élément / Composant | Référence / Spécification Tinytronics | Lien Tinytronics | Usage & Remarques |
| --- | --- | --- | --- |
| **Set de résistances CMS 0805** | *1Ω-10MΩ 0805 SMD Resistor Set* | [Résistances CMS 0805](https://www.google.com/search?q=https://www.tinytronics.nl/en/components/resistors/smd-resistors) | Couvre l'ensemble des besoins en résistances CMS 0805 de signal et de polarisation. |
| **Résistances de puissance / Shunts** | Résistances traversantes (1/4W / 1W) ou CMS 1206/2512 | [Toutes les Résistances](https://www.tinytronics.nl/en/components/resistors) | Nécessaires uniquement pour les valeurs < 1 Ω ou les lignes dissipant plus de 125 mW. |
| **Set de condensateurs CMS (Optionnel)** | *0805 SMD Capacitor Set* (ex. 10 pF à 10 µF) | [Condensateurs CMS](https://www.tinytronics.nl/en/components/capacitors) | Complément idéal pour le filtrage et le découplage associés aux résistances. |
| **Accessoires de brasage CMS** | Flux de soudure, tresse à désouder et fil d'étain fin | [Matériel de Soudure](https://www.tinytronics.nl/en/tools-and-mounting/soldering) | Recommandés pour faciliter la manipulation et le brasage des boîtiers 0805. |

### Pico 2 WH

| # | Part | Price | Link |
|---|---|---|---|
| 1 | TP4056 USB-C with protection (5V 1A, DW01A) | €2.50 | [TinyTronics](https://www.tinytronics.nl/en/power/bms-and-chargers/li-ion-and-li-po/with-protection-circuit/tp4056-usb-c-li-ion-charger-1a-with-li-ion-protection-circuit) |
| 2 | Solar Panel 5V 1A with USB (275×170mm, monocrystalline, DC-DC converter) | €11.50 | [TinyTronics](https://www.tinytronics.nl/shop/en/power-supplies/solar-panels/solar-panel-with-dc-dc-converter-and-usb-5v-1a) |
| 3 | PKCELL Li-Po 3.7V 2500mAh (JST-PH, PCB protection) | €8.50 | [TinyTronics](https://www.tinytronics.nl/en/power/batteries/li-po/pkcell-li-po-battery-3.7v-2500mah-jst-ph-lp785060) |
| 4 | 2× HC-12 SI4438 433MHz (wireless serial, UART, 1000m range) | €11.00 | [TinyTronics](https://www.tinytronics.nl/en/communication-and-signals/wireless/rf/modules/hc-12-si4438-wireless-serial-port-module-433mhz) |
| 5 | 2× Female header 20-pin (2.54mm, socket for Pico) | €0.72 | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/pin-headers/female/20-pins-header-female) |
| 6 | Perfboard double-sided 5×7cm | €0.80 | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/prototyping-supplies/experiment-pcbs) |
| 7 | Pico 2 (RP2350, no WiFi, headers not soldered) | €7.25 | [TinyTronics](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/others/raspberry-pi-pico-2-rp2350) |
| | **Subtotal** | **~€42.27** | |
| | **Shipping to Belgium** (PostNL) | **~€7** | |
| | **TinyTronics total** | **~€49** | |


## References

### Books

| Title | Author | Publisher | Edition | Link |
|---|---|---|---|---|
| **L'électronique en pratique : 30 expériences ludiques** | Charles Platt | Eyrolles | 3rd (2022) | [Eyrolles](https://www.eyrolles.com/Informatique/Livre/l-electronique-en-pratique-9782416006999/) |
| **L'Électronique pour les Nuls** | Cathleen Shamieh | First Interactive | 4th (2024) | [Eyrolles](https://www.eyrolles.com/Sciences/Livre/electronique-pour-les-nuls-4e-edition-9782412102886/) |

**Note**: The list of the electronic components needed is listed [here](book-make-electronics-material.md)

### Weather station projects

**1. Harald Kreuzer**

The blog of Harald contains a lot of valuable blog posts

- https://www.haraldkreuzer.net/en/news/build-guide-esp32-weather-station-and-environmental-monitor
- https://www.haraldkreuzer.net/en/news/firebeetle-2-esp32-c6-low-cost-sensor-esp32-weather-station

**2. Harald Schlangmann**

Code repository and circuits: https://github.com/HarrysLapTimer/WeatherStationOne

- https://www.printables.com/model/61709-weather-station-one-part-1-the-central-station
- https://www.printables.com/model/61719-weather-station-one-part-2-the-base-station
- https://www.printables.com/model/61766-weather-station-one-part-3-the-temperature-humidit
- https://www.printables.com/model/61720-weather-station-one-part-4-the-rain-gauge
- https://www.printables.com/model/61764-weather-station-one-part-5-the-wind-vane-and-anemo/files
- https://www.printables.com/model/61859-weather-station-one-part-7-optional-battery-pack
- https://www.printables.com/model/109429-weather-station-one-part-9-the-solar-panel-mount

**3. Giovanni Aggiustatutto**

https://www.instructables.com/DIY-Weather-Station-With-ESP32/

**Pico 2**

The following blog posts rely on Pico 2 but contains information applicable too to ESP32 !

https://stfn.pl/blog/34-pico-power-consumption-solar-panels/
https://stfn.pl/blog/02-pico-weather-station/
https://stfn.pl/blog/04-pico-weather-station2/
https://stfn.pl/blog/06-pico-aa-batteries/
https://stfn.pl/blog/09-pico-solar-panels/

**ESP32-C6:**
- [Espressif ESP32-C6 Product Page](https://www.espressif.com/en/products/socs/esp32-c6) — official specs, features, and technical documents
- [ESP32-C6 Getting Started](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/index.html) — Official development board guide with pinout diagram

**Arduino**

- Tutorial's bible:
    - FR: https://newbiely.fr/tutorials/arduino-uno-r4/
    - EN: https://newbiely.com/tutorials/arduino-uno-r4-tutorial
- Official doc: https://docs.arduino.cc/tutorials/ and https://projecthub.arduino.cc
- https://www.makerguides.com/arduino-weather-station-kit-dfrobot-tutorial/
- https://docs.arduino.cc/tutorials/uno-r4-minima/shield-guide/


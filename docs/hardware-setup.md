# Hardware Selection, Wiring & Pi Configuration

## TODO

- Reference to be evaluated: https://esphome.io/components/esp32/
- Tuto/DIY to be read:
  - Pi + [Adafruit HAT Pi](https://www.adafruit.com/product/2310) + sensors: https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/0 
  - https://www.haraldkreuzer.net/en/news/esp32-weather-station-weather-forecast-wireless-sensors-and-air-quality-measurement
  - https://github.com/joelmartin11/Weather-Station
  - https://www.instructables.com/DIY-Weather-Station-With-ESP32/
  - https://www.makerguides.com/fr/simple-esp32-internet-weather-station-fr/
  - https://www.raspberrypi-france.fr/station-meteo-diy-comparatif-et-tutoriel/
- Vendeur: 
  - https://www.gotronic.fr/cat-cartes-esp32.htm
  - https://www.arduino.cc/
  - https://www.upesy.fr/
  - Weather board for Pi: https://thepihut.com/products/weather-board-for-raspberry-pi & tuto: https://bc-robotics.com/tutorials/raspberry-pi-weather-station-part-1/, https://bc-robotics.com/tutorials/raspberry-pi-weather-station-part-2/
  - Weather componants bc-robotics: https://bc-robotics.com/?product_cat=&s=weather&post_type=product
- Forum: https://forums.raspberrypi.com/viewforum.php?f=112&sid=e893b51c323da761164dc232a929f962

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

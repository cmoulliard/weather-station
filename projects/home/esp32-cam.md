## Bill of Materials (BOM) — Tinytronics

![esp32-cam.svg](img/esp32-cam.svg)

The following components are required to build the ESP32-CAM video IP camera with an outdoor/indoor protective enclosure:

### Updated Bill of Materials (Tinytronics Direct Links)

| Component | Description | Tinytronics Direct Product Page |
| --- | --- | --- |
| **ESP32-CAM Board** | ESP32-CAM WiFi + Bluetooth Board with OV2640 Camera Module (4MB PSRAM) | [tinytronics](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/esp32-cam-wifi-and-bluetooth-board-with-ov2640-camera) |
| **Programmer Baseboard** | ESP32-CAM-MB Micro USB Programmer Baseboard | [tinytronics](https://www.tinytronics.nl/en/development-boards/accessories/adapter-boards/esp32-cam-mb-programmer-shield) |
| **Power Supply** | 5V 2A Power Adapter with Micro USB Cable | [tinytronics](https://www.google.com/search?q=https://www.tinytronics.nl/en/power/power-supplies/5v/5v-power-adapter-2a-with-micro-usb-cable) |
| **Project Enclosure (Case)** | ABS Plastic Enclosure 100x60x25mm (Black) | [Printable](https://www.printables.com/model/75024-esp32-cam-case) |
| **MicroSD Card** | Kingston Canvas Select Plus 16GB MicroSDHC Class 10 | [tinytronics](https://www.tinytronics.nl/en/data-storage/sd-cards/sandisk-extreme-32gb-v30-uhs-i-u3-a1-microsdhc-card-with-sd-card-adapter) |

---

## Step-by-Step Implementation Guide

1. **Programmer & Power Wiring:** Required only if flashing via FTDI programmer instead of ESP32-CAM-MB.
   Connect the FTDI USB-to-Serial converter to the ESP32-CAM header:

* **FTDI VCC (5V)** to **ESP32 5V**
* **FTDI GND** to **ESP32 GND**
* **FTDI TX** to **ESP32 U0R (RX)**
* **FTDI RX** to **ESP32 U0T (TX)**
* **Boot Mode Jumper:** Connect **GPIO 0** to **GND** using a jumper wire to force the ESP32 into serial flashing mode.

2. **Arduino IDE Configuration:** Use the official Espressif board package.
1. Navigate to **Tools > Board > ESP32 Arduino > AI Thinker ESP32-CAM**.
2. Set the following board parameters in the **Tools** menu:
* **PSRAM:** `Enabled` *(Crucial for video processing)*
* **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)`
* **CPU Frequency:** `240MHz (WiFi/BT)`
* **Flash Frequency:** `80MHz`

3. **Configure the Sketch:** Official Espressif CameraWebServer sample.
1. Open **File > Examples > ESP32 > Camera > CameraWebServer**.
2. Enable the AI-Thinker pinout mapping by uncommenting:

```cpp
#define CAMERA_MODEL_AI_THINKER // Has PSRAM

```

3. Enter your Wi-Fi network credentials:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

```

4. **Flashing & System DDL:** Disconnect GPIO 0 jumper prior to normal boot.
1. Click **Upload**. When the terminal displays `Connecting...`, press the **RST** button on the back of the board if transfer does not start automatically.
2. Once uploaded, **disconnect the GPIO 0 to GND jumper**.
3. Open the Serial Monitor (**115200 baud**), then press **RST**. Note the assigned local IP address (e.g., `[http://192.168.1.45](http://192.168.1.45)`).


## Flash MicroPython firmware

1. Download the latest MicroPython firmware for ESP32-C3 from https://micropython.org/download/ESP32_GENERIC_C3/ and read from this page the installation instructions !
2. Plug in the ESP32-C3 Super Mini via USB-C. Hold the **BOOT** button while plugging in if the port doesn't appear.
3. Erase the flash:
   ```bash
   esptool --chip esp32c3 --port /dev/cu.usbmodem101 erase_flash
   ```
4. Flash MicroPython (replace the `.bin` filename with the one you downloaded):
   ```bash
   esptool --chip esp32c3 --port /dev/cu.usbmodem101 write_flash -z 0x0 firmware/ESP32_GENERIC_C3-20260824-v1.29.0.bin
   ```

Alternatively, use the following Rust tool - https://github.com/esp-rs/espflash/tree/main/espflash able to erase, flash but not only (see help):

```bash
// Fetch the latest firmware version locally
set ESP_VERSION 20260824-v1.29.0
wget https://micropython.org/resources/firmware/ESP32_GENERIC_C3-$ESP_VERSION.bin -O firmware/ESP32_GENERIC_C3-$ESP_VERSION.bin

// to flash
espflash write-bin --chip esp32c3 --port /dev/cu.usbmodem101 0x0 firmware/ESP32_GENERIC_C3-$ESP_VERSION.bin

// to erase
espflash erase-flash --chip esp32c3 --port /dev/cu.usbmodem101
```

**Note**: `espflash flash` expects an ELF binary (from a Rust/C ESP-IDF build), not a raw .bin. For MicroPython `.bin` firmware, use espflash write-bin which writes a raw binary to a specific flash address (0x0 for ESP32-C3 MicroPython).
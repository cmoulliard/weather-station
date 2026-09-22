# Tutorials

## Test internal led on/off

Create the file `blink.py` and add the code:

```python
from machine import Pin
import time

led = Pin(8, Pin.OUT)
print("Blink started")

while True:
    print(f"Led ON for 2s ...")
    led.value(0)   # LED ON (active LOW on this board)
    time.sleep(2)
    print(f"Led OFF for 2s ...")
    led.value(1)   # LED OFF
    time.sleep(2)
```
Next, run it using `REPL` as explained before and verify that the board led (color blue) is blinking.

## Push button

Schema: <img src="svg/push-button.svg" alt="push-button" style="width:50%; height:auto;">

Code:

```python
from machine import Pin
import time

PIN_BUTTON = 3

button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)

@micropython.native
def check_button():
    while True:
        if button.value() == 0:
            print("Button pressed!")
            time.sleep(0.3)

print("Waiting for to press the button...")
check_button()
```

## Red Led loop

```
  ESP32-C3 Super Mini

  GPIO3 (+) ────> 220Ω (red - red - black - black - brown) ────> Long pin (+) - LED - Small pin (-) ────> GND
```

Schema: <img src="svg/led.svg" alt="led-button" style="width:50%; height:auto;">

Code:
```python
from machine import Pin
import time

led = Pin(3, Pin.OUT)

while True:
    print("Change led value from 0 to 1 - ON ...")
    led.value(1)
    print("Sleep 3s ...")
    time.sleep(3)
    print("Change led value from 1 to 0 - OFF ...")
    led.value(0)
    print("Sleep 3s ...")
    time.sleep(3)
```

## Led and push button


TODO: To be reviewed !!

```
  ESP32-C3 Super Mini

  GPIO7 ──── 220Ω ──── LED(+) ──── GND

  GPIO3 ──── Button pin 1
             Button pin 2 ──────── GND  (button pulls to ground)
```

Code:

```python
from machine import Pin
import time

led = Pin(7, Pin.OUT)
button = Pin(3, Pin.IN, Pin.PULL_UP)

while True:
    if button.value() == 0:
        led.value(1)
        print("Button pressed — LED ON")
    else:
        led.value(0)
    time.sleep_ms(50)
```

## Raspberry Pi 3B+ — Shared setup

The Wi-Fi and BLE tutorials below both use a Raspberry Pi 3B+ as the infrastructure (Wi-Fi hotspot, MQTT broker, BLE gateway). Set it up once here.

### What you need

- Raspberry Pi 3B+ with Raspberry Pi OS
- Ethernet cable (for internet access while the Pi acts as a Wi-Fi hotspot)

### Set up the Wi-Fi hotspot (2.4 GHz) on Pi

```shell
sudo nmcli device wifi hotspot ifname wlan0 ssid MonReseauPi password MonMotDePasse123
# Force 2.4 GHz (band bg) as ESP32-C3 does not support 5 GHz (band a)
# Set the channel to "1" to avoid to conflict with another WiFi network
sudo nmcli connection modify Hotspot 802-11-wireless.band bg 802-11-wireless.channel 1
sudo nmcli connection down Hotspot && sudo nmcli connection up Hotspot
```

Verify it is active:

```shell
sudo nmcli connection show --active
NAME                UUID                                  TYPE      DEVICE
Hotspot             7b638336-3c1e-4665-a065-083367329e56  wifi      wlan0
Wired connection 1  4ac25893-4dd6-34ad-963d-ccc0aa6bc95d  ethernet  eth0
lo                  f7071334-c471-4d92-a811-88248f0c4f2b  loopback  lo
```

### Install and configure Mosquitto

```shell
sudo apt-get update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
```

Verify the broker is running:

```shell
sudo systemctl status mosquitto.service
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/usr/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since ...
```

### Installing umqtt.simple on the ESP32

Connect to the board's REPL and run:

```python
import mip
mip.install("umqtt.simple")
```

Or using `mpremote` from your computer:

```bash
mpremote mip install umqtt.simple
mpremote mip install aioble # For Bluetooth BLE
```

## Project structure — modular code

The Wi-Fi and BLE tutorials share a modular codebase under `wifi-bluetooth-mqtt/`. This avoids duplicating the MQTT logic across transports.

```
wifi-bluetooth-mqtt/
├── config.py            # Shared settings (SSID, password, broker IP, topic)
├── wifi.py              # Wi-Fi DHCP connection module
├── mqtt_client.py       # MQTT connect + publish loop (transport-agnostic)
├── ble.py               # BLE peripheral module (runs on ESP32)
├── main_wifi.py         # Entry point: Wi-Fi + MQTT
├── main_bluetooth.py    # Entry point: BLE peripheral
└── pi_ble_gateway.py    # BLE-to-MQTT gateway (runs on Pi)
```

### Copying files to the board

MicroPython imports modules from the board's root filesystem. Copy all `.py` files flat to the board:

```bash
for f in wifi-bluetooth-mqtt/*.py
    mpremote connect /dev/cu.usbmodem101 cp $f :(basename $f)
end
```

### Shared configuration — `config.py`

Edit this file to match your network before copying to the board:

```python
# Shared configuration
SSID = "MonReseauPi"
PASSWORD = "MonMotDePasse123"

# IP address of the Pi 3B+ running the MQTT Broker and HotSpot
MQTT_BROKER = "10.42.0.1"
TOPIC = "esp32c3/test"
CLIENT_ID = "ESP32C3_Client"

# Static IP config — set to None for DHCP (ESP32-C3 L2 link only works with DHCP)
STATIC_IP = None
```

### Shared MQTT module — `mqtt_client.py`

This module is used by Wi-Fi directly (ESP32 publishes to the broker). For BLE, the gateway on the Pi handles MQTT instead.

```python
from umqtt.simple import MQTTClient
import time


def publish_loop(broker, topic, client_id="ESP32C3_Client"):
    """Connect to MQTT broker and publish messages in a loop."""
    print("Connecting to MQTT broker ...")
    client = MQTTClient(client_id=client_id, server=broker)

    try:
        client.connect()
        print("MQTT connected to the local server !")

        counter = 0
        while True:
            message = f"Hello local MQTT ! Message numero {counter}"
            print("Send :", message)
            client.publish(topic, message)
            counter += 1
            time.sleep(5)

    except Exception as e:
        print("MQTT connection error:", e)
```

## Wi-Fi & MQTT

This tutorial connects the ESP32-C3 to a Wi-Fi network and publishes messages directly to the MQTT broker. No breadboard circuit needed — just the ESP32-C3 plugged into USB.

```
ESP32-C3  ──Wi-Fi──>  Pi (Mosquitto broker)
```

### Wi-Fi module — `wifi.py`

```python
import network
import time


def connect(ssid, password, timeout=90):
    """Connect to Wi-Fi via DHCP. Returns the WLAN interface."""
    wlan = network.WLAN(network.STA_IF)

    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)

    print("List the SSI Wifi networks available ...")
    for ap in wlan.scan():
        print(f'  SSID={ap[0]}  ch={ap[2]}  rssi={ap[3]}')

    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)

    print(f"Connecting to Wi-Fi '{ssid}' ...")
    try:
        wlan.connect(ssid, password)
    except OSError as e:
        print(f"Wi-Fi connect error: {e}")
        raise

    start = time.time()
    while not wlan.isconnected():
        elapsed = time.time() - start
        if elapsed > timeout:
            raise RuntimeError(f"Wi-Fi timeout after {timeout}s — status: {wlan.status()}")
        print(f"  waiting... ({int(elapsed)}s, status={wlan.status()})")
        time.sleep(2)

    print("Wi-Fi connected ! IP :", wlan.ifconfig())
    return wlan
```

> **Note:** The timeout is set to 90 seconds because the ESP32-C3's DHCP client can take up to 60 seconds to obtain an IP address from the Pi's hotspot.

### Entry point — `main_wifi.py`

```python
from config import SSID, PASSWORD, MQTT_BROKER, TOPIC, CLIENT_ID
from wifi import connect
from mqtt_client import publish_loop

connect(SSID, PASSWORD)
publish_loop(MQTT_BROKER, TOPIC, CLIENT_ID)
```

### Running

Copy the files to the board and run:

```bash
# Copy all modules to the board
for f in wifi-bluetooth-mqtt/*.py
    mpremote connect /dev/cu.usbmodem101 cp $f :(basename $f)
end

# Reset the board and run
mpremote connect /dev/cu.usbmodem101 reset
mpremote connect /dev/cu.usbmodem101 run wifi-bluetooth-mqtt/main_wifi.py
```

### What you should see

```shell
List the SSI Wifi networks available ...
  SSID=b'MonReseauPi'  ch=1  rssi=-71
Connecting to Wi-Fi 'MonReseauPi' ...
  waiting... (0s, status=1001)
  waiting... (2s, status=1001)
  ...
Wi-Fi connected ! IP : ('10.42.0.50', '255.255.255.0', '10.42.0.1', '10.42.0.1')
Connecting to MQTT broker ...
MQTT connected to the local server !
Send : Hello local MQTT ! Message numero 0
Send : Hello local MQTT ! Message numero 1
```

On the Pi, verify messages arrive:

```bash
mosquitto_sub -t "esp32c3/test"
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Wi-Fi timeout with status 201 | The AP is not responding — check that SSID and password are correct, and that the network is 2.4 GHz (not 5 GHz) |
| Wi-Fi timeout with status 202 | `ESP_IDF_GOT_IP_PENDING` — DHCP is slow. Restart the hotspot on the Pi: `sudo nmcli connection down Hotspot && sudo nmcli connection up Hotspot` |
| Wi-Fi timeout with status 3 | `STAT_NO_AP_FOUND` — the network is not visible. Check that the hotspot is running and within range |
| Wi-Fi timeout with status 2 | `STAT_WRONG_PASSWORD` — double-check the password string |
| `ImportError: no module named 'umqtt'` | Install the library: `import mip; mip.install("umqtt.simple")` |
| MQTT connection refused | Check that Mosquitto is running on the Pi (`systemctl status mosquitto`) and that the listener allows external connections |
| MQTT connection timeout | Verify the broker IP address matches the Pi's hotspot IP (default: `10.42.0.1` for NetworkManager hotspots) |

### What you learned

- **`network.WLAN(network.STA_IF)`** creates a Wi-Fi station (client) interface
- **`wlan.scan()`** lists nearby access points with signal strength (RSSI)
- **`wlan.status()`** returns numeric codes useful for debugging connection failures
- The ESP32-C3 only supports **2.4 GHz** Wi-Fi — 5 GHz networks are invisible to it
- The ESP32-C3's DHCP client can be slow (up to 60s) — use a generous timeout
- **`umqtt.simple`** is a lightweight MQTT client for MicroPython — `publish(topic, message)` sends data to the broker
- MQTT uses a **publish/subscribe** pattern: the ESP32 publishes, and any subscriber listening on the same topic receives the messages

## BLE & MQTT

This tutorial uses Bluetooth Low Energy (BLE) to send data from the ESP32-C3 to a Raspberry Pi, which acts as a gateway to the MQTT broker. Unlike Wi-Fi, the ESP32 does not connect to the broker directly — the Pi bridges BLE to MQTT.

```
ESP32-C3 (BLE peripheral)  ──BLE──>  Pi (BLE gateway)  ──MQTT──>  Mosquitto broker
```

### Prerequisites

- Completed the [Raspberry Pi shared setup](#raspberry-pi-3b--shared-setup) (Mosquitto must be running)
- The Pi's Bluetooth must be enabled (it is by default on Raspberry Pi OS)
- Python packages on the Pi: `bleak` and `paho-mqtt`

### Pi setup — install BLE gateway dependencies

```bash
pip3 install --break-system-packages bleak paho-mqtt
```

Or using a virtual environment:

```bash
python3 -m venv ~/ble-gateway
source ~/ble-gateway/bin/activate
pip install bleak paho-mqtt
```

### BLE peripheral module — `ble.py` (runs on ESP32)

The ESP32 acts as a BLE peripheral: it registers a GATT service with a notifiable characteristic, advertises itself as `ESP32C3-MQTT`, and sends messages to any connected central (the Pi).

```python
import bluetooth
import struct
import time

# Custom BLE service and characteristic UUIDs
_SERVICE_UUID = bluetooth.UUID("12345678-1234-1234-1234-123456789abc")
_CHAR_UUID = bluetooth.UUID("12345678-1234-1234-1234-123456789abd")

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)


def advertise(ble, name="ESP32C3-MQTT"):
    """Start BLE advertising with the given name."""
    payload = bytearray()
    # Flags: general discoverable + BR/EDR not supported
    payload += struct.pack("BBB", 2, 0x01, 0x06)
    # Complete local name
    name_bytes = name.encode()
    payload += struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes
    ble.gap_advertise(100_000, adv_data=payload)
    print(f"BLE advertising as '{name}' ...")


def start_peripheral(interval=5):
    """Start BLE peripheral that notifies connected centrals with messages."""
    ble = bluetooth.BLE()
    ble.active(True)
    time.sleep(1)

    # Register GATT service
    service = (
        _SERVICE_UUID,
        ((_CHAR_UUID, _FLAG_READ | _FLAG_NOTIFY),),
    )
    ((char_handle,),) = ble.gatts_register_services((service,))

    connected = False
    conn_handle = None

    def on_event(event, data):
        nonlocal connected, conn_handle
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle = data[0]
            connected = True
            print(f"BLE central connected (handle={conn_handle})")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            connected = False
            conn_handle = None
            print("BLE central disconnected")
            advertise(ble)

    ble.irq(on_event)
    advertise(ble)

    print("Waiting for BLE central to connect ...")
    counter = 0
    while True:
        if connected:
            message = f"Hello BLE MQTT ! Message numero {counter}"
            print("Send :", message)
            ble.gatts_write(char_handle, message.encode())
            ble.gatts_notify(conn_handle, char_handle)
            counter += 1
        time.sleep(interval)
```

### Entry point — `main_bluetooth.py` (runs on ESP32)

```python
from ble import start_peripheral

start_peripheral(interval=5)
```

### BLE-to-MQTT gateway — `pi_ble_gateway.py` (runs on Pi)

This Python script runs on the Pi. It scans for the ESP32 by name, connects via BLE, subscribes to GATT notifications, and publishes each received message to the Mosquitto broker.

```python
#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner
import paho.mqtt.client as mqtt

DEVICE_NAME = "ESP32C3-MQTT"
CHAR_UUID = "12345678-1234-1234-1234-123456789abd"

MQTT_BROKER = "127.0.0.1"
MQTT_TOPIC = "esp32c3/test"

BLE_CONNECT_TIMEOUT = 30.0
BLE_CONNECT_RETRIES = 3


async def main():
    # Scan for the ESP32-C3
    print(f"Scanning for BLE device '{DEVICE_NAME}' ...")
    device = None
    while device is None:
        devices = await BleakScanner.discover(timeout=5.0)
        for d in devices:
            if d.name and DEVICE_NAME in d.name:
                device = d
                break
        if device is None:
            print("  not found, retrying ...")

    print(f"Found {device.name} ({device.address})")

    # Connect to MQTT broker
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Pi_BLE_Gateway")
    mqtt_client.connect(MQTT_BROKER, 1883)
    mqtt_client.loop_start()
    print(f"MQTT connected to {MQTT_BROKER}")

    # Connect to BLE peripheral with retries
    def on_notify(sender, data):
        message = data.decode()
        print(f"BLE -> MQTT: {message}")
        mqtt_client.publish(MQTT_TOPIC, message)

    client = BleakClient(device.address, timeout=BLE_CONNECT_TIMEOUT)
    for attempt in range(1, BLE_CONNECT_RETRIES + 1):
        try:
            print(f"BLE connecting (attempt {attempt}/{BLE_CONNECT_RETRIES}, timeout={BLE_CONNECT_TIMEOUT}s) ...")
            await client.connect()
            print(f"BLE connected to {device.name}")
            break
        except (TimeoutError, asyncio.TimeoutError) as e:
            print(f"  connection timeout: {e}")
            if attempt == BLE_CONNECT_RETRIES:
                raise RuntimeError(f"Failed to connect after {BLE_CONNECT_RETRIES} attempts")
            await asyncio.sleep(2)

    try:
        await client.start_notify(CHAR_UUID, on_notify)
        print("Listening for BLE notifications (Ctrl+C to stop) ...")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        await client.stop_notify(CHAR_UUID)
        await client.disconnect()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Gateway stopped")


if __name__ == "__main__":
    asyncio.run(main())
```

### Running

**Step 1 — Copy the gateway script to the Pi:**

```bash
scp wifi-bluetooth-mqtt/pi_ble_gateway.py dabou@pi3-wifi:~/
```

**Step 2 — Copy files to the ESP32 and start the BLE peripheral:**

```bash
# Copy modules to the board
for f in wifi-bluetooth-mqtt/*.py
    mpremote connect /dev/cu.usbmodem101 cp $f :(basename $f)
end

# Reset and run
mpremote connect /dev/cu.usbmodem101 reset
mpremote connect /dev/cu.usbmodem101 run wifi-bluetooth-mqtt/main_bluetooth.py
```

**Step 3 — Start the gateway on the Pi:**

```bash
python3 ~/pi_ble_gateway.py
```

**Step 4 — Verify messages arrive via MQTT (on a second Pi terminal):**

```bash
mosquitto_sub -t "esp32c3/test"
```

### What you should see

On the ESP32 (your computer):

```
BLE advertising as 'ESP32C3-MQTT' ...
Waiting for BLE central to connect ...
BLE central connected (handle=1)
Send : Hello BLE MQTT ! Message numero 0
Send : Hello BLE MQTT ! Message numero 1
```

On the Pi (gateway):

```
Scanning for BLE device 'ESP32C3-MQTT' ...
Found ESP32C3-MQTT (18:8B:0E:93:18:8A)
MQTT connected to 127.0.0.1
BLE connecting (attempt 1/3, timeout=30.0s) ...
BLE connected to ESP32C3-MQTT
Listening for BLE notifications (Ctrl+C to stop) ...
BLE -> MQTT: Hello BLE MQTT ! Message numero 0
BLE -> MQTT: Hello BLE MQTT ! Message numero 1
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'bleak'` | Install on Pi: `pip3 install --break-system-packages bleak paho-mqtt` |
| `AttributeError: 'module' object has no attribute 'BLE'` | A file named `bluetooth.py` on the board is shadowing the built-in module. Delete it: `mpremote exec "import os; os.remove('bluetooth.py')"` and reset |
| BLE device not found | Make sure `main_bluetooth.py` is running on the ESP32 before starting the gateway |
| BLE connection timeout | Retry — the first connection can be slow. The gateway retries 3 times with a 30s timeout |
| MQTT connection refused on Pi | Check Mosquitto is running: `systemctl status mosquitto` |

### What you learned

- The ESP32-C3 supports **BLE** (Bluetooth Low Energy), not classic Bluetooth
- **BLE peripheral** — the ESP32 advertises a GATT service and sends data via notifications
- **BLE central** — the Pi connects to the peripheral and reads notifications
- Unlike Wi-Fi, BLE cannot talk to the MQTT broker directly — a **gateway** on the Pi bridges BLE to MQTT
- **`bleak`** is a Python BLE library for the Pi that works with BlueZ (the Linux Bluetooth stack)
- **`paho-mqtt`** is a Python MQTT client used by the gateway to publish messages to Mosquitto
- The same MQTT topic (`esp32c3/test`) is used by both transports, so subscribers see messages regardless of how they were sent
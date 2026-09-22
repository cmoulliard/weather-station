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

## Wi-Fi & MQTT

This tutorial connects the ESP32-C3 to a Wi-Fi network and publishes messages to an MQTT broker. No breadboard circuit needed — just the ESP32-C3 plugged into USB.

### Prerequisites

- A Wi-Fi network on the **2.4 GHz** band (the ESP32-C3 does not support 5 GHz)
- An MQTT broker (e.g., Mosquitto running on a Raspberry Pi 3B+)
- The `umqtt.simple` MicroPython library installed on the board

### Installing umqtt.simple (optional)

Connect to the board's REPL and run:

```python
import mip
mip.install("umqtt.simple")
```

Or using `mpremote` from your computer:

```bash
mpremote mip install umqtt.simple
```

### Raspberry Pi 3B+ — Wi-Fi hotspot & Mosquitto broker

<!-- TODO: Detail the steps to set up the Pi 3B+ as a Wi-Fi access point and MQTT broker -->

#### What you need

- Raspberry Pi 3B+ with Raspberry Pi OS
- Ethernet cable (for internet access while the Pi acts as a Wi-Fi hotspot)

#### Set up the Wi-Fi hotspot (2.4 GHz)

```shell
sudo nmcli device wifi hotspot ifname wlan0 ssid MonReseauPi password MonMotDePasse123
# Force 2.4 GHz (band bg) — the ESP32-C3 does not support 5 GHz (band a)
sudo nmcli connection modify Hotspot 802-11-wireless.band bg 802-11-wireless.channel 6
sudo nmcli connection down Hotspot && sudo nmcli connection up Hotspot
```

#### Install and configure Mosquitto

```shell
sudo apt-get update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service
```

#### Verify the broker is running

```shell
sudo systemctl status mosquitto.service
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/usr/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Sun 2026-09-20 15:06:40 CEST; 1 day 3h ago
 Invocation: 46c5bc7607fa4aa5821d68be8d6cd9dc
       Docs: man:mosquitto.conf(5)
...       
```

### Configuration for MicroPython

Edit the script constants to match your network:

```python
SSID = "MonReseauPi"           # Your Wi-Fi network name
PASSWORD = "MonMotDePasse123"   # Your Wi-Fi password
MQTT_BROKER = "10.42.0.1"      # IP of the Pi running Mosquitto
TOPIC = "esp32c3/test"          # MQTT topic to publish to
```

### Code (MicroPython)

```python
import network
import time
from umqtt.simple import MQTTClient

# 1. Configuration: Wi-Fi & MQTT
SSID = "MonReseauPi"
PASSWORD = "MonMotDePasse123"

# IP address of the Pi 3B+ running the MQTT Broker and HotSpot
MQTT_BROKER = "10.42.0.1"
TOPIC = "esp32c3/test"

# 2. Wi-Fi connection
wlan = network.WLAN(network.STA_IF)

# Reset the interface to clear any stale state
wlan.active(False)
time.sleep(1)
wlan.active(True)
time.sleep(1)

print("List the SSI Wifi networks available ...")
for ap in wlan.scan():
    print(f'  SSID={ap[0]}  ch={ap[2]}  rssi={ap[3]}')

# Disconnect if previously connected
if wlan.isconnected():
    wlan.disconnect()
    time.sleep(1)

print(f"Connecting to Wi-Fi '{SSID}' ...")
try:
    wlan.connect(SSID, PASSWORD)
except OSError as e:
    print(f"Wi-Fi connect error: {e}")
    print(f"  wlan status : {wlan.status()}")
    print(f"  wlan active : {wlan.active()}")
    print(f"  wlan config : {wlan.config('mac')}")
    raise

status_names = {
    0: "STAT_IDLE",
    1: "STAT_CONNECTING",
    2: "STAT_WRONG_PASSWORD",
    3: "STAT_NO_AP_FOUND",
    -1: "STAT_ASSOC_FAIL",
    -2: "STAT_BEACON_TIMEOUT",
    -3: "STAT_HANDSHAKE_TIMEOUT",
    200: "ESP_IDF_ASSOCIATING",
    201: "ESP_IDF_WAITING_AUTH — AP not responding (check SSID, password, 2.4GHz band)",
    202: "ESP_IDF_GOT_IP_PENDING",
    1000: "STAT_GOT_IP",
    1001: "STAT_GOT_IP",
}

timeout = 20
start = time.time()
while True:
    status = wlan.status()
    ip = wlan.ifconfig()[0]
    if (wlan.isconnected() or status in (1000, 1001)) and ip != "0.0.0.0":
        break
    elapsed = time.time() - start
    if elapsed > timeout:
        name = status_names.get(status, "UNKNOWN")
        raise RuntimeError(f"Wi-Fi timeout after {timeout}s — status: {status} ({name}), IP: {ip}")
    print(f"  waiting... ({int(elapsed)}s, status={status}, ip={ip})")
    time.sleep(2)
print("Wi-Fi connected ! IP :", wlan.ifconfig())

# 3. Broker MQTT connection
print("Connecting to MQTT broker ...")
client = MQTTClient(client_id="ESP32C3_Client", server=MQTT_BROKER)

try:
    client.connect()
    print("MQTT connected to the local server !")

    # 4. Loop to send data
    counter = 0
    while True:
        message = f"Hello local MQTT ! Message numero {counter}"
        print("Send :", message)

        client.publish(TOPIC, message)

        counter += 1
        time.sleep(5)

except Exception as e:
    print("MQTT connection error:", e)
```

### What you should see


```shell
mpremote run wifi-mqtt.py 
...
List the SSI Wifi networks available ...
  SSID=b'MonReseauPi'  ch=6  rssi=-45
Connecting to Wi-Fi 'MonReseauPi' ...
  waiting... (0s, status=1)
Wi-Fi connected ! IP : ('10.42.0.42', '255.255.255.0', '10.42.0.1', '10.42.0.1')
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
- **`umqtt.simple`** is a lightweight MQTT client for MicroPython — `publish(topic, message)` sends data to the broker
- MQTT uses a **publish/subscribe** pattern: the ESP32 publishes, and any subscriber listening on the same topic receives the messages
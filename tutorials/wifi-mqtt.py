# Wi-Fi & MQTT script for ESP32-C3
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

timeout = 20
start = time.time()
while not wlan.isconnected():
    elapsed = time.time() - start
    if elapsed > timeout:
        status = wlan.status()
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
        name = status_names.get(status, "UNKNOWN")
        raise RuntimeError(f"Wi-Fi timeout after {timeout}s — status: {status} ({name})")
    print(f"  waiting... ({int(elapsed)}s, status={wlan.status()})")
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
        time.sleep(5) # Wait 5s

except Exception as e:
    print("MQTT connection error:", e)
#!/usr/bin/env python3
"""
BLE-to-MQTT gateway — runs on the Raspberry Pi.

Connects to the ESP32-C3 BLE peripheral, subscribes to notifications,
and publishes each received message to the MQTT broker.

Prerequisites (install on Pi):
  sudo apt install -y python3-pip
  pip3 install bleak paho-mqtt
"""
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

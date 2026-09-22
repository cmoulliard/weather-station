#!/usr/bin/env python3
"""
BLE-to-MQTT gateway — runs on Raspberry Pi 3B+.

Connects to ESP32-C3 BLE peripheral, subscribes to notifications,
publishes received messages to MQTT, and handles auto-reconnection.
"""
import asyncio
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
import paho.mqtt.client as mqtt

DEVICE_NAME = "ESP32C3-MQTT"
CHAR_UUID = "12345678-1234-1234-1234-123456789abd"

MQTT_BROKER = "127.0.0.1"
MQTT_TOPIC = "esp32c3/test"

BLE_CONNECT_TIMEOUT = 10.0
BLE_CONNECT_RETRIES = 5


def create_mqtt_client():
    """Compatibility wrapper across paho-mqtt v1.x and v2.x."""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Pi_BLE_Gateway")
    except AttributeError:
        return mqtt.Client(client_id="Pi_BLE_Gateway")


async def connect_ble(device):
    """Attempt BLE connection passing BLEDevice object directly to BlueZ."""
    client = None
    for attempt in range(1, BLE_CONNECT_RETRIES + 1):
        try:
            # Pass BLEDevice object directly to prevent duplicate scanning on BlueZ
            client = BleakClient(device, timeout=BLE_CONNECT_TIMEOUT)
            print(f"BLE connecting (attempt {attempt}/{BLE_CONNECT_RETRIES}) ...")
            await client.connect()
            print(f"BLE connected to {device.name}")
            return client
        except (TimeoutError, asyncio.TimeoutError, BleakError) as e:
            print(f"  connection failed: {e}")
            if client and client.is_connected:
                await client.disconnect()
            if attempt == BLE_CONNECT_RETRIES:
                raise RuntimeError(f"Failed to connect after {BLE_CONNECT_RETRIES} attempts")

            print("  clearing BlueZ cache before retry ...")
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl", "remove", device.address,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            await asyncio.sleep(2)


async def main():
    # Connect to local MQTT broker
    mqtt_client = create_mqtt_client()
    mqtt_client.connect(MQTT_BROKER, 1883)
    mqtt_client.loop_start()
    print(f"MQTT connected to {MQTT_BROKER}")

    def on_notify(sender, data):
        message = data.decode('utf-8', errors='replace')
        print(f"BLE -> MQTT: {message}")
        mqtt_client.publish(MQTT_TOPIC, message)

    try:
        # Outer loop ensures automatic reconnection if connection drops
        while True:
            print(f"Scanning for BLE device '{DEVICE_NAME}' ...")
            device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=5.0)

            if not device:
                print("  device not found, retrying ...")
                await asyncio.sleep(2)
                continue

            print(f"Found {device.name} ({device.address})")
            client = None

            try:
                client = await connect_ble(device)
                await client.start_notify(CHAR_UUID, on_notify)
                print("Listening for BLE notifications ...")

                # Monitor connection state
                while client.is_connected:
                    await asyncio.sleep(1)

                print("BLE connection lost. Attempting reconnect ...")

            except Exception as e:
                print(f"BLE Session Error: {e}")

            finally:
                if client and client.is_connected:
                    try:
                        await client.stop_notify(CHAR_UUID)
                    except Exception:
                        pass
                    await client.disconnect()

            await asyncio.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping gateway ...")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Gateway stopped clean")


if __name__ == "__main__":
    asyncio.run(main())
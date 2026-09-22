#!/usr/bin/env python3
"""
BLE client for macOS — connects to the ESP32-C3 BLE peripheral
and prints received notifications.

Prerequisites:
  pip3 install bleak

Usage:
  python3 mac_ble_client.py
"""
import asyncio
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "ESP32"
SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
SENSOR_CHAR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
LED_CHAR_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214"


async def main():
    print(f"Scanning for BLE device '{DEVICE_NAME}' ...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)

    if device is None:
        print(f"Could not find '{DEVICE_NAME}'. Is the ESP32 running and advertising?")
        return

    print(f"Found {device.name} ({device.address})")

    def on_notify(_sender, data: bytearray):
        print(f"Sensor value: {data.decode()}")

    async with BleakClient(device) as client:
        print(f"Connected to {device.name}")

        value = await client.read_gatt_char(SENSOR_CHAR_UUID)
        print(f"Initial sensor value: {value.decode()}")

        await client.start_notify(SENSOR_CHAR_UUID, on_notify)
        print("Listening for sensor notifications (Ctrl+C to stop) ...")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass

        await client.stop_notify(SENSOR_CHAR_UUID)

    print("Disconnected")


if __name__ == "__main__":
    asyncio.run(main())

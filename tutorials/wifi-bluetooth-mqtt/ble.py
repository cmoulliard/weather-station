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

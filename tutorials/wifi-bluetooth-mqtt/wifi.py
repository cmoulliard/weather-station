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

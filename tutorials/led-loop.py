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
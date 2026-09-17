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
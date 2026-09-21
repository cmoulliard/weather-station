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
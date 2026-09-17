from machine import Pin
import time

PIN_BUTTON = 3
PIN_LED = 7

button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)
led = Pin(PIN_LED, Pin.OUT)

print(f"Led PIN: {PIN_LED} and Button PIN: {PIN_BUTTON} configured.")

while True:
    print("Let's wait till we press on the button...")

    val = button.value()
    print(f"Button raw value: {val}")

    # Button reads 0 (LOW) when pressed
    if button.value() == 0:
        print("Button pressed ...")
        led.value(1)  # Turn LED ON
    else:
        print("Button not pressed ...")
        led.value(0)  # Turn LED OFF
    time.sleep(5)
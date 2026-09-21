# Tutorials

## Test internal led on/off

Create the file `blink.py` and add the code:

```python
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
```
Next, run it using `REPL` as explained before and verify that the board led (color blue) is blinking.

## Push button

Schema: <img src="svg/push-button.svg" alt="push-button" style="width:50%; height:auto;">

Code:

```python
from machine import Pin
import time

PIN_BUTTON = 3

button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)

@micropython.native
def check_button():
    while True:
        if button.value() == 0:
            print("Button pressed!")
            time.sleep(0.3)

print("Waiting for to press the button...")
check_button()
```

## Red Led loop

```
  ESP32-C3 Super Mini

  GPIO3 (+) ────> 220Ω (red - red - black - black - brown) ────> Long pin (+) - LED - Small pin (-) ────> GND
```

Schema: <img src="svg/led.svg" alt="led-button" style="width:50%; height:auto;">

Code:
```python
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
```

## Led and push button


TODO: To be reviewed !!

```
  ESP32-C3 Super Mini

  GPIO7 ──── 220Ω ──── LED(+) ──── GND

  GPIO3 ──── Button pin 1
             Button pin 2 ──────── GND  (button pulls to ground)
```

Code:

```python
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
```
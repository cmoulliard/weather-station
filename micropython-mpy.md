## Optimization: native build

Read: https://www.luisllamas.es/en/micropython-optimization-native-viper/

- To create bytecode of some functions, add `@micropython.native` before a function of a Python file:

```python
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
- Next, compile it to create a `mpy` file and deploy it

```bash
# For ESP32-C3 (RISC-V)
mpy-cross -march=rv32imc your_file.py
```

This produces `your_file.mpy` in the same directory.

- Deploy `.mpy` to the device

```bash
# Upload the compiled file
mpremote connect /dev/cu.usbmodem101 cp your_file.mpy :your_file.mpy

# For libraries, put them in /lib
mpremote connect /dev/cu.usbmodem101 mkdir :lib
mpremote connect /dev/cu.usbmodem101 cp my_module.mpy :lib/my_module.mpy
```

MicroPython automatically prefers `.mpy` over `.py` if both exist with the same name.

### Version compatibility

**Important:** the `mpy-cross` version must match the MicroPython firmware version on your device. Check with:

```bash
# On your computer
mpy-cross --version
# Example output: MicroPython v1.24.1 mpy-cross emitting mpy v6.3

# On the device (via REPL)
mpremote connect /dev/cu.usbmodem101 exec "import sys; print(sys.version, sys.implementation)"
```

If there's a mismatch, install a specific version:

```bash
uv install tool mpy-cross==1.24.1
```

### Architecture reference

| Board                      | `-march=` flag |
| -------------------------- | -------------- |
| ESP32                      | `xtensawin`    |
| ESP32-S2                   | `xtensawin`    |
| ESP32-S3                   | `xtensawin`    |
| **ESP32-C3**               | **`rv32imc`**  |
| ESP32-C6                   | `rv32imc`      |
| Raspberry Pi Pico (RP2040) | `armv6m`       |
| Pico 2 (RP2350)            | `armv6m`       |

### Optimization levels

```bash
# Default (no optimization)
mpy-cross -march=rv32imc main.py

# Optimize (remove assert statements, set __debug__ = False)
mpy-cross -O1 -march=rv32imc main.py

# More aggressive (also remove docstrings)
mpy-cross -O2 -march=rv32imc main.py
```

### Full example workflow

```bash
# Compile all .py files in your project
for f in boot.py main.py config.py; do
    mpy-cross -march=rv32imc -O1 "$f"
done

# Upload all .mpy files
PORT=/dev/cu.usbmodem101
for f in *.mpy; do
    mpremote connect $PORT cp "$f" :"$f"
done

# Reset the device to run the new code
mpremote connect $PORT reset
```


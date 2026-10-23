# Wind Vane (Wind Direction)

## Overview

The wind vane measures wind direction using an **AS5600 magnetic rotary encoder**. A diametrically magnetized magnet is mounted on the rotating shaft of the vane. The AS5600, fixed below the magnet, reads the angular position over I2C with 12-bit resolution (0.088° per step), providing a continuous 0-360° direction reading.

## Diagram

```
        WIND VANE (wind direction)

                     Fin / Tail
                    ╱       ╲
          ─────────╱─────────╲─────────
                  │           │
                  │  Rotating │
                  │   shaft   │
             ┌────┴───────────┴────┐
             │    ┌───────────┐    │
             │    │  Magnet   │    │    ← diametric magnet glued under fin
             │    │  (⊕   ⊖)  │    │
             │    └─────┬─────┘    │
             │     ~~~~ │ ~~~~     │    ← air gap ~1-2mm
             │    ┌─────┴─────┐    │
             │    │  AS5600   │    │    ← fixed sensor, reads angle 0-360°
             │    │  (I²C)    │    │
             │    └───────────┘    │
             │   Fixed mount       │
             └─────────┬───────────┘
                       │
                  ═══ Mast ═══
```

## Wiring to ESP32

```
        AS5600                        ESP32
        ┌──────────┐                ┌──────────┐
        │ VCC  ────┼────────────────┤ 3.3V     │
        │ GND  ────┼────────────────┤ GND      │
        │ SDA  ────┼────────────────┤ GPIO 21  │  (I²C data)
        │ SCL  ────┼────────────────┤ GPIO 22  │  (I²C clock)
        └──────────┘                └──────────┘
```

> **Note:** The AS5600 has a fixed I2C address of `0x36`. If you need multiple I2C devices, they can share the same bus as long as addresses don't conflict.

## Bill of Materials

| # | Component | Specification | Qty | Link |
|---|-----------|---------------|-----|------|
| 1 | AS5600 magnetic angle sensor module | 12-bit resolution, I2C, 3.3-5V | 1 | [TinyTronics](https://www.tinytronics.nl/en/sensors/magnetic-field/as5600-magnetic-angle-sensor-encoder-module) |
| 2 | Diametric magnet | 6mm diameter disc, diametrically magnetized (N-S across the diameter) | 1 | Usually included with AS5600 module |
| 3 | Fin / tail | Flat vane to catch the wind (3D printed or sheet metal) | 1 | |
| 4 | Counterweight | Balances the fin on the opposite side (optional) | 1 | |
| 5 | Shaft + bearing | Low-friction rotating shaft aligned with AS5600 center | 1 | |
| 6 | Housing | Weatherproof enclosure for AS5600 and wiring | 1 | |

## How It Works

1. Wind pushes the fin, rotating the shaft to align with the wind direction
2. The diametric magnet rotates with the shaft
3. The AS5600 detects the magnet's angular position via its internal Hall sensors
4. The ESP32 reads the angle over I2C (value 0-4095 maps to 0-360°)
5. The raw angle is mapped to a compass direction (N, NE, E, SE, S, SW, W, NW)

### Magnet Placement

The magnet must be:
- **Diametrically magnetized** (N and S poles on opposite sides of the disc, not top/bottom)
- Centered directly above the AS5600 chip
- At a distance of **1-2mm** (air gap) from the sensor surface

## ESP32 Code Snippet

```cpp
#include <Wire.h>

#define AS5600_ADDR 0x36
#define RAW_ANGLE_REG 0x0C

float readWindDirection() {
    Wire.beginTransmission(AS5600_ADDR);
    Wire.write(RAW_ANGLE_REG);
    Wire.endTransmission(false);
    Wire.requestFrom(AS5600_ADDR, 2);

    uint16_t raw = (Wire.read() << 8) | Wire.read();
    raw &= 0x0FFF; // 12-bit value
    return raw * 360.0 / 4096.0;
}

const char* directionToCompass(float degrees) {
    const char* directions[] = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
    int index = ((int)(degrees + 22.5) % 360) / 45;
    return directions[index];
}
```
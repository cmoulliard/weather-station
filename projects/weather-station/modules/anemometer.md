# Anemometer (Wind Speed)

## Overview

The anemometer measures wind speed by counting the revolutions of rotating cups. A magnet attached to the rotating shaft passes in front of a fixed **A3144 Hall effect sensor**, generating one interrupt pulse per revolution. The ESP32 counts pulses per second and converts them to wind speed.

## Diagram

```
        ANEMOMETER (wind speed)

        Top view:
               ╭───╮
              ╱     ╲
          ╭──╯   ●   ╰──╮       ● = rotating shaft
          │    cup      │
          ╰──╮       ╭──╯
              ╲     ╱
               ╰───╯

        Side view (cross section):

            ╭─╮  Shaft   ╭─╮
            │U│────┼─────│U│     ← 3 cups on cross arms
            ╰─╯    │     ╰─╯
                   │
              ┌────┴────┐
              │ Magnet  │        ← magnet glued under rotating shaft
              │  (N/S)  │
              └────┬────┘
               ~~~~│~~~~         ← passes in front of sensor
              ┌────┴────┐
              │  A3144  │        ← fixed sensor, 1 pulse per revolution
              └─────────┘
                   │
              ═══ Mast ═══
```

## Wiring to ESP32

```
        A3144                       ESP32
        ┌──────────┐                ┌──────────┐
        │ VCC  ────┼────────────────┤ 3.3V     │
        │ GND  ────┼────────────────┤ GND      │
        │ OUT  ────┼──── R 10kΩ ────┤ GPIO 34  │  (interrupt)
        └──────────┘   (pull-up)    └──────────┘
```

## Bill of Materials

| # | Component | Specification | Qty | Link |
|---|-----------|---------------|-----|------|
| 1 | A3144 Hall effect switch | Digital output, active low, 3.3-5V | 1 | [TinyTronics](https://www.tinytronics.nl/en/sensors/magnetic-field/3144-hall-effect-switch) |
| 2 | Diametric magnet | Small N/S disc magnet (~6mm) | 1 | |
| 3 | 10kΩ resistor | Pull-up resistor for A3144 output | 1 | |
| 4 | Cups | 3x hemispherical cups (3D printed or ping pong balls) | 3 | |
| 5 | Cross arms | 3x rods connecting cups to shaft (~10cm each) | 3 | |
| 6 | Shaft + bearing | Rotating shaft with low-friction bearing | 1 | |
| 7 | Housing | Weatherproof enclosure for sensor and wiring | 1 | |

## How It Works

1. Wind pushes the cups, causing the shaft to rotate
2. The magnet attached to the shaft passes in front of the A3144 once per revolution
3. The A3144 pulls its output LOW each time the magnet is near, generating an interrupt on the ESP32
4. The ESP32 counts pulses over a time window (e.g. 1 second)
5. Wind speed is calculated: `speed = pulses_per_second × calibration_factor`

A typical calibration factor is **2.4 km/h per pulse per second**, but this depends on the cup geometry and arm length. Calibrate against a known reference anemometer for best accuracy.

## ESP32 Code Snippet

```cpp
#define ANEMOMETER_PIN 34

volatile unsigned long pulseCount = 0;

void IRAM_ATTR anemometerISR() {
    pulseCount++;
}

void setup() {
    pinMode(ANEMOMETER_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ANEMOMETER_PIN), anemometerISR, FALLING);
}

float getWindSpeedKmh(unsigned long intervalMs) {
    unsigned long count = pulseCount;
    pulseCount = 0;
    float pulsesPerSecond = (float)count / (intervalMs / 1000.0);
    return pulsesPerSecond * 2.4; // calibration factor
}
```
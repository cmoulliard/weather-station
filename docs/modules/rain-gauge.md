# Rain Gauge (Tipping Bucket Pluviometer)

## Overview

The rain gauge measures rainfall using a **tipping bucket mechanism**. Rainwater is collected by a funnel and directed into one of two small buckets mounted on a seesaw pivot. When one bucket fills to a calibrated volume, it tips over, emptying itself and moving the other bucket into position. A magnet attached to the tipping mechanism passes in front of a fixed **A3144 Hall effect sensor** on each tip, generating an interrupt pulse counted by the ESP32.

## Diagram

```
        RAIN GAUGE (tipping bucket)

        Side view (cross section):

             Rain  ↓ ↓ ↓ ↓ ↓
            ╲                   ╱
             ╲     Funnel      ╱
              ╲               ╱
               ╲             ╱
                ╲           ╱
                 ╲─────────╱
                   │     │
                   │spout│
                   └──┬──┘
                      │ water
                      ▼
            ┌─────────────────────┐
            │                     │
            │   Tipping buckets   │
            │                     │
            │    ╭──┬──╮ pivot    │
            │   ╱ A │   ╲         │   ← State 1: bucket A fills
            │  ╱~~~~│    ╲        │
            │ ╱water│     ╲       │
            │╱______│______╲      │
            │       ●  (pivot)    │   ← tipping axis
            │                     │
            │  When A is full,    │
            │  it tips over:      │
            │                     │
            │       ╭──┬──╮      │
            │      ╱   │ B╲     │   ← State 2: bucket B fills
            │     ╱    │~~~╲    │     bucket A empties by gravity
            │    ╱     │wtr ╲   │
            │   ╱______│_____╲  │
            │          ●         │
            │                     │
            │  ┌───────┐         │
            │  │Magnet │ ←─────── magnet glued under one bucket
            │  └───┬───┘         │
            │  ~~~~│~~~~         │
            │  ┌───┴───┐         │
            │  │ A3144 │ ←─────── fixed sensor on chassis
            │  └───────┘         │
            │         ↓          │
            └──── water drains ──┘


        Tipping mechanism detail (front view):

               water ↓
            ┌─────────┐
            │         │
        ╔═══╧════╤════╧═══╗
        ║ Bucket │ Bucket ║
        ║   A    ● pivot B ║      ← tips around pivot ●
        ╚════════╧════════╝
                 │
            ┌────┴────┐
            │ [N  S]  │           ← magnet
            └────┬────┘
            ~~~~~│~~~~~
            ┌────┴────┐
            │  A3144  │           ← detects each tip
            └─────────┘
```

## Wiring to ESP32

```
        A3144                       ESP32
        ┌──────────┐                ┌──────────┐
        │ VCC  ────┼────────────────┤ 3.3V     │
        │ GND  ────┼────────────────┤ GND      │
        │ OUT  ────┼──── R 10kΩ ────┤ GPIO 35  │  (interrupt)
        └──────────┘   (pull-up)    └──────────┘
```

## Bill of Materials

| # | Component | Specification | Qty | Link |
|---|-----------|---------------|-----|------|
| 1 | A3144 Hall effect switch | Digital output, active low, 3.3-5V | 1 | [TinyTronics](https://www.tinytronics.nl/en/sensors/magnetic-field/3144-hall-effect-switch) |
| 2 | Small disc magnet | Neodymium, ~6mm diameter | 1 | |
| 3 | 10kΩ resistor | Pull-up resistor for A3144 output | 1 | |
| 4 | Funnel | ~100mm diameter opening, smooth interior | 1 | |
| 5 | Tipping bucket assembly | Two small buckets on a seesaw pivot (3D printed) | 1 | |
| 6 | Pivot axle | Low-friction pin or small bearing | 1 | |
| 7 | Enclosure | Weatherproof housing with drain holes at bottom | 1 | |

## How It Works

1. Rain falls into the funnel, which concentrates water into a narrow spout
2. Water drips into one of the two buckets (bucket A)
3. When bucket A reaches a calibrated volume, gravity tips the seesaw
4. Bucket A empties, bucket B moves into position to collect water
5. The magnet attached to the bucket passes in front of the A3144 sensor
6. The A3144 generates an interrupt on the ESP32
7. Each tip represents a known volume of rainfall

### Calibration

| Parameter | Typical Value |
|-----------|---------------|
| Volume per tip | ~4.73 ml |
| Rainfall per tip | **0.2794 mm** (for a standard funnel area) |
| Formula | `total_rainfall_mm = tip_count × 0.2794` |
| Intensity | `mm/h = tips_per_hour × 0.2794` |

The rainfall per tip depends on the funnel collection area: `rainfall_mm = volume_ml / funnel_area_cm² × 10`

## ESP32 Code Snippet

```cpp
#define RAIN_GAUGE_PIN 35
#define MM_PER_TIP 0.2794

volatile unsigned long tipCount = 0;
volatile unsigned long lastTipTime = 0;

void IRAM_ATTR rainGaugeISR() {
    unsigned long now = millis();
    if (now - lastTipTime > 200) { // 200ms debounce
        tipCount++;
        lastTipTime = now;
    }
}

void setup() {
    pinMode(RAIN_GAUGE_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(RAIN_GAUGE_PIN), rainGaugeISR, FALLING);
}

float getTotalRainfallMm() {
    return tipCount * MM_PER_TIP;
}

void resetRainfall() {
    tipCount = 0;
}
```

> **Important:** The ISR includes a 200ms debounce to prevent false counts from mechanical bounce when the bucket tips.
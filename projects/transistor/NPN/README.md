# NPN transistor as a switch

A small current into the **base** of an NPN transistor lets a much larger current flow from the
**collector** to the **emitter**. In this circuit, a push button sends current into the base, and the
transistor turns an LED on.

![Breadboard layout](npn-switch-breadboard.png)

## Schematic

```
+9 V ── 1 kΩ ── LED (+ → −) ── C
                               NPN
+9 V ── button ── 10 kΩ ────── B
                               E ── GND
```

## Parts

| Qty | Part | Notes |
|---|---|---|
| 1 | Half breadboard (30 columns) | |
| 1 | NPN transistor, TO-92 | S8050 (Freenove kit), 2N2222, PN2222, BC547… |
| 1 | Push button 6×6 | |
| 1 | Resistor 10 kΩ (brown-black-orange) | base resistor |
| 1 | Resistor 1 kΩ (brown-black-red) | LED current limit |
| 1 | Red LED | |
| 1 | 9 V battery + snap cable | |
| 4 | Jumper wires | |

## Build steps

The rows are named `a`–`j` and the columns `1`–`30`. Only the **bottom half** (rows f–j) and the
**bottom rails** (`b+` / `b−`) are used.

1. **Transistor**: flat face towards you, legs down. Put E, B and C in **f8, f9 and f10**. The body
   sits over the center channel.
2. **Push button**: put it across the channel, with its legs in columns **3 and 5** (rows e and f).
3. **Base resistor 10 kΩ**: from **h5** to **h9**, which links column 5 (button) to column 9 (base).
4. **LED**: put the anode (+, the long leg) in **j12** and the cathode (−, the flat side) in **j13**.
5. **LED resistor 1 kΩ**: from **h12** to **h16**.
6. **Wires**:
   - red: **j3 → b+** (+9 V to the button)
   - red: **j16 → b+** (+9 V to the 1 kΩ)
   - orange: **g10 → g13** (collector to the LED cathode)
   - black: **j8 → b−** (emitter to GND)
7. **Battery last**: connect + to the `b+` rail (column 1) and − to the `b−` rail (column 2).

**Test:** with the button released, the LED is off. With the button pressed, the LED turns on.

## How it works

| | Button released | Button pressed |
|---|---|---|
| Base current | 0 | (9 − 0.7) / 10 kΩ ≈ **0.8 mA** |
| Transistor | OFF (cutoff) | ON (saturation) |
| LED current | 0 | (9 − 2 − 0.1) / 1 kΩ ≈ **7 mA** |

The transistor needs a base current of about 7 mA / β. β is 100 or more for these transistors, so
0.8 mA is enough to switch it fully on (saturation).

## Common mistakes

- **Wrong pinout:** E-B-C is the usual order for S8050 and 2N2222 parts, but a **BC547 is C-B-E**
  (turn it 180°). Always check the datasheet for your part.
- **No base resistor:** too much current flows into the base and destroys the transistor.
- **LED backwards:** the long leg (+) goes to the resistor and the short leg (−) to the collector.
- **Hot transistor:** it is not fully on (saturated). Use a smaller base resistor.

## Next steps

- Replace the button with an Arduino or ESP32 GPIO pin: 3.3 V or 5 V → 1 kΩ to 10 kΩ → base.
- Replace the LED with a relay, a buzzer or a motor. Add a flyback diode on an inductive load.
- See [`../../photoresistor`](../../photoresistor): the same transistor, driven by a light sensor.

## Files

| File | Content |
|---|---|
| `gen_breadboard.py` | Generates the diagram from the parts in [`../../drawio-lib`](../../drawio-lib) |
| `npn-switch-breadboard.drawio` | Diagram you can edit in draw.io |
| `npn-switch-breadboard.png` | Image export |

To regenerate the diagram and the image:

```sh
python3 gen_breadboard.py
drawio -x -f png -s 1 -b 10 -o npn-switch-breadboard.png npn-switch-breadboard.drawio
```

## References

- [Arduino Slovakia — NPN transistor as a switch](https://www.arduinoslovakia.eu/blog/2019/7/pre-zaciatocnikov--npn-tranzistor-ako-spinac?lang=en): button + LED, no microcontroller
- [All About Circuits — Bipolar Transistor as a Switch (lab)](https://www.allaboutcircuits.com/textbook/experiments/chpt-5/transistor-as-a-switch/)
- [DIY Engineers — How to use the 2N2222 transistor (NPN)](https://www.diyengineers.com/2020/12/17/2n2222-transistor-npn/)
- [Nuts & Volts — How to Use a Transistor as a Switch](https://www.nutsvolts.com/magazine/article/may2015_Secura): how to calculate the resistors
- [Instructables — Use an NPN Transistor as a Switch](https://www.instructables.com/Use-an-NPN-Transistor-as-a-Switch/)
- [YouTube — How to Use an NPN Transistor to Switch on an LED](https://www.youtube.com/watch?v=8ZEQEV-Stkc)

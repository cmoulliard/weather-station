# LED Battery Circuit — KiCad 10 Project

Simple series circuit: **9 V battery → current-limiting resistor → 5 mm red LED → GND**.

---

## Project files

| File | Description |
|------|-------------|
| `led-battery-circuit.kicad_pro` | KiCad 10 project file |
| `led-battery-circuit.kicad_sch` | Schematic (Battery + R1 + D1) |
| `led-battery-circuit.kicad_pcb` | PCB layout (60 × 40 mm, all THT) |
| `led_circuit_calculator.py`     | Python script — measures V, I, P and validates R |

---

## Circuit topology

```
BT1 (+) ──────┤ R1 ├──────┤ D1 ├────── GND ──── BT1 (-)
   9 V        330 Ω       LED Red
                          Vf = 2 V
                          If_max = 25 mA
```

### Components

| Ref | Value | Description |
|-----|-------|-------------|
| BT1 | 9 V   | 9 V block battery (Keystone 1042 holder) |
| R1  | 330 Ω **½ W** | Current-limiting resistor — see power note below |
| D1  | LED Red 5 mm | Vf = 2.0 V, If_typ = 20 mA, If_max = 25 mA |

---

## Electrical calculations

```
V_R   = Vbat − Vf        = 9 − 2        = 7.0 V
I     = V_R / R           = 7.0 / 330    ≈ 21.2 mA
P_R1  = V_R × I           = 7.0 × 0.0212 ≈ 148 mW
R_min = V_R / If_max      = 7.0 / 0.025  = 280 Ω
R_ideal = V_R / If_typ    = 7.0 / 0.020  = 350 Ω  → 360 Ω E24
```

### ⚠ Power note — resistor wattage

With 9 V and 330 Ω, the resistor dissipates **148 mW**.  
A standard ¼ W (250 mW) resistor should be derated to 50 % → max 125 mW.  
**Always use a ½ W rated resistor for R1 with this circuit.**

Alternatively use **470 Ω ¼ W** → I = 14.9 mA, P = 104 mW ✅

---

## Python calculator

```bash
# Default values (330 Ω, ½ W rating)
python led_circuit_calculator.py --r 330 --r-watt 0.5

# Safer ¼ W option
python led_circuit_calculator.py --r 470

# Custom LED and supply
python led_circuit_calculator.py \
  --vbat 5 --vf 1.8 --if-typ 0.010 --if-max 0.020 --r 150

# Full help
python led_circuit_calculator.py --help
```

The script outputs:

- Voltage across R1 (`V_R`)
- Circuit current (`I`)
- Power dissipated in R1 (`P_R1`)
- Ideal and minimum R values
- Three safety checks (min current, max current, resistor power derate)
- E24 nearest standard value suggestion
- Exit code `0` = PASS, `1` = FAIL

---

## PCB layout

Board size: **60 × 40 mm**  
All components through-hole (THT).  
Three nets: `VBAT_POS`, `V_AFTER_R`, `GND`.

```
 BT1          R1          D1
(9V batt)  (330Ω ½W)   (LED Red)
  @ (10,20)  @ (30,20)   @ (48,20)
```

---

## Opening in KiCad

1. Open **KiCad 10**.
2. **File → Open Project** → select `led-battery-circuit.kicad_pro`.
3. Open the schematic editor for `led-battery-circuit.kicad_sch`.
4. Open the PCB editor for `led-battery-circuit.kicad_pcb`.

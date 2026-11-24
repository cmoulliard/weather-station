# Solar lamp PCB (YX8018) - KiCad project

Single-sided board, 38 × 27 mm, through-hole parts. Traces are on the bottom copper (`B.Cu`).
Checked with KiCad 10.0.8: **ERC 0 errors / 0 warnings, DRC 0 errors, 0 unconnected pads.**

| File | Content |
|---|---|
| `solar-lamp.kicad_pro` | Project, open this in KiCad |
| `solar-lamp.kicad_sch` | Schematic |
| `solar-lamp.kicad_pcb` | PCB layout |
| `solar-lamp.kicad_sym`, `solar-lamp.pretty` | Project symbol & footprint libraries |
| `solar-lamp-gerbers.zip` | **Ready to upload** to JLCPCB / PCBWay / Aisler |
| `gerbers` | Unzipped Gerber + Excellon drill files |

## YX8018 pinout

Taken from the [YX8018 datasheet](https://www.datasheetcafe.com/wp-content/uploads/2024/03/yx8018-led-controller.pdf) Ver2.1, **Table 1** (TO-94):

| Pin | Name | Function |
|---|---|---|
| 1 | **LX** | Power switch drain — internal NMOS drain, drives L and the LED anode |
| 2 | **GND** | Battery − |
| 3 | **CE** | Solar cell − : chip enable (dark = on) *and* the charging-current return |
| 4 | **VCC** | Battery + **and** solar cell + — they share one rail |

> Earlier revisions of this project used `1 SBAT, 2 BAT, 3 GND, 4 LX`. That is wrong — it is
> the datasheet order read from the wrong end of the package. v1 Gerbers would not have worked.

## Nets

| Net | Pins |
|---|---|
| VCC | J1 (Solar+), SW1.2 (common), U1.4, L1.1 |
| VB | J3 (Battery+), SW1.1 |
| CE | J2 (Solar−), U1.3 |
| LX | U1.1, L1.2, D1.2 (anode) |
| GND | J4 (Battery−), U1.2, D1.1 (cathode) |

Note that **`S−` is not ground**. It goes to CE. Only the battery negative is GND.

## Footprints

| Footprint | Use |
|---|---|
| `YX8018_TO94_Spread2.54mm` | **Used on this board.** Legs formed out from 1.27 → 2.54 mm. Easier to etch and drill at home. |
| `YX8018_TO94_P1.27mm` | Native 1.27 mm pitch, drawn from the datasheet mechanical table (p.10: `e`=1.270 TYP, `e1`=3.71–3.91, `b`=0.36–0.50, `D`=4.98–5.28, `E`=3.45–3.75). Use it if you order the board rather than etch it. |

U1 is placed at **180°** so that VCC lands nearest the solar/battery pads and LX nearest the
inductor and LED — that is what lets the whole board route on one copper layer. Insert the
TO-94 accordingly: the **square pad is pin 1 (LX)**, and the silkscreen prints `LX GND CE VCC`
under the pads plus a pin-1 triangle.

## Known DRC warning

DRC reports one `lib_footprint_mismatch` warning on U1. This is a KiCad 10.0.8 quirk, not a
board problem: the check flags **any** footprint placed at a non-zero rotation (rotating an
untouched footprint such as `LED_D5.0mm` by 90° reproduces it). The board copy and the library
copy of `YX8018_TO94_Spread2.54mm` are byte-identical in geometry. Safe to ignore.

## Before ordering

- **Switch** footprint assumes SS12D07 with 3.0 mm pitch. Measure yours.
- **Inductor** sets the LED current (datasheet Table 1, p.8): 220 µH → 5.8 mA, 150 µH → 8.2 mA,
  82 µH → 14.8 mA, 47 µH → 26.6 mA, 22 µH → 51.4 mA. The fitted 470 µH extrapolates to ≈3 mA —
  dim, but matched to the 40 mAh cell.

## Re-export Gerbers after a change

```bash
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb export gerbers --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts -o gerbers/ solar-lamp.kicad_pcb
$K pcb export drill --format excellon -o gerbers/ solar-lamp.kicad_pcb
(cd gerbers && zip -q ../solar-lamp-gerbers.zip *)
```

Re-run the checks with:

```bash
$K sch erc --severity-error --severity-warning -o /tmp/erc.rpt solar-lamp.kicad_sch
$K pcb drc --severity-error --severity-warning -o /tmp/drc.rpt solar-lamp.kicad_pcb
```

## Order settings

2 layers · 38 × 27 mm · FR-4 · 1.6 mm · HASL · any color · qty 5 · no assembly.

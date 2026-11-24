#!/usr/bin/env python3
"""Generate npn-switch-breadboard.drawio — NPN transistor used as a switch: a push button drives the base
through 10 kΩ, the transistor switches an LED (+ 470 Ω). Half breadboard (30 columns), powered at 5 V (or 3.3 V)
by the breadboard power module of the Freenove FNK0020 kit, fed by a 9 V battery.
Parts come from ../../drawio-lib (gen_lib.py), same style as ../../photoresistor/gen_breadboard.py.

Usage:  python3 gen_breadboard.py
        drawio -x -f png -s 1 -b 10 -o npn-switch-breadboard.png npn-switch-breadboard.drawio
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "drawio-lib"))
import gen_lib as L  # noqa: E402

def find(prefix):
    return next(p for p in L.PARTS if p["title"].startswith(prefix))

bb = find("Breadboard half (30 columns)")
npn, led, btn, bat = find("NPN transistor"), find("LED red"), find("Push button 12x6"), L.bat
r10k, r470 = find("Resistor 10 kΩ"), find("Resistor 470 Ω")

BX, BY = 430, 130                       # breadboard top-left on the page
cells, n = [], [0]
def nid(p): n[0] += 1; return f"{p}{n[0]}"
def hole(col, row): return BX + L.bb_x(col), BY + L.BB_ROWS[row]
def href(col, row): return L.bb_x(col) / L.BB_W, L.BB_ROWS[row] / L.BB_H

def place(p, pin, col, row, value=None):
    hx, hy = hole(col, row)
    px, py = p["pins"][pin]
    q = dict(p) if value is None else dict(p, value=value)
    cells.append(L.vertex_xml(q, nid("p"), hx - px, hy - py))

def wire(color, a, b, pts=(), src="bb", dst="bb", sref=None, dref=None):
    s = sref or href(*a); t = dref or href(*b)
    arr = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts)
    st = (L.wire_style(color) + f"exitX={s[0]:.5f};exitY={s[1]:.5f};exitDx=0;exitDy=0;exitPerimeter=0;"
          f"entryX={t[0]:.5f};entryY={t[1]:.5f};entryDx=0;entryDy=0;entryPerimeter=0;")
    cells.append(f'<mxCell id="{nid("w")}" value="" style="{st}" edge="1" parent="1" source="{src}" target="{dst}">'
                 f'<mxGeometry relative="1" as="geometry">{f"<Array as=\"points\">{arr}</Array>" if arr else ""}'
                 f'</mxGeometry></mxCell>')

def text(x, y, s, size=12, bold=False, color="#1d2a3a", w=None, font="Helvetica"):
    w = w or len(s) * size * 0.62 + 12
    html = 0 if font == "Courier New" else 1  # html=0 keeps leading spaces (schematic alignment)
    cells.append(f'<mxCell id="{nid("t")}" value="{L.esc(s)}" style="text;html={html};align=left;verticalAlign=middle;'
                 f'fontFamily={font};fontSize={size};fontStyle={1 if bold else 0};fontColor={color};strokeColor=none;'
                 f'fillColor=none;whiteSpace=nowrap;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
                 f'height="{size * 1.8}" as="geometry"/></mxCell>')

def bubble(x, y, s, w=None):
    w = w or len(s) * 7.6 + 16
    cells.append(f'<mxCell id="{nid("l")}" value="{L.esc(s)}" style="rounded=1;arcSize=50;html=1;fillColor=#e8f4fb;'
                 f'strokeColor=#1d2a3a;fontSize=13;fontColor=#1d2a3a;" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="22" as="geometry"/></mxCell>')

# ---------------------------------------------------------------- title
text(40, 14, "NPN transistor as a switch — breadboard layout", 28, True)
text(40, 60, "Push button → 10 kΩ → base · LED + 470 Ω on the collector · emitter to GND · 5 V from the breadboard power module (BPM, Freenove FNK0020) fed by a 9 V battery", 13, color="#33465c")

# ---------------------------------------------------------------- breadboard, BPM, battery
# BPM (HW-131, Freenove FNK0020) at the left end: its rail pins go into columns 3 and 7 of the 4 rails,
# and the module covers columns 1-8. The circuit starts at column 11.
bpm = L.bpm_h
PMX, PMY = BX + L.bb_x(7) - bpm["pins"][0][0], BY
cells.append(L.vertex_xml(bb, "bb", BX, BY))
cells.append(L.vertex_xml(dict(bpm, value=""), "pm", PMX, PMY))
RED, BLK, ORA, YEL = "#d62728", "#1b1b1b", "#f28e1c", "#f2c200"
BATX, BATY = 60, BY + 150
cells.append(L.vertex_xml(dict(bat, value=""), "bat", BATX, BATY))
for k, color in enumerate((RED, BLK)):   # 9 V battery cable (snap -> DC barrel plug, pins 8 = +, 9 = −)
    bx = BATX + bat["pins"][k][0]
    px, py = bpm["pins"][8 + k]
    ytop, xdown = BATY - 40 + 10 * k, PMX - 40 - 10 * k
    wire(color, None, None, [(bx, ytop), (xdown, ytop), (xdown, PMY + py)],
         src="bat", dst="pm", sref=(bat["pins"][k][0] / bat["w"], bat["pins"][k][1] / bat["h"]),
         dref=(px / bpm["w"], py / bpm["h"]))
text(BATX - 20, BATY - 76, "9 V battery cable → DC jack", 11, True)

# ---------------------------------------------------------------- components (bottom half, rows f–j)
place(btn, 0, 11, "g", "")              # 12x6 mm button straddles the channel: cols 11 / 13, rows d / g
place(r10k, 0, 13, "c", "10 kΩ")        # c13 → c17 (base resistor)
place(npn, 0, 16, "e", "")              # E e16 · B e17 · C e18 (body sits over the channel)
place(r470, 0, 20, "c", "470 Ω")        # c20 → c24 (LED resistor)
place(led, 0, 20, "a")                  # + a20 · − a21

wire(RED, (11, "a"), (11, "b+"))        # + rail → button (col 11)
wire(BLK, (16, "a"), (16, "b-"))        # emitter → − rail
wire(ORA, (18, "d"), (21, "d"))         # collector → LED cathode (col 21)
wire(RED, (24, "a"), (24, "b+"))        # + rail → 470 Ω

# labels
bubble(BX + L.BB_W + 20, hole(30, "g")[1] - 11, "← push button 12×6 mm (cols 11/13, rows d/g)")
bubble(BX + L.BB_W + 20, hole(30, "e")[1] - 40, "← NPN: E e16 · B e17 · C e18")
bubble(BX + L.BB_W + 20, hole(30, "c")[1] - 11, "← 10 kΩ c13–c17 · 470 Ω c20–c24")
bubble(BX + L.BB_W + 20, hole(30, "a")[1] + 14, "← LED + a20 · − a21")
text(PMX - 10, BY + L.BB_H + 8, "BPM HW-131 on the rails (pins in cols 3 and 7), jumpers on 5V (or 3.3), press the switch", 12, True)

# ---------------------------------------------------------------- legend + schematic + notes panel
PY = BY + L.BB_H + 50
cells.append(f'<mxCell id="panel" value="" style="rounded=1;absoluteArcSize=1;arcSize=16;html=1;fillColor=#eef1f6;'
             f'strokeColor=#9aa3ab;" vertex="1" parent="1"><mxGeometry x="40" y="{PY}" width="1380" height="330" as="geometry"/></mxCell>')
text(60, PY + 10, "Wires", 16, True)
for k, (color, lab) in enumerate([(RED, "5 V (+ rail) / battery +"), (BLK, "GND (− rail) / battery −"), (ORA, "Collector → LED −")]):
    y = PY + 56 + 36 * k
    cells.append(f'<mxCell id="{nid("s")}" value="" style="{L.wire_style(color)}" edge="1" parent="1"><mxGeometry relative="1" '
                 f'as="geometry"><mxPoint x="60" y="{y}" as="sourcePoint"/><mxPoint x="106" y="{y}" as="targetPoint"/>'
                 f'</mxGeometry></mxCell>')
    text(118, y - 11, lab, 12)
text(60, PY + 170, "Schematic", 16, True)
for k, s in enumerate(["+5V ─ 470 Ω ─ LED(+ → −) ─ C", " " * 25 + "NPN",
                       "+5V ─ button ─ 10 kΩ ──── B", " " * 26 + "E ─ GND"]):
    text(60, PY + 204 + 22 * k, s.replace(" ", "\u00a0"), 12, font="Courier New")  # nbsp: keep alignment
text(380, PY + 10, "Notes", 16, True)
notes = [
    "• 9 V battery → battery cable → DC jack of the BPM (HW-131). It feeds the 4 rails; jumper of each side on 5V, then press the switch.",
    "• 12×6 mm button straddles the channel (cols 11 and 13, rows d and g). Col 11 gets +5 V from the b+ rail; pressing links col 11 → col 13.",
    "• Col 13 → 10 kΩ (c13 → c17) → base of the NPN (col 17). Base current ≈ (5 − 0.7) / 10 kΩ ≈ 0.43 mA (3.3 V: ≈ 0.26 mA).",
    "• Collector (col 18) → orange wire d18 → d21 → LED cathode (a21). LED anode (a20) → 470 Ω (c20 → c24) → + rail.",
    "• Emitter (col 16) → black wire → − rail. LED ≈ (5 − 2 − 0.1) / 470 Ω ≈ 6 mA at 5 V, ≈ 2.6 mA at 3.3 V.",
    "• Button released: no base current → transistor OFF → LED off. Pressed: transistor ON (saturated) → LED on.",
    "• Pinout E-B-C (flat face towards you, legs down) for S8050 / 2N2222 / PN2222. A BC547 is C-B-E: turn it 180°.",
    "• Never connect the base without its resistor. Built from projects/drawio-lib — regenerate with python3 gen_breadboard.py.",
]
for k, s in enumerate(notes):
    text(380, PY + 48 + 32 * k, s, 12)

xml = ('<mxfile host="app.diagrams.net"><diagram name="npn-switch" id="npn-switch"><mxGraphModel dx="1300" dy="1100" '
       'grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
       f'pageWidth="1460" pageHeight="{PY + 370}" background="#bac7dc" math="0" shadow="0"><root><mxCell id="0"/>'
       '<mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
out = os.path.join(HERE, "npn-switch-breadboard.drawio")
open(out, "w").write(xml)
print("wrote", out)

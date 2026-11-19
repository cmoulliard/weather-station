#!/usr/bin/env python3
"""Generate npn-switch-breadboard.drawio — NPN transistor used as a switch: a push button drives the base
through 10 kΩ, the transistor switches an LED (+ 1 kΩ) on a 9 V battery. Half breadboard (30 columns).
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
npn, led, btn, bat = find("NPN transistor"), find("LED red"), find("Push button"), L.bat
r10k, r1k = find("Resistor 10 kΩ"), find("Resistor 1 kΩ")

BX, BY = 260, 130                       # breadboard top-left on the page
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
text(40, 60, "Push button → 10 kΩ → base · LED + 1 kΩ on the collector · emitter to GND · 9 V battery", 13, color="#33465c")

# ---------------------------------------------------------------- breadboard + battery (below, feeding the bottom rails)
cells.append(L.vertex_xml(bb, "bb", BX, BY))
BATX, BATY = BX, BY + L.BB_H + 50       # + snap under column 1, − snap under column 2
cells.append(L.vertex_xml(dict(bat, value=""), "bat", BATX, BATY))
RED, BLK, ORA, YEL = "#d62728", "#1b1b1b", "#f28e1c", "#f2c200"
wire(RED, None, (1, "b+"), src="bat", sref=(bat["pins"][0][0] / bat["w"], bat["pins"][0][1] / bat["h"]))
wire(BLK, None, (2, "b-"), src="bat", sref=(bat["pins"][1][0] / bat["w"], bat["pins"][1][1] / bat["h"]))

# ---------------------------------------------------------------- components (bottom half, rows f–j)
place(btn, 0, 3, "e")                   # straddles the channel: cols 3 / 5, rows e / f
place(r10k, 0, 5, "h", "10 kΩ")         # h5 → h9  (base resistor)
place(npn, 0, 8, "f")                   # E f8 · B f9 · C f10 (body sits over the channel)
place(r1k, 0, 12, "h", "1 kΩ")          # h12 → h16 (LED resistor)
place(led, 0, 12, "j")                  # + j12 · − j13

wire(RED, (3, "j"), (3, "b+"))          # + rail → button (col 3)
wire(BLK, (8, "j"), (8, "b-"))          # emitter → − rail
wire(ORA, (10, "g"), (13, "g"))         # collector → LED cathode (col 13)
wire(RED, (16, "j"), (16, "b+"))        # + rail → 1 kΩ

# labels
bubble(BX - 215, hole(3, "e")[1] - 11, "push button (cols 3/5) →")
bubble(BX + L.BB_W + 20, hole(30, "f")[1] - 40, "← NPN: E f8 · B f9 · C f10")
bubble(BX + L.BB_W + 20, hole(30, "h")[1] - 11, "← 10 kΩ h5–h9 · 1 kΩ h12–h16")
bubble(BX + L.BB_W + 20, hole(30, "j")[1] + 14, "← LED + j12 · − j13")
text(BX + 100, BATY + 40, "9 V battery: + → + rail (b+1), − → − rail (b−2)", 12, True)

# ---------------------------------------------------------------- legend + schematic + notes panel
PY = BATY + bat["h"] + 40
cells.append(f'<mxCell id="panel" value="" style="rounded=1;absoluteArcSize=1;arcSize=16;html=1;fillColor=#eef1f6;'
             f'strokeColor=#9aa3ab;" vertex="1" parent="1"><mxGeometry x="40" y="{PY}" width="1180" height="330" as="geometry"/></mxCell>')
text(60, PY + 10, "Wires", 16, True)
for k, (color, lab) in enumerate([(RED, "9 V (+ rail)"), (BLK, "GND (− rail)"), (ORA, "Collector → LED −")]):
    y = PY + 56 + 36 * k
    cells.append(f'<mxCell id="{nid("s")}" value="" style="{L.wire_style(color)}" edge="1" parent="1"><mxGeometry relative="1" '
                 f'as="geometry"><mxPoint x="60" y="{y}" as="sourcePoint"/><mxPoint x="106" y="{y}" as="targetPoint"/>'
                 f'</mxGeometry></mxCell>')
    text(118, y - 11, lab, 12)
text(60, PY + 170, "Schematic", 16, True)
for k, s in enumerate(["+9V ─ 1 kΩ ─ LED(+ → −) ─ C", " " * 25 + "NPN",
                       "+9V ─ button ─ 10 kΩ ──── B", " " * 26 + "E ─ GND"]):
    text(60, PY + 204 + 22 * k, s.replace(" ", "\u00a0"), 12, font="Courier New")  # nbsp: keep alignment
text(380, PY + 10, "Notes", 16, True)
notes = [
    "• 9 V battery feeds the bottom rails: + → b+ (red), − → b− (black). The top rails and the top half are not used.",
    "• Button straddles the channel (cols 3 and 5). Col 3 gets +9 V from the rail; pressing links col 3 → col 5.",
    "• Col 5 → 10 kΩ (h5 → h9) → base of the NPN (col 9). Base current ≈ (9 − 0.7) / 10 kΩ ≈ 0.8 mA.",
    "• Collector (col 10) → orange wire g10 → g13 → LED cathode (j13). LED anode (j12) → 1 kΩ (h12 → h16) → + rail.",
    "• Emitter (col 8) → black wire → − rail. LED current ≈ (9 − 2 − 0.1) / 1 kΩ ≈ 7 mA: the transistor is saturated.",
    "• Button released: no base current → transistor OFF → LED off. Pressed: transistor ON → LED on.",
    "• Pinout E-B-C (flat face towards you, legs down) for S8050 / 2N2222 / PN2222. A BC547 is C-B-E: turn it 180°.",
    "• Never connect the base without its resistor. Built from projects/drawio-lib — regenerate with python3 gen_breadboard.py.",
]
for k, s in enumerate(notes):
    text(380, PY + 48 + 32 * k, s, 12)

xml = ('<mxfile host="app.diagrams.net"><diagram name="npn-switch" id="npn-switch"><mxGraphModel dx="1300" dy="1100" '
       'grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
       f'pageWidth="1260" pageHeight="{PY + 370}" background="#bac7dc" math="0" shadow="0"><root><mxCell id="0"/>'
       '<mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
out = os.path.join(HERE, "npn-switch-breadboard.drawio")
open(out, "w").write(xml)
print("wrote", out)

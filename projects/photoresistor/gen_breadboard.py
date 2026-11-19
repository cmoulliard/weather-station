#!/usr/bin/env python3
"""Generate photoresistor-breadboard.drawio — dark-activated LED (LDR + 100 kΩ pot + NPN) on a vertical
half breadboard, powered by a breadboard power module (Freenove FNK0020 kit) + 9 V battery.
Same style as ../anniversaire/anniversaire-breadboard.drawio, parts from ../drawio-lib (gen_lib.py).

Usage:  python3 gen_breadboard.py
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "drawio-lib"))
import gen_lib as L  # noqa: E402

def find(prefix):
    return next(p for p in L.PARTS if p["title"].startswith(prefix))

bb = L.bbv
ldr, npn, led = L.ldr_2, find("NPN transistor"), find("LED red")
r10k, r220, bat = L.r10k, find("Resistor 220 Ω"), L.bat
C = L.BBV_COLS

# ---------------------------------------------------------------- Baoter 3296W multi-turn trimmer (top adjust, 3 pins in line)
def trimmer3296w():
    w, h = 30, 90                         # pins 1-2-3 at (15,30) (15,50) (15,70), 2.54 mm pitch, wiper = middle
    b = ('<rect x="1" y="1" width="28" height="88" rx="2" fill="#2f74c0" stroke="#174a85" stroke-width="1.5"/>'
         '<circle cx="15" cy="13" r="9" fill="#e2c46a" stroke="#7a5d18" stroke-width="1.5"/>'
         '<line x1="9" y1="13" x2="21" y2="13" stroke="#7a5d18" stroke-width="2.5" stroke-linecap="round"/>'
         + "".join(f'<circle cx="15" cy="{y}" r="3.5" fill="#c3b0e0" stroke="#4a2d7a"/>' for y in (30, 50, 70))
         + L.T(15, 87, "104", 7, "#fff", "bold"))
    pins = [(15, 30), (15, 50), (15, 70)]
    return dict(w=w, h=h, pins=pins, value="",
                style=(f"shape=image;html=1;imageAspect=0;aspect=fixed;image={L.svg_uri(w, h, b)};"
                       f"{L.pins_style(w, h, pins)}{L.LABEL}"))
trim = trimmer3296w()

BX, BY = 520, 200                       # breadboard top-left on the page
cells, n = [], [0]
def nid(p): n[0] += 1; return f"{p}{n[0]}"
def hole(col, row): return BX + C[col], BY + L.bbv_y(row)
def href(col, row): return C[col] / bb["w"], L.bbv_y(row) / bb["h"]

def rot_pins(p, rot):
    s = p["w"]
    f = {0: lambda x, y: (x, y), 90: lambda x, y: (s - y, x), 270: lambda x, y: (y, s - x)}[rot]
    return [f(x, y) for x, y in p["pins"]]

def place(p, pin, col, row, value="", rot=0, extra=""):
    hx, hy = hole(col, row)
    px, py = rot_pins(p, rot)[pin]
    q = dict(p, value=value)
    cells.append(L.vertex_xml(q, nid("p"), hx - px, hy - py, (f"rotation={rot};" if rot else "") + extra))

def wire(color, a, b, pts=(), src="bb", dst="bb", sref=None, dref=None):
    s = sref or href(*a); t = dref or href(*b)
    arr = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts)
    st = (L.wire_style(color) + f"exitX={s[0]:.5f};exitY={s[1]:.5f};exitDx=0;exitDy=0;exitPerimeter=0;"
          f"entryX={t[0]:.5f};entryY={t[1]:.5f};entryDx=0;entryDy=0;entryPerimeter=0;")
    cells.append(f'<mxCell id="{nid("w")}" value="" style="{st}" edge="1" parent="1" source="{src}" target="{dst}">'
                 f'<mxGeometry relative="1" as="geometry">{f"<Array as=\"points\">{arr}</Array>" if arr else ""}'
                 f'</mxGeometry></mxCell>')

def text(x, y, s, size=12, bold=False, color="#1d2a3a", align="left", w=None):
    w = w or len(s) * size * 0.62 + 12
    cells.append(f'<mxCell id="{nid("t")}" value="{L.esc(s)}" style="text;html=1;align={align};verticalAlign=middle;'
                 f'fontFamily=Helvetica;fontSize={size};fontStyle={1 if bold else 0};fontColor={color};strokeColor=none;'
                 f'fillColor=none;whiteSpace=nowrap;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
                 f'height="{size * 1.8}" as="geometry"/></mxCell>')

def bubble(x, y, s, w=None):
    w = w or len(s) * 7.6 + 16
    cells.append(f'<mxCell id="{nid("l")}" value="{L.esc(s)}" style="rounded=1;arcSize=50;html=1;fillColor=#e8f4fb;'
                 f'strokeColor=#1d2a3a;fontSize=13;fontColor=#1d2a3a;" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="22" as="geometry"/></mxCell>')

# ---------------------------------------------------------------- breadboard power module (Freenove / MB102 style)
PM_W, PM_H = bb["w"], 180               # placed at (BX, BY-100): pins at y 150/170 -> rail rows 0/1
def T(x, y, s, size=9, color="#fff", weight="bold", anchor="middle"): return L.T(x, y, s, size, color, weight, anchor)
def jumper(x0, label_side):
    b = [f'<rect x="{x0}" y="78" width="66" height="22" rx="2" fill="#111"/>']
    for k in range(3):
        b.append(f'<rect x="{x0 + 8 + 20*k}" y="84" width="10" height="10" fill="#d4a017"/>')
    b.append(f'<rect x="{x0 + 3}" y="80" width="40" height="18" rx="2" fill="#e5322d" stroke="#7a0d0a"/>')  # cap on 5V
    b.append(T(x0 + 13, 112, "5V", 9) + T(x0 + 33, 112, "|", 9) + T(x0 + 53, 112, "3.3V", 8, "#bcd"))
    return "".join(b)
pm = ['<rect x="1" y="1" width="398" height="138" rx="6" fill="#1f4f8f" stroke="#0f2c55" stroke-width="2"/>',
      # DC jack (left) + USB
      '<rect x="4" y="44" width="58" height="50" rx="4" fill="#151515" stroke="#000"/>',
      '<circle cx="22" cy="69" r="11" fill="#333" stroke="#777" stroke-width="2"/><circle cx="22" cy="69" r="3" fill="#bbb"/>',
      T(33, 38, "DC 6.5–12 V", 9),
      '<rect x="80" y="10" width="44" height="26" rx="2" fill="#c9ced3" stroke="#666"/>' + T(102, 50, "USB", 8, "#cde"),
      # switch + LED + regulator
      '<rect x="150" y="16" width="30" height="40" rx="3" fill="#ececec" stroke="#555"/><rect x="156" y="20" width="18" height="16" fill="#222"/>',
      T(165, 70, "ON/OFF", 8),
      '<circle cx="210" cy="30" r="6" fill="#ff4a3d" stroke="#7a0d0a"/>' + T(210, 50, "PWR", 8),
      '<rect x="240" y="18" width="50" height="34" rx="2" fill="#2a2a2a"/>' + T(265, 40, "AMS1117", 7, "#bbb"),
      T(330, 30, "Breadboard", 11) + T(330, 44, "power module", 11), T(330, 60, "(Freenove kit)", 9, "#cde", "normal"),
      jumper(100, "L"), jumper(260, "R")]
for x, lab, col in ((30, "+", "#ff6b6b"), (50, "−", "#8fc1ff"), (350, "+", "#ff6b6b"), (370, "−", "#8fc1ff")):
    pm.append(f'<rect x="{x-8}" y="122" width="16" height="56" rx="2" fill="#111"/>'
              f'<circle cx="{x}" cy="150" r="3.5" fill="#d4a017"/><circle cx="{x}" cy="170" r="3.5" fill="#d4a017"/>')
    pm.append(T(x, 116, lab, 13, col))
PM_PINS = [(30, 150), (50, 150), (350, 150), (370, 150), (30, 170), (50, 170), (350, 170), (370, 170), (6, 64), (6, 74)]
pm_style = (f"shape=image;html=1;imageAspect=0;aspect=fixed;image={L.svg_uri(PM_W, PM_H, ''.join(pm))};"
            f"{L.pins_style(PM_W, PM_H, PM_PINS)}")

# ---------------------------------------------------------------- title
text(BX - 40, 14, "Photoresistor night light — breadboard layout", 28, True)
text(BX - 40, 60, "LDR + Baoter 3296W 100 kΩ trimmer + S8050 NPN transistor + LED · 5 V from a breadboard power module fed by a 9 V battery", 13,
     color="#33465c")

# ---------------------------------------------------------------- breadboard, module, battery
cells.append(L.vertex_xml(bb, "bb", BX, BY))
cells.append(f'<mxCell id="pm" value="" style="{pm_style}" vertex="1" parent="1">'
             f'<mxGeometry x="{BX}" y="{BY - 100}" width="{PM_W}" height="{PM_H}" as="geometry"/></mxCell>')
BATX, BATY = BX - 300, BY + 40
cells.append(L.vertex_xml(dict(bat, value=""), "bat", BATX, BATY))
# 9 V battery cable (snap -> DC barrel plug)
for k, (color, dy) in enumerate((("#d62728", 64), ("#1b1b1b", 74))):
    bx = BATX + bat["pins"][k][0]
    ytop, xdown = BY - 80 + 10 * k, BX - 40 - 10 * k
    wire(color, None, None, [(bx, ytop), (xdown, ytop), (xdown, BY - 100 + dy)],
         src="bat", dst="pm", sref=(bat["pins"][k][0] / bat["w"], bat["pins"][k][1] / bat["h"]),
         dref=(6 / PM_W, dy / PM_H))
text(BATX - 20, BY - 112, "9 V battery cable → DC jack", 11, True)

# ---------------------------------------------------------------- components
R = 8                                    # divider node row (left half a–e)
place(ldr, 0, "L-", R)                   # LDR: − rail (GND) ↔ a8
place(r10k, 0, "d", R, "10 kΩ")          # d8 → f8 (across the channel)
place(npn, 0, "g", R - 1, rot=90)        # E g7 · B g8 · C g9
place(led, 1, "f", R + 1, rot=270)       # − f9 · + f10
place(r220, 0, "h", R + 2, "220 Ω")      # h10 → + rail (right)
place(trim, 0, "b", R + 2)               # b10 (5 V) · b11 (wiper) · b12 (n.c.)

RED, BLK, YEL = "#d62728", "#1b1b1b", "#f2c200"
wire(RED, ("a", R + 2), ("L+", R + 2))   # pot end -> + rail
wire(YEL, ("c", R + 3), ("c", R))        # pot wiper -> divider node
wire(BLK, ("j", R - 1), ("R-", R - 1))   # emitter -> − rail

# labels (bubbles + arrows like the birthday-box diagram)
x0, y0 = hole("a", R)
bubble(BX - 80, y0 - 42, "LDR →")
bubble(BX - 245, hole("a", R + 3)[1] - 11, "trimmer 3296W 100 kΩ (104) →")
bubble(BX + 420, hole("j", R)[1] - 11, "← S8050 NPN (E g7 · B g8 · C g9)")
bubble(BX + 420, hole("j", R + 1)[1] + 8, "← LED (− f9 · + f10)")
text(BX - 40, BY + bb["h"] + 4, "Power module plugs into the rails (rows 0–1), both jumpers on 5 V", 11, True)

# ---------------------------------------------------------------- legend + notes panel
PY = BY + bb["h"] + 40
cells.append(f'<mxCell id="panel" value="" style="rounded=1;absoluteArcSize=1;arcSize=16;html=1;fillColor=#eef1f6;'
             f'strokeColor=#9aa3ab;" vertex="1" parent="1"><mxGeometry x="40" y="{PY}" width="1240" height="300" as="geometry"/></mxCell>')
text(60, PY + 10, "Wires", 16, True)
for k, (color, lab) in enumerate([(RED, "5 V (+ rail) / battery +"), (BLK, "GND (− rail) / battery −"),
                                  (YEL, "Pot wiper → divider node")]):
    y = PY + 56 + 36 * k
    cells.append(f'<mxCell id="{nid("s")}" value="" style="{L.wire_style(color)}" edge="1" parent="1"><mxGeometry relative="1" '
                 f'as="geometry"><mxPoint x="60" y="{y}" as="sourcePoint"/><mxPoint x="106" y="{y}" as="targetPoint"/>'
                 f'</mxGeometry></mxCell>')
    text(118, y - 11, lab, 12)
text(380, PY + 10, "Notes", 16, True)
notes = [
    "• 9 V battery → Freenove 9 V battery cable → DC jack of the breadboard power module. Both jumpers on 5 V (not 3.3 V), switch ON.",
    "• The module feeds the + / − rails on both sides: left rails for the trimmer and the LDR, right rails for the transistor and the LED.",
    "• Light divider: + rail → Baoter 3296W 100 kΩ trimmer (code 104; b10 = 5 V, wiper = middle pin b11, b12 not connected) → yellow wire c11 → c8 → node row 8 (a8 LDR, c8 wire, d8 10 kΩ) → LDR → − rail.",
    "• Node row 8 → 10 kΩ (d8 → f8, across the channel) → base of the S8050 (column g: E row 7, B row 8, C row 9).",
    "• LED: + rail → 220 Ω (row 10) → LED + (f10) / LED − (f9) → collector (row 9). Emitter (row 7) → black wire → − rail.",
    "• Set-up: in room light turn the trimmer screw (multi-turn, ~25 turns end to end) until the LED just goes OFF, then cover the LDR → the LED lights.",
    "• S8050 (TO-92, flat face towards you, legs down) = E-B-C, left to right. Same holes for a 2N2222 / PN2222; a BC547 (C-B-E) goes in rotated 180°.",
    "• Built from projects/drawio-lib/breadboard-electronics.xml — regenerate with python3 gen_breadboard.py.",
]
for k, s in enumerate(notes):
    text(380, PY + 48 + 30 * k, s, 12)

xml = ('<mxfile host="app.diagrams.net"><diagram name="photoresistor" id="photoresistor"><mxGraphModel dx="1300" dy="1140" '
       'grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
       f'pageWidth="1320" pageHeight="{PY + 340}" background="#bac7dc" math="0" shadow="0"><root><mxCell id="0"/>'
       '<mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
out = os.path.join(HERE, "photoresistor-breadboard.drawio")
open(out, "w").write(xml)
print("wrote", out)

#!/usr/bin/env python3
"""Generate resistor-box-label.drawio — lid label (195 x 145 mm, Werckmann translucent box) for an 8-compartment box holding the Tinytronics
10 Ω–1 MΩ resistor set (30 values, 1 % metal film = 5-band colour code).

Usage:  python3 gen_label.py
        drawio -x -f png -s 1.1811 -o resistor-box-label.png resistor-box-label.drawio   # 300 dpi
        sips -s dpiWidth 300 -s dpiHeight 300 resistor-box-label.png              # prints at 195 x 145 mm
"""
import base64, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
esc = lambda s: html.escape(str(s), quote=True)

COLORS = {-2: ("silver", "#c0c0c0"), -1: ("gold", "#c9a227"), 0: ("black", "#111111"), 1: ("brown", "#7b3f12"),
          2: ("red", "#e02020"), 3: ("orange", "#ff8a00"), 4: ("yellow", "#ffd400"), 5: ("green", "#2e9e3e"),
          6: ("blue", "#1f5fd6"), 7: ("violet", "#8a2be2"), 8: ("grey", "#8a8a8a"), 9: ("white", "#ffffff")}
TOL = "#7b3f12"                          # brown = 1 %

BOXES = [  # (title, values in ohms) — 30 values in increasing order, box 8 = parts to sort
    ("10 – 100 Ω", [10, 22, 47, 100]),
    ("150 – 330 Ω", [150, 200, 220, 270, 330]),
    ("470 Ω – 1 k", [470, 510, 680, 1_000]),
    ("2 k – 4.7 k", [2_000, 2_200, 3_300, 4_700]),
    ("5.1 k – 20 k", [5_100, 6_800, 10_000, 20_000]),
    ("47 k – 100 k", [47_000, 51_000, 68_000, 100_000]),
    ("220 k – 1 M", [220_000, 300_000, 470_000, 680_000, 1_000_000]),
    ("To sort", []),
]

def bands(ohms):
    """5-band code: 3 significant digits + multiplier exponent."""
    exp = 0
    v = ohms
    while v >= 1000:
        v //= 10; exp += 1
    while v < 100:
        v *= 10; exp -= 1
    d = [int(c) for c in str(v)]
    return d + [exp]

def fmt(ohms):
    if ohms >= 1_000_000: s, u = ohms / 1_000_000, "M"
    elif ohms >= 1_000: s, u = ohms / 1_000, "k"
    else: s, u = ohms, ""
    s = f"{s:g}"
    return f"{s} {u}Ω" if u else f"{s} Ω"

def T(x, y, s, size=14, color="#1d2a3a", weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')

def resistor(x0, y0, ohms, scale=1.0):
    """Resistor drawn horizontally, centre-left at (x0, y0): leads + blue body + 5 bands + value."""
    x = y = 0
    b = [f'<g transform="translate({x0},{y0}) scale({scale})">', f'<line x1="{x}" y1="{y}" x2="{x + 130}" y2="{y}" stroke="#9a9a9a" stroke-width="3" stroke-linecap="round"/>',
         f'<rect x="{x + 18}" y="{y - 13}" width="94" height="26" rx="12" fill="#86b8e8" stroke="#3b6f9e" stroke-width="1.5"/>']
    for k, (bx, c) in enumerate(zip((32, 46, 60, 74, 96), [COLORS[n][1] for n in bands(ohms)] + [TOL])):
        b.append(f'<rect x="{x + bx}" y="{y - 13}" width="7" height="26" fill="{c}" stroke="#444" stroke-width="0.6"/>')
    names = " · ".join(COLORS[n][0] for n in bands(ohms))
    b.append(T(x + 145, y + 2, fmt(ohms), 20, weight="bold"))
    b.append(T(x + 145, y + 22, names, 13, "#4a5a6a"))
    return "".join(b) + "</g>"

# Werckmann box lid 195 x 145 mm, 8 compartments = 4 columns x 2 rows. 1 unit = 0.1 mm.
W, H, M, LEGEND = 1950, 1450, 15, 150
COLS, ROWS = 4, 2
CW, CH = (W - 2 * M) / COLS, (H - 2 * M - LEGEND) / ROWS
S = 1.3                                   # scale of a resistor entry (drawn 280 units wide at scale 1)
svg = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>']
for i, (title, vals) in enumerate(BOXES):
    cx, cy = M + (i % COLS) * CW, M + (i // COLS) * CH
    svg.append(f'<rect x="{cx + 4}" y="{cy + 4}" width="{CW - 8}" height="{CH - 8}" rx="14" '
               f'fill="#f4f7fb" stroke="#9aa3ab" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx + 36}" cy="{cy + 38}" r="20" fill="#1d2a3a"/>' + T(cx + 36, cy + 46, i + 1, 22, "#fff", "bold", "middle"))
    svg.append(T(cx + 64, cy + 47, title, 26 if len(title) < 14 else 23, weight="bold"))
    if vals:
        step = (CH - 120) / max(len(vals), 4)
        for k, v in enumerate(vals):
            svg.append(resistor(cx + 22, cy + 105 + k * step, v, S if len(vals) <= 4 else 1.2))
    else:
        for k, line in enumerate(["parts back from a circuit:", "check with a multimeter,", "then put them back", "in their box"]):
            svg.append(T(cx + CW / 2, cy + CH / 2 + k * 30, line, 20, "#4a5a6a", anchor="middle"))

# colour legend
ly = M + ROWS * CH + 30
svg.append(T(M + 6, ly + 4, "1 % metal film · 5 bands: digit · digit · digit · multiplier · tolerance (brown, set apart)", 19, weight="bold"))
for k, n in enumerate(range(-1, 10)):
    name, c = COLORS[n]
    x = M + 6 + k * 175
    svg.append(f'<rect x="{x}" y="{ly + 24}" width="30" height="30" rx="4" fill="{c}" stroke="#444"/>')
    svg.append(T(x + 38, ly + 46, f"{n} {name}" if n >= 0 else "gold ×0.1", 18))
svg.append(T(M + 6, ly + 92, "Multiplier: black ×1 · brown ×10 · red ×100 · orange ×1 k · yellow ×10 k · gold ×0.1", 18, "#4a5a6a"))

body = "".join(svg)
svg_doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W / 10}mm" height="{H / 10}mm" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica,Arial,sans-serif">{body}</svg>')
uri = "data:image/svg+xml," + base64.b64encode(svg_doc.encode()).decode()
xml = ('<mxfile host="app.diagrams.net"><diagram name="label" id="label"><mxGraphModel grid="0" page="0" background="#ffffff">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       f'<mxCell id="2" value="" style="shape=image;html=1;imageAspect=0;aspect=fixed;image={uri};" vertex="1" parent="1">'
       f'<mxGeometry x="0" y="0" width="{W}" height="{H}" as="geometry"/></mxCell></root></mxGraphModel></diagram></mxfile>\n')
with open(os.path.join(HERE, "resistor-box-label.drawio"), "w") as f:
    f.write(xml)
with open(os.path.join(HERE, "resistor-box-label.svg"), "w") as f:
    f.write(svg_doc)
print("wrote resistor-box-label.drawio + .svg")

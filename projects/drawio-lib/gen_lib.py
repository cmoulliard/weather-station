#!/usr/bin/env python3
"""Generate a draw.io library of breadboard parts + coloured wires, and a demo diagram.

Every part is ONE draw.io shape (an embedded SVG) whose pins are draw.io connection
points. All pins sit on a 20 px pitch (= one breadboard hole, 2.54 mm), so parts drop
straight onto breadboard holes when the grid is 10 or 20 px.

Usage:  python3 gen_lib.py            -> breadboard-electronics.xml + demo-relay-led.drawio
"""
import base64, json, urllib.parse, zlib, html, os

P = 20                      # pitch in px (one hole)
HERE = os.path.dirname(os.path.abspath(__file__))
esc = lambda s: html.escape(str(s), quote=True)

# --------------------------------------------------------------------------- helpers
def compress(xml):
    """Same as draw.io Graph.compress(): encodeURIComponent -> raw deflate -> base64."""
    data = urllib.parse.quote(xml, safe="-_.!~*'()").encode()
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(data) + c.flush()).decode()

def svg_uri(w, h, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="Helvetica,Arial,sans-serif">{body}</svg>')
    return "data:image/svg+xml," + base64.b64encode(svg.encode()).decode()

def pins_style(w, h, pins):
    return "points=[" + ",".join(f"[{x/w:.5f},{y/h:.5f},0]" for x, y in pins) + "];"

# part label under the image: bold, dark, on a white box so it stays readable over holes and wires
LABEL = ("verticalLabelPosition=bottom;verticalAlign=top;align=center;labelBackgroundColor=#ffffff;"
         "labelBorderColor=#9aa3ab;fontSize=12;fontStyle=1;fontColor=#111111;spacingTop=1;")

PARTS = []   # dicts: title, w, h, style, value, pins

def part(title, w, h, body, pins, value="", extra=""):
    style = (f"shape=image;html=1;imageAspect=0;aspect=fixed;"
             f"image={svg_uri(w, h, body)};{pins_style(w, h, pins)}{LABEL}{extra}")
    PARTS.append(dict(title=title, w=w, h=h, style=style, value=value, pins=pins))
    return PARTS[-1]

def T(x, y, s, size=9, color="#222", weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')

def lead(x1, y1, x2, y2): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#9a9a9a" stroke-width="2.5" stroke-linecap="round"/>'
def pinmark(x, y): return f'<circle cx="{x}" cy="{y}" r="3" fill="#6d6d6d"/>'

# --------------------------------------------------------------------------- breadboard (half size, 30 columns)
BB_W, BB_H = 640, 400
LBL = "#111111"            # colour of the row letters / column numbers on the breadboards
# Real breadboard turned 90° (row 1 on the left): the f–j half is on top (j next to the top rails),
# the a–e half at the bottom (a next to the bottom rails).
BB_ROWS = {"t-": 30, "t+": 50, "j": 90, "i": 110, "h": 130, "g": 150, "f": 170,
           "e": 230, "d": 250, "c": 270, "b": 290, "a": 310, "b-": 350, "b+": 370}
def bb_x(col): return 10 + P*col          # col 1..30
def breadboard():
    b = [f'<rect x="1" y="1" width="{BB_W-2}" height="{BB_H-2}" rx="8" fill="#fbfbf8" stroke="#9aa0a6" stroke-width="2"/>',
         f'<rect x="20" y="186" width="{BB_W-40}" height="28" fill="#e4e6e4"/>',
         f'<rect x="20" y="198" width="{BB_W-40}" height="4" fill="#b9bdbb"/>']
    for y, c in ((19, "#3d8fd6"), (61, "#e05a5a"), (339, "#3d8fd6"), (381, "#e05a5a")):
        b.append(f'<rect x="24" y="{y}" width="{BB_W-48}" height="2.5" fill="{c}"/>')
    for y, s, c in ((30, "−", "#1f6fd0"), (50, "+", "#d62728"), (350, "−", "#1f6fd0"), (370, "+", "#d62728")):
        b.append(T(12, y+4, s, 13, c, "bold")); b.append(T(BB_W-12, y+4, s, 13, c, "bold"))
    for r, y in BB_ROWS.items():
        if len(r) == 1:
            b.append(T(12, y+4.5, r, 13, LBL, "bold")); b.append(T(BB_W-12, y+4.5, r, 13, LBL, "bold"))
    for col in range(1, 31):
        if col == 1 or col % 5 == 0:
            b.append(T(bb_x(col), 76, str(col), 12, LBL, "bold")); b.append(T(bb_x(col), 332, str(col), 12, LBL, "bold"))
        for y in BB_ROWS.values():
            b.append(f'<rect x="{bb_x(col)-5}" y="{y-5}" width="10" height="10" rx="1.5" fill="#d4d6d6"/>'
                     f'<rect x="{bb_x(col)-3}" y="{y-3}" width="6" height="6" fill="#4a4a4a"/>')
    pins = [(bb_x(c), y) for y in BB_ROWS.values() for c in range(1, 31)]
    return part("Breadboard half (30 columns) — every hole is a connection point", BB_W, BB_H, "".join(b), pins)

def perfboard(cols=12, rows=10):
    w, h = P*(cols+1)+20, P*(rows+1)+20
    w, h = P*cols + 40, P*rows + 40
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="5" fill="#c98a4b" stroke="#8a5a2b" stroke-width="2"/>']
    pins = []
    for i in range(cols):
        for j in range(rows):
            x, y = 30 + P*i, 30 + P*j
            pins.append((x, y))
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#e9b65a" stroke="#a87a2a" stroke-width="1"/>'
                     f'<circle cx="{x}" cy="{y}" r="2.5" fill="#5a3a1a"/>')
    return part(f"Perfboard / PCB {cols}x{rows} holes", w, h, "".join(b), pins)

def pad():
    b = '<circle cx="10" cy="10" r="7" fill="#e9b65a" stroke="#a87a2a" stroke-width="1.5"/><circle cx="10" cy="10" r="3" fill="#5a3a1a"/>'
    return part("PCB hole / pad (1 connection point)", 20, 20, b, [(10, 10)])

# --------------------------------------------------------------------------- passive parts
BANDS = {"0": "#111111", "1": "#7b4a1e", "2": "#d62728", "3": "#f28e1c", "4": "#f2c200",
         "5": "#2ca02c", "6": "#1f6fd0", "7": "#8a2be2", "8": "#8a8a8a", "9": "#ffffff"}
def resistor(label, ohms):
    """1 % metal-film resistor, 5-band code: 3 digits + multiplier + brown tolerance band (set apart)."""
    exp, v = 0, ohms
    while v >= 1000: v //= 10; exp += 1
    cols = [BANDS[d] for d in f"{v:03d}"] + [BANDS[str(exp)], BANDS["1"]]
    b = [lead(10, 10, 90, 10), pinmark(10, 10), pinmark(90, 10),
         '<rect x="30" y="3" width="40" height="14" rx="6" fill="#86b8e8" stroke="#3b6f9e" stroke-width="1.2"/>']
    for x, c in zip((35, 41, 47, 53, 62), cols):
        b.append(f'<rect x="{x}" y="3.5" width="3.5" height="13" fill="{c}" stroke="#555" stroke-width="0.3"/>')
    return part(f"Resistor {label} (pins 4 holes apart)", 100, 20, "".join(b), [(10, 10), (90, 10)], label)

def diode(label, body, band, title, band_left=False):
    bx, ka, kk = (38, 82, 18) if band_left else (58, 18, 82)
    b = (lead(10, 10, 90, 10) + pinmark(10, 10) + pinmark(90, 10) +
         f'<rect x="34" y="4" width="32" height="12" rx="3" fill="{body}" stroke="#000" stroke-width="1"/>'
         f'<rect x="{bx}" y="4" width="4" height="12" fill="{band}"/>' +
         T(ka, 7, "A", 7, "#555") + T(kk, 7, "K", 7, "#555"))
    side = "left" if band_left else "right"
    return part(f"{title} — band = cathode ({side})", 100, 20, b, [(10, 10), (90, 10)], label)

def led(color, name, hi):
    b = (pinmark(10, 20) + pinmark(30, 20) +
         f'<circle cx="20" cy="20" r="14" fill="{color}" stroke="#333" stroke-width="1.5" opacity="0.95"/>'
         f'<line x1="31" y1="9" x2="31" y2="31" stroke="#333" stroke-width="1.5"/>'
         f'<circle cx="15" cy="15" r="4" fill="{hi}" opacity="0.8"/>' + T(4, 9, "+", 10, "#d62728", "bold"))
    return part(f"LED {name} (top view, + left / flat side = cathode right)", 40, 40, b, [(10, 20), (30, 20)], f"LED {name}")

def cap_ceramic():
    b = (lead(10, 50, 10, 34) + lead(30, 50, 30, 34) + pinmark(10, 50) + pinmark(30, 50) +
         '<ellipse cx="20" cy="22" rx="17" ry="15" fill="#e8823a" stroke="#9a4a10" stroke-width="1.2"/>' + T(20, 26, "104", 9, "#5a2a00", "bold"))
    return part("Capacitor ceramic 0.1 µF (104)", 40, 60, b, [(10, 50), (30, 50)], "0.1 µF")

def cap_electrolytic():
    b = (pinmark(10, 50) + pinmark(30, 50) +
         '<circle cx="20" cy="26" r="17" fill="#2a4f9e" stroke="#13306b" stroke-width="1.5"/>'
         '<path d="M 31 13 A 17 17 0 0 1 31 39 Z" fill="#cfd8ea"/>' + T(26, 30, "−", 12, "#13306b", "bold") + T(8, 12, "+", 11, "#d62728", "bold"))
    return part("Capacitor electrolytic 10 µF (+ left, stripe = −)", 40, 60, b, [(10, 50), (30, 50)], "10 µF")

# --------------------------------------------------------------------------- switches & relay
def push_button():
    b = ('<rect x="2" y="2" width="56" height="76" rx="4" fill="#3a3a3a" stroke="#111" stroke-width="1.5"/>'
         '<line x1="10" y1="10" x2="10" y2="70" stroke="#777" stroke-width="1.5" stroke-dasharray="3,3"/>'
         '<line x1="50" y1="10" x2="50" y2="70" stroke="#777" stroke-width="1.5" stroke-dasharray="3,3"/>'
         '<circle cx="30" cy="40" r="15" fill="#151515" stroke="#666" stroke-width="2"/>' +
         "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#c3b0e0" stroke="#4a2d7a"/>' for x in (10, 50) for y in (10, 70)))
    return part("Push button 6x6 (straddle channel; dashed = always linked, press links left↔right)",
                60, 80, b, [(10, 10), (50, 10), (10, 70), (50, 70)], "button")

def push_button_12x6():
    """Push button of the Freenove FNK0020 kit: body 12 x 6 mm (≈ 94 x 47 px). Legs 5 holes apart across the
    channel (rows d / g) and 2 holes apart along it. Pins on the same side (dashed) are always linked."""
    b = ('<line x1="10" y1="4" x2="10" y2="116" stroke="#9a9a9a" stroke-width="3"/>'
         '<line x1="50" y1="4" x2="50" y2="116" stroke="#9a9a9a" stroke-width="3"/>'
         '<rect x="6.5" y="13" width="47" height="94" rx="4" fill="#3a3a3a" stroke="#111" stroke-width="1.5"/>'
         '<line x1="12" y1="18" x2="12" y2="102" stroke="#777" stroke-width="1.5" stroke-dasharray="3,3"/>'
         '<line x1="48" y1="18" x2="48" y2="102" stroke="#777" stroke-width="1.5" stroke-dasharray="3,3"/>'
         '<rect x="15" y="40" width="30" height="40" rx="5" fill="#151515" stroke="#666" stroke-width="2"/>'
         '<circle cx="30" cy="60" r="11" fill="#202020" stroke="#555" stroke-width="1.5"/>' +
         "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#c3b0e0" stroke="#4a2d7a"/>' for x in (10, 50) for y in (10, 110)))
    return part("Push button 12x6 mm, Freenove kit (legs rows d / g, 2 holes apart; dashed = always linked)",
                60, 120, b, [(10, 10), (50, 10), (10, 110), (50, 110)], "button")

def slide_switch():
    b = ('<rect x="2" y="6" width="56" height="20" rx="3" fill="#b8bcc0" stroke="#666"/>'
         '<rect x="12" y="10" width="16" height="12" rx="2" fill="#222"/>' + "".join(pinmark(x, 30) + lead(x, 26, x, 30) for x in (10, 30, 50)))
    return part("Slide switch SPDT (3 pins)", 60, 40, b, [(10, 30), (30, 30), (50, 30)], "switch")

def relay(rotated=False):
    # HK4100F top view. Pin map (LCSC C12072 / HKE datasheet): 1 NO, 2 NC, 3-4 coil, 5-6 COM (linked)
    pins = {"NO 1": (10, 10), "NC 2": (10, 70), "3": (30, 10), "4": (30, 70), "COM 5": (110, 10), "COM 6": (110, 70)}
    if rotated:
        pins = {k: (120 - x, 80 - y) for k, (x, y) in pins.items()}
    b = ['<rect x="1" y="1" width="118" height="78" rx="4" fill="#f2b632" stroke="#8a6200" stroke-width="2"/>']
    cx = 120 - 30 if rotated else 30
    comx = 10 if rotated else 110
    b.append(f'<line x1="{cx}" y1="18" x2="{cx}" y2="62" stroke="#8a6200" stroke-width="1.5"/>'
             f'<rect x="{cx-6}" y="28" width="12" height="24" fill="#fff6dc" stroke="#8a6200"/>')
    b.append(f'<line x1="{comx}" y1="18" x2="{comx}" y2="62" stroke="#8a6200" stroke-width="2" stroke-dasharray="4,3"/>')
    b.append(T(60, 37, "HK4100F", 11, "#3a2a00", "bold") + T(60, 49, "DC5V-SHG", 8, "#3a2a00"))
    for name, (x, y) in pins.items():
        b.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#d9d9d9" stroke="#555"/>')
        lab = "coil" if name in ("3", "4") else name.split()[0]
        ty = y + 14 if y < 40 else y - 8
        b.append(T(x, ty, lab, 7.5, "#3a2a00", "bold"))
    t = "Relay HK4100F-DC5V-SHG" + (" (rotated 180°: COM left)" if rotated else " (COM right)")
    return part(t + " — straddle channel", 120, 80, "".join(b), list(pins.values()), "relay")

# --------------------------------------------------------------------------- power
def battery9v():
    b = ('<rect x="6" y="22" width="68" height="116" rx="6" fill="#2b2b2b" stroke="#111" stroke-width="1.5"/>'
         '<rect x="6" y="60" width="68" height="46" fill="#f2a33a"/>'
         '<rect x="6" y="22" width="68" height="14" rx="4" fill="#9aa3ab"/>' +
         T(40, 90, "9V", 22, "#1b1b1b", "bold") +
         '<circle cx="30" cy="12" r="6" fill="#d9dde0" stroke="#555" stroke-width="1.5"/>'
         '<polygon points="50,4 57,8 57,16 50,20 43,16 43,8" fill="#d9dde0" stroke="#555" stroke-width="1.5"/>' +
         T(19, 15, "+", 12, "#d62728", "bold") + T(64, 15, "−", 13, "#111", "bold"))
    return part("Battery 9 V (+ / − snap terminals)", 80, 140, b, [(30, 10), (50, 10)], "9 V")

def battery_aa2():
    b = ('<rect x="2" y="2" width="136" height="76" rx="5" fill="#1f1f1f"/>'
         '<rect x="10" y="10" width="110" height="26" rx="12" fill="#c9a227"/><rect x="10" y="44" width="110" height="26" rx="12" fill="#c9a227"/>' +
         T(65, 28, "AA 1.5V", 10, "#222", "bold") + T(65, 62, "AA 1.5V", 10, "#222", "bold") +
         lead(130, 30, 150, 30).replace("#9a9a9a", "#d62728") + lead(130, 50, 150, 50).replace("#9a9a9a", "#111") +
         pinmark(150, 30) + pinmark(150, 50) + T(144, 24, "+", 10, "#d62728", "bold") + T(144, 64, "−", 11, "#111", "bold"))
    return part("Battery holder 2x AA (3 V): + top lead / − bottom lead", 160, 80, b, [(150, 30), (150, 50)], "2x AA")

def screw_terminal(n):
    w = 40*n + 20 - 40 + 20
    w = P*2*(n-1) + 20
    b = [f'<rect x="1" y="1" width="{w-2}" height="58" rx="3" fill="#2f74c0" stroke="#174a85" stroke-width="1.5"/>']
    pins = []
    for k in range(n):
        x = 10 + 2*P*k
        pins.append((x, 50))
        b.append(f'<circle cx="{x}" cy="20" r="8" fill="#c8ccd0" stroke="#555"/><line x1="{x-5}" y1="20" x2="{x+5}" y2="20" stroke="#444" stroke-width="2"/>'
                 f'<rect x="{x-6}" y="34" width="12" height="8" fill="#174a85"/>' + pinmark(x, 50))
    return part(f"Screw terminal {n} pins (5.08 mm pitch = 2 holes)", w, 60, "".join(b), pins, f"{n}P terminal")

# --------------------------------------------------------------------------- semis & misc
def transistor(kind):
    # E / B / C: bold dark letters on a white box, same look as the part labels (LABEL)
    pin_lab = "".join(f'<rect x="{x - 6.5}" y="46" width="13" height="13" fill="#ffffff" stroke="#9aa3ab" stroke-width="1"/>'
                      + T(x, 56.5, s, 11, "#111111", "bold") for x, s in ((10, "E"), (30, "B"), (50, "C")))
    b = ('<path d="M 4 30 L 4 16 A 26 26 0 0 1 56 16 L 56 30 Z" fill="#1f1f1f" stroke="#000"/>' + T(30, 24, kind, 10, "#ddd", "bold") +
         "".join(lead(x, 30, x, 42) + pinmark(x, 42) for x in (10, 30, 50)) + pin_lab)
    return part(f"{kind} transistor TO-92 (E B C, flat face front — check your part)", 60, 60, b, [(10, 42), (30, 42), (50, 42)], kind)

def potentiometer():
    b = ('<rect x="4" y="6" width="92" height="48" rx="6" fill="#2f74c0" stroke="#174a85"/>'
         '<circle cx="50" cy="30" r="19" fill="#e9e9e9" stroke="#777" stroke-width="2"/><line x1="50" y1="30" x2="50" y2="13" stroke="#444" stroke-width="3"/>' +
         "".join(lead(x, 54, x, 70) + pinmark(x, 70) for x in (10, 50, 90)))
    return part("Potentiometer 10 kΩ (3 pins, 2 holes apart)", 100, 80, b, [(10, 70), (50, 70), (90, 70)], "10 kΩ")

def buzzer():
    b = ('<circle cx="40" cy="40" r="36" fill="#1b1b1b" stroke="#000"/><circle cx="40" cy="40" r="5" fill="#555"/>' +
         pinmark(10, 40) + pinmark(70, 40) + T(10, 24, "+", 13, "#ff5a4f", "bold"))
    return part("Buzzer 12 mm (pins 3 holes apart, + left)", 80, 80, b, [(10, 40), (70, 40)], "buzzer")

def ldr():
    b = (lead(10, 50, 10, 30) + lead(30, 50, 30, 30) + pinmark(10, 50) + pinmark(30, 50) +
         '<circle cx="20" cy="18" r="14" fill="#e8d9b0" stroke="#8a6a3a" stroke-width="1.5"/>'
         '<path d="M 11 12 H 29 M 11 18 H 29 M 11 24 H 29 M 14 12 V 18 M 26 18 V 24" stroke="#b5452b" stroke-width="2" fill="none"/>')
    return part("Photoresistor (LDR)", 40, 60, b, [(10, 50), (30, 50)], "LDR")

ESP_L = ["EN", "VP", "VN", "D34", "D35", "D32", "D33", "D25", "D26", "D27", "D14", "D12", "D13", "GND", "VIN"]
ESP_R = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "TX2", "RX2", "D4", "D2", "D15", "GND", "3V3"]
def esp32():
    w, h = 220, 420
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="8" fill="#161616" stroke="#000" stroke-width="2"/>',
         '<rect x="50" y="10" width="120" height="120" rx="4" fill="#202020" stroke="#555"/>',
         '<path d="M 62 22 v 22 h 14 v -22 h 14 v 22 h 14 v -22 h 14 v 22 h 14 v -22 h 14" stroke="#c9a227" stroke-width="4" fill="none"/>',
         '<rect x="62" y="56" width="96" height="66" rx="3" fill="#b9c0c7"/>', T(110, 92, "ESP32-WROOM-32", 9, "#333", "bold"),
         T(110, 200, "ESP32", 18, "#fff", "bold"), T(110, 218, "DevKit · 30 pins", 10, "#bbb"),
         '<rect x="88" y="392" width="44" height="26" rx="3" fill="#b9c0c7"/>']
    pins = []
    for k in range(15):
        y = 70 + P*k
        for x, name, anchor, tx in ((10, ESP_L[k], "start", 22), (210, ESP_R[k], "end", 198)):
            pins.append((x, y))
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#d4a017" stroke="#7a5a00"/><circle cx="{x}" cy="{y}" r="2.5" fill="#222"/>')
            b.append(T(tx, y+3.5, name, 9, "#e8e8e8", "bold" if name in ("GND", "3V3", "VIN") else "normal", anchor))
    return part("ESP32 DevKit 30 pins (rows 10 holes apart)", w, h, "".join(b), pins, "")


# --------------------------------------------------------------------------- vertical breadboard + modules
BBV_W, BBV_H = 400, 720
BBV_COLS = {"L+": 30, "L-": 50, "a": 90, "b": 110, "c": 130, "d": 150, "e": 170,
            "f": 230, "g": 250, "h": 270, "i": 290, "j": 310, "R+": 350, "R-": 370}
def bbv_y(row): return 50 + P*row        # row 1..30 (rails also have rows 0 and 31)
def breadboard_vertical():
    W_, H_ = BBV_W, BBV_H
    b = [f'<rect x="1" y="1" width="{W_-2}" height="{H_-2}" rx="8" fill="#fbfbf8" stroke="#9aa0a6" stroke-width="2"/>',
         f'<rect x="186" y="20" width="28" height="{H_-40}" fill="#e4e6e4"/>',
         f'<rect x="198" y="20" width="4" height="{H_-40}" fill="#b9bdbb"/>']
    for x, c in ((19, "#e05a5a"), (61, "#3d8fd6"), (339, "#e05a5a"), (381, "#3d8fd6")):
        b.append(f'<rect x="{x}" y="24" width="2.5" height="{H_-48}" fill="{c}"/>')
    for k, x in BBV_COLS.items():
        if k.endswith("+"): b.append(T(x, 22, "+", 14, "#d62728", "bold")); b.append(T(x, H_-8, "+", 14, "#d62728", "bold"))
        elif k.endswith("-"): b.append(T(x, 22, "−", 14, "#1f6fd0", "bold")); b.append(T(x, H_-8, "−", 14, "#1f6fd0", "bold"))
        else: b.append(T(x, bbv_y(0)+4.5, k, 13, LBL, "bold")); b.append(T(x, bbv_y(31)+4.5, k, 13, LBL, "bold"))
    pins = []
    for r in range(0, 32):
        y = bbv_y(r)
        if 1 <= r <= 30 and (r == 1 or r % 5 == 0):
            b.append(T(72, y+4, str(r), 12, LBL, "bold")); b.append(T(330, y+4, str(r), 12, LBL, "bold"))
        for k, x in BBV_COLS.items():
            if len(k) == 1 and not 1 <= r <= 30: continue
            pins.append((x, y))
            b.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" rx="1.5" fill="#d4d6d6"/>'
                     f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="#4a4a4a"/>')
    p = part("Breadboard half VERTICAL (30 rows, rails extended) — every hole is a connection point", W_, H_, "".join(b), pins)
    p["holes"] = {}
    i = 0
    for r in range(0, 32):
        for k in BBV_COLS:
            if len(k) == 1 and not 1 <= r <= 30: continue
            p["holes"][(k, r)] = i; i += 1
    return p

MPU_PINS = ["VCC", "GND", "SCL", "SDA", "XDA", "XCL", "AD0", "INT"]
def mpu6050():
    w, h = 140, 200
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="6" fill="#2f78c4" stroke="#174a85" stroke-width="2"/>',
         '<circle cx="118" cy="20" r="8" fill="#e8eef5" stroke="#9fb3c8"/><circle cx="118" cy="180" r="8" fill="#e8eef5" stroke="#9fb3c8"/>',
         '<rect x="78" y="62" width="40" height="40" fill="#151515"/><circle cx="84" cy="68" r="2" fill="#666"/><circle cx="124" cy="112" r="3" fill="#e53935"/>',
         T(98, 132, "MPU-6050", 12, "#ffffff", "bold"), T(98, 147, "GY-521", 9, "#d8e8f6")]
    pins = []
    for k, name in enumerate(MPU_PINS):
        y = 30 + P*k; pins.append((10, y))
        b.append(f'<rect x="2" y="{y-8}" width="16" height="16" fill="#111"/><rect x="7" y="{y-3}" width="6" height="6" fill="#d4a017"/>')
        b.append(T(24, y+3.5, name, 9, "#ffffff", "bold", "start"))
    return part("MPU-6050 accelerometer/gyro module GY-521 (I²C 0x68)", w, h, "".join(b), pins, "MPU-6050 · I²C 0x68")

OLED_PINS = ["GND", "VCC", "SCL", "SDA"]
def oled096():
    w, h = 200, 200
    b = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="6" fill="#1e5bb5" stroke="#123e7f" stroke-width="2"/>']
    for cx, cy in ((16, 16), (184, 16), (16, 184), (184, 184)):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#e8eef5" stroke="#9fb3c8"/>')
    b.append('<rect x="14" y="48" width="172" height="112" rx="3" fill="#111"/><rect x="22" y="56" width="156" height="92" fill="#050a1e"/>'
             '<rect x="80" y="164" width="40" height="18" fill="#c9a227"/>' + T(100, 106, "128×64 · I²C", 10, "#4fd1ff"))
    pins = []
    for k, name in enumerate(OLED_PINS):
        x = 70 + P*k; pins.append((x, 10))
        b.append(f'<rect x="{x-8}" y="2" width="16" height="16" fill="#111"/><circle cx="{x}" cy="10" r="3.5" fill="#e0e0e0"/>')
        b.append(T(x, 32, name, 8, "#ffffff", "bold"))
    return part("OLED 0.96\" 128x64 I²C (SSD1306, 0x3C) — pins GND VCC SCL SDA", w, h, "".join(b), pins, "OLED 0.96\" · I²C 0x3C")

def trimmer3386():
    b = ('<rect x="3" y="3" width="54" height="54" rx="4" fill="#2f74c0" stroke="#174a85" stroke-width="1.5"/>'
         '<circle cx="36" cy="30" r="15" fill="#e2c46a" stroke="#7a5d18" stroke-width="1.5"/>'
         '<path d="M 28 30 H 44 M 36 22 V 38" stroke="#7a5d18" stroke-width="3" stroke-linecap="round"/>' +
         "".join(f'<circle cx="10" cy="{y}" r="3.5" fill="#c3b0e0" stroke="#4a2d7a"/>' for y in (10, 30, 50)))
    return part("Trimmer potentiometer 3386P (3 pins in line, 1 hole apart)", 60, 60, b, [(10, 10), (10, 30), (10, 50)], "10 kΩ")

def ldr2():
    b = (lead(10, 50, 20, 34) + lead(50, 50, 40, 34) + pinmark(10, 50) + pinmark(50, 50) +
         '<circle cx="30" cy="22" r="15" fill="#e8d9b0" stroke="#8a6a3a" stroke-width="1.5"/>'
         '<path d="M 21 16 H 39 M 21 22 H 39 M 21 28 H 39 M 24 16 V 22 M 36 22 V 28" stroke="#b5452b" stroke-width="2" fill="none"/>')
    return part("Photoresistor (LDR), legs 2 holes apart", 60, 60, b, [(10, 50), (50, 50)], "LDR")

# --------------------------------------------------------------------------- wires
WIRES = [("red", "#d62728"), ("black", "#1b1b1b"), ("yellow", "#f2c200"), ("green", "#2ca02c"), ("blue", "#1f77b4"),
         ("orange", "#f28e1c"), ("white", "#f4f4f4"), ("purple", "#8e44ad"), ("brown", "#8c564b"), ("grey", "#8a8a8a")]
def wire_style(color, ortho=False):
    return ("endArrow=oval;startArrow=oval;startFill=1;endFill=1;startSize=6;endSize=6;html=1;"
            f"strokeWidth=4;strokeColor={color};rounded=1;arcSize=20;jumpStyle=arc;jumpSize=10;"
            + ("edgeStyle=orthogonalEdgeStyle;" if ortho else "edgeStyle=none;"))

# --------------------------------------------------------------------------- build library
bb = breadboard(); perfboard(); pad()
r100 = resistor("100 Ω", 100); r220 = resistor("220 Ω", 220); r470 = resistor("470 Ω", 470); r1k = resistor("1 kΩ", 1_000); resistor("10 kΩ", 10_000)
diode("1N4007", "#202020", "#cfd3d6", "Diode 1N4007 rectifier")
d4007 = diode("1N4007", "#202020", "#cfd3d6", "Diode 1N4007 rectifier", band_left=True)
diode("1N4148", "#e8603a", "#111", "Diode 1N4148 signal"); diode("1N4148", "#e8603a", "#111", "Diode 1N4148 signal", band_left=True)
ledr = led("#ff3b30", "red", "#ffc2bd"); led("#34c759", "green", "#c8f5d2"); led("#2f7bf5", "blue", "#c9dcff"); led("#ffd60a", "yellow", "#fff3b0"); led("#f2f2f2", "white", "#ffffff")
cap_ceramic(); cap_electrolytic()
btn = push_button(); btn12 = push_button_12x6(); slide_switch(); rel = relay(); relr = relay(rotated=True)
bat = battery9v(); battery_aa2(); screw_terminal(2); screw_terminal(3)
transistor("NPN"); transistor("PNP"); potentiometer(); buzz = buzzer(); ldr(); esp = esp32()
bbv = breadboard_vertical(); mpu = mpu6050(); oled = oled096(); trim = trimmer3386(); ldr_2 = ldr2()
r10k = [p for p in PARTS if p["title"].startswith("Resistor 10 kΩ")][0]

# --------------------------------------------------------------------------- breadboard power module (BPM)
# HW-131 module of the Freenove FNK0020 kit, drawn from a photo: DC jack, push switch, green LED, USB-A,
# two SOT-223 regulators, 5V / 3.3V / GND header, one "5V OFF 3.3" jumper per side.
# Drawn for the VERTICAL board (400 x 250): rail pins at x 30/50 (left + −) and 350/370 (right + −),
# two pins per rail at y 150 and 230 (4 holes apart). DC plug enters at the top-left (pins 8, 9).
BPM_W, BPM_H = 400, 250
def _bpm_body():
    W = "#f2f2f2"
    def t(x, y, s, size=9, anchor="middle", color=W, weight="bold"): return T(x, y, s, size, color, weight, anchor)
    b = ['<path d="M 6 2 H 394 V 216 L 394 246 L 330 246 L 320 236 H 80 L 70 246 L 6 246 Z" fill="#141414" stroke="#000" stroke-width="2"/>',
         # DC jack (top-left), plug from the top
         '<rect x="2" y="0" width="92" height="134" rx="4" fill="#222" stroke="#000"/><rect x="14" y="0" width="68" height="20" fill="#0d0d0d"/>',
         '<circle cx="48" cy="70" r="24" fill="#2e2e2e" stroke="#555" stroke-width="2"/><circle cx="48" cy="70" r="6" fill="#999"/>',
         t(48, 124, "DC-10", 9, color="#888"),
         # push switch (latching)
         '<rect x="98" y="8" width="72" height="80" rx="3" fill="#c9c9c4" stroke="#777"/><rect x="116" y="20" width="36" height="50" rx="2" fill="#efefea" stroke="#999"/>',
         '<rect x="104" y="94" width="58" height="34" fill="none" stroke="#ddd" stroke-width="1.5"/>',
         # green LED + SMD resistor, electrolytic capacitor
         '<circle cx="198" cy="51" r="12" fill="#3fd25a" stroke="#1b7a2c" stroke-width="2"/><circle cx="194" cy="47" r="4" fill="#b9f5c4"/>',
         '<rect x="232" y="44" width="10" height="16" fill="#222" stroke="#ddd"/>',
         '<circle cx="198" cy="94" r="18" fill="#1e1e1e" stroke="#555" stroke-width="2"/><circle cx="198" cy="94" r="12" fill="#e6e6e6"/>',
         # USB-A female (top-right)
         '<rect x="254" y="12" width="122" height="122" rx="3" fill="#c3c6c9" stroke="#777" stroke-width="1.5"/>',
         '<rect x="276" y="34" width="26" height="50" rx="2" fill="#9ea2a6"/><rect x="330" y="34" width="26" height="50" rx="2" fill="#9ea2a6"/>',
         f'<text x="392" y="64" font-size="13" fill="{W}" font-weight="bold" text-anchor="middle" transform="rotate(-90 392 64)">HW-131</text>',
         # 5V / 3.3V / GND header (4 x 2 pins)
         t(120, 175, "5V", 9, "end"), t(120, 207, "3.3V", 9, "end"),
         f'<text x="186" y="182" font-size="8" fill="{W}" font-weight="bold" text-anchor="middle" transform="rotate(-90 186 182)">GND</text>']
    for y in (148, 170, 194, 216):
        b.append(f'<rect x="132" y="{y - 9}" width="44" height="18" rx="2" fill="#efd27a" stroke="#a88a2a"/>'
                 f'<circle cx="143" cy="{y}" r="3" fill="#7a5d18"/><circle cx="165" cy="{y}" r="3" fill="#7a5d18"/>')
    # two SOT-223 regulators (no readable marking) + SMD capacitors
    for x0 in (192, 252):
        b.append(f'<rect x="{x0 + 6}" y="138" width="34" height="16" fill="#cfd2d4" stroke="#888"/>'
                 f'<rect x="{x0}" y="152" width="46" height="26" fill="#1c1c1c" stroke="#444"/>'
                 + "".join(f'<rect x="{x0 + 4 + 16 * k}" y="182" width="9" height="10" fill="#cfd2d4"/>' for k in range(3)))
    for x0 in (194, 226, 258):
        b.append(f'<rect x="{x0}" y="204" width="26" height="14" fill="none" stroke="#ddd"/><rect x="{x0 + 8}" y="207" width="10" height="8" fill="#b08a5a"/>')
    # jumpers "5V OFF 3.3" (cap on 5V) on each side
    for x0, labs in ((10, (("5V", 18), ("OFF", 52), ("3.3", 92))), (306, (("5V", 314), ("OFF", 348), ("3.3", 384)))):
        b.append(f'<rect x="{x0}" y="190" width="86" height="22" rx="2" fill="#efd27a" stroke="#a88a2a"/>'
                 + "".join(f'<circle cx="{x0 + 11 + 21 * k}" cy="201" r="3" fill="#7a5d18"/>' for k in range(4))
                 + f'<rect x="{x0 + 2}" y="186" width="40" height="30" rx="3" fill="#f3e3a6" stroke="#a88a2a"/>')
        b.append("".join(t(x, 182, s, 9) for s, x in labs))
    # rail pins: two per rail (y 150 and 230), labels + / −
    for x, lab in ((30, "+"), (50, "−"), (350, "+"), (370, "−")):
        for y in (150, 230):
            b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#111" stroke="#bbb" stroke-width="1.5"/><circle cx="{x}" cy="{y}" r="3" fill="#d4a017"/>')
        b.append(t(x + 12, 216, lab, 11, color="#ffffff"))
    return "".join(b)
_BPM_PINS_V = [(30, 230), (50, 230), (350, 230), (370, 230), (30, 150), (50, 150), (350, 150), (370, 150), (56, 0), (40, 0)]
def bpm(horizontal=False):
    """BPM part. pins: 0 L+ 1 L− 2 R+ 3 R− (y 230) · 4-7 same rails at y 150 · 8/9 DC plug + / −.
    horizontal=True: rotated for the horizontal board (250 x 400), left of the board:
    L+ → b+ (y 370), L− → b− (350), R+ → t+ (50), R− → t− (30); pins at x 230 and 150; DC plug on the left edge."""
    body = _bpm_body()
    if not horizontal:
        return part("Breadboard power module BPM HW-131 (vertical board)", BPM_W, BPM_H, body, _BPM_PINS_V)
    pins = [(y, BPM_W - x) for x, y in _BPM_PINS_V]
    return part("Breadboard power module BPM HW-131 (horizontal board, plug on the left)", BPM_H, BPM_W,
                f'<g transform="matrix(0,-1,1,0,0,{BPM_W})">{body}</g>', pins)
bpm_v = bpm(); bpm_h = bpm(horizontal=True)

def vertex_xml(p, cid="2", x=0, y=0, extra=""):
    return (f'<mxCell id="{cid}" value="{esc(p["value"])}" style="{p["style"]}{extra}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{p["w"]}" height="{p["h"]}" as="geometry"/></mxCell>')
def model(cells): return f'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{cells}</root></mxGraphModel>'

def main():
    entries = [dict(xml=compress(model(vertex_xml(p))), w=p["w"], h=p["h"], aspect="fixed", title=p["title"]) for p in PARTS]
    for ortho in (False, True):
        for name, c in WIRES:
            cell = (f'<mxCell id="2" value="" style="{wire_style(c, ortho)}" edge="1" parent="1"><mxGeometry width="120" relative="1" as="geometry">'
                    f'<mxPoint x="0" y="10" as="sourcePoint"/><mxPoint x="120" y="10" as="targetPoint"/></mxGeometry></mxCell>')
            entries.append(dict(xml=compress(model(cell)), w=120, h=20, title=f"Wire {name}" + (" (orthogonal routing)" if ortho else " (straight, add bends)")))
    with open(os.path.join(HERE, "breadboard-electronics.xml"), "w") as f:
        f.write("<mxlibrary>" + json.dumps(entries, ensure_ascii=False) + "</mxlibrary>\n")

    # --------------------------------------------------------------------------- demo: relay + LED on 9 V, built only from library parts
    BX, BY = 200, 100
    cells, n = [], [10]
    def hole(col, row): return BX + bb_x(col), BY + BB_ROWS[row]
    def place(p, pin, col, row):
        hx, hy = hole(col, row); px, py = p["pins"][pin]
        n[0] += 1; cid = f"p{n[0]}"
        cells.append(vertex_xml(p, cid, hx - px, hy - py)); return cid
    def pin_ref(p, i): x, y = p["pins"][i]; return x / p["w"], y / p["h"]
    def bb_ref(col, row): return bb_x(col) / BB_W, BB_ROWS[row] / BB_H
    def wire(color, src, sref, dst, dref, pts=()):
        n[0] += 1
        arr = f'<Array as="points">{"".join(f"<mxPoint x=\"{x}\" y=\"{y}\"/>" for x, y in pts)}</Array>' if pts else ""
        st = (wire_style(color) + f"exitX={sref[0]:.5f};exitY={sref[1]:.5f};exitDx=0;exitDy=0;exitPerimeter=0;"
              f"entryX={dref[0]:.5f};entryY={dref[1]:.5f};entryDx=0;entryDy=0;entryPerimeter=0;")
        cells.append(f'<mxCell id="w{n[0]}" value="" style="{st}" edge="1" parent="1" source="{src}" target="{dst}">'
                     f'<mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')

    cells.append(vertex_xml(bb, "bb", BX, BY))
    B = "bb"
    batt = place(bat, 0, 1, "t+"); cells.pop()                       # place battery off-board instead:
    n[0] += 1; batt = f"p{n[0]}"; cells.append(vertex_xml(bat, batt, 40, 160))
    b1 = place(btn, 0, 3, "f")                                       # button cols 3/5
    ra = place(r100, 0, 5, "h")                                      # 100R  col5 -> col9
    k1 = place(relr, 5, 14, "f")                                     # pin 5 = COM 6 at (10,10) after rotation                                     # relay COM col14, coil col18, NC/NO col19
    dd = place(d4007, 0, 18, "h")                                    # band-left variant: cathode col18, anode col22
    rb = place(r1k, 0, 19, "c")                                      # 1k   col19 -> col23 (bottom half)
    l1 = place(ledr, 0, 23, "d")                                     # LED anode col23, cathode col24
    R, K, O = "#d62728", "#1b1b1b", "#f28e1c"
    wire(R, batt, pin_ref(bat, 0), B, bb_ref(1, "t+"), [(70, 130)])
    wire(K, batt, pin_ref(bat, 1), B, bb_ref(1, "t-"), [(90, 150)])
    wire(R, B, bb_ref(30, "t+"), B, bb_ref(30, "b+"), [(880, 130), (880, 470)])
    wire(K, B, bb_ref(30, "t-"), B, bb_ref(30, "b-"), [(860, 150), (860, 450)])
    wire(R, B, bb_ref(3, "t+"), B, bb_ref(3, "j"))                    # + rail -> button
    wire(O, B, bb_ref(9, "i"), B, bb_ref(18, "i"))                    # 100R -> coil (pin 4)
    wire(K, B, bb_ref(22, "j"), B, bb_ref(22, "t-"))                  # diode anode -> - rail
    wire(R, B, bb_ref(14, "j"), B, bb_ref(14, "t+"))                  # COM -> + rail
    wire(K, B, bb_ref(18, "a"), B, bb_ref(18, "b-"))                  # coil (pin 3) -> - rail
    wire(K, B, bb_ref(24, "a"), B, bb_ref(24, "b-"))                  # LED cathode -> - rail
    def text(x, y, s, size=13, bold=False):
        n[0] += 1
        cells.append(f'<mxCell id="t{n[0]}" value="{esc(s)}" style="text;html=1;align=left;verticalAlign=middle;fontSize={size};fontStyle={1 if bold else 0};fontColor=#1d2a3a;" vertex="1" parent="1">'
                     f'<mxGeometry x="{x}" y="{y}" width="{len(s)*size*0.6+10}" height="{size*1.8}" as="geometry"/></mxCell>')
    text(200, 20, "Demo — HK4100F relay + LED on a 9 V battery (built from breadboard-electronics.xml)", 18, True)
    text(200, 52, "Button cols 3/5 · 100 Ω cols 5–9 · relay COM col 14, coil col 18, NO col 19 (bottom) · 1N4007 cols 18–22 · 1 kΩ cols 19–23 · LED cols 23/24", 12)
    demo = ('<mxfile host="app.diagrams.net"><diagram name="demo" id="demo"><mxGraphModel dx="1000" dy="600" grid="1" gridSize="10" guides="1" '
            'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1000" pageHeight="560" background="#ffffff" math="0" shadow="0">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>\n')
    with open(os.path.join(HERE, "demo-relay-led.drawio"), "w") as f:
        f.write(demo)
    print(f"{len(PARTS)} parts + {2*len(WIRES)} wires -> breadboard-electronics.xml ; demo-relay-led.drawio")

if __name__ == "__main__":
    main()

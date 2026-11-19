#!/usr/bin/env python3
"""Generate catalog.drawio — every part of breadboard-electronics.xml laid out on a grid with its title.

Usage:  python3 gen_catalog.py
        drawio -x -f png -s 1 -o catalog.png catalog.drawio      # export to PNG (draw.io desktop CLI)
"""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_lib as L  # noqa: E402

MAX_W, GAP_X, GAP_Y, LABEL_H, MARGIN = 1800, 50, 40, 46, 40
cells, n = [], [0]

def nid(p):
    n[0] += 1
    return f"{p}{n[0]}"

def text(x, y, w, s, size=11, bold=False, align="center"):
    cells.append(f'<mxCell id="{nid("t")}" value="{L.esc(s)}" style="text;html=1;whiteSpace=wrap;align={align};verticalAlign=top;'
                 f'fontSize={size};fontStyle={1 if bold else 0};fontColor=#1d2a3a;" vertex="1" parent="1">'
                 f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{LABEL_H}" as="geometry"/></mxCell>')

text(MARGIN, 10, 1200, f"breadboard-electronics.xml — {len(L.PARTS)} parts + {2 * len(L.WIRES)} wires (1 hole = 20 px = 2.54 mm)",
     20, True, "left")

x, y, row_h = MARGIN, 70, 0
for i, p in enumerate(L.PARTS, 1):
    slot_w = max(p["w"], 170)
    if x + slot_w > MAX_W and x > MARGIN:
        x, y, row_h = MARGIN, y + row_h + GAP_Y, 0
    px = x + (slot_w - p["w"]) / 2
    cells.append(L.vertex_xml(p, nid("p"), px, y))
    label_y = y + p["h"] + (20 if p["value"] else 6)
    text(x, label_y, slot_w, f"{i}. {p['title']}", 10)
    row_h = max(row_h, label_y - y + LABEL_H)
    x += slot_w + GAP_X

# wires: one sample per colour (straight style)
x, y = MARGIN, y + row_h + GAP_Y
text(x, y, 400, "Wires (straight + orthogonal variants in the library)", 13, True, "left")
y += 30
for name, c in L.WIRES:
    if x + 160 > MAX_W:
        x, y = MARGIN, y + 60
    cells.append(f'<mxCell id="{nid("w")}" value="" style="{L.wire_style(c, False)}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x}" y="{y + 10}" as="sourcePoint"/><mxPoint x="{x + 120}" y="{y + 10}" as="targetPoint"/></mxGeometry></mxCell>')
    text(x, y + 20, 120, name, 10)
    x += 160

doc = ('<mxfile host="app.diagrams.net"><diagram name="catalog" id="catalog"><mxGraphModel grid="1" gridSize="10" page="0" '
       'background="#ffffff"><root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) +
       '</root></mxGraphModel></diagram></mxfile>\n')
with open(os.path.join(HERE, "catalog.drawio"), "w") as f:
    f.write(doc)
print(f"{len(L.PARTS)} parts -> catalog.drawio")

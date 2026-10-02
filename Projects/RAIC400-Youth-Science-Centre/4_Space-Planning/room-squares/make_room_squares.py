"""Room squares for paper space planning — Cairn Youth Centre, program v0.7 (00_Brief.md, 2026-09-29).

Every room is drawn as a square of side sqrt(net area). Outputs:
  Cairn_Room-Squares.dxf            model space at 1:1, metres, one block per room type, one layer per zone
  Cairn_Room-Squares_1-100_Tabloid.pdf   true scale 1:100 on 11x17 landscape
  Cairn_Room-Squares_1-200_Letter.pdf    true scale 1:200 on 8.5x11 landscape
Print PDFs at 100% / "Actual size" and check the 100 mm test bar.

Run: python make_room_squares.py
"""
import math
from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent

# (zone, room, count, net m2 each) — straight from Program v0.7
ZONES = {
    "PUBLIC": ((0.99, 0.87, 0.74), 30),        # fill RGB, DXF ACI colour
    "SEMI-PUBLIC": ((0.99, 0.95, 0.74), 2),
    "PRIVATE": ((0.80, 0.91, 0.99), 4),
    "EXPEDITION": ((0.82, 0.95, 0.82), 3),
    "SERVICE": ((0.90, 0.88, 0.95), 6),
    "MECHANICAL": ((0.88, 0.88, 0.88), 8),
}
ROOMS = [
    ("PUBLIC", "Flexible hall + gym", 1, 360),
    ("PUBLIC", "Entry hub", 1, 56),
    ("PUBLIC", "Public washrooms", 1, 28),
    ("SEMI-PUBLIC", "Science + field lab", 1, 130),
    ("SEMI-PUBLIC", "Maker + tech lab", 1, 111),
    ("SEMI-PUBLIC", "Dining (48)", 1, 72),
    ("SEMI-PUBLIC", "Classroom", 2, 46.5),
    ("SEMI-PUBLIC", "Staff workroom", 1, 45),
    ("SEMI-PUBLIC", "Staff + teachers", 1, 35),
    ("SEMI-PUBLIC", "Reception", 1, 19),
    ("SEMI-PUBLIC", "Office", 4, 14),
    ("PRIVATE", "Lounge (32)", 1, 84),
    ("PRIVATE", "Pod room (4 beds)", 8, 20),
    ("PRIVATE", "Laundry", 1, 20),
    ("PRIVATE", "Leader suite", 4, 18.6),
    ("PRIVATE", "Node washroom", 4, 18),
    ("PRIVATE", "Health room", 1, 16),
    ("PRIVATE", "Night station", 1, 14),
    ("PRIVATE", "Accessible WC", 2, 6.5),
    ("EXPEDITION", "Garage + vehicle bay", 1, 74),
    ("EXPEDITION", "Gear store", 1, 60),
    ("EXPEDITION", "Packing + boot room", 1, 50),
    ("EXPEDITION", "Gear wash + repair", 1, 20),
    ("EXPEDITION", "Drying room", 1, 16),
    ("SERVICE", "Kitchen + walk-in", 1, 60),
    ("SERVICE", "General storage", 1, 50),
    ("SERVICE", "Shipping + garbage", 1, 21),
    ("SERVICE", "Staff change", 1, 15),
    ("SERVICE", "Janitor + IT", 1, 10),
    ("MECHANICAL", "Mech + elec", 1, 70),
]
GYM_COURT = (24.0, 15.0)  # the court size the hall is actually sized from (reference outline)
NET = sum(n * a for _, _, n, a in ROOMS)
GROSS_FACTOR = 1.30


def instances():
    """One entry per physical room, numbered where count > 1."""
    out = []
    for zone, name, n, area in ROOMS:
        for i in range(n):
            base, _, tail = name.partition(" (")
            label = (f"{base} {i + 1}" + (f" ({tail}" if tail else "")) if n > 1 else name
            out.append((zone, name, label, area, math.sqrt(area)))
    return out


def fmt_side(s):
    return f"{s:.2f} x {s:.2f} m"


# ---------------------------------------------------------------- DXF (1:1, metres)
def make_dxf(path):
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 6  # metres
    doc.header["$MEASUREMENT"] = 1
    msp = doc.modelspace()
    for zone, (_, aci) in ZONES.items():
        doc.layers.add(f"ROOM-{zone}", color=aci)
    doc.layers.add("ROOM-TEXT", color=7)
    doc.layers.add("REF-COURT", color=1, linetype="DASHED")
    doc.layers.add("ANNO", color=7)

    # one block per room type, origin at the square's lower-left corner
    for zone, name, n, area in ROOMS:
        s = math.sqrt(area)
        blk = doc.blocks.new(name=f"RM_{name}".replace(" ", "_").replace("+", "and").replace("(", "").replace(")", ""))
        blk.add_lwpolyline([(0, 0), (s, 0), (s, s), (0, s)], close=True, dxfattribs={"layer": f"ROOM-{zone}"})
        info = f"{area:g} m2  ({s:.2f} m sq.)"
        # fit both lines inside the square (sized for ~0.95 h per character, a safe upper bound)
        h = min(0.6, s / 10, 0.85 * s / (0.95 * len(name)), 0.85 * s / (0.95 * 0.7 * len(info)))
        blk.add_text(name, height=h, dxfattribs={"layer": "ROOM-TEXT"}).set_placement(
            (s / 2, s / 2 + h * 0.8), align=TextEntityAlignment.MIDDLE_CENTER)
        blk.add_text(info, height=h * 0.7, dxfattribs={"layer": "ROOM-TEXT"}).set_placement(
            (s / 2, s / 2 - h * 0.6), align=TextEntityAlignment.MIDDLE_CENTER)

    # lay each zone out in a row, zones stacked downward, 2 m gaps
    gap, y = 2.0, 0.0
    msp.add_text("CAIRN YOUTH CENTRE - ROOM SQUARES (program v0.7, net areas, side = sqrt(area))",
                 height=1.0, dxfattribs={"layer": "ANNO"}).set_placement((0, 4))
    msp.add_text(f"Net {NET:,.0f} m2 x {GROSS_FACTOR} = gross {NET * GROSS_FACTOR:,.0f} m2. Units: metres. "
                 "Each room is a block: move/rotate freely.", height=0.6, dxfattribs={"layer": "ANNO"}).set_placement((0, 2.5))
    inst = instances()
    for zone in ZONES:
        rooms = [r for r in inst if r[0] == zone]
        row_h = max(r[4] for r in rooms)
        y -= row_h
        msp.add_text(zone, height=1.0, dxfattribs={"layer": "ANNO"}).set_placement((-12, y + row_h - 1))
        x = 0.0
        for _, name, label, area, s in rooms:
            bname = f"RM_{name}".replace(" ", "_").replace("+", "and").replace("(", "").replace(")", "")
            msp.add_blockref(bname, (x, y + row_h - s))
            x += s + gap
        if zone == "PUBLIC":  # reference outline of the real court next to the gym square
            w, d = GYM_COURT
            msp.add_lwpolyline([(x, y + row_h - d), (x + w, y + row_h - d), (x + w, y + row_h), (x, y + row_h)],
                               close=True, dxfattribs={"layer": "REF-COURT"})
            msp.add_text("REF: hall as 24 x 15 m court (same 360 m2)", height=0.5,
                         dxfattribs={"layer": "REF-COURT"}).set_placement((x + w / 2, y + row_h - d / 2),
                                                                           align=TextEntityAlignment.MIDDLE_CENTER)
        y -= gap * 3
    doc.saveas(path)


# ---------------------------------------------------------------- PDF (true scale)
def make_pdf(path, pagesize, scale, title_scale):
    W, H = pagesize
    margin, title_h, gap = 10 * mm, 16 * mm, 5 * mm
    k = 1000 * mm / scale  # PDF points per real metre
    c = canvas.Canvas(str(path), pagesize=pagesize)
    c.setTitle(f"Cairn Youth Centre - Room Squares {title_scale}")
    page = [0]

    def header():
        page[0] += 1
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, H - margin - 10, f"Cairn Youth Centre - room squares at {title_scale}")
        c.setFont("Helvetica", 7)
        c.drawString(margin, H - margin - 20,
                     f"Program v0.7 net areas; each square's side = sqrt(area). Net {NET:,.0f} m² × {GROSS_FACTOR} "
                     f"≈ gross {NET * GROSS_FACTOR:,.0f} m² (circulation + walls not shown). "
                     "PRINT AT 100% / ACTUAL SIZE.")
        # 100 mm test bar + scale bar, bottom right
        bx, by = W - margin - 100 * mm, margin
        c.setLineWidth(0.8)
        c.line(bx, by + 3 * mm, bx + 100 * mm, by + 3 * mm)
        for t in (0, 100):
            c.line(bx + t * mm, by + 1.5 * mm, bx + t * mm, by + 4.5 * mm)
        c.setFont("Helvetica", 6)
        c.drawString(bx, by + 5.5 * mm, "Print check: this bar must measure 100 mm")
        sb = 10  # scale bar length in metres
        sx = margin + 70 * mm
        for i in range(sb // 5):
            c.setFillColorRGB(0, 0, 0) if i % 2 == 0 else c.setFillColorRGB(1, 1, 1)
            c.rect(sx + i * 5 * k, by + 2 * mm, 5 * k, 2 * mm, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(sx, by + 5.5 * mm, "0")
        c.drawString(sx + 5 * k - 2, by + 5.5 * mm, "5")
        c.drawString(sx + sb * k - 4, by + 5.5 * mm, f"{sb} m")
        c.drawString(sx + sb * k + 8, by + 2.5 * mm, f"scale {title_scale}")
        # legend
        c.setFont("Helvetica", 5.5)
        col = 0
        for zone, (rgb, _) in ZONES.items():
            yy = by + (6 * mm if col < 3 else 1 * mm)
            xx = margin + (col % 3) * 22 * mm
            c.setFillColorRGB(*rgb)
            c.rect(xx, yy, 3 * mm, 3 * mm, fill=1, stroke=1)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(xx + 4 * mm, yy + 0.8 * mm, zone.title())
            col += 1
        c.drawRightString(W - margin, H - margin - 10, f"Sheet {page[0]}")

    def room(x, y, s_pt, label, area, s_m, rgb, dashed=False, zone=""):
        c.setFillColorRGB(*rgb)
        c.setLineWidth(0.6)
        if dashed:
            c.setDash(3, 2)
        c.rect(x, y, s_pt[0], s_pt[1], fill=0 if dashed else 1, stroke=1)
        c.setDash()
        c.setFillColorRGB(0, 0, 0)
        w = s_pt[0]
        fs = max(4.5, min(9, w / 9))
        cx, cy = x + w / 2, y + s_pt[1] / 2
        name_fs = fs
        while c.stringWidth(label, "Helvetica-Bold", name_fs) > w - 2 and name_fs > 3.5:
            name_fs -= 0.25
        c.setFont("Helvetica-Bold", name_fs)
        c.drawCentredString(cx, cy + fs * 0.35, label)
        c.setFont("Helvetica", fs * 0.8)
        c.drawCentredString(cx, cy - fs * 0.8, f"{area:g} m²")
        c.setFont("Helvetica", fs * 0.7)
        c.drawCentredString(cx, cy - fs * 1.65, s_m)
        c.setFont("Helvetica", 4)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.drawString(x + 1.2, y + s_pt[1] - 5, zone)
        c.setFillColorRGB(0, 0, 0)

    # Skyline bottom-left packing, page by page. Rooms go in zone order, largest first; each square
    # carries its zone tag and colour, so zones stay readable without headings.
    top, bottom, left, right = H - margin - title_h, margin + 14 * mm, margin, W - margin
    Wu, Hu = right - left, top - bottom
    stream = [(zone, rgb, label, area, s, s * k, s * k)
              for zone, (rgb, _) in ZONES.items()
              for z, _, label, area, s in instances() if z == zone]
    stream.append(("REFERENCE", ZONES["PUBLIC"][0], "REF: hall as 24 × 15 m court", 360, None,
                   GYM_COURT[0] * k, GYM_COURT[1] * k))

    def fit(sky, w, h):
        best = None
        for i, (sx, _, _) in enumerate(sky):
            if sx + w > Wu + 0.01:
                break
            d = max(sd for x0, sw, sd in sky if x0 < sx + w - 0.01 and x0 + sw > sx + 0.01)
            if d + h <= Hu + 0.01 and (best is None or (d, sx) < best):
                best = (d, sx)
        return best

    def place(sky, x, w, d):
        out = []
        for x0, sw, sd in sky:
            if x0 + sw <= x + 0.01 or x0 >= x + w - 0.01:
                out.append((x0, sw, sd))
                continue
            if x0 < x:
                out.append((x0, x - x0, sd))
            if x0 + sw > x + w:
                out.append((x + w, x0 + sw - x - w, sd))
        out.append((x, w, d))
        out.sort()
        merged = []
        for seg in out:
            if merged and abs(merged[-1][2] - seg[2]) < 0.01:
                merged[-1] = (merged[-1][0], merged[-1][1] + seg[1], seg[2])
            else:
                merged.append(seg)
        return merged

    header()
    sky = [(0.0, Wu, 0.0)]
    for zone, rgb, label, area, s, wpt, hpt in stream:
        pos = fit(sky, wpt + gap, hpt + gap)
        if pos is None:
            c.showPage()
            header()
            sky = [(0.0, Wu, 0.0)]
            pos = fit(sky, wpt + gap, hpt + gap)
        d, x = pos
        sky = place(sky, x, wpt + gap, d + hpt + gap)
        xx, yy = left + x, top - d - hpt
        if s is None:
            room(xx, yy, (wpt, hpt), label, area, "24.00 x 15.00 m (same room)", rgb, dashed=True, zone="reference")
        else:
            room(xx, yy, (wpt, hpt), label, area, fmt_side(s), rgb, zone=zone.lower())
    c.save()
    return page[0]


if __name__ == "__main__":
    make_dxf(HERE / "Cairn_Room-Squares.dxf")
    tabloid = landscape((11 * 72, 17 * 72))
    n1 = make_pdf(HERE / "Cairn_Room-Squares_1-100_Tabloid.pdf", tabloid, 100, "1:100")
    n2 = make_pdf(HERE / "Cairn_Room-Squares_1-200_Letter.pdf", landscape(letter), 200, "1:200")
    print(f"net {NET:.1f} m2, rooms {len(instances())}; 1:100 tabloid {n1} sheets, 1:200 letter {n2} sheets")

"""Editable 11x17 PDF of the site-selection deck, built like the RAIC 400 Bluebeam template
(RAIC 400/Templates/_build/build_template.py): every word is a Bluebeam Text Box markup, every rule/box a
Line/Rectangle markup, every map an Image stamp, and the map pins are Circle + Text Box markups.
Same content as the HTML preview (data and wording come from build_preview.py).

    python build_pdf.py            -> Cairn_Site-Selection_11x17.pdf  (Bluebeam: text drawn from DS/RC styles)
    python build_pdf.py --check    -> _check/*.png  (same layout with text burned in, to proof without Bluebeam)
"""
import re, sys
from pathlib import Path
import pymupdf
import build_preview as bp

HERE = Path(__file__).resolve().parent
FONTS = Path(r"C:\Users\BHackman\OneDrive - DIALOG\BHackman Drive\00_AI\Claude\RAIC 400\Templates\Fonts")
CHECK = "--check" in sys.argv
OUT = HERE / ("_check/_check.pdf" if CHECK else "Cairn_Site-Selection_11x17.pdf")

W, H = 1224, 792
M = 45
INK, RED, PAPER, PANEL, RULE = "#1B1B1B", "#A63A26", "#F5F2EA", "#E8E3D6", "#8D877C"
FONT_FILES = {"bcm": "BarlowCondensed-Medium.ttf", "bcs": "BarlowCondensed-SemiBold.ttf", "bcb": "BarlowCondensed-Bold.ttf",
              "ssr": "SourceSerif4-Regular.ttf", "ssi": "SourceSerif4-It.ttf", "sss": "SourceSerif4-Semibold.ttf"}
FONT = {k: pymupdf.Font(fontfile=str(FONTS / f)) for k, f in FONT_FILES.items()}
CSS_FONT = {"bcb": ("Barlow Condensed", "bold "), "bcm": ("Barlow Condensed Medium", ""),
            "bcs": ("Barlow Condensed SemiBold", ""), "ssr": ("Source Serif 4", ""),
            "ssi": ("Source Serif 4", "italic "), "sss": ("Source Serif 4 Semibold", "")}
INSET_X, INSET_Y = 4.3, 3.7
ALIGN = {0: "left", 1: "center", 2: "right", "left": "left", "center": "center", "right": "right"}

doc = pymupdf.open()
OC_PAPER = doc.add_ocg("Paper tint (turn off to save toner)", on=True)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def new_page():
    p = doc.new_page(width=W, height=H)
    for k, f in FONT_FILES.items():
        p.insert_font(fontname=k, fontfile=str(FONTS / f))
    p.draw_rect(p.rect, color=None, fill=hx(PAPER), oc=OC_PAPER)
    return p


# ------------------------------------------------------------------ text (Bluebeam Text Box markups)
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def css(font, size, color, lh=None, align="left"):
    fam, wt = CSS_FONT[font]
    c = f"font: {wt}{size:g}pt '{fam}'; text-align:{ALIGN[align]}; color:{color}"
    return c + (f"; line-height:{lh * size:.1f}pt" if lh else "")


def markup(p, rect, lines, font="ssr", size=10.8, color=INK, lh=None, align="left", name="Text"):
    """lines: list; each line is a str or a list of (text, font) runs."""
    if CHECK:   # burn the text in so the layout can be proofed without Bluebeam
        x0, y0, x1, y1 = rect
        lead = (lh or 1.2) * size
        y = y0 + INSET_Y + 1.024 * size
        for ln in lines:
            runs = [(ln, font)] if isinstance(ln, str) else ln
            wid = sum(FONT[f].text_length(t, size) for t, f in runs)
            x = {"left": x0 + INSET_X, "right": x1 - INSET_X - wid, "center": (x0 + x1 - wid) / 2}[ALIGN[align]]
            for t, f in runs:
                p.insert_text((x, y), t, fontname=f, fontsize=size, color=hx(color))
                x += FONT[f].text_length(t, size)
            y += lead
        return
    base = css(font, size, color, lh, align)
    html = ""
    for ln in lines:
        if isinstance(ln, str):
            html += f"<p>{esc(ln) if ln else '&#160;'}</p>"
        else:
            html += "<p>" + "".join(f"<span style=\"{css(f, size, color)}\">{esc(t)}</span>" for t, f in ln) + "</p>"
    a = p.add_freetext_annot(pymupdf.Rect(rect), "x", fontsize=size, fontname="helv", border_width=0)
    a.set_info(title="Ben Hackman", subject="Text Box", content=name)
    a.update()
    rc = ('<?xml version="1.0"?><body xmlns="http://www.w3.org/1999/xhtml" '
          'xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/" xfa:contentType="text/html" '
          f'xfa:APIVersion="BluebeamPDFRevu:2018" xfa:spec="2.2.0" style="{base}">{html}</body>')
    plain = "\r".join(ln if isinstance(ln, str) else "".join(t for t, _ in ln) for ln in lines)
    doc.xref_set_key(a.xref, "DS", pymupdf.get_pdf_str(base))
    doc.xref_set_key(a.xref, "RC", pymupdf.get_pdf_str(rc))
    doc.xref_set_key(a.xref, "Contents", pymupdf.get_pdf_str(plain))
    doc.xref_set_key(a.xref, "AP", "null")


def text(p, x, y, s, font="ssr", size=10.8, color=INK, align="left"):
    """One editable line with its baseline at y, starting (left), ending (right) or centred on x."""
    width = FONT[font].text_length(s, size) + 24
    x0 = {"left": x - INSET_X, "right": x - width + INSET_X, "center": x - width / 2}[align]
    markup(p, (x0, y - INSET_Y - 1.024 * size, x0 + width, y + 0.4 * size + INSET_Y), [s], font, size, color,
           align=align, name=s[:40])
    return width - 24


def label(p, x, y, s, color=RED, size=10.8, align="left"):
    return text(p, x, y, s.upper(), "bcs", size, color, align)


def wrap(runs, width, size):
    """Greedy word wrap of (text, font) runs to width; returns a list of run-lists."""
    words = []
    for t, f in runs:
        if t[:1].isspace() and words:
            words[-1] = (words[-1][0].rstrip() + " ", words[-1][1])
        for w_ in re.findall(r"\S+\s*", t):
            words.append((w_, f))
    lines, cur, cw = [], [], 0.0
    for w_, f in words:
        ww = FONT[f].text_length(w_.rstrip(), size)
        if cur and cw + ww > width:
            lines.append(cur); cur, cw = [], 0.0
        cur.append((w_, f)); cw += FONT[f].text_length(w_, size)
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:   # merge same-font neighbours, strip the trailing space
        merged = []
        for t, f in ln:
            if merged and merged[-1][1] == f:
                merged[-1] = (merged[-1][0] + t, f)
            else:
                merged.append((t, f))
        merged[-1] = (merged[-1][0].rstrip(), merged[-1][1])
        out.append(merged)
    return out


def para(p, x, y, width, s, font="ssr", size=11.5, lh=1.4, color=INK, align="left"):
    """Wrapped paragraph whose first line sits in a box starting at y (top). s may hold <b>bold</b>. Returns the bottom y."""
    runs = []
    for part in re.split(r"(<b>.*?</b>)", s):
        if part.startswith("<b>"):
            runs.append((part[3:-4], "sss" if font.startswith("ss") else "bcb"))
        elif part:
            runs.append((part, font))
    lines = wrap(runs, width, size)
    lines = [ln[0][0] if len(ln) == 1 and ln[0][1] == font else ln for ln in lines]
    hgt = len(lines) * lh * size
    markup(p, (x - INSET_X, y - INSET_Y, x + width + INSET_X + 2, y + hgt + INSET_Y), lines, font, size, color, lh, align,
           name=re.sub("<.*?>", "", s)[:40])
    return y + hgt


# ------------------------------------------------------------------ lines, boxes, images, pins
def mline(p, a, b, w=1.5, color=INK, name="Rule"):
    if CHECK:
        p.draw_line(a, b, color=hx(color), width=w); return
    an = p.add_line_annot(a, b)
    an.set_colors(stroke=hx(color))
    an.set_border(width=w)
    an.set_info(title="Ben Hackman", subject="Line", content=name)
    an.update()


def rule(p, x0, y, x1, w=1.5, color=INK):
    mline(p, (x0, y), (x1, y), w, color)


def mrect(p, r, stroke=None, fill=None, w=0.6, name="Rectangle"):
    if CHECK:
        p.draw_rect(pymupdf.Rect(r), color=hx(stroke) if stroke else None, fill=hx(fill) if fill else None, width=w); return
    an = p.add_rect_annot(pymupdf.Rect(r))
    an.set_colors(stroke=hx(stroke) if stroke else [], fill=hx(fill) if fill else [])
    an.set_border(width=w if stroke else 0)
    an.set_info(title="Ben Hackman", subject="Rectangle", content=name)
    an.update()


def image(p, x, y, w, path, maxh=None, border=False):
    """Image stamp (movable/resizable in Bluebeam). Returns (x, y, w, h) actually used."""
    pix = pymupdf.Pixmap(str(path))
    h = w * pix.height / pix.width
    if maxh and h > maxh:
        h = maxh; w = h * pix.width / pix.height
    if CHECK:
        p.insert_image(pymupdf.Rect(x, y, x + w, y + h), filename=str(path))
    else:
        a = p.add_stamp_annot(pymupdf.Rect(x, y, x + w, y + h), stamp=str(path))
        a.set_info(title="Ben Hackman", subject="Image", content=Path(path).name)
        a.update()
    if border:
        mrect(p, (x, y, x + w, y + h), RULE, None, 0.6, name="Image frame")
    return x, y, w, h


def dot(p, rect, w=2.2, name="Site dot"):
    if CHECK:
        p.draw_oval(pymupdf.Rect(rect), color=(1, 1, 1), fill=hx(RED), width=w); return
    an = p.add_circle_annot(pymupdf.Rect(rect))
    an.set_colors(stroke=(1, 1, 1), fill=hx(RED))
    an.set_border(width=w)
    an.set_info(title="Ben Hackman", subject="Ellipse", content=name)
    an.update()


def pin(p, cx, cy, num, lab, left=False, r=12):
    dot(p, (cx - r, cy - r, cx + r, cy + r), 2.2, f"Site {num}")
    text(p, cx, cy + 5.3, str(num), "bcb", 15, "#FFFFFF", "center")
    if lab:
        text(p, cx - r - 6 if left else cx + r + 6, cy + 5, lab, "bcb", 14.5, RED, "right" if left else "left")


# ------------------------------------------------------------------ sheet furniture
TOP = 136          # body top
BOT = 728          # body bottom
GAP = 26


def header(p, eyebrow, title, sub, num=None):
    x = M
    if num is not None:
        mrect(p, (M, 50, M + 66, 116), None, INK, name="Site number badge")
        text(p, M + 33, 102, str(num), "bcb", 46, PAPER, "center")
        x = M + 66 + 16
    label(p, x, 62, eyebrow)
    text(p, x, 99, title.upper(), "bcb", 43)
    text(p, x, 114, sub, "ssr", 13)
    rule(p, M, 124, W - M)


def score_block(p, sid):
    t = bp.P[sid]
    text(p, W - M, 100, "/ 35", "bcb", 19, INK, "right")
    text(p, W - M - FONT["bcb"].text_length("/ 35", 19) - 4, 100, str(t["total"]), "bcb", 55, RED, "right")
    tag = f"RANK {bp.rank(sid)} OF 4"
    tw = FONT["bcs"].text_length(tag, 10.8) + 14
    mrect(p, (W - M - tw, 104, W - M, 119), None, INK, name="Rank tag")
    text(p, W - M - 7, 115, tag, "bcs", 10.8, PAPER, "right")


def footer(p, n, note):
    rule(p, M, 742, W - M, 0.75, RULE)
    text(p, M, 758, f"Ben Hackman · RAIC 400 · {bp.DATE}", "ssr", 9.4)
    text(p, W / 2, 758, note, "ssr", 9.4, INK, "center")
    label(p, W - M, 758, f"Sheet {n:02d}/{bp.TOTAL:02d}", INK, 10, "right")


def caption(p, x, y, w, s):
    return para(p, x, y + 6, w, s, "ssi", 9.4, 1.35)


class Col:
    """Stacking cursor for a right-hand column."""
    def __init__(self, p, x0, x1, y=TOP):
        self.p, self.x0, self.x1, self.y = p, x0, x1, y

    def label(self, s, gap=True):
        if gap and self.y > TOP + 1:
            self.y += 12
        label(self.p, self.x0, self.y + 10, s)
        self.y += 15
        rule(self.p, self.x0, self.y, self.x1, 1.5)
        self.y += 3

    def kv(self, k, v):
        text(self.p, self.x0, self.y + 14, k, "ssr", 11.5)
        text(self.p, self.x1, self.y + 14, v, "bcs", 13.7, INK, "right")
        self.y += 20
        rule(self.p, self.x0, self.y, self.x1, 0.6, RULE)

    def para(self, s, size=12.2):
        self.y = para(self.p, self.x0, self.y + 5, self.x1 - self.x0, s, "ssr", size, 1.45) + 2

    def bullets(self, items, size=11.5):
        for it in items:
            text(self.p, self.x0 + 2, self.y + 14, "•", "ssr", size)
            self.y = para(self.p, self.x0 + 13, self.y + 3, self.x1 - self.x0 - 13, it, "ssr", size, 1.35) + 2

    def adj(self, k, v):
        text(self.p, self.x0, self.y + 14, k, "bcs", 12.2)
        self.y = para(self.p, self.x0 + 16, self.y + 3, self.x1 - self.x0 - 16, v, "ssr", 11.5, 1.35) + 3
        rule(self.p, self.x0, self.y, self.x1, 0.6, RULE)


def city_map(p, x, w):
    x, y, w, h = image(p, x, TOP, w, HERE / "img" / "city_plan.png", border=True)
    for i, sid in enumerate(bp.ORDER, 1):
        px, py = bp.PINS[sid]
        pin(p, x + px * w, y + py * h, i, f"{bp.LET[sid]} · {bp.P[sid]['name']}", left=sid in ("C", "F"))
    return y + h


# ------------------------------------------------------------------ sheets
def sheet_cover():
    p = new_page()
    header(p, "RAIC 400 · Assignment · Site selection", "Four candidate sites",
           "Cairn Youth Centre: a year-round residential centre for visiting students aged 12 to 15. Calgary and the western foothills.")
    mw = 835
    yb = city_map(p, M, mw)
    caption(p, M, yb, mw, f"Fig. 1. The four sites, numbered urban to rural, with reference destinations (black squares). {bp.GRAY_CREDIT}")
    c = Col(p, M + mw + GAP, W - M)
    c.label("The sites", gap=False)
    for i, sid in enumerate(bp.ORDER, 1):
        t = bp.P[sid]
        dot(p, (c.x0, c.y + 7, c.x0 + 24, c.y + 31), 2)
        text(p, c.x0 + 12, c.y + 24.5, str(i), "bcb", 14.5, "#FFFFFF", "center")
        text(p, c.x0 + 34, c.y + 19, f"{bp.LET[sid]} · {t['name']}".upper(), "bcb", 15.8)
        text(p, c.x0 + 34, c.y + 32, f"{t['setting']} · {t['character'].lower()}", "ssr", 10)
        c.y += 38
        rule(p, c.x0, c.y, c.x1, 0.6, RULE)
    c.label("Why these four")
    c.para("A range from inner city to provincial park, narrowed from 11 zones for spread, talking points and the chance to visit each one.")
    c.label("Programme")
    pr = bp.D["program"]
    c.kv("Beds", f"{pr['beds']}, in {pr['nodes']} nodes of 8, pods of 4")
    c.kv("Building", f"about {round(pr['gross_m2'], -2):,.0f} m²")
    c.kv("Land needed", "about 1 ha")
    footer(p, 1, "Early site analysis: values are approximate and for comparison only.")


def sheet_zone(i, sid, n):
    p = new_page()
    s, t = bp.SITES[sid], bp.P[sid]
    header(p, f"Site {i} of 4 · Context · {t['setting']}", f"{bp.LET[sid]} · {t['name']}", t["where"], i)
    mw = 850
    x, y, w, h = image(p, M, TOP, mw, HERE / "img" / f"zone_{sid}.jpg")
    caption(p, M, y + h, mw, f"Fig. {n}.1. Neighbourhood context, about 10 km across. Yellow dot: site. Dashed ring: 400 m. {bp.IMG_CREDIT}")
    c = Col(p, M + mw + GAP, W - M)
    c.label("Next to the site", gap=False)
    for a in s["context"]["adjacent"]:
        k, v = a.split(":", 1)
        v = v.strip(); c.adj(k, v[:1].upper() + v[1:])
    c.label("Within reach")
    extra = ["MAX Yellow bus rapid transit on 14 St SW, beside the site"] if sid == "F" else []
    c.bullets((extra + s["context"]["ring_amenities"])[:5])
    c.label("Nuisances")
    c.bullets(s["context"]["ring_nuisances"][:4])
    footer(p, n, "Context from OpenStreetMap and City of Calgary open data, checked against aerial imagery.")


def sheet_site(i, sid, n):
    p = new_page()
    t = bp.P[sid]
    header(p, f"Site {i} of 4 · Site · {t['setting']}", f"{bp.LET[sid]} · {t['name']}", t["where"], i)
    score_block(p, sid)
    mw = 720
    x, y, w, h = image(p, M, TOP, mw, HERE / "img" / f"site_{sid}.jpg")
    caption(p, M, y + h, mw, f"Fig. {n}.1. The site, about 2.4 km across. Cyan: the site chosen. Arcs: sunrise to sunset at the "
            f"summer and winter solstices (schematic). Arrow: prevailing wind. {bp.IMG_CREDIT}")
    c = Col(p, M + mw + GAP, W - M)
    c.label("Scores (1 to 5)", gap=False)
    for k, lab in bp.CRIT:
        text(p, c.x0, c.y + 14, lab, "ssr", 11.5)
        text(p, c.x0 + 150, c.y + 15, str(t["scores"][k]), "bcb", 14.4, INK, "center")
        text(p, c.x0 + 168, c.y + 14, t["notes"][k], "ssr", 10)
        c.y += 19.5
        rule(p, c.x0, c.y, c.x1, 0.6, RULE)
    text(p, c.x0, c.y + 15, "Total", "sss", 11.5)
    text(p, c.x0 + 150, c.y + 16, str(t["total"]), "bcb", 14.4, INK, "center")
    text(p, c.x0 + 168, c.y + 15, "out of 35", "ssr", 10)
    c.y += 21
    rule(p, c.x0, c.y, c.x1, 1.5)
    c.label("The site")
    for k, v in (("Character", t["character"]), ("Land", t["land"]), ("Room", t["roomw"]), ("Flexibility", t["flex"]),
                 ("Transit", t["transit"]), ("Flood risk", t["flood"]), ("Busy edge", t["edge"])):
        c.kv(k, v)
    c.label("Drive times (off-peak)")
    for lab, mn in bp.drives(sid):
        c.kv(lab, bp.r5(mn))
    footer(p, n, "Drive times rounded to 5 min, off-peak; allow more at rush hour or in winter. Flood risk from the Alberta flood hazard maps.")


def sheet_terrain(i, sid, n):
    p = new_page()
    t, f = bp.P[sid], bp.TERR[sid]
    header(p, f"Site {i} of 4 · Terrain · {t['setting']}", f"{bp.LET[sid]} · {t['name']}", t["terrain"], i)
    mw = 878
    x, y, w, h = image(p, M, TOP, mw, HERE / "img" / f"terrain_{sid}.jpg", maxh=560)
    caption(p, M, y + h, mw, f"Fig. {n}.1. Looking north over the site, about 2.4 km across, heights exaggerated ×5. Yellow pin: site. "
            f"Elevation: AWS Terrain Tiles (CDEM-derived). {bp.IMG_CREDIT}")
    c = Col(p, M + mw + GAP, W - M)
    c.label("Where it sits", gap=False)
    c.para(t["terrain"] + ".")
    c.label("Within 500 m")
    rnd = lambda v: f"about {max(5, int(5 * round(v / 5)))} m"
    c.kv("Above the lowest ground", rnd(f["above_low_m"]))
    c.kv("Below the highest ground", rnd(f["below_high_m"]))
    footer(p, n, "Elevation model is about 20–30 m resolution: reads the landform, not the fine grading. A site survey comes later.")


def sheet_summary():
    p = new_page()
    header(p, "RAIC 400 · Site selection · Summary", "Four sites compared", "Seven criteria, each scored 1 to 5, out of 35.")
    mw = 562
    yb = city_map(p, M, mw)
    caption(p, M, yb, mw, f"Fig. {bp.TOTAL}.1. The four sites. {bp.GRAY_CREDIT}")
    c = Col(p, M + mw + GAP, W - M)
    c.label("Overall", gap=False)
    cols = [("", 22, "c"), ("Site", 108, "l"), ("/35", 26, "r"), ("Character", 78, "l"), ("City", 46, "r"),
            ("Mountains", 56, "r"), ("Room", 70, "l"), ("Flood", 44, "l"), ("Land", 0, "l")]
    cols[-1] = ("Land", (c.x1 - c.x0) - sum(cw for _, cw, _ in cols[:-1]) - 4 * (len(cols) - 1), "l")
    xs, xx = [], c.x0
    for _, cw, _ in cols:
        xs.append(xx); xx += cw + 4
    for (hd, cw, al), x0 in zip(cols, xs):
        if hd:
            label(p, x0 + (cw if al == "r" else 0), c.y + 11, hd, INK, 10, "right" if al == "r" else "left")
    c.y += 15
    rule(p, c.x0, c.y, c.x1, 0.75)
    top = max(bp.TOTALS)
    for i, sid in enumerate(bp.ORDER, 1):
        t = bp.P[sid]
        mtn = min(bp.MTN[sid]["wildhorn"]["min"], bp.MTN[sid]["kananaskis_village"]["min"])
        cells = ["", f"{bp.LET[sid]} · {t['name']}", str(t["total"]), t["character"], bp.r5(bp.city_min(sid)), bp.r5(mtn),
                 t["roomw"], t["flood"], t["land"]]
        fonts = [None, "sss", "bcb", "ssr", "bcs", "bcs", "ssr", "ssr", "ssr"]
        sizes = [0, 10.8, 13.7, 10.4, 12.2, 12.2, 10.4, 10.4, 10.4]
        nlines = [len(wrap([(cl, fo)], cw, sz)) if fo else 1 for cl, (_, cw, _), fo, sz in zip(cells, cols, fonts, sizes)]
        rh = max(22, 7 + 13.5 * max(nlines))
        if t["total"] == top:
            mrect(p, (c.x0, c.y, c.x1, c.y + rh), None, PANEL, name="Leading site")
        dot(p, (xs[0] + 1, c.y + rh / 2 - 10, xs[0] + 21, c.y + rh / 2 + 10), 1.6)
        text(p, xs[0] + 11, c.y + rh / 2 + 4.3, str(i), "bcb", 12.2, "#FFFFFF", "center")
        for cl, (_, cw, al), x0, fo, sz in list(zip(cells, cols, xs, fonts, sizes))[1:]:
            ls = wrap([(cl, fo)], cw, sz)
            lines = [ln[0][0] for ln in ls]
            yy = c.y + (rh - len(lines) * 13.5) / 2
            if al == "r":
                text(p, x0 + cw, yy + 11, cl, fo, sz, INK, "right")
            else:
                markup(p, (x0 - INSET_X, yy - INSET_Y + 0.5, x0 + cw + INSET_X + 2, yy + len(lines) * 13.5 + INSET_Y), lines,
                       fo, sz, INK, 13.5 / sz, name=cl[:40])
        c.y += rh
        rule(p, c.x0, c.y, c.x1, 0.6, RULE)
    c.label("How the sites were scored")
    for k, lab in bp.CRIT:
        text(p, c.x0, c.y + 14, lab, "bcs", 12.2)
        text(p, c.x0 + 112, c.y + 14, bp.DEFS[k], "ssr", 11)
        c.y += 19
        rule(p, c.x0, c.y, c.x1, 0.6, RULE)
    c.label("Where it lands")
    c.para(bp.LANDS)
    footer(p, bp.TOTAL, "Early site analysis: scores are judgments for comparison, not measurements.")


def build():
    sheet_cover()
    n = 2
    toc = [[1, "01 City plan", 1]]
    for i, sid in enumerate(bp.ORDER, 1):
        nm = f"{bp.LET[sid]} {bp.P[sid]['name']}"
        sheet_zone(i, sid, n); sheet_site(i, sid, n + 1); sheet_terrain(i, sid, n + 2)
        toc += [[1, f"{n:02d} {nm}: context", n], [1, f"{n+1:02d} {nm}: site", n + 1], [1, f"{n+2:02d} {nm}: terrain", n + 2]]
        n += 3
    sheet_summary()
    toc.append([1, f"{bp.TOTAL:02d} Summary", bp.TOTAL])
    doc.set_metadata({"title": "Cairn Youth Centre: Site selection", "author": "Ben Hackman", "subject": "RAIC 400 site selection, 11x17"})
    doc.set_toc(toc)
    OUT.parent.mkdir(exist_ok=True)
    doc.subset_fonts()
    doc.save(OUT, garbage=3, deflate=True)
    print("wrote", OUT, len(doc), "pages")
    if CHECK:
        for k, pg in enumerate(doc, 1):
            pg.get_pixmap(dpi=72).save(OUT.parent / f"p{k:02d}.png")


if __name__ == "__main__":
    build()

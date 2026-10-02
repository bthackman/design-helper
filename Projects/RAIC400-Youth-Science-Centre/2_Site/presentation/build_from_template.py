"""Fill Ben's revised Bluebeam template (2026-10-05) with all four sites.

Source: Desktop/00_PDF/"Pages from 2026-10-05 Presentation - For Claude.pdf" (3 pages Ben set up in Revu:
01 overall city plan, 02 A Inglewood context, 03 A Inglewood site). Pages 02-03 are re-imported for B, C, D and
their text/images swapped; Ben's styles (DS strings), positions and header/footer markups are kept as he set them.
Clean-up only: sheet numbers, date, evenly spaced score rules, Programme label/value baselines on sheet 01, the
context-column spacing (re-flowed with Ben's own pitch), and the YYC label that was clipped at the map edge.

    python build_from_template.py          -> 2026-10-05 Presentation - Site Selection.pdf (here + next to the source)
    python build_from_template.py --check  -> _check_tpl/pNN.png proofs (edited text drawn in, since Bluebeam
                                              rebuilds those appearances itself)
"""
import re, sys, shutil
from pathlib import Path
import pymupdf
import build_preview as bp

HERE = Path(__file__).resolve().parent
SRC = Path(r"C:\Users\BHackman\OneDrive - DIALOG\Desktop\00_PDF\Pages from 2026-10-05 Presentation - For Claude.pdf")
OUTNAME = "2026-10-05 Presentation - Site Selection.pdf"
FONTS = Path(r"C:\Users\BHackman\OneDrive - DIALOG\BHackman Drive\00_AI\Claude\RAIC 400\Templates\Fonts")
FONT = {k: pymupdf.Font(fontfile=str(FONTS / f)) for k, f in {
    "bcm": "BarlowCondensed-Medium.ttf", "bcs": "BarlowCondensed-SemiBold.ttf", "bcb": "BarlowCondensed-Bold.ttf",
    "ssr": "SourceSerif4-Regular.ttf", "ssi": "SourceSerif4-It.ttf", "sss": "SourceSerif4-Semibold.ttf"}.items()}
PH = 792
INSET_X, INSET_Y = 4.3, 3.7

# Page order: 01 overall, then per site: context, site, terrain; last: summary. Terrain and summary sheets
# start from a fresh copy of Ben's site page (03) with everything but the header/footer removed.
doc = pymupdf.open(SRC)
doc.insert_pdf(pymupdf.open(SRC), from_page=2, to_page=2)           # A terrain base
for _ in bp.ORDER[1:]:
    doc.insert_pdf(pymupdf.open(SRC), from_page=1, to_page=2)       # fresh, independent copies of 02 + 03
    doc.insert_pdf(pymupdf.open(SRC), from_page=2, to_page=2)       # terrain base
doc.insert_pdf(pymupdf.open(SRC), from_page=2, to_page=2)           # summary base
TOTAL = 2 + 3 * len(bp.ORDER)


# ------------------------------------------------------------------ helpers on Bluebeam FreeText markups
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ds_of(a):
    return doc.xref_get_key(a.xref, "DS")[1]


def set_rect(a, r):
    x0, y0, x1, y1 = r
    doc.xref_set_key(a.xref, "Rect", f"[{x0:.2f} {PH - y1:.2f} {x1:.2f} {PH - y0:.2f}]")


def set_text(a, lines, rect=None):
    """Replace a Text Box's words, keeping its Bluebeam style (DS). Bluebeam rebuilds the appearance."""
    ds = ds_of(a)
    html = "".join(f"<p>{esc(ln) if ln else '&#160;'}</p>" for ln in lines)
    rc = ('<?xml version="1.0"?><body xmlns="http://www.w3.org/1999/xhtml" '
          'xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/" xfa:contentType="text/html" '
          f'xfa:APIVersion="BluebeamPDFRevu:2018" xfa:spec="2.2.0" style="{ds}">{html}</body>')
    doc.xref_set_key(a.xref, "RC", pymupdf.get_pdf_str(rc))
    doc.xref_set_key(a.xref, "Contents", pymupdf.get_pdf_str("\r".join(lines)))
    doc.xref_set_key(a.xref, "AP", "null")
    if rect:
        set_rect(a, rect)


def new_text(p, rect, lines, ds, name):
    a = p.add_freetext_annot(pymupdf.Rect(rect), "x", fontsize=10, fontname="helv", border_width=0)
    a.set_info(title="BHackman", subject="Text Box", content=name)
    a.update()
    doc.xref_set_key(a.xref, "DS", pymupdf.get_pdf_str(ds))
    set_text(a, lines)
    return a


def new_line(p, x0, x1, y, w, color, name="Rule"):
    an = p.add_line_annot((x0, y), (x1, y))
    an.set_colors(stroke=color)
    an.set_border(width=w)
    an.set_info(title="BHackman", subject="Line", content=name)
    an.update()


def move_line(a, dy_to):
    """Move a horizontal Line markup so it sits at y=dy_to (top-left coordinates)."""
    L = [float(v) for v in doc.xref_get_key(a.xref, "L")[1].strip("[]").split()]
    yb = PH - dy_to
    doc.xref_set_key(a.xref, "L", f"[{L[0]:.2f} {yb:.2f} {L[2]:.2f} {yb:.2f}]")
    r = a.rect
    doc.xref_set_key(a.xref, "Rect", f"[{r.x0:.2f} {yb - 6:.2f} {r.x1:.2f} {yb + 6:.2f}]")
    doc.xref_set_key(a.xref, "AP", "null")


def line_y(a):
    L = [float(v) for v in doc.xref_get_key(a.xref, "L")[1].strip("[]").split()]
    return PH - L[1]


def fonts_of(ds):
    size = float(re.search(r"([\d.]+)pt", ds).group(1))
    if "Source Serif 4 Semibold" in ds: k = "sss"
    elif "Source Serif" in ds: k = "ssi" if "italic" in ds else "ssr"
    elif "SemiBold" in ds: k = "bcs"
    elif "Medium" in ds: k = "bcm"
    else: k = "bcb"
    return k, size


def wrap(s, key, size, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and FONT[key].text_length(t, size) > width:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def fit_left(a, s):
    """Single-line left-aligned box: keep x0, size the box to the text."""
    k, sz = fonts_of(ds_of(a))
    r = a.rect
    set_text(a, [s], (r.x0, r.y0, r.x0 + FONT[k].text_length(s, sz) + 2 * INSET_X + 12, r.y1))


def fit_right(a, s):
    k, sz = fonts_of(ds_of(a))
    r = a.rect
    set_text(a, [s], (r.x1 - FONT[k].text_length(s, sz) - 2 * INSET_X - 24, r.y0, r.x1, r.y1))


def texts(p):
    return [a for a in p.annots() if a.type[1] == "FreeText"]


def by_content(p, s, after_y=None):
    for a in texts(p):
        if a.info.get("content", "").replace("\ufffd", "·") == s and (after_y is None or a.rect.y0 > after_y):
            return a
    raise KeyError(s)


def stamp(p, name):
    return next(a for a in p.annots() if a.type[1] == "Stamp" and a.info.get("content") == name)


def _image_xrefs(xref, seen=None):
    """Image XObjects reachable from a form XObject (a stamp's appearance)."""
    seen = seen or set()
    out = []
    t, xo = doc.xref_get_key(xref, "Resources/XObject")
    if t != "dict":
        return out
    for ref in re.findall(r"(\d+) 0 R", xo):
        r = int(ref)
        if r in seen:
            continue
        seen.add(r)
        if doc.xref_get_key(r, "Subtype")[1] == "/Image":
            out.append(r)
        else:
            out += _image_xrefs(r, seen)
    return out


_scratch = None


def swap_image(p, old, path):
    """Put a new picture inside Ben's existing Image stamp: same rect, size and stacking order."""
    global _scratch
    a = stamp(p, old)
    ap = int(doc.xref_get_key(a.xref, "AP/N")[1].split()[0])
    imgs = _image_xrefs(ap)
    assert len(imgs) == 1, (old, imgs)
    if _scratch is None:
        _scratch = doc.new_page(-1, width=10, height=10)
    nx = _scratch.insert_image(_scratch.rect, filename=str(path))
    doc.xref_copy(nx, imgs[0])
    doc.xref_set_key(a.xref, "Contents", pymupdf.get_pdf_str(Path(path).name))


# ------------------------------------------------------------------ every sheet: header/footer clean-up
def furniture(p, n, title=None):
    for a in texts(p):
        c = a.info.get("content", "")
        if c.endswith("/xx") or re.fullmatch(r"\d\d/\d\d", c):
            set_text(a, [f"{n:02d}/{TOTAL:02d}"])
        elif c.startswith("Student:"):
            rc = doc.xref_get_key(a.xref, "RC")[1]
            if "September 2026" in rc:
                doc.xref_set_key(a.xref, "RC", pymupdf.get_pdf_str(rc.replace("September 2026", "October 2026")))
                doc.xref_set_key(a.xref, "Contents", pymupdf.get_pdf_str(c.replace("September 2026", "October 2026")))
                doc.xref_set_key(a.xref, "AP", "null")
    if title:
        a = next(a for a in texts(p) if fonts_of(ds_of(a)) == ("bcb", 30.0))
        set_text(a, [title.upper()])


# ------------------------------------------------------------------ sheet 01: overall
def sheet_overall(p):
    furniture(p, 1)
    # Programme rows: values sat 3.7 pt above their labels; put both on one baseline (label baseline kept)
    for lab in ("Beds", "Building", "Land needed"):
        L = by_content(p, lab)
        vals = [a for a in texts(p) if a.rect.x0 > 1000 and abs(a.rect.y0 - L.rect.y0) < 8 and fonts_of(ds_of(a))[0] == "bcs"]
        for v in vals:
            r = v.rect
            set_rect(v, (r.x0, L.rect.y0 - 2.2, r.x1, L.rect.y0 - 2.2 + r.height))
            doc.xref_set_key(v.xref, "AP", "null")
            # keep the existing words; Bluebeam redraws from RC
    swap_image(p, "city_plan.png", HERE / "img" / "city_plan.png")   # YYC label no longer clipped


# ------------------------------------------------------------------ context sheets
CX_LABEL, CX_KEY, CX_ADJ, CX_BUL, CX_BTXT, CX_R = 916.7, 916.7, 932.7, 918.7, 929.7, 1185.3
ADJ_W, BUL_W = 242.0, 245.0


def sheet_context(p, sid, n):
    s, t = bp.SITES[sid], bp.P[sid]
    furniture(p, n, f"{bp.LET[sid]} · {t['name']}")
    if sid != "C":
        swap_image(p, "zone_C.jpg", HERE / "img" / f"zone_{sid}.jpg")
    # collect Ben's styles from the existing column, then re-flow it
    col = [a for a in texts(p) if a.rect.x0 > 900 and 120 < a.rect.y0 < 720]
    ds_label = ds_of(by_content(p, "NEXT TO THE SITE"))
    ds_key = ds_of(by_content(p, "N"))
    ds_body = ds_of(by_content(p, "Nature Centre building and the sanctuary gate"))
    ds_bul = ds_of(next(a for a in col if a.info.get("content") in ("•", "\ufffd")))
    rules = sorted([a for a in p.annots() if a.type[1] == "Line" and a.rect.x0 > 900 and line_y(a) > 120], key=line_y)
    rule_x = [float(v) for v in doc.xref_get_key(rules[0].xref, "L")[1].strip("[]").split()]
    rule_color, rule_w = rules[0].colors["stroke"], rules[0].border["width"]
    start_y = by_content(p, "NEXT TO THE SITE").rect.y0
    for a in col:
        p.delete_annot(a)
    for a in rules:
        p.delete_annot(a)
    _, bsz = fonts_of(ds_body)
    LH = 15.5
    y = start_y

    def section(title):
        nonlocal y
        new_text(p, (CX_LABEL, y, CX_LABEL + FONT["bcs"].text_length(title, 14) + 30, y + 40.1), [title], ds_label, title)
        new_line(p, rule_x[0], rule_x[2], y + 22.3, rule_w, rule_color)
        y += 22.3 + 1.8

    section("NEXT TO THE SITE")
    for a_ in s["context"]["adjacent"]:
        k, v = a_.split(":", 1)
        v = v.strip(); v = v[:1].upper() + v[1:]
        lines = wrap(v, "ssr", bsz, ADJ_W)
        new_text(p, (CX_KEY, y - 0.5, CX_KEY + 30, y + 24.3), [k], ds_key, k)
        new_text(p, (CX_ADJ, y, CX_R, y + len(lines) * LH + 7.5), lines, ds_body, v[:40])
        y += len(lines) * LH + 6
    for title, items in (("WITHIN REACH", ((["MAX Yellow bus rapid transit on 14 St SW, beside the site"] if sid == "F" else [])
                                            + s["context"]["ring_amenities"])[:5]),
                         ("NUISANCES", s["context"]["ring_nuisances"][:4])):
        y += 3
        section(title)
        for it in items:
            it = it[:1].upper() + it[1:]
            lines = wrap(it, "ssr", bsz, BUL_W)
            new_text(p, (CX_BUL, y - 0.8, CX_BUL + 27.5, y + 23), ["•"], ds_bul, "•")
            new_text(p, (CX_BTXT, y, CX_R, y + len(lines) * LH + 7.5), lines, ds_body, it[:40])
            y += len(lines) * LH + 5


# ------------------------------------------------------------------ site sheets
def sheet_site(p, sid, n):
    t = bp.P[sid]
    furniture(p, n, f"{bp.LET[sid]} · {t['name']}")
    if sid != "C":
        swap_image(p, "site_C.jpg", HERE / "img" / f"site_{sid}.jpg")
    A = bp.P["C"]
    # score rows (Ben's rows sit 19.5 pt apart; the rules under them had drifted)
    for i, (k, lab) in enumerate(bp.CRIT):
        row = by_content(p, lab)
        y0 = row.rect.y0
        num = next(a for a in texts(p) if 900 < a.rect.x0 < 930 and abs(a.rect.y0 - y0 + 1.9) < 3)
        note = next(a for a in texts(p) if 950 < a.rect.x0 < 960 and abs(a.rect.y0 - y0 - 1.6) < 3)
        set_text(num, [str(t["scores"][k])])
        fit_left(note, t["notes"][k])
    tot = by_content(p, "Total")
    num = next(a for a in texts(p) if 900 < a.rect.x0 < 930 and abs(a.rect.y0 - tot.rect.y0 + 1.9) < 3)
    set_text(num, [str(t["total"])])
    thin = sorted([a for a in p.annots() if a.type[1] == "Line" and a.border.get("width", 1) < 1 and 160 < line_y(a) < 300], key=line_y)
    first = by_content(p, bp.CRIT[0][1]).rect.y0
    for i, a in enumerate(thin):
        move_line(a, first + 22 + 19.5 * i)
    # big score
    big = next(a for a in texts(p) if fonts_of(ds_of(a)) == ("bcb", 55.0))
    fit_right(big, str(t["total"]))
    # the site + drive times: right-aligned values
    vals = [("Character", t["character"]), ("Land", t["land"]), ("Room", t["roomw"]), ("Flexibility", t["flex"]),
            ("Transit", t["transit"]), ("Flood risk", t["flood"]), ("Busy edge", t["edge"])]
    vals += [(lab, bp.r5(mn)) for lab, mn in bp.drives(sid)]
    for lab, v in vals:
        L = by_content(p, lab, after_y=320)
        a = next(a for a in texts(p) if a.rect.x1 > 1180 and a.rect.x0 > 950 and abs(a.rect.y0 - L.rect.y0 + 2.2) < 3)
        fit_right(a, v)


# ------------------------------------------------------------------ terrain + summary (new sheets, Ben's styles)
def grab_styles():
    """DS strings and pin styling read from Ben's own markups (sheets 01 and 03), before anything changes."""
    p1, p3 = doc[0], doc[2]
    st = {
        "label": ds_of(by_content(p3, "SCORES (1 TO 5)")),
        "kv_k": ds_of(by_content(p3, "Character")),
        "kv_v": ds_of(next(a for a in texts(p3) if a.info.get("content") == "Riverside grassland")),
        "num": ds_of(next(a for a in texts(p3) if a.info.get("content") == "3")),
        "body": ds_of(next(a for a in texts(p1) if a.info.get("content", "").startswith("Cairn Youth Centre"))),
        "pin_n": ds_of(next(a for a in texts(p1) if a.info.get("content") == "1" and a.rect.x0 < 880)),
        "pin_l": ds_of(next(a for a in texts(p1) if a.info.get("content", "").replace("�", "·") == "A · Inglewood")),
    }
    c = next(a for a in p1.annots() if a.type[1] == "Circle")
    st["pin_colors"], st["pin_w"], st["pin_r"] = c.colors, c.border.get("width", 2.2), c.rect.width / 2
    thin = next(a for a in p3.annots() if a.type[1] == "Line" and a.border.get("width", 1) < 1)
    thick = next(a for a in p3.annots() if a.type[1] == "Line" and abs(line_y(a) - 146.5) < 1)
    st["thin"] = (thin.colors["stroke"], thin.border["width"])
    st["thick"] = (thick.colors["stroke"], thick.border["width"])
    return st


def ds_size(ds, size, color=None, align=None):
    ds = re.sub(r"[\d.]+pt", f"{size:g}pt", ds, count=1)
    ds = re.sub(r"line-height:\s*[\d.]+pt", f"line-height:{size * 1.15:.2f}pt", ds)
    if color:
        ds = re.sub(r"color:\s*#[0-9A-Fa-f]{6}", f"color:{color}", ds)
    if align:
        ds = re.sub(r"text-align:\s*\w+", f"text-align:{align}", ds)
    return ds


def blank_body(p):
    """Keep only the header/footer furniture of a copied site page."""
    for a in list(p.annots()):
        keep = a.rect.y1 < 124 or a.rect.y0 > 735
        if a.type[1] == "FreeText" and fonts_of(ds_of(a))[1] in (55.0, 19.0):   # the big score
            keep = False
        if not keep:
            p.delete_annot(a)


class Column:
    """Right-hand column to Ben's site-sheet geometry: label box, 1.5 pt rule at +22.3, rows 20 pt apart."""
    def __init__(self, p, st, tl, tr=1179.0, y=124.2):
        self.p, self.st, self.tl, self.tr, self.y = p, st, tl, tr, y

    def label(self, s, gap=True):
        if gap:
            self.y += 10
        new_text(self.p, (self.tl - INSET_X, self.y, self.tl + FONT["bcs"].text_length(s, 14) + 30, self.y + 40.1), [s], self.st["label"], s)
        new_line(self.p, self.tl + 4.5, self.tr + 4.5, self.y + 22.3, self.st["thick"][1], self.st["thick"][0])
        self.y += 28.3

    def kv(self, k, v):
        new_text(self.p, (self.tl - INSET_X, self.y, self.tl + FONT["ssr"].text_length(k, 11.5) + 30, self.y + 23.8), [k], self.st["kv_k"], k)
        w = FONT["bcs"].text_length(v, 13.7) + 2 * INSET_X + 24
        new_text(self.p, (self.tr + 4.3 - w, self.y - 2.2, self.tr + 4.3, self.y + 24.7), [v], self.st["kv_v"], v)
        new_line(self.p, self.tl + 4.1, self.tr + 4.1, self.y + 19.4, self.st["thin"][1], self.st["thin"][0])
        self.y += 20

    def para(self, s, size=12.2):
        lines = wrap(s, "ssr", size, self.tr - self.tl)
        lh = 17.7 * size / 12.2
        ds = self.st["body"] if size == 12.2 else re.sub(r"line-height:\s*[\d.]+pt", f"line-height:{lh:.1f}pt", ds_size(self.st["body"], size))
        new_text(self.p, (self.tl - INSET_X, self.y + 2, self.tr + INSET_X, self.y + 2 + len(lines) * lh + 7.4), lines, ds, s[:40])
        self.y += len(lines) * lh + 6


def new_rich(p, rect, lines, ds, name):
    """Text Box with mixed regular/semibold runs; lines = [[(text, 'ssr'|'sss'), ...], ...]."""
    a = new_text(p, rect, ["x"], ds, name)
    fam = {"ssr": "Source Serif 4", "sss": "Source Serif 4 Semibold"}
    html = "".join("<p>" + "".join(f"<span style=\"font-family:'{fam[f]}'\">{esc(t)}</span>" for t, f in ln) + "</p>" for ln in lines)
    rc = ('<?xml version="1.0"?><body xmlns="http://www.w3.org/1999/xhtml" '
          'xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/" xfa:contentType="text/html" '
          f'xfa:APIVersion="BluebeamPDFRevu:2018" xfa:spec="2.2.0" style="{ds}">{html}</body>')
    doc.xref_set_key(a.xref, "RC", pymupdf.get_pdf_str(rc))
    doc.xref_set_key(a.xref, "Contents", pymupdf.get_pdf_str("\r".join("".join(t for t, _ in ln) for ln in lines)))


def wrap_runs(runs, size, width):
    words = [(w, f) for t, f in runs for w in t.split()]
    sp = FONT["ssr"].text_length(" ", size)
    lines, cur, cw = [], [], 0.0
    for w, f in words:
        ww = FONT[f].text_length(w, size)
        if cur and cw + sp + ww > width:
            lines.append(cur); cur, cw = [], 0.0
        cw += (sp if cur else 0) + ww
        cur.append((w, f))
    lines.append(cur)
    out = []
    for ln in lines:
        merged = []
        for i, (w, f) in enumerate(ln):
            t = (" " if i else "") + w
            if merged and merged[-1][1] == f:
                merged[-1] = (merged[-1][0] + t, f)
            else:
                merged.append((t, f))
        out.append(merged)
    return out


def image_stamp(p, rect, path):
    a = p.add_stamp_annot(pymupdf.Rect(rect), stamp=str(path))
    a.set_info(title="BHackman", subject="Image", content=Path(path).name)
    a.update()
    return a.rect


def circle(p, cx, cy, r, st, w, name):
    an = p.add_circle_annot(pymupdf.Rect(cx - r, cy - r, cx + r, cy + r))
    an.set_colors(stroke=st["pin_colors"]["stroke"], fill=st["pin_colors"]["fill"])
    an.set_border(width=w)
    an.set_info(title="BHackman", subject="Ellipse", content=name)
    an.update()


def sheet_terrain(p, sid, n, st):
    t, f = bp.P[sid], bp.TERR[sid]
    blank_body(p)
    furniture(p, n, f"{bp.LET[sid]} · {t['name']}")
    path = HERE / "img" / f"terrain_{sid}.jpg"
    pix = pymupdf.Pixmap(str(path))
    w = 720.0
    h = w * pix.height / pix.width
    if h > 590:
        h = 590.0; w = h * pix.width / pix.height
    image_stamp(p, (45, 136, 45 + w, 136 + h), path)
    c = Column(p, st, 791.0)
    c.label("WHERE IT SITS", gap=False)
    c.para(t["terrain"] + ".")
    c.label("WITHIN 500 M")
    rnd = lambda v: f"about {max(5, int(5 * round(v / 5)))} m"
    c.kv("Above the lowest ground", rnd(f["above_low_m"]))
    c.kv("Below the highest ground", rnd(f["below_high_m"]))
    c.label("THE VIEW")
    c.para("Looking north over the site, about 2.4 km across, with heights exaggerated five times. The yellow pin marks the site.", 11.5)
    c.para("The elevation model is about 20 to 30 m resolution: it reads the landform, not the fine grading. A site survey comes later.", 11.5)


def sheet_summary(p, st):
    blank_body(p)
    furniture(p, TOTAL, "Four sites compared")
    path = HERE / "img" / "city_plan.png"
    pix = pymupdf.Pixmap(str(path))
    mw = 562.0
    mh = mw * pix.height / pix.width
    r = image_stamp(p, (45, 136, 45 + mw, 136 + mh), path)
    fr = p.add_rect_annot(r)
    fr.set_colors(stroke=st["thin"][0]); fr.set_border(width=0.6)
    fr.set_info(title="BHackman", subject="Rectangle", content="Image frame"); fr.update()
    R_ = st["pin_r"]
    for i, sid in enumerate(bp.ORDER, 1):
        px, py = bp.PINS[sid]
        cx, cy = r.x0 + px * r.width, r.y0 + py * r.height
        circle(p, cx, cy, R_, st, st["pin_w"], f"Site {i}")
        new_text(p, (cx - 15, cy - 13.8, cx + 15, cy + 15), [str(i)], st["pin_n"], str(i))
        lab = f"{bp.LET[sid]} · {bp.P[sid]['name']}"
        lw = FONT["bcb"].text_length(lab, 14.5) + 2 * INSET_X + 20
        left = sid in ("C", "F")
        x0 = cx - R_ - 2 - lw if left else cx + R_ + 2
        new_text(p, (x0, cy - 14.5, x0 + lw, cy + 14.5), [lab], ds_size(st["pin_l"], 14.5, align="right" if left else "left"), lab)
    # right column
    c = Column(p, st, 633.0)
    c.label("OVERALL", gap=False)
    cols = [("", 22, "c"), ("SITE", 108, "l"), ("/35", 26, "r"), ("CHARACTER", 80, "l"), ("CITY", 46, "r"),
            ("MOUNTAINS", 56, "r"), ("ROOM", 70, "l"), ("FLOOD", 44, "l"), ("LAND", 0, "l")]
    cols[-1] = ("LAND", (c.tr - c.tl) - sum(cw for _, cw, _ in cols[:-1]) - 4 * (len(cols) - 1), "l")
    xs, xx = [], c.tl
    for _, cw, _ in cols:
        xs.append(xx); xx += cw + 4
    hd_ds = ds_size(st["label"], 10, color="#1B1B1B")
    for (hd, cw, al), x0 in zip(cols, xs):
        if hd:
            wdt = FONT["bcs"].text_length(hd, 10) + 2 * INSET_X + 10
            rr = (x0 + cw + INSET_X - wdt, c.y, x0 + cw + INSET_X, c.y + 20) if al == "r" else (x0 - INSET_X, c.y, x0 - INSET_X + wdt, c.y + 20)
            new_text(p, rr, [hd], ds_size(hd_ds, 10, align="right" if al == "r" else "left"), hd)
    c.y += 17
    new_line(p, c.tl + 4.1, c.tr + 4.1, c.y, 0.75, st["thick"][0])
    top = max(bp.TOTALS)
    semi = st["kv_k"].replace("'Source Serif 4'", "'Source Serif 4 Semibold'")
    cell_ds = {"sss": semi, "ssr": st["kv_k"], "bcb": st["num"], "bcs": st["kv_v"]}
    for i, sid in enumerate(bp.ORDER, 1):
        t = bp.P[sid]
        mtn = min(bp.MTN[sid]["wildhorn"]["min"], bp.MTN[sid]["kananaskis_village"]["min"])
        cells = [f"{bp.LET[sid]} · {t['name']}", str(t["total"]), t["character"], bp.r5(bp.city_min(sid)), bp.r5(mtn),
                 t["roomw"], t["flood"], t["land"]]
        fonts = ["sss", "bcb", "ssr", "bcs", "bcs", "ssr", "ssr", "ssr"]
        sizes = [10.8, 13.7, 10.4, 12.2, 12.2, 10.4, 10.4, 10.4]
        wl = [wrap(cl, fo, sz, cw) for cl, fo, sz, (_, cw, _) in zip(cells, fonts, sizes, cols[1:])]
        rh = max(22, 7 + 13.5 * max(len(x) for x in wl))
        if t["total"] == top:
            hl = p.add_rect_annot(pymupdf.Rect(c.tl + 4.1, c.y + 0.4, c.tr + 4.1, c.y + rh - 0.4))
            hl.set_colors(stroke=[], fill=(232 / 255, 227 / 255, 214 / 255)); hl.set_border(width=0)
            hl.set_info(title="BHackman", subject="Rectangle", content="Leading site"); hl.update()
        cx, cy = xs[0] + 11, c.y + rh / 2
        circle(p, cx, cy, 10, st, 1.6, f"Site {i}")
        new_text(p, (cx - 13, cy - 11.5, cx + 13, cy + 12.5), [str(i)], ds_size(st["pin_n"], 12.2), str(i))
        for cl, lines, fo, sz, (_, cw, al), x0 in zip(cells, wl, fonts, sizes, cols[1:], xs[1:]):
            yy = c.y + (rh - len(lines) * 13.5) / 2 - 1
            ds = ds_size(cell_ds[fo], sz, align="right" if al == "r" else "left")
            ds = re.sub(r"line-height:\s*[\d.]+pt", "line-height:13.5pt", ds)
            new_text(p, (x0 - INSET_X, yy - INSET_Y + 2, x0 + cw + INSET_X + 2, yy + len(lines) * 13.5 + INSET_Y + 2), lines, ds, cl[:40])
        c.y += rh
        new_line(p, c.tl + 4.1, c.tr + 4.1, c.y, st["thin"][1], st["thin"][0])
    c.label("HOW THE SITES WERE SCORED")
    for k, lab in bp.CRIT:
        new_text(p, (c.tl - INSET_X, c.y - 2.2, c.tl + 112, c.y + 24.7), [lab], ds_size(st["kv_v"], 12.2, align="left"), lab)
        new_text(p, (c.tl + 116 - INSET_X, c.y, c.tr + INSET_X, c.y + 23.8), [bp.DEFS[k]], st["kv_k"], bp.DEFS[k])
        new_line(p, c.tl + 4.1, c.tr + 4.1, c.y + 19.4, st["thin"][1], st["thin"][0])
        c.y += 20
    c.label("WHERE IT LANDS")
    runs = []
    for part in re.split(r"(<b>.*?</b>)", bp.LANDS):
        if part:
            runs.append((part[3:-4], "sss") if part.startswith("<b>") else (part, "ssr"))
    lines = wrap_runs(runs, 12.2, c.tr - c.tl)
    new_rich(p, (c.tl - INSET_X, c.y + 2, c.tr + INSET_X, c.y + 2 + len(lines) * 17.7 + 7.4), lines, st["body"], "Where it lands")


# ------------------------------------------------------------------ build
def build():
    sheet_overall(doc[0])
    styles = grab_styles()
    n = 2
    for i, sid in enumerate(bp.ORDER):
        sheet_context(doc[1 + 3 * i], sid, n)
        sheet_site(doc[2 + 3 * i], sid, n + 1)
        sheet_terrain(doc[3 + 3 * i], sid, n + 2, styles)
        n += 3
    sheet_summary(doc[TOTAL - 1], styles)
    if _scratch is not None:
        doc.delete_page(_scratch.number)
    toc = [[1, "01 Site selection", 1]]
    for i, sid in enumerate(bp.ORDER):
        nm = f"{bp.LET[sid]} {bp.P[sid]['name']}"
        k = 2 + 3 * i
        toc += [[1, f"{k:02d} {nm}: context", k], [1, f"{k+1:02d} {nm}: site", k + 1], [1, f"{k+2:02d} {nm}: terrain", k + 2]]
    toc.append([1, f"{TOTAL:02d} Summary", TOTAL])
    doc.set_toc(toc)
    doc.set_metadata({**doc.metadata, "title": "Cairn Youth Centre: Site selection", "author": "Ben Hackman"})
    out = HERE / OUTNAME
    doc.save(out, garbage=3, deflate=True)
    shutil.copy(out, SRC.parent / OUTNAME)
    print("wrote", out, "and a copy beside the source;", len(doc), "pages")


def proof():
    """Draw every Text Box that has no appearance (the ones Bluebeam will rebuild) so the layout can be checked."""
    d = pymupdf.open(HERE / OUTNAME)
    outdir = HERE / "_check_tpl"; outdir.mkdir(exist_ok=True)
    for k, p in enumerate(d, 1):
        todo, kill = [], []
        for a in p.annots():
            if a.type[1] == "FreeText" and doc_ap_null(d, a):
                todo.append((a.rect, a.info.get("content", ""), d.xref_get_key(a.xref, "DS")[1]))
                kill.append(a.xref)
            if a.type[1] == "Line" and doc_ap_null(d, a):
                L = [float(v) for v in d.xref_get_key(a.xref, "L")[1].strip("[]").split()]
                p.draw_line((L[0], PH - L[1]), (L[2], PH - L[3]), color=a.colors["stroke"], width=a.border["width"])
        for a in [a for a in p.annots() if a.xref in kill]:
            p.delete_annot(a)
        for kk, f in (("bcs", "BarlowCondensed-SemiBold.ttf"), ("bcb", "BarlowCondensed-Bold.ttf"), ("bcm", "BarlowCondensed-Medium.ttf"),
                      ("ssr", "SourceSerif4-Regular.ttf"), ("ssi", "SourceSerif4-It.ttf"), ("sss", "SourceSerif4-Semibold.ttf")):
            p.insert_font(fontname=kk, fontfile=str(FONTS / f))
        for r, c, ds in todo:
            key, sz = fonts_of(ds)
            col = re.search(r"color:\s*(#[0-9A-Fa-f]{6})", ds)
            col = tuple(int(col.group(1)[i:i + 2], 16) / 255 for i in (1, 3, 5)) if col else (0, 0, 0)
            m = re.search(r"line-height:\s*([\d.]+)pt", ds)
            lead = float(m.group(1)) if m else 1.2 * sz
            al = "right" if "right" in ds else "center" if "center" in ds else "left"
            y = r.y0 + INSET_Y + 1.024 * sz
            for ln in c.split("\r"):
                w = FONT[key].text_length(ln, sz)
                x = {"left": r.x0 + INSET_X, "right": r.x1 - INSET_X - w, "center": (r.x0 + r.x1 - w) / 2}[al]
                p.insert_text((x, y), ln, fontname=key, fontsize=sz, color=col)
                y += lead
        p.get_pixmap(dpi=100).save(outdir / f"p{k:02d}.png")
    print("proofs in", outdir)


def doc_ap_null(d, a):
    return d.xref_get_key(a.xref, "AP")[0] in ("null", "none")


if __name__ == "__main__":
    build()
    if "--check" in sys.argv:
        proof()

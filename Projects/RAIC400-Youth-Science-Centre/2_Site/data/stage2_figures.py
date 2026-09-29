"""Figures for stage2_scan.py: Esri clips (dot + 400 m ring + footprint) and proportional sun sections.
Called by stage2_scan.py; not meant to be run alone."""
import math
from pathlib import Path
from PIL import ImageDraw, ImageFont
import make_maps_reframe as mm

YEL = (255, 212, 0)
CYAN = (0, 229, 255)
CREDIT = "Imagery: Esri, Maxar, Earthstar Geographics, and the GIS User Community"

# building used in every section (schematic, same for all sites so they compare): 2 storeys x 4.0 m, 16 m deep,
# south glazing 2.4 m tall per storey starting 0.9 m above each floor
BLDG = {"depth": 16.0, "storey": 4.0, "storeys": 2, "glass_h": 2.4, "sill": 0.9}


def clip(site, rec, out_dir, z=16):
    lat, lon = rec["anchor"]
    img, x0, y0 = mm.render(lat, lon, z, mm.ESRI, mm.W, mm.H)
    d = ImageDraw.Draw(img)

    def px(la, lo):
        x, y = mm.merc(la, lo, z)
        return x - x0, y - y0
    # footprint outline
    for ring in rec["footprint"]["rings"]:
        pts = [px(a, b) for a, b in ring]
        d.line(pts + [pts[0]], fill=CYAN, width=3)
    # stage 1 anchor, if different and in frame
    s1 = site["stage1_anchor"]
    sx, sy = px(*s1)
    if 0 < sx < mm.W and 0 < sy < mm.H and math.hypot(sx - mm.W / 2, sy - mm.H / 2) > 20:
        d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], outline=(255, 255, 255), width=3)
        f = ImageFont.truetype(mm.FONT, 18)
        d.text((sx + 12, sy - 10), "Stage 1 anchor", font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    # ring + dot (convention)
    x, y = mm.W / 2, mm.H / 2
    rpx = 400 / mm.mpp(lat, z)
    for k in range(0, 360, 6):
        a0, a1 = math.radians(k), math.radians(k + 3.5)
        d.line([(x + rpx * math.cos(a0), y + rpx * math.sin(a0)), (x + rpx * math.cos(a1), y + rpx * math.sin(a1))], fill=YEL, width=4)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=YEL, outline=(0, 0, 0), width=3)
    mm.scale_bar(d, z, lat)
    f = ImageFont.truetype(mm.FONT, 22)
    f2 = ImageFont.truetype(mm.FONT, 15)
    title = f"{site['id']}  {site['name']}"
    d.rectangle([20, 18, 30 + d.textlength(title, font=f), 52], fill=(255, 255, 255))
    d.text((26, 22), title, font=f, fill=(0, 0, 0))
    leg = f"yellow: anchor + 400 m ring   cyan: {rec['footprint']['label']}"
    d.rectangle([20, 58, 30 + d.textlength(leg, font=f2), 80], fill=(255, 255, 255))
    d.text((26, 61), leg, font=f2, fill=(0, 0, 0))
    d.text((mm.W - d.textlength(CREDIT, font=f2) - 12, mm.H - 22), CREDIT, font=f2, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    p = Path(out_dir) / f"stage2_{site['id']}.jpg"
    img.save(p, quality=86)
    print("clip", p.name)


class Panel:
    """True-scale drawing panel: one metre is the same number of pixels on both axes."""
    def __init__(self, d, box, x0, x1, y0, y1):
        self.d, self.box = d, box
        L, T, R, B = box
        self.s = min((R - L) / (x1 - x0), (B - T) / (y1 - y0))
        self.x0, self.y0 = x0, y0
        self.L, self.B = L, T + (y1 - y0) * self.s
        self.R = L + (x1 - x0) * self.s

    def p(self, x, y):
        return (self.L + (x - self.x0) * self.s, self.B - (y - self.y0) * self.s)

    def line(self, pts, **kw):
        self.d.line([self.p(*q) for q in pts], **kw)

    def poly(self, pts, **kw):
        self.d.polygon([self.p(*q) for q in pts], **kw)


def sun_section(site, rec, sun, out_dir, obstruction=None):
    from PIL import Image
    e = rec["elev"]
    z0 = e["anchor_cdem"]
    ws, eq, ss = (sun[k]["noon_altitude_deg"] for k in ("winter_solstice", "equinox", "summer_solstice"))
    RED, ORG, OLV, GRN, BRN, BLU = (214, 39, 40), (255, 127, 14), (170, 170, 30), (46, 125, 50), (107, 79, 42), (31, 119, 180)
    W_, H_ = 1700, 1600
    img = Image.new("RGB", (W_, H_), "white")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(mm.FONT.replace("arialbd", "arial"), 17)
    fb = ImageFont.truetype(mm.FONT, 22)
    fs = ImageFont.truetype(mm.FONT.replace("arialbd", "arial"), 14)
    d.text((30, 18), f"Sun section {site['id']}: {site['name']}  (lat {rec['anchor'][0]:.4f})", font=fb, fill="black")
    gs = e["near_south_cdem_400m"]; gn = e["prof_N_300m"]
    D, Hs, n = BLDG["depth"], BLDG["storey"], BLDG["storeys"]
    H = Hs * n
    sh = H / math.tan(math.radians(ws))
    ob = obstruction or {}
    # ---------------- panel 1: near field, true scale
    x0, x1 = -D - sh - 8, 125
    lo = min(min(g - z0 for g in gs[:14]), min(g - z0 for g in gn[:7])) - 4
    hi = max(H, ob.get("height_m", 0)) + 12
    P = Panel(d, (60, 90, W_ - 40, 700), x0, x1, lo, hi)
    yb0 = int(P.B) + 40            # everything below follows the near panel
    d.text((60, 62), "Near field, true scale: schematic 2-storey node wing on the anchor (south face at 0 m)", font=f, fill="black")
    for gx in range(int(x0 // 10) * 10, int(x1) + 1, 10):     # 10 m grid
        P.line([(gx, lo), (gx, hi)], fill=(232, 232, 232), width=1)
        d.text((P.p(gx, lo)[0] - 10, P.p(gx, lo)[1] + 4), f"{gx}", font=fs, fill=(90, 90, 90))
    for gy in range(int(lo // 5) * 5, int(hi) + 1, 5):
        P.line([(x0, gy), (x1, gy)], fill=(232, 232, 232), width=1)
        d.text((P.L - 40, P.p(x0, gy)[1] - 8), f"{gy}", font=fs, fill=(90, 90, 90))
    # ground (north profile 25 m steps, south profile 10 m steps)
    ground = [(-25 * k, g - z0) for k, g in enumerate(gn)][::-1] + [(10 * k, g - z0) for k, g in enumerate(gs)]
    ground = [q for q in ground if x0 - 30 <= q[0] <= x1 + 10]
    P.poly(ground + [(ground[-1][0], lo), (ground[0][0], lo)], fill=(222, 206, 176))
    P.line(ground, fill=BRN, width=3)
    # obstruction
    if ob:
        d0, hh, w = ob["distance_m"], ob["height_m"], ob.get("depth_m", 25)
        gz = gs[min(len(gs) - 1, int(d0 // 10))] - z0
        P.poly([(d0, gz), (d0, gz + hh), (min(d0 + w, x1), gz + hh), (min(d0 + w, x1), gz)], fill=(170, 205, 160), outline=GRN)
        ang = math.degrees(math.atan2(gz + hh - BLDG["sill"], d0))
        P.line([(0, BLDG["sill"]), (d0, gz + hh)], fill=GRN, width=2)
        tx, ty = P.p(d0 + 2, gz + hh + 1)
        tx = min(tx, W_ - 560)
        d.text((tx, ty - 44), f"{ob['label']}: ~{hh:.0f} m tall, {d0:.0f} m S (imagery estimate)", font=fs, fill=GRN)
        d.text((tx, ty - 24), f"obstruction angle {ang:.1f} deg from the lower sill", font=fs, fill=GRN)
    # building, glass, overhang
    P.poly([(0, 0), (0, H), (-D, H), (-D, 0)], fill=(154, 167, 176), outline=(80, 80, 80))
    for k in range(n):
        g0 = k * Hs + BLDG["sill"]
        P.line([(0, g0), (0, g0 + BLDG["glass_h"])], fill=BLU, width=6)
    oh = BLDG["glass_h"] / math.tan(math.radians(ss))
    top_glass = (n - 1) * Hs + BLDG["sill"] + BLDG["glass_h"]
    P.line([(0, top_glass + 0.3), (oh, top_glass + 0.3)], fill="black", width=5)
    # rays to the lower sill
    for alt, col, lab in ((ws, RED, "winter solstice"), (eq, ORG, "equinox"), (ss, OLV, "summer solstice")):
        L = (hi - BLDG["sill"]) / math.tan(math.radians(alt))
        L = min(L, x1)
        if ob:
            yb = BLDG["sill"] + ob["distance_m"] * math.tan(math.radians(alt))
            if yb < gz + ob["height_m"] and L > ob["distance_m"]:     # ray blocked by the obstruction
                P.line([(0, BLDG["sill"]), (ob["distance_m"], yb)], fill=col, width=3)
                bx, by = P.p(ob["distance_m"], yb)
                d.ellipse([bx - 6, by - 6, bx + 6, by + 6], outline=col, width=3)
                d.text((bx + 8, by - 2), f"{lab} noon ray blocked", font=fs, fill=col)
                continue
        P.line([(0, BLDG["sill"]), (L, BLDG["sill"] + L * math.tan(math.radians(alt)))], fill=col, width=3)
    # winter-noon shadow to the north
    P.line([(-D, 0.2), (-D - sh, 0.2)], fill=(240, 150, 150), width=8)
    sx, sy = P.p(-D - sh / 2, 0.5)
    d.text((sx - 90, sy - 26), f"winter-noon shadow {sh:.0f} m", font=fs, fill=RED)
    ox, oy = P.p(oh, top_glass + 0.6)
    d.text((ox + 6, oy - 20), f"overhang {oh:.2f} m = 2.4 m glass / tan {ss} deg", font=fs, fill="black")
    # legend
    ly = yb0
    for col, txt in ((RED, f"winter solstice noon {ws} deg"), (ORG, f"equinox noon {eq} deg"), (OLV, f"summer solstice noon {ss} deg"),
                     (BRN, "ground, NRCan CDEM (bare earth)"), (BLU, "south glazing 2.4 m per storey")):
        d.line([(70, ly + 9), (110, ly + 9)], fill=col, width=4)
        d.text((118, ly), txt, font=f, fill="black")
        ly += 24
    note = sun_note(site, sun, rec)
    d.text((700, yb0), note, font=f, fill="black")
    # ---------------- panel 2: far field due south, true scale
    far = e["horizon"]["cdem"].get("180") or e["horizon"]["cdem"].get(180)
    zf = [g - z0 for g in far]
    y0f, y1f = min(zf) - 15, max(max(zf) + 25, 60)
    fy = ly + 50
    Q = Panel(d, (60, fy, W_ - 40, fy + 400), 0, 4000, y0f, y1f)
    d.text((60, fy - 36), "Far field due south to 4 km, true scale (ray = winter-solstice noon from eye height)", font=f, fill="black")
    pts = [(50 * k, z) for k, z in enumerate(zf)]
    Q.poly(pts + [(pts[-1][0], y0f), (0, y0f)], fill=(222, 206, 176))
    Q.line(pts, fill=BRN, width=2)
    xr = min(4000, (y1f - 1.6) / math.tan(math.radians(ws)))
    Q.line([(0, 1.6), (xr, 1.6 + xr * math.tan(math.radians(ws)))], fill=RED, width=2)
    for gx in range(0, 4001, 500):
        d.text((Q.p(gx, y0f)[0] - 12, Q.p(gx, y0f)[1] + 4), f"{gx} m", font=fs, fill=(90, 90, 90))
    hz = max(math.degrees(math.atan2(z - 1.6, x)) for x, z in pts[1:])
    d.text((70, Q.p(0, y1f)[1] - 2), f"terrain horizon due S: {hz:.1f} deg  vs winter-noon sun {ws} deg", font=fs, fill="black")
    H_ = int(Q.B) + 70
    img = img.crop((0, 0, W_, H_))
    d = ImageDraw.Draw(img)
    d.text((30, H_ - 30), "Solar noon altitude = 90 - latitude + declination (+/-23.44 deg). Terrain: NRCan CDEM via geogratis, concept grade. "
           "Tree heights are imagery estimates (unverified). Same schematic building on every site.", font=fs, fill=(60, 60, 60))
    p = Path(out_dir) / f"stage2_sun_{site['id']}.png"
    img.save(p, optimize=True)
    print("sun", p.name)


def sun_note(site, sun, rec):
    w = sun["winter_solstice"]; s = sun["summer_solstice"]
    return (f"Winter solstice: noon {w['noon_altitude_deg']} deg, day {w['day_length_h']} h, sun rises at az {w['sunrise_azimuth_deg']}\n"
            f"Summer solstice: noon {s['noon_altitude_deg']} deg, day {s['day_length_h']} h, rises at az {s['sunrise_azimuth_deg']}\n"
            f"Equinox: noon {sun['equinox']['noon_altitude_deg']} deg, 12 h")


def draw_all(sites, raw, img_dir, diag_dir):
    import stage2_scan as s2
    Path(diag_dir).mkdir(exist_ok=True)
    for s in sites:
        rec = raw["sites"][s["id"]]
        clip(s, rec, img_dir)
        import stage2_narrative as NARR
        sun_section(s, rec, s2.sun_geometry(rec["anchor"][0]), diag_dir, NARR.OBSTRUCTION.get(s["id"]))

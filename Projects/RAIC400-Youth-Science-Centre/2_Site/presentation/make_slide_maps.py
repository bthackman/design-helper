"""Clean map images for the class presentation (Stage 2 four sites), no burned-in titles.
- city_plan.png: Esri Light Gray base, Calgary west to Bragg Creek, numbered site pins + reference marks.
- zone_<id>.jpg: Esri imagery z14, anchor dot + 400 m ring (neighbourhood context).
- site_<id>.jpg: Esri imagery z16, anchor dot + 400 m ring + chosen footprint (cyan).
Data: ../data/stage2_2026-09-29.json. Usage: python make_slide_maps.py
"""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "data"))
import make_maps_reframe as mm  # tile cache, merc, mpp, render

import hashlib, time

_orig_tile = mm.tile
TILES = HERE / "_tiles"  # disk cache (untracked); the network here drops DNS intermittently
TILES.mkdir(exist_ok=True)


def _tile(url, z, x, y):
    f = TILES / (hashlib.md5(url.encode()).hexdigest()[:6] + f"_{z}_{x}_{y}.png")
    if f.exists():
        return Image.open(f).convert("RGB")
    for attempt in range(12):
        try:
            im = _orig_tile(url, z, x, y)
            im.save(f)
            return im
        except Exception:
            if attempt == 11:
                raise
            time.sleep(5)


mm.tile = _tile
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)
FONTS = Path(r"C:\Users\BHackman\OneDrive - DIALOG\BHackman Drive\00_AI\Claude\RAIC 400\Templates\Fonts")
FB = str(FONTS / "BarlowCondensed-Bold.ttf")
FM = str(FONTS / "BarlowCondensed-SemiBold.ttf")
INK, RED, PAPER = (27, 27, 27), (166, 58, 38), (245, 242, 234)
YEL, CYAN = (255, 212, 0), (0, 229, 255)

# presentation order: urban -> rural
ORDER = ["C", "F", "I", "N"]
SHORT = {"C": "Inglewood", "F": "Glenmore Landing", "I": "Loch McKinnon", "N": "Glenbow Ranch"}

data = json.loads((HERE.parent / "data" / "stage2_2026-09-29.json").read_text(encoding="utf-8"))
SITES = {s["id"]: s for s in data["sites"]}
DEST = data["destinations"]


def ring(d, x, y, rpx, col=YEL, w=4):
    for k in range(0, 360, 6):
        a0, a1 = math.radians(k), math.radians(k + 3.5)
        d.line([(x + rpx * math.cos(a0), y + rpx * math.sin(a0)), (x + rpx * math.cos(a1), y + rpx * math.sin(a1))], fill=col, width=w)


def scale_and_north(d, W, H, z, lat, dark=False):
    m = mm.mpp(lat, z)
    for L in (5000, 2000, 1000, 500, 250, 200, 100):
        if L / m <= 300:
            break
    px = L / m
    f = ImageFont.truetype(FM, 26)
    x, y = 40, H - 46
    d.rectangle([x - 14, y - 44, x + px + 20, y + 22], fill=(255, 255, 255))
    d.rectangle([x, y, x + px, y + 9], fill=INK)
    d.rectangle([x + px / 2, y, x + px, y + 9], fill=(255, 255, 255), outline=INK)
    d.text((x, y - 38), f"{L // 1000} km" if L >= 1000 else f"{L} m", font=f, fill=INK)
    ax, ay = W - 50, 58
    d.polygon([(ax, ay - 34), (ax - 16, ay + 10), (ax, ay), (ax + 16, ay + 10)], fill=(255, 255, 255), outline=INK)
    d.text((ax - 7, ay + 12), "N", font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=INK)


SUMMER, WINTER = (255, 150, 30), (140, 205, 255)


def arc_az(d, cx, cy, R, a0, a1, col, w=6):
    """Arc in plan from azimuth a0 to a1 (degrees clockwise from N, through S)."""
    pts = [(cx + R * math.sin(math.radians(a)), cy - R * math.cos(math.radians(a))) for a in [a0 + (a1 - a0) * k / 60 for k in range(61)]]
    d.line(pts, fill=INK, width=w + 4, joint="curve")
    d.line(pts, fill=col, width=w, joint="curve")
    return pts


def label(d, xy, t, col, size=26):
    f = ImageFont.truetype(FB, size)
    d.text(xy, t, font=f, fill=col, stroke_width=4, stroke_fill=INK)


def sun_and_wind(d, cx, cy, s):
    """Schematic sun path (sunrise/sunset directions at the solstices, through due south) and the prevailing wind."""
    sun = s["metrics"]["sun"]
    for key, R, col, txt in (("summer_solstice", 310, SUMMER, "Summer sun"), ("winter_solstice", 370, WINTER, "Winter sun")):
        rise = sun[key]["sunrise_azimuth_deg"]; set_ = sun[key]["sunset_azimuth_deg"]
        pts = arc_az(d, cx, cy, R, rise, set_, col)
        for (x, y), t in ((pts[0], "rise"), (pts[-1], "set")):
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col, outline=INK, width=3)
            label(d, (x + (14 if t == "rise" else -60), y - 34), t, col, 24)
        mx, my = pts[30]
        label(d, (mx - 52, my + 10), txt, col)
    # prevailing wind: from the W
    y = cy + 40
    x0, x1 = 50, cx - 400
    for wdt, col in ((16, INK), (10, (255, 255, 255))):
        d.line([(x0, y), (x1 - 10, y)], fill=col, width=wdt)
    d.polygon([(x1 + 14, y), (x1 - 30, y - 26), (x1 - 30, y + 26)], fill=(255, 255, 255), outline=INK, width=3)
    label(d, (x0, y - 46), "Prevailing wind (W)", (255, 255, 255))


def site_img(sid, z, W, H, name, footprint):
    s = SITES[sid]
    lat, lon = s["anchor"]["lat"], s["anchor"]["lon"]
    img, x0, y0 = mm.render(lat, lon, z, mm.ESRI, W, H)
    d = ImageDraw.Draw(img)
    if footprint:
        for rg in s["footprint"]["rings_latlon"]:
            pts = [(mm.merc(a, b, z)[0] - x0, mm.merc(a, b, z)[1] - y0) for a, b in rg]
            d.line(pts + [pts[0]], fill=CYAN, width=4)
    rpx = 400 / mm.mpp(lat, z)
    ring(d, W / 2, H / 2, rpx, w=4 if z >= 15 else 3)
    r = 14 if z >= 15 else 11
    d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=YEL, outline=INK, width=3)
    if footprint:
        sun_and_wind(d, W / 2, H / 2, s)
    scale_and_north(d, W, H, z, lat)
    img.save(OUT / name, quality=88)
    print(name, "view width m", round(W * mm.mpp(lat, z)))


# city plan frame (lon/lat box), rendered at z12
CP = {"w": -115.24, "e": -113.93, "n": 51.235, "s": 50.765, "z": 12}
MTN = {"Wildhorn (Forgetmenot Ridge)": (50.8101, -114.8273), "Kananaskis Village": (50.9172, -115.1478)}  # OSRM-snapped


def darken(img, x0, y0, z):
    """Light Gray base is too pale on paper: stretch contrast, tint water, multiply a soft hillshade."""
    import numpy as np
    import make_terrain as mt
    a = np.asarray(img).astype(np.float64)
    g = a.mean(axis=2)
    out = 255 - (255 - a) * 2.4
    water = g < 214
    out[water] = (128, 152, 178)
    roads = g > 247                      # white road casing in the base -> mid-dark grey lines
    out[roads] = 255 - (g[roads, None] - 247) / 8 * 150
    # hillshade from Terrarium z(z-1) on the same pixel grid (upsampled x2)
    H, W = g.shape
    zx0, zy0 = x0 / 2, y0 / 2
    dem = np.zeros((H // 2 + 2, W // 2 + 2))
    for tx in range(int(zx0 // 256), int((zx0 + W / 2) // 256) + 1):
        for ty in range(int(zy0 // 256), int((zy0 + H / 2) // 256) + 1):
            t = mt.dem_tile(z - 1, tx, ty)
            ox, oy = int(tx * 256 - zx0), int(ty * 256 - zy0)
            sx0, sy0, dx0, dy0 = max(0, -ox), max(0, -oy), max(0, ox), max(0, oy)
            w, h = min(256 - sx0, dem.shape[1] - dx0), min(256 - sy0, dem.shape[0] - dy0)
            if w > 0 and h > 0:
                dem[dy0:dy0 + h, dx0:dx0 + w] = t[sy0:sy0 + h, sx0:sx0 + w]
    demi = Image.fromarray(dem.astype(np.float32), mode="F").resize((dem.shape[1] * 2, dem.shape[0] * 2), Image.BILINEAR)
    zz = mt.blur(np.asarray(demi).astype(np.float64), 2)[:H, :W]
    m = mm.mpp(51.0, z)
    gy, gx = np.gradient(zz * 2.0, m)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    az, alt = math.radians(315), math.radians(40)
    hs = np.clip(np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect), 0, 1)
    k = 0.62 + 0.38 * hs / np.percentile(hs, 90)
    out = np.clip(out * np.clip(k, 0, 1.08)[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def city_plan():
    z = CP["z"]
    xw, yn = mm.merc(CP["n"], CP["w"], z)
    xe, ys = mm.merc(CP["s"], CP["e"], z)
    W, H = int(xe - xw), int(ys - yn)
    img, x0, y0 = mm.render((CP["n"] + CP["s"]) / 2, (CP["w"] + CP["e"]) / 2, z, mm.GRAY, W, H)
    S = 1  # site pins are drawn by the slide layer (HTML/PDF) from city_plan_pins.json
    img = darken(img, x0, y0, z)
    d = ImageDraw.Draw(img)

    def px(lat, lon):
        x, y = mm.merc(lat, lon, z)
        return (x - x0) * S, (y - y0) * S

    fl = ImageFont.truetype(FM, 58)
    fs = ImageFont.truetype(FB, 40)
    # reference marks (small squares, ink)
    refs = {"Downtown": tuple(DEST["city_hall_downtown"]), "YYC airport": tuple(DEST["yyc_airport"]),
            "Cochrane": (51.1894, -114.4675), "Bragg Creek": (50.9480, -114.5710), **MTN,
            "U of C": tuple(DEST["university_of_calgary"])}
    for lab, (la, lo) in refs.items():
        x, y = px(la, lo)
        d.rectangle([x - 13, y - 13, x + 13, y + 13], fill=INK)
        tx = x - 24 - d.textlength(lab, font=fl) if lab == "YYC airport" else x + 24  # keep YYC inside the frame
        d.text((tx, y - 36), lab, font=fl, fill=INK, stroke_width=6, stroke_fill=(255, 255, 255))
    pins = {}
    for sid in ORDER:
        s = SITES[sid]
        x, y = px(s["anchor"]["lat"], s["anchor"]["lon"])
        pins[sid] = [round(x / (W * S), 4), round(y / (H * S), 4)]
    # scale bar 10 km
    m = mm.mpp((CP["n"] + CP["s"]) / 2, z) / S
    L = 10000 / m
    bx, by = 50, H * S - 60
    d.rectangle([bx, by, bx + L, by + 12], fill=INK)
    d.rectangle([bx + L / 2, by, bx + L, by + 12], fill=(255, 255, 255), outline=INK)
    d.text((bx, by - 50), "10 km", font=fl, fill=INK)
    ax, ay = W * S - 70, 80
    d.polygon([(ax, ay - 46), (ax - 22, ay + 14), (ax, ay), (ax + 22, ay + 14)], fill=INK)
    d.text((ax - 9, ay + 18), "N", font=fl, fill=INK)
    img.save(OUT / "city_plan.png", optimize=True)
    (OUT / "city_plan_pins.json").write_text(json.dumps({"size": [W * S, H * S], "pins": pins}, indent=1))
    print("city_plan.png", W * S, H * S, pins)


if __name__ == "__main__":
    force = "--force" in sys.argv  # otherwise skip images already rendered
    if force or not (OUT / "city_plan.png").exists():
        city_plan()
    for sid in ORDER:
        for z, name, fp in ((14, f"zone_{sid}.jpg", False), (16, f"site_{sid}.jpg", True)):
            if force or not (OUT / name).exists():
                site_img(sid, z, 1600, 1040, name, footprint=fp)

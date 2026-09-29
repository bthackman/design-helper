"""Site-package map clips: Esri World Imagery for each site, CARTO light basemap for the overview.
Parcel outlines (A, B: the lots Ben picked) from City of Calgary assessments (4bsw-nn7w); every other zone gets an
anchor dot + 400 m ring until a parcel is chosen. Usage: python make_maps.py [site ids]. The overview map
(Esri World Light Gray Canvas, z13, 2000 px downsampled to 1000) was built in a one-off step, not here."""
import io, json, math, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "img"
OUT.mkdir(exist_ok=True)
UA = {"User-Agent": "RAIC400-student-site-search"}
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
CARTO = "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png"
FONT = "C:/Windows/Fonts/arialbd.ttf"
W, H = 1200, 800

def merc(lat, lon, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y

def mpp(lat, z):
    return 156543.03392 * math.cos(math.radians(lat)) / 2 ** z

_cache = {}
def tile(url, z, x, y, size):
    k = (url, z, x, y)
    if k not in _cache:
        r = requests.get(url.format(z=z, x=x, y=y), headers=UA, timeout=60)
        r.raise_for_status()
        _cache[k] = Image.open(io.BytesIO(r.content)).convert("RGB").resize((size, size))
        time.sleep(0.05)
    return _cache[k]

def render(clat, clon, z, url, w=W, h=H):
    cx, cy = merc(clat, clon, z)
    x0, y0 = cx - w / 2, cy - h / 2
    img = Image.new("RGB", (w, h))
    for tx in range(int(x0 // 256), int((x0 + w) // 256) + 1):
        for ty in range(int(y0 // 256), int((y0 + h) // 256) + 1):
            img.paste(tile(url, z, tx, ty, 256), (int(tx * 256 - x0), int(ty * 256 - y0)))
    to_px = lambda la, lo: (merc(la, lo, z)[0] - x0, merc(la, lo, z)[1] - y0)
    return img, to_px

def parcel_rings(addr, min_area=0):
    rows = requests.get("https://data.calgary.ca/resource/4bsw-nn7w.json",
                        params={"$where": f"address = '{addr}'", "$limit": 5}, timeout=60).json()
    rows = [r for r in rows if float(r.get("land_size_sm", 0)) >= min_area]
    rows.sort(key=lambda r: -float(r["land_size_sm"]))
    return [ring for poly in rows[0]["multipolygon"]["coordinates"] for ring in poly]

def scale_bar(d, z, lat):
    m = mpp(lat, z)
    for L in (1000, 500, 250, 200, 100, 50):
        if L / m <= 260: break
    px = L / m
    f = ImageFont.truetype(FONT, 22)
    x, y = 36, H - 44
    d.rectangle([x - 12, y - 40, x + px + 110, y + 22], fill=(255, 255, 255))
    d.rectangle([x, y, x + px, y + 8], fill=(0, 0, 0))
    d.rectangle([x + px / 2, y, x + px, y + 8], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((x, y - 32), f"{L} m", font=f, fill=(0, 0, 0))
    # north arrow
    ax, ay = W - 56, 64
    d.polygon([(ax, ay - 34), (ax - 16, ay + 10), (ax, ay), (ax + 16, ay + 10)], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((ax - 8, ay + 14), "N", font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))

YEL = (255, 212, 0)
SITES = {
    "A": {"parcel": "633 15 AV SW"},
    "B": {"parcel": "708 1 AV SW"},
    "C": {"pt": (51.027895, -114.006957)},
    "D": {"pt": (50.923014, -114.07307)},
    "E": {"pt": (51.033572, -113.939943)},
    "F": {"pt": (50.9737, -114.097874)},   # zone anchor: no parcel picked yet
    "G": {"pt": (51.0883561, -114.1308072)},  # zone anchor: Brentwood Co-op
    "I": {"pt": (51.10090, -114.23840)},  # zone anchor: lagoon north shore
    "J": {"pt": (51.04643, -113.99114)},  # school reserve, Albert Park/Radisson Heights
    "K": {"pt": (51.05856, -113.97458)},  # school reserve, Marlborough
}
import sys
ONLY = sys.argv[1:] or list(SITES)
meta = {}
for sid, s in [(k, v) for k, v in SITES.items() if k in ONLY]:
    if "parcel" in s:
        rings = parcel_rings(s["parcel"], s.get("min_area", 0))
        pts = [p for r in rings for p in r]
        lats = [p[1] for p in pts]; lons = [p[0] for p in pts]
        clat, clon = (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
        z = 18
        while z > 13:
            (x1, y1), (x2, y2) = merc(max(lats), min(lons), z), merc(min(lats), max(lons), z)
            f = s.get("fit", 2.4)
            if (x2 - x1) * f <= W and (y2 - y1) * f <= H and W * mpp(clat, z) >= 700: break
            z -= 1
    else:
        clat, clon = s["pt"]; z = 16; rings = []
    img, to_px = render(clat, clon, z, ESRI)
    d = ImageDraw.Draw(img)
    for r in rings:
        xy = [to_px(p[1], p[0]) for p in r]
        d.line(xy + [xy[0]], fill=(0, 0, 0), width=9, joint="curve")
        d.line(xy + [xy[0]], fill=YEL, width=4, joint="curve")
    if not rings:
        x, y = to_px(clat, clon)
        rpx = 400 / mpp(clat, z)
        for k in range(0, 360, 6):
            a0, a1 = math.radians(k), math.radians(k + 3.5)
            d.line([(x + rpx * math.cos(a0), y + rpx * math.sin(a0)), (x + rpx * math.cos(a1), y + rpx * math.sin(a1))], fill=YEL, width=4)
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=YEL, outline=(0, 0, 0), width=3)
    scale_bar(d, z, clat)
    p = OUT / f"site_{sid}.jpg"
    img.save(p, quality=86)
    meta[sid] = {"lat": clat, "lon": clon, "zoom": z, "m_per_px": round(mpp(clat, z), 3),
                 "view_width_m": round(W * mpp(clat, z)), "file": p.name}
    print(sid, meta[sid])


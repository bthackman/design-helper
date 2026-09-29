"""Reframe (2026-09-29) map clips, extending make_maps.py.
- Site clips for the new rural/edge zones L-Q: Esri World Imagery, z16, 1200x800, anchor dot + 400 m ring
  (never a parcel outline: projects are new builds). Same style as make_maps.py.
- Overview basemap: Esri World Light Gray Canvas (base only), z12, covering Calgary west to Bragg Creek and
  Cochrane, downsampled to 1440x1000 (shown at 720x500). Pin positions (display px) are written as JSON
  to the path given by --pins (default: print only).
Anchors come from scan_2026-09-29_reframe.json. Usage: python make_maps_reframe.py [--pins out.json] [site ids]
"""
import io, json, math, sys, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)
UA = {"User-Agent": "RAIC400-student-site-search"}
ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
GRAY = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
FONT = "C:/Windows/Fonts/arialbd.ttf"
W, H = 1200, 800
YEL = (255, 212, 0)


def merc(lat, lon, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def mpp(lat, z):
    return 156543.03392 * math.cos(math.radians(lat)) / 2 ** z


_cache = {}


def tile(url, z, x, y):
    k = (url, z, x, y)
    if k not in _cache:
        for attempt in range(3):
            try:
                r = requests.get(url.format(z=z, x=x, y=y), headers=UA, timeout=60)
                r.raise_for_status()
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(1)
        _cache[k] = Image.open(io.BytesIO(r.content)).convert("RGB").resize((256, 256))
        time.sleep(0.03)
    return _cache[k]


def render(clat, clon, z, url, w, h):
    cx, cy = merc(clat, clon, z)
    x0, y0 = cx - w / 2, cy - h / 2
    img = Image.new("RGB", (w, h))
    for tx in range(int(x0 // 256), int((x0 + w) // 256) + 1):
        for ty in range(int(y0 // 256), int((y0 + h) // 256) + 1):
            img.paste(tile(url, z, tx, ty), (int(tx * 256 - x0), int(ty * 256 - y0)))
    return img, x0, y0


def scale_bar(d, z, lat):
    m = mpp(lat, z)
    for L in (1000, 500, 250, 200, 100, 50):
        if L / m <= 260:
            break
    px = L / m
    f = ImageFont.truetype(FONT, 22)
    x, y = 36, H - 44
    d.rectangle([x - 12, y - 40, x + px + 110, y + 22], fill=(255, 255, 255))
    d.rectangle([x, y, x + px, y + 8], fill=(0, 0, 0))
    d.rectangle([x + px / 2, y, x + px, y + 8], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((x, y - 32), f"{L} m", font=f, fill=(0, 0, 0))
    ax, ay = W - 56, 64
    d.polygon([(ax, ay - 34), (ax - 16, ay + 10), (ax, ay), (ax + 16, ay + 10)], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((ax - 8, ay + 14), "N", font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))


def site_clip(sid, lat, lon, z=16):
    img, x0, y0 = render(lat, lon, z, ESRI, W, H)
    d = ImageDraw.Draw(img)
    x, y = W / 2, H / 2
    rpx = 400 / mpp(lat, z)
    for k in range(0, 360, 6):
        a0, a1 = math.radians(k), math.radians(k + 3.5)
        d.line([(x + rpx * math.cos(a0), y + rpx * math.sin(a0)), (x + rpx * math.cos(a1), y + rpx * math.sin(a1))], fill=YEL, width=4)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=YEL, outline=(0, 0, 0), width=3)
    scale_bar(d, z, lat)
    p = OUT / f"site_{sid}.jpg"
    img.save(p, quality=86)
    print(sid, p.name, "zoom", z, "view width m", round(W * mpp(lat, z)))


# Overview frame: display 720x500, rendered at z12 then downsampled to 1440x1000 (2x).
OV_Z, OV_CENTER = 12, (51.052, -114.335)
OV_W, OV_H = 2360, 1640
DISP_W, DISP_H = 720, 500


def overview(sites, extra):
    img, x0, y0 = render(OV_CENTER[0], OV_CENTER[1], OV_Z, GRAY, OV_W, OV_H)
    img = img.resize((DISP_W * 2, DISP_H * 2), Image.LANCZOS)
    p = OUT / "overview_reframe_lightgray.png"
    img.save(p, optimize=True)
    k = DISP_W / OV_W

    def disp(lat, lon):
        x, y = merc(lat, lon, OV_Z)
        return round((x - x0) * k, 1), round((y - y0) * k, 1)

    pins = {s["letter"]: disp(s["lat"], s["lon"]) for s in sites}
    marks = {name: disp(*ll) for name, ll in extra.items()}
    km_px = 1000 / (mpp(OV_CENTER[0], OV_Z) / k)
    lon_w = OV_CENTER[1] - (OV_W / 2) / (256 * 2 ** OV_Z) * 360
    print("overview", p.name, "km per display px", round(1 / km_px, 3), "west edge lon", round(lon_w, 3))
    return {"pins": pins, "marks": marks, "px_per_km": round(km_px, 3), "west_edge_lon": lon_w}


if __name__ == "__main__":
    args = sys.argv[1:]
    pins_out = None
    if "--pins" in args:
        i = args.index("--pins")
        pins_out = args[i + 1]
        args = args[:i] + args[i + 2:]
    scan = json.loads((HERE / "scan_2026-09-29_reframe.json").read_text(encoding="utf-8"))
    sites = scan["sites"]
    only = args or ["L", "M", "N", "O", "P", "Q"]
    for s in sites:
        if s["letter"] in only:
            site_clip(s["letter"], s["lat"], s["lon"])
    extra = {
        "City Hall": (51.0453, -114.0581),
        "YYC": tuple(scan["destinations"]["yyc_airport"]),
        "West Bragg Creek": tuple(scan["destinations"]["west_bragg_creek_trailhead"]),
        "Cochrane": (51.1894, -114.4675),
        "Bragg Creek": (50.9480, -114.5710),
        "Kananaskis": tuple(scan["destinations"]["kananaskis_hwy1_hwy40"]),
    }
    meta = overview(sites, extra)
    print(json.dumps(meta, indent=1))
    if pins_out:
        Path(pins_out).write_text(json.dumps(meta, indent=1), encoding="utf-8")

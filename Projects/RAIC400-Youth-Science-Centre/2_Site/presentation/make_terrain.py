"""Oblique 3D terrain views (looking north) with Esri imagery draped on an elevation model, one per site.
Elevation: AWS Terrain Tiles (Terrarium encoding; CDEM/SRTM-derived in Canada), z14, upsampled to the z15 imagery grid.
Rendered with a simple painter's algorithm (parallel oblique projection), vertical exaggeration EXAG.
Also writes terrain_<id>.json with the relative-elevation facts used on the slides.
Usage: python make_terrain.py [site ids]"""
import io, json, math, sys
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import make_slide_maps as sm  # tile cache + retry, fonts, colours, SITES
mm = sm.mm

DEM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
Z = 16                  # imagery zoom (matches the 250 m-scale site view); DEM fetched at Z-1 and upsampled x2
HALF_W, HALF_S, HALF_N = 1150, 700, 1100   # metres: half width, south and north of the anchor
EXAG = 5.0
VIEW = math.radians(24)
BASE_M = 30             # slab thickness under the lowest point (metres, before exaggeration)  # view elevation angle above the horizon


def dem_tile(z, x, y):
    f = sm.TILES / f"dem_{z}_{x}_{y}.png"
    if not f.exists():
        for k in range(12):
            try:
                r = requests.get(DEM.format(z=z, x=x, y=y), timeout=60); r.raise_for_status()
                f.write_bytes(r.content); break
            except Exception:
                if k == 11: raise
                import time; time.sleep(5)
    a = np.asarray(Image.open(f).convert("RGB"), dtype=np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def blur(a, r, passes=3):
    """Separable box blur (x3 ~ Gaussian) to remove the DEM's stair-stepping before shading."""
    for _ in range(passes):
        for ax in (0, 1):
            p = np.pad(a, [(r, r) if i == ax else (0, 0) for i in range(2)], mode="edge")
            c = np.cumsum(p, axis=ax)
            c = np.insert(c, 0, 0, axis=ax)
            a = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return a


def grid(lat, lon):
    m = mm.mpp(lat, Z)
    cx, cy = mm.merc(lat, lon, Z)
    x0, x1 = cx - HALF_W / m, cx + HALF_W / m
    y0, y1 = cy - HALF_N / m, cy + HALF_S / m
    W, H = int(x1 - x0), int(y1 - y0)
    img = Image.new("RGB", (W, H))
    for tx in range(int(x0 // 256), int(x1 // 256) + 1):
        for ty in range(int(y0 // 256), int(y1 // 256) + 1):
            img.paste(mm.tile(mm.ESRI, Z, tx, ty), (int(tx * 256 - x0), int(ty * 256 - y0)))
    # DEM at Z-1: pixel coords halve
    zx0, zy0, zx1, zy1 = x0 / 2, y0 / 2, x1 / 2, y1 / 2
    tiles = {}
    dem = np.zeros((int(zy1 - zy0) + 2, int(zx1 - zx0) + 2))
    for tx in range(int(zx0 // 256), int((zx1 + 3) // 256) + 1):
        for ty in range(int(zy0 // 256), int((zy1 + 3) // 256) + 1):
            t = dem_tile(Z - 1, tx, ty)
            ox, oy = int(tx * 256 - zx0), int(ty * 256 - zy0)
            sx0, sy0 = max(0, -ox), max(0, -oy)
            dx0, dy0 = max(0, ox), max(0, oy)
            w = min(256 - sx0, dem.shape[1] - dx0); h = min(256 - sy0, dem.shape[0] - dy0)
            if w > 0 and h > 0:
                dem[dy0:dy0 + h, dx0:dx0 + w] = t[sy0:sy0 + h, sx0:sx0 + w]
    demi = Image.fromarray(dem.astype(np.float32), mode="F").resize((dem.shape[1] * 2, dem.shape[0] * 2), Image.BILINEAR)
    demz = blur(np.asarray(demi).astype(np.float64), 3)[:H, :W]
    ax, ay = cx - x0, cy - y0
    return np.asarray(img), demz, m, (ax, ay)


def hillshade(z, m, az=225, alt=35):
    gy, gx = np.gradient(z * EXAG, m)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, h = math.radians(az), math.radians(alt)
    sh = np.sin(h) * np.cos(slope) + np.cos(h) * np.sin(slope) * np.cos(a - aspect)
    return np.clip(sh, 0, 1)


def render(rgb, z, m, anchor):
    H, W = z.shape
    hs = hillshade(z, m)
    k = 0.45 + 0.8 * hs / max(hs.mean(), 1e-6) * 0.62
    rgb = np.clip(rgb.astype(np.float64) * k[..., None], 0, 255).astype(np.uint8)
    zr = (z - z.min() + BASE_M) * EXAG                       # metres, exaggerated
    north = (H - 1 - np.arange(H))[:, None] * m      # metres north of the south edge
    sy = -(north * math.sin(VIEW) + zr * math.cos(VIEW)) / m   # screen y (up is negative)
    sy -= sy.min()
    sy = sy.astype(np.int32)
    outH = int(sy.max()) + int(BASE_M * EXAG * math.cos(VIEW) / m) + 4
    out = np.full((outH, W, 3), (245, 242, 234), np.uint8)  # sheet paper colour
    xs = np.arange(W)
    # painter: far (top row) to near; each row fills down to the next nearer row's screen y
    for i in range(H):
        top = sy[i]
        bot = sy[i + 1] if i + 1 < H else top + 2
        if i == H - 1:  # front edge: draw the slab face down to the base
            base = (-(0 * math.sin(VIEW)) / m)
            face_bot = top + 34  # cut edge follows the terrain
            for x in range(W):
                out[top[x]:min(face_bot[x], outH - 1), x] = (92, 84, 74)
        L = np.maximum(bot - top, 1)
        col = rgb[i]
        for k in range(int(L.max())):
            msk = L > k
            out[np.minimum(top[msk] + k, outH - 1), xs[msk]] = col[msk]
    # anchor pin
    ax, ay = int(anchor[0]), int(anchor[1])
    pin_y = sy[ay, ax]
    return Image.fromarray(out), (ax, pin_y)


def facts(sid, z, m, anchor):
    ax, ay = int(anchor[0]), int(anchor[1])
    za = float(z[ay - 3:ay + 4, ax - 3:ax + 4].mean())
    yy, xx = np.mgrid[0:z.shape[0], 0:z.shape[1]]
    d = np.hypot(xx - ax, yy - ay) * m
    r2 = z[d <= 500]
    return {"site_m": round(za), "low_500m_m": round(float(r2.min())), "high_500m_m": round(float(r2.max())),
            "above_low_m": round(za - float(r2.min())), "below_high_m": round(float(r2.max()) - za)}


def main(ids):
    for sid in ids:
        s = sm.SITES[sid]
        rgb, z, m, anchor = grid(s["anchor"]["lat"], s["anchor"]["lon"])
        img, (px, py) = render(rgb, z, m, anchor)
        d = ImageDraw.Draw(img)
        d.line([(px, py), (px, py - 60)], fill=sm.INK, width=5)
        d.line([(px, py), (px, py - 60)], fill=sm.YEL, width=3)
        d.ellipse([px - 16, py - 88, px + 16, py - 56], fill=sm.YEL, outline=sm.INK, width=3)
        # trim the empty sky band, keep a margin
        arr = np.asarray(img)
        rows = np.where((np.abs(arr.astype(int) - (245, 242, 234)) > 6).any(axis=(1, 2)))[0]
        img = img.crop((0, max(0, rows.min() - 40), img.width, rows.max() + 1))
        img.save(sm.OUT / f"terrain_{sid}.jpg", quality=88)
        f = facts(sid, z, m, anchor)
        (sm.OUT / f"terrain_{sid}.json").write_text(json.dumps(f, indent=1))
        print(sid, img.size, f)


if __name__ == "__main__":
    main(sys.argv[1:] or sm.ORDER)

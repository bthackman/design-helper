"""Topo extent preview (2026-10-05): 400 m vs 600 m squares centred on the Glenmore site parcel,
contours inside each, over faint base linework. Helps pick the Revit Toposolid extent.
Run: python topo_extent_preview.py -> ../site-base-test/topo-extent-B-F.html
"""
import math
import shapely
import numpy as np
import rasterio, contourpy
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from shapely.geometry import shape, box, LineString, Point
from shapely.ops import transform as shp_transform

from site_base_test import fetch, path_of, outline, smooth, to3776, to4326, SITES, DTM, OUT, LAYERS
from site_linework import CFG, IMPERVIOUS

EXTENTS = [(400, "#c0392b"), (600, "#2f6fb0")]


def main(SID="F"):
    s = SITES[SID]
    xmin, xmax, ymin, ymax = CFG[SID]["frame"]
    x0, y0 = to3776.transform(s["lon"], s["lat"])
    clip = box(x0 + xmin, y0 + ymin, x0 + xmax, y0 + ymax)
    lons, lats = to4326.transform([x0 + xmin - 50, x0 + xmax + 50], [y0 + ymin - 50, y0 + ymax + 50])
    bbox_ll = (min(lons), min(lats), max(lons), max(lats))   # same key as site_linework -> cached
    loc = lambda x, y, z=None: (x - x0, y - y0)

    def load(ds):
        out = []
        for f in fetch(ds, bbox_ll):
            if f.get("geometry"):
                g = shp_transform(lambda x, y, z=None: to3776.transform(x, y), shape(f["geometry"])).intersection(clip)
                if not g.is_empty:
                    out.append((shp_transform(loc, g), f.get("properties", {})))
        return out

    parcels = load(LAYERS["parcels"][0])
    from shapely.ops import unary_union
    site = unary_union([g for g, p in parcels if (s["focus"] and any(a in (p.get("address") or "").upper() for a in s["focus"]))
                        or (not s["focus"] and g.contains(Point(0, 0)))])
    cx, cy = site.centroid.x, site.centroid.y
    base = [outline(g) for g, p in load(IMPERVIOUS) if p.get("surface_type") in ("Curb Gutter Sidewalk", "Roads Paved", "Roads Gravel Or Gravel Areas", "Paved Areas Or Paved Parking Lots")]
    base += [outline(g) for g, _ in load(LAYERS["buildings"][0])] + [outline(g) for g, _ in load(LAYERS["water"][0])]

    big = max(e for e, _ in EXTENTS) / 2
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(DTM[SID]) as r, WarpedVRT(r, crs="EPSG:3776", resampling=Resampling.bilinear) as vrt:
            win = rasterio.windows.from_bounds(x0 + cx - big, y0 + cy - big, x0 + cx + big, y0 + cy + big, vrt.transform)
            z = vrt.read(1, window=win, masked=True).astype("float64").filled(np.nan)
            tr = vrt.window_transform(win)
    zs_raw = z.copy()
    z = smooth(z)
    ny, nx = z.shape
    xs = tr.c + tr.a * (np.arange(nx) + 0.5) - x0
    ys = tr.f + tr.e * (np.arange(ny) + 0.5) - y0
    gen = contourpy.contour_generator(xs, ys, z)
    lines = []
    for lev in np.arange(math.floor(np.nanmin(z)), math.ceil(np.nanmax(z)) + 1, 1.0):
        for ln in gen.lines(lev):
            if len(ln) > 5:
                lines.append((float(lev), LineString(ln).simplify(0.25)))

    stats, frames = [], []
    for e, col in EXTENTS:
        h = e / 2
        sq = box(cx - h, cy - h, cx + h, cy + h)
        inside = [(lev, g.intersection(sq)) for lev, g in lines]
        inside = [(lev, g) for lev, g in inside if not g.is_empty]
        X, Y = np.meshgrid(xs, ys)
        m = (abs(X - cx) <= h) & (abs(Y - cy) <= h)
        zz = zs_raw[m]; zz = zz[~np.isnan(zz)]
        verts = int(sum(shapely.get_num_coordinates(g) for _, g in inside))
        stats.append(dict(e=e, col=col, n=len(inside), verts=verts, zmin=zz.min(), zmax=zz.max(),
                          pts2=int((e / 2 + 1) ** 2), pts5=int((e / 5 + 1) ** 2),
                          len_km=sum(g.length for _, g in inside) / 1000))
        frames.append(f'<rect x="{cx-h:.1f}" y="{-(cy+h):.1f}" width="{e}" height="{e}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="10 5" vector-effect="non-scaling-stroke"/>'
                      f'<text x="{cx-h+6:.1f}" y="{-(cy+h)+16:.1f}" fill="{col}" font-size="13" font-weight="600">{e} m topo</text>')

    big_sq = box(cx - big, cy - big, cx + big, cy + big)
    vb = (cx - big - 40, -(cy + big) - 40, 2 * big + 80, 2 * big + 80)
    view = box(vb[0], -(vb[1] + vb[3]), vb[0] + vb[2], -vb[1])
    basep = "".join(f'<path d="{path_of(g.intersection(view).simplify(0.2))}"/>' for g in base if not g.intersection(view).is_empty)
    minor = "".join(f'<path d="{path_of(g.intersection(big_sq))}"/>' for lev, g in lines if lev % 5 and not g.intersection(big_sq).is_empty)
    major = "".join(f'<path d="{path_of(g.intersection(big_sq))}"/>' for lev, g in lines if not lev % 5 and not g.intersection(big_sq).is_empty)
    svg = (f'<svg viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}" xmlns="http://www.w3.org/2000/svg"><rect x="{vb[0]:.1f}" y="{vb[1]:.1f}" width="{vb[2]:.1f}" height="{vb[3]:.1f}" fill="#fff"/>'
           f'<g fill="none" stroke="#cfcfcf" stroke-width="0.5" vector-effect="non-scaling-stroke">{basep}</g>'
           f'<g fill="none" stroke="#a08a64" stroke-width="0.35" vector-effect="non-scaling-stroke">{minor}</g>'
           f'<g fill="none" stroke="#6b5534" stroke-width="0.9" vector-effect="non-scaling-stroke">{major}</g>'
           f'<path d="{path_of(outline(site))}" fill="none" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="16 4 3 4" vector-effect="non-scaling-stroke"/>'
           + "".join(frames) +
           f'<g font-size="11" fill="#222"><path d="M{vb[0]+30:.1f},{vb[1]+vb[3]-20:.1f}h100" stroke="#222" stroke-width="1.5"/><text x="{vb[0]+30:.1f}" y="{vb[1]+vb[3]-26:.1f}">0</text><text x="{vb[0]+112:.1f}" y="{vb[1]+vb[3]-26:.1f}">100 m</text></g></svg>')
    rows = "".join(f'<tr><td style="color:{d["col"]};font-weight:600">{d["e"]} m × {d["e"]} m</td><td>{d["e"]**2/10000:.0f} ha</td><td>{d["zmin"]:.0f}–{d["zmax"]:.0f} m ({d["zmax"]-d["zmin"]:.0f} m)</td>'
                   f'<td>{d["n"]}</td><td>{d["len_km"]:.0f} km</td><td>{d["verts"]:,}</td><td>{d["pts2"]:,}</td><td>{d["pts5"]:,}</td></tr>' for d in stats)
    f = OUT / f"topo-extent-{s['letter']}-{SID}.html"
    f.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Topo Extent {s['letter']}</title><style>:root{{--bg:#f4f4f2;--ink:#222}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--ink:#e6e6e6}}}} :root[data-theme="dark"]{{--bg:#1b1b1b;--ink:#e6e6e6}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.45 system-ui,sans-serif}} main{{max-width:1000px;margin:0 auto;padding:16px}}
h1{{font-size:18px;margin:0 0 4px}} .k{{font-size:12px;opacity:.8}} svg{{width:100%;height:auto;border:1px solid #bbb;margin-top:10px}}
.t{{overflow-x:auto}} table{{border-collapse:collapse;margin-top:10px;font-size:12px;min-width:640px}} td,th{{border-bottom:1px solid #ccc;padding:4px 8px;text-align:left}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: how much topo?</h1>
<p class="k">400 m and 600 m squares centred on the site parcel(s) (red dash-dot), over faint base linework. Contours 1 m (thin) and 5 m (bold) from the NRCan HRDEM 1 m DTM (2020), lightly smoothed. EPSG:3776.</p>
<div class="t"><table><tr><th>Extent</th><th>Area</th><th>Ground range</th><th>Contour lines</th><th>Total length</th><th>Vertices</th><th>Points at 2 m</th><th>Points at 5 m</th></tr>{rows}</table></div>
{svg}</main></body></html>""", encoding="utf-8")
    print(f, f.stat().st_size // 1024, "KB"); [print(d) for d in stats]


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "F")

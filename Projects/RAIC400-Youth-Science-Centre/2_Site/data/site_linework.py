"""Site base linework, CAD-style (2026-10-05). Glenmore Landing (B / data id F) first.

Lines only, one colour per layer, named as the DXF layers will be. Frame extended north to take in
the Heritage Park entrance. Sources: City of Calgary Open Data (parcels, street centrelines, buildings,
hydrology, regulatory flood map, tree canopy 2022, Impervious Surface 2021, Tracks – Non-LRT) and NRCan HRDEM 1 m DTM (2020).
CRS EPSG:3776, local metres from the site anchor (the shared DXF origin).

Run: python site_linework.py [F|C]  ->  ../site-base-test/site-linework-<letter>-<id>.html
"""
import math, pathlib
import numpy as np
import rasterio, contourpy
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from shapely.geometry import shape, box, LineString, Point
from shapely.ops import transform as shp_transform, unary_union, linemerge

from site_base_test import get, fetch, path_of, outline, smooth, to3776, to4326, SITES, DTM, OUT, LAYERS

IMPERVIOUS = "rgsu-3v7u"

# (layer, label, source, stroke, width, dash, on by default) - bottom to top
CAD = [
    ("TOPO-CONTOUR-MINOR", "Contours 1 m", "c-min", "#c4c4c4", 0.25, "", True),
    ("TOPO-CONTOUR-MAJOR", "Contours 5 m", "c-maj", "#8c8c8c", 0.55, "", True),
    ("SITE-TREE-CANOPY", "Tree canopy outlines", "canopy", "#6a9a58", 0.3, "", True),
    ("SITE-WATER-EDGE", "Water edge", "water", "#2f6fb0", 0.8, "", True),
    ("SITE-FLOOD-LIMIT", "Flood map limit", "flood", "#2f6fb0", 0.5, "8 4", True),
    ("SITE-SETBACK-WATER", "50 m water setback", "setback", "#c0392b", 0.5, "10 4 2 4", True),
    ("SITE-DRIVEWAY", "Driveways, pads", "imp:Driveway|Concrete Pad", "#b0a0c8", 0.25, "", False),
    ("SITE-PATH", "Pathways", "imp:Pathways", "#4e8a3a", 0.4, "", True),
    ("SITE-PARKING", "Parking lots, paved areas", "imp:Paved Areas Or Paved Parking Lots|Parking Pad", "#555", 0.4, "", True),
    ("SITE-ROAD-GRAVEL", "Gravel roads and lots", "imp:Roads Gravel Or Gravel Areas", "#a0743c", 0.45, "", True),
    ("SITE-ROAD-PAVED", "Paved road surfaces", "imp:Roads Paved", "#333", 0.45, "", True),
    ("SITE-ROAD-CURB", "Curb, gutter, sidewalk", "imp:Curb Gutter Sidewalk", "#222", 0.5, "", True),
    ("SITE-ROAD-CL", "Street centrelines", "roads", "#9a9a9a", 0.3, "14 4 3 4", False),
    ("SITE-RAIL", "Rail tracks", "rail", "#222", 0.45, "", True),
    ("SITE-BLDG-EXIST", "Buildings", "buildings", "#111", 0.5, "", True),
    ("SITE-PROPERTY", "Property lines", "parcels", "#444", 0.3, "12 3 2 3", True),
    ("SITE-PROPERTY-SITE", "Site parcel", "focus", "#c0392b", 1.3, "16 4 3 4", True),
]
# Per site: frame (xmin, xmax, ymin, ymax, local m from the anchor); road labels placed where a scan line
# crosses the named road (axis, value), rotated along it; place labels at fixed points (checked on imagery).
CFG = {
    "F": dict(frame=(-550, 550, -500, 950), note="extended north to the Heritage Park entrance",
              roads=[("14 ST SW", "y", -150), ("HERITAGE DR SW", "x", 330), ("90 AV SW", "x", -150)],
              places=[("HERITAGE PARK ENTRANCE", -335, 800, "#222"), ("HERITAGE PARK PARKING", -90, 650, "#555"),
                      ("GLENMORE RESERVOIR", -420, 100, "#2f6fb0"), ("GLENMORE LANDING", -60, -330, "#555")]),
    "C": dict(frame=(-400, 800, -650, 500), note="takes in the 9 Av SE approach (NW), the Bow (N and E) and the far bank",
              roads=[("9 AV SE", "x", -330), ("SANCTUARY RD SE", "y", -120), ("8 AV SE", "x", -480), ("17 AV SE", "x", 0)],
              places=[]),   # filled from geometry in main() (Nature Centre, Bow River) plus fixed ones below
}
CFG["C"]["places"] = [("INGLEWOOD BIRD SANCTUARY", 270, -210, "#4e7a3e"), ("INGLEWOOD WILDLAND PARK", -300, -260, "#4e7a3e"),
                      ("BOW RIVER", 260, 330, "#2f6fb0")]
SID = "F"
FRAME = CFG[SID]["frame"]
LAST = {}   # what main() drew, in real local coordinates, for the DXF export (site_dxf.py)

def main(sid="F"):
    cfg = CFG[sid]
    s = SITES[sid]
    xmin, xmax, ymin, ymax = cfg["frame"]
    x0, y0 = to3776.transform(s["lon"], s["lat"])
    clip = box(x0 + xmin, y0 + ymin, x0 + xmax, y0 + ymax)
    lons, lats = to4326.transform([x0 + xmin - 50, x0 + xmax + 50], [y0 + ymin - 50, y0 + ymax + 50])
    bbox_ll = (min(lons), min(lats), max(lons), max(lats))
    loc = lambda x, y, z=None: (x - x0, y - y0)

    def load(ds):
        out = []
        for f in fetch(ds, bbox_ll):
            if not f.get("geometry"):
                continue
            g = shp_transform(lambda x, y, z=None: to3776.transform(x, y), shape(f["geometry"])).intersection(clip)
            if not g.is_empty:
                out.append((shp_transform(loc, g), f.get("properties", {})))
        return out

    src = {k: load(ds) for k, (ds, _) in LAYERS.items()}
    imp = load(IMPERVIOUS)
    focus = [(g, p) for g, p in src["parcels"]
             if (s["focus"] and any(a in (p.get("address") or "").upper() for a in s["focus"]))
             or (not s["focus"] and g.contains(Point(0, 0)))]
    water_u = unary_union([g for g, _ in src["water"]])
    setback = water_u.buffer(50).intersection(box(xmin, ymin, xmax, ymax)) if not water_u.is_empty else None

    # contours from the smoothed 1 m DTM
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(DTM[sid]) as r, WarpedVRT(r, crs="EPSG:3776", resampling=Resampling.bilinear) as vrt:
            win = rasterio.windows.from_bounds(x0 + xmin, y0 + ymin, x0 + xmax, y0 + ymax, vrt.transform)
            z = vrt.read(1, window=win, masked=True).astype("float64").filled(np.nan)
            tr = vrt.window_transform(win)
    z = smooth(z)
    ny, nx = z.shape
    xs = tr.c + tr.a * (np.arange(nx) + 0.5) - x0
    ys = tr.f + tr.e * (np.arange(ny) + 0.5) - y0
    gen = contourpy.contour_generator(xs, ys, z)
    contours = []
    for lev in np.arange(math.floor(np.nanmin(z)), math.ceil(np.nanmax(z)) + 1, 1.0):
        for line in gen.lines(lev):
            if len(line) > 5:
                contours.append((float(lev), LineString(line).simplify(0.25)))

    def geoms_for(key):
        if key == "c-min":
            return [g for lev, g in contours if lev % 5]
        if key == "c-maj":
            return [g for lev, g in contours if not lev % 5]
        if key == "setback":
            return [outline(setback)] if setback is not None and not setback.is_empty else []
        if key == "focus":
            return [outline(g) for g, _ in focus]
        if key.startswith("imp:"):
            types = set(key[4:].split("|"))
            return [outline(g) for g, p in imp if p.get("surface_type") in types]
        gs = [g for g, _ in src[key]]
        if key == "canopy":
            gs = [g for g in gs if g.area >= 10]
        return gs if key == "roads" else [outline(g) for g in gs]

    W, H = xmax - xmin, ymax - ymin
    parts, rows = [], []
    LAST.clear()
    LAST.update(sid=sid, origin=(x0, y0), frame=cfg["frame"], layers={}, texts=[], contours=contours,
                focus=[g for g, _ in focus])
    for lname, label, key, stroke, w, dash, on in CAD:
        gs = [g for g in geoms_for(key) if not g.is_empty]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        hide = "" if on else ' style="display:none"'
        parts.append(f'<g id="L-{lname}" fill="none" stroke="{stroke}" stroke-width="{w}"{da} vector-effect="non-scaling-stroke"{hide}>'
                     + "".join(f'<path d="{path_of(g.simplify(0.15))}"/>' for g in gs) + "</g>")
        rows.append((lname, label, stroke, dash, on, len(gs)))
        LAST["layers"][lname] = gs

    # text: major contour elevations and main road names (a TEXT layer in the DXF)
    txt = []
    for lev, g in contours:
        if not lev % 5 and g.length > 120:
            p = g.interpolate(0.5, normalized=True)
            txt.append(f'<text x="{p.x:.1f}" y="{-p.y:.1f}" fill="#7a7a7a" font-size="6">{int(lev)}</text>')
            LAST["texts"].append(("TEXT-CONTOUR", str(int(lev)), p.x, p.y, 0.0, 1.5))
    by_name = {}
    for g, p in src["roads"]:
        by_name.setdefault(p.get("full_name", ""), []).append(g)
    for name, axis, v in cfg["roads"]:
        if name not in by_name:
            continue
        scan = LineString([(v, ymin), (v, ymax)]) if axis == "x" else LineString([(xmin, v), (xmax, v)])
        hit = unary_union(by_name[name]).intersection(scan)
        pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
        if not pts:
            continue
        px = sum(q.x for q in pts) / len(pts); py = sum(q.y for q in pts) / len(pts)
        near = min(by_name[name], key=lambda l: l.distance(Point(px, py)))
        d0 = near.project(Point(px, py))
        a_, b_ = near.interpolate(max(d0 - 10, 0)), near.interpolate(min(d0 + 10, near.length))
        ang = math.degrees(math.atan2(-(b_.y - a_.y), b_.x - a_.x))
        if ang > 90: ang -= 180
        if ang <= -90: ang += 180
        nx_, ny_ = -math.sin(math.radians(ang)), -math.cos(math.radians(ang))   # offset to one side of the road
        dx, dy = 12 * nx_, 12 * ny_
        txt.append(f'<text x="{px+dx:.1f}" y="{-py+dy:.1f}" transform="rotate({ang} {px+dx:.1f} {-py+dy:.1f})" fill="#222" font-size="9" letter-spacing="1">{name}</text>')
        LAST["texts"].append(("TEXT", name, px + dx, py - dy, -ang, 3.0))
    for name, px, py, col in cfg["places"]:
        txt.append(f'<text x="{px}" y="{-py}" fill="{col}" font-size="9" letter-spacing="1.5">{name}</text>')
        LAST["texts"].append(("TEXT", name, px, py, 0.0, 3.5))
    parts.append('<g id="L-TEXT" text-anchor="middle" font-family="Arial, sans-serif">' + "".join(txt) + "</g>")
    rows.append(("TEXT", "Labels", "#222", "", True, len(txt)))

    parts.append(f'<g font-size="10" fill="#222" font-family="Arial, sans-serif"><path d="M{xmin+20},{-ymin-24}h100" stroke="#222" stroke-width="1"/>'
                 f'<text x="{xmin+20}" y="{-ymin-30}">0</text><text x="{xmin+100}" y="{-ymin-30}">100 m</text>'
                 f'<path d="M{xmax-30},{-ymax+50}v-28l-6,10m6,-10l6,10" stroke="#222" stroke-width="1" fill="none"/>'
                 f'<text x="{xmax-34}" y="{-ymax+64}">N</text><path d="M-6,0h12M0,-6v12" stroke="#c0392b" stroke-width="1"/></g>')
    svg = (f'<svg viewBox="{xmin} {-ymax} {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect x="{xmin}" y="{-ymax}" width="{W}" height="{H}" fill="#fff"/>' + "".join(parts) + "</svg>")
    ctl = "".join(f'<label><input type="checkbox" {"checked" if on else ""} data-l="{l}"><span class="sw" style="border-top:2px {"dashed" if d else "solid"} {c}"></span>'
                  f'{lab} <small>({n})</small><code>{l}</code></label>' for l, lab, c, d, on, n in rows)
    zs = z[~np.isnan(z)]
    f = OUT / f"site-linework-{s['letter']}-{sid}.html"
    f.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Linework {s['letter']}</title><style>
:root{{--bg:#f4f4f2;--ink:#222}} @media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--ink:#e6e6e6}}}}
:root[data-theme="dark"]{{--bg:#1b1b1b;--ink:#e6e6e6}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.45 system-ui,sans-serif}} main{{max-width:1240px;margin:0 auto;padding:16px}}
h1{{font-size:18px;margin:0 0 4px}} .k{{font-size:12px;opacity:.8;margin:2px 0}}
.wrap{{display:grid;grid-template-columns:1fr 330px;gap:16px;align-items:start}} @media (max-width:820px){{.wrap{{grid-template-columns:1fr}}}}
svg{{width:100%;height:auto;border:1px solid #bbb}} label{{display:flex;align-items:center;gap:6px;margin:4px 0}}
.sw{{display:inline-block;width:22px;flex:none}} code{{margin-left:auto;font-size:10px;opacity:.7}} small{{opacity:.6}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: base linework (CAD preview)</h1>
<p class="k">Lines only, one colour per layer; DXF layer names on the right. Frame {W/1000:.2f} × {H/1000:.2f} km, {cfg['note']}. EPSG:3776, local metres from the red cross (origin {x0:.2f}, {y0:.2f}).
Sources: City of Calgary Open Data (assessment parcels, street centrelines, buildings, hydrology, regulatory flood map, tree canopy 2022, Impervious Surface 2021, Tracks – Non-LRT); NRCan HRDEM 1 m DTM (2020 LiDAR).
Parcels are assessment parcels, not survey lines. Road edges are the City's 2021 impervious-surface outlines. Canopy outlines under 10 m² dropped. Place labels checked against Esri imagery.</p>
<div class="wrap"><div>{svg}</div><aside>{ctl}
<p class="k" style="margin-top:10px"><b>Ground:</b> {zs.min():.1f}–{zs.max():.1f} m; contours from the 1 m DTM, lightly smoothed (σ 1.5 m).</p></aside></div></main>
<script>document.querySelectorAll('input[data-l]').forEach(c=>c.onchange=()=>{{const g=document.getElementById('L-'+c.dataset.l);if(g)g.style.display=c.checked?'':'none'}})</script>
</body></html>""", encoding="utf-8")
    print(f, f.stat().st_size // 1024, "KB", {r[0]: r[5] for r in rows})


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "F")

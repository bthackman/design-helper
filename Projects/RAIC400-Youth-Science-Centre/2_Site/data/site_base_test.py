"""Quick test of the two-site base (2026-10-05): City open data + NRCan 1 m DTM contours,
drawn as a layered SVG preview in HTML, before committing to the full DXF pipeline.

Sites: B Glenmore Landing (data id F) and A Inglewood (data id C). Box: +/-HALF m around the anchor.
CRS: EPSG:3776 (NAD83 / Alberta 3TM ref merid 114 W), shown in local metres from the anchor.
Run: python site_base_test.py   ->  ../site-base-test/site-base-<id>.html
"""
import json, math, pathlib, time
import numpy as np
import requests
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from pyproj import Transformer
from shapely.geometry import shape, Point, box, mapping
from shapely.ops import transform as shp_transform, unary_union
import contourpy

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "site-base-test"
OUT.mkdir(exist_ok=True)
CACHE = HERE / "_cache_site_base_test.json"
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}

HALF = 500
SITES = {
    "F": dict(letter="B", name="Glenmore Landing", lat=50.97622, lon=-114.09711, focus=[]),
    "C": dict(letter="A", name="Inglewood", lat=51.0307, lon=-114.0106,
              focus=["2405 9 AV SE", "2425 9 AV SE"]),
}
LAYERS = {  # key: (dataset id, label)
    "parcels": ("4bsw-nn7w", "Property (assessment parcels)"),
    "roads": ("4dx8-rtm5", "Street centrelines"),
    "buildings": ("uc4c-6kbd", "Buildings (roof outlines)"),
    "water": ("47bt-eefd", "Hydrology"),
    "flood": ("tp6q-x2v7", "Regulatory flood map"),
    "canopy": ("mn2n-4z98", "Tree canopy 2022"),
    "rail": ("cq6k-mmku", "Rail tracks (non-LRT)"),
}
DTM = {
    "F": "https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-lidar/NRCAN-Calgary_West_utm11_2020-1m-dtm.tif",
    # Inglewood sits on the UTM 11/12 line: the East tile is only 41% valid here, the West tile 100%
    "C": "https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-lidar/NRCAN-Calgary_West_utm11_2020-1m-dtm.tif",
}

to3776 = Transformer.from_crs(4326, 3776, always_xy=True)
to4326 = Transformer.from_crs(3776, 4326, always_xy=True)


def get(url, params=None, tries=4):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def geom_col(ds):
    key = f"col:{ds}"
    if key not in cache:
        cols = get(f"https://data.calgary.ca/api/views/{ds}.json").json()["columns"]
        geo = [c["fieldName"] for c in cols
               if c["dataTypeName"] in ("multipolygon", "polygon", "multiline", "line", "point", "multipoint", "location")]
        cache[key] = geo[0]
    return cache[key]


def fetch(ds, bbox_ll):
    key = f"{ds}:{bbox_ll}"
    if key not in cache:
        w, s, e, n = bbox_ll
        col = geom_col(ds)
        feats, off = [], 0
        while True:
            r = get(f"https://data.calgary.ca/resource/{ds}.geojson",
                    {"$where": f"intersects({col}, 'POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))')",
                     "$limit": 5000, "$offset": off})
            batch = r.json().get("features", [])
            feats += batch
            if len(batch) < 5000:
                break
            off += 5000
        cache[key] = feats
        CACHE.write_text(json.dumps(cache))
    return cache[key]


def build(sid, s):
    x0, y0 = to3776.transform(s["lon"], s["lat"])
    clip = box(x0 - HALF, y0 - HALF, x0 + HALF, y0 + HALF)
    lons, lats = to4326.transform([x0 - HALF - 50, x0 + HALF + 50], [y0 - HALF - 50, y0 + HALF + 50])
    bbox_ll = (min(lons), min(lats), max(lons), max(lats))
    loc = lambda x, y, z=None: (x - x0, y - y0)

    layers, info = {}, {}
    for key, (ds, label) in LAYERS.items():
        geoms = []
        for f in fetch(ds, bbox_ll):
            if not f.get("geometry"):
                continue
            g = shp_transform(lambda x, y, z=None: to3776.transform(x, y), shape(f["geometry"]))
            g = g.intersection(clip)
            if g.is_empty:
                continue
            geoms.append((shp_transform(loc, g), f.get("properties", {})))
        layers[key] = geoms
        info[key] = len(geoms)

    # Focus parcels: named addresses, or the parcel under the anchor
    focus = []
    for g, p in layers["parcels"]:
        addr = (p.get("address") or "").upper()
        if any(a in addr for a in s["focus"]) or (not s["focus"] and g.contains(Point(0, 0))):
            focus.append((g, p))

    # Water setback (test): 50 m from all mapped water, one layer
    water_u = unary_union([g for g, _ in layers["water"]]) if layers["water"] else None
    setback = water_u.buffer(50).intersection(shp_transform(loc, clip)) if water_u else None

    # Terrain: 1 m DTM window warped to EPSG:3776
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        with rasterio.open(DTM[sid]) as src:
            with WarpedVRT(src, crs="EPSG:3776", resampling=Resampling.bilinear) as vrt:
                win = rasterio.windows.from_bounds(x0 - HALF, y0 - HALF, x0 + HALF, y0 + HALF, vrt.transform)
                z = vrt.read(1, window=win, masked=True).astype("float64").filled(np.nan)
                tr = vrt.window_transform(win)
    ny, nx = z.shape
    xs = tr.c + tr.a * (np.arange(nx) + 0.5) - x0
    ys = tr.f + tr.e * (np.arange(ny) + 0.5) - y0
    zs = z[~np.isnan(z)]
    zmin, zmax = float(zs.min()), float(zs.max())
    z0 = float(z[ny // 2, nx // 2])
    gen = contourpy.contour_generator(xs, ys, z)
    contours = []
    for lev in np.arange(math.floor(zmin), math.ceil(zmax) + 1, 1.0):
        for line in gen.lines(lev):
            if len(line) > 3:
                contours.append((float(lev), line[::2] if len(line) > 40 else line))
    info.update(contours=len(contours), zmin=round(zmin, 1), zmax=round(zmax, 1), z_anchor=round(z0, 1))
    return dict(layers=layers, focus=focus, setback=setback, contours=contours, info=info,
                origin=(round(x0, 2), round(y0, 2)))


# ---------- SVG ----------
def path_of(g):
    def ring(c):
        return "M" + "L".join(f"{x:.1f},{-y:.1f}" for x, y in c)
    t = g.geom_type
    if t == "Polygon":
        return ring(g.exterior.coords) + "Z" + "".join(ring(i.coords) + "Z" for i in g.interiors)
    if t == "LineString":
        return ring(g.coords)
    if t == "Point":
        return f"M{g.x - 1:.1f},{-g.y:.1f}h2"
    if hasattr(g, "geoms"):
        return "".join(path_of(p) for p in g.geoms)
    return ""


STYLE = {
    "canopy": 'fill="var(--tree)" stroke="none"',
    "flood": 'fill="var(--flood)" stroke="var(--flood-l)" stroke-width="0.6"',
    "water": 'fill="var(--water)" stroke="var(--water-l)" stroke-width="0.8"',
    "parcels": 'fill="none" stroke="var(--parcel)" stroke-width="0.5"',
    "buildings": 'fill="var(--bldg)" stroke="var(--ink)" stroke-width="0.4"',
    "roads": 'fill="none" stroke="var(--road)" stroke-width="1.6"',
}


def html(sid, s, d):
    parts = []
    for key in ["canopy", "flood", "water"]:
        parts.append(f'<g id="L-{key}" {STYLE[key]}>' + "".join(f'<path d="{path_of(g)}"/>' for g, _ in d["layers"][key]) + "</g>")
    if d["setback"] is not None and not d["setback"].is_empty:
        parts.append(f'<g id="L-setback" fill="none" stroke="var(--hazard)" stroke-width="1.2" stroke-dasharray="6 4"><path d="{path_of(d["setback"])}"/></g>')
    minor = "".join(f'<path d="{path_of_line(c)}"/>' for lev, c in d["contours"] if lev % 5)
    major = "".join(f'<path d="{path_of_line(c)}"/>' for lev, c in d["contours"] if not lev % 5)
    parts.append(f'<g id="L-contours"><g stroke="var(--topo)" stroke-width="0.3" fill="none">{minor}</g>'
                 f'<g stroke="var(--topo-maj)" stroke-width="0.7" fill="none">{major}</g></g>')
    for key in ["parcels", "buildings", "roads"]:
        parts.append(f'<g id="L-{key}" {STYLE[key]}>' + "".join(f'<path d="{path_of(g)}"/>' for g, _ in d["layers"][key]) + "</g>")
    parts.append('<g id="L-focus" fill="var(--focus-f)" stroke="var(--focus)" stroke-width="2">' +
                 "".join(f'<path d="{path_of(g)}"/>' for g, _ in d["focus"]) + "</g>")
    parts.append('<g id="L-anchor"><circle r="4" fill="var(--focus)"/><circle r="400" fill="none" stroke="var(--focus)" stroke-width="0.8" stroke-dasharray="3 5"/></g>')
    # scale bar + north
    parts.append(f'<g font-size="11" fill="var(--ink)"><path d="M{-HALF+20},{HALF-24}h100" stroke="var(--ink)" stroke-width="2"/>'
                 f'<text x="{-HALF+20}" y="{HALF-30}">0</text><text x="{-HALF+108}" y="{HALF-30}">100 m</text>'
                 f'<path d="M{HALF-30},{-HALF+50}l0,-28l-7,12m7,-12l7,12" stroke="var(--ink)" stroke-width="1.5" fill="none"/>'
                 f'<text x="{HALF-34}" y="{-HALF+64}">N</text></g>')
    svg = (f'<svg viewBox="{-HALF} {-HALF} {2*HALF} {2*HALF}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect x="{-HALF}" y="{-HALF}" width="{2*HALF}" height="{2*HALF}" fill="var(--paper)"/>' + "".join(parts) + "</svg>")
    i = d["info"]
    focus_txt = "; ".join(f'{p.get("address","?")} ({shp_area(g):,.0f} m², {p.get("land_use_designation","")})' for g, p in d["focus"]) or "none found"
    toggles = [("canopy", "Tree canopy"), ("flood", "Flood map"), ("water", "Water"), ("setback", "50 m water setback"),
               ("contours", "Contours 1 m / 5 m"), ("parcels", "Property lines"), ("buildings", "Buildings"),
               ("roads", "Street centrelines"), ("focus", "Site parcel(s)"), ("anchor", "Anchor + 400 m ring")]
    tg = "".join(f'<label><input type="checkbox" checked data-l="{k}"> {lab}</label>' for k, lab in toggles)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Base {s['letter']}</title><style>
:root{{--paper:#F5F2EA;--ink:#2b2b2b;--parcel:#8a6d3b;--bldg:#d9d4c7;--road:#9a9a9a;--water:#bcd7ea;--water-l:#4a86b5;
--flood:rgba(74,134,181,.15);--flood-l:rgba(74,134,181,.5);--tree:rgba(110,150,90,.35);--topo:#b9a27a;--topo-maj:#8a7046;
--focus:#c4462b;--focus-f:rgba(196,70,43,.12);--hazard:#c4462b;--bg:#fbfaf6}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1d1d1b;--ink:#e8e4da}}}}
:root[data-theme="dark"]{{--bg:#1d1d1b;--ink:#e8e4da}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:16px}} h1{{font-size:20px;margin:0 0 4px}} p{{margin:4px 0}}
.wrap{{display:grid;grid-template-columns:1fr 240px;gap:16px;align-items:start}}
@media (max-width:760px){{.wrap{{grid-template-columns:1fr}}}}
svg{{width:100%;height:auto;border:1px solid #ccc;background:var(--paper)}} label{{display:block;margin:3px 0}}
.k{{font-size:12px;opacity:.8}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: site base test</h1>
<p class="k">Quick test, 2026-10-05. 1 km square around the anchor. EPSG:3776, local metres from the anchor (origin {d['origin'][0]}, {d['origin'][1]}).
City of Calgary Open Data (assessment parcels, street centrelines, buildings, hydrology, regulatory flood map, tree canopy 2022). Terrain: NRCan HRDEM 1 m DTM (2020 LiDAR).
Parcels are assessment parcels, not survey lines. The 50 m setback is drawn from all mapped water (a test; still water would be 30 m).</p>
<div class="wrap"><div>{svg}</div><aside>{tg}
<p class="k" style="margin-top:12px"><b>Site parcel(s):</b> {focus_txt}</p>
<p class="k"><b>Ground:</b> {i['zmin']}–{i['zmax']} m (anchor {i['z_anchor']} m), {i['contours']} contour lines</p>
<p class="k"><b>Features:</b> {', '.join(f'{k} {i[k]}' for k in LAYERS)}</p></aside></div></main>
<script>document.querySelectorAll('input[data-l]').forEach(c=>c.onchange=()=>{{const g=document.getElementById('L-'+c.dataset.l);if(g)g.style.display=c.checked?'':'none'}})</script>
</body></html>"""


def path_of_line(c):
    return "M" + "L".join(f"{x:.1f},{-y:.1f}" for x, y in c)


def shp_area(g):
    return g.area


# ---------- CAD-style line drawing (2026-10-05): strokes only, one colour per layer, as it would sit in a DXF ----------
CAD_LAYERS = [  # (svg id, label, layer name a DXF would use, stroke, width, dash)
    ("contours-min", "Contours 1 m", "TOPO-CONTOUR-MINOR", "#b8b8b8", 0.25, ""),
    ("contours-maj", "Contours 5 m", "TOPO-CONTOUR-MAJOR", "#8c8c8c", 0.6, ""),
    ("canopy", "Tree canopy outlines", "SITE-TREE-CANOPY", "#5f8f4e", 0.35, ""),
    ("water", "Water edge", "SITE-WATER-EDGE", "#2f6fb0", 0.8, ""),
    ("flood", "Flood map limit", "SITE-FLOOD-LIMIT", "#2f6fb0", 0.6, "8 4"),
    ("setback", "50 m water setback", "SITE-SETBACK-WATER", "#c0392b", 0.6, "10 4 2 4"),
    ("roads", "Street centrelines", "SITE-ROAD-CL", "#7a7a7a", 0.4, "14 4 3 4"),
    ("buildings", "Buildings", "SITE-BLDG-EXIST", "#222", 0.5, ""),
    ("parcels", "Property lines", "SITE-PROPERTY", "#222", 0.35, "12 3 2 3"),
    ("focus", "Site parcel", "SITE-PROPERTY-SITE", "#c0392b", 1.4, "16 4 3 4"),
]


def smooth(z, sigma=1.5):
    """Separable Gaussian on the DTM (NaN-aware) so 1 m contours read as CAD lines, not pixel stairs."""
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    m = ~np.isnan(z); v = np.where(m, z, 0.0)
    def conv(a, ax):
        return np.apply_along_axis(lambda x: np.convolve(x, k, mode="same"), ax, a)
    num = conv(conv(v, 0), 1); den = conv(conv(m.astype(float), 0), 1)
    out = num / np.where(den == 0, np.nan, den); out[~m] = np.nan
    return out


def outline(g):
    """Polygon -> its boundary lines (CAD has outlines, not fills)."""
    if g.geom_type in ("Polygon", "MultiPolygon", "GeometryCollection"):
        return g.boundary if g.geom_type != "GeometryCollection" else unary_union([outline(p) for p in g.geoms])
    return g


def html_lines(sid, s, d, contours):
    def grp(gid, stroke, w, dash, paths):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<g id="L-{gid}" fill="none" stroke="{stroke}" stroke-width="{w}"{da} vector-effect="non-scaling-stroke">{paths}</g>'
    geo = {
        "canopy": [outline(g) for g, _ in d["layers"]["canopy"] if g.area >= 10],
        "water": [outline(g) for g, _ in d["layers"]["water"]],
        "flood": [outline(g) for g, _ in d["layers"]["flood"]],
        "setback": [outline(d["setback"])] if d["setback"] is not None and not d["setback"].is_empty else [],
        "roads": [g for g, _ in d["layers"]["roads"]],
        "buildings": [outline(g) for g, _ in d["layers"]["buildings"]],
        "parcels": [outline(g) for g, _ in d["layers"]["parcels"]],
        "focus": [outline(g) for g, _ in d["focus"]],
    }
    parts = []
    for gid, label, lname, stroke, w, dash in CAD_LAYERS:
        if gid == "contours-min":
            paths = "".join(f'<path d="{path_of_line(c)}"/>' for lev, c in contours if lev % 5)
        elif gid == "contours-maj":
            paths = "".join(f'<path d="{path_of_line(c)}"/>' for lev, c in contours if not lev % 5)
        else:
            paths = "".join(f'<path d="{path_of(g.simplify(0.15))}"/>' for g in geo[gid] if not g.is_empty)
        parts.append(grp(gid, stroke, w, dash, paths))
    # major contour labels (every 5 m), one per line at its midpoint
    labels = "".join(f'<text x="{c[len(c)//2][0]:.1f}" y="{-c[len(c)//2][1]:.1f}">{int(lev)}</text>'
                     for lev, c in contours if not lev % 5 and len(c) > 60)
    parts.append(f'<g id="L-contour-labels" font-size="7" fill="#6e6e6e" text-anchor="middle">{labels}</g>')
    parts.append(f'<g font-size="10" fill="#222"><path d="M{-HALF+20},{HALF-24}h100" stroke="#222" stroke-width="1"/>'
                 f'<text x="{-HALF+20}" y="{HALF-30}">0</text><text x="{-HALF+100}" y="{HALF-30}">100 m</text>'
                 f'<path d="M{HALF-30},{-HALF+50}v-28l-6,10m6,-10l6,10" stroke="#222" stroke-width="1" fill="none"/>'
                 f'<text x="{HALF-34}" y="{-HALF+64}">N</text><path d="M-6,0h12M0,-6v12" stroke="#c0392b" stroke-width="1"/></g>')
    svg = (f'<svg viewBox="{-HALF} {-HALF} {2*HALF} {2*HALF}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect x="{-HALF}" y="{-HALF}" width="{2*HALF}" height="{2*HALF}" fill="#fff"/>' + "".join(parts) + "</svg>")
    rows = "".join(f'<label><input type="checkbox" checked data-l="{gid}"><span class="sw" style="border-top:2px {"dashed" if dash else "solid"} {stroke}"></span>'
                   f'{label}<code>{lname}</code></label>' for gid, label, lname, stroke, w, dash in CAD_LAYERS)
    i = d["info"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Linework {s['letter']}</title><style>
:root{{--bg:#f4f4f2;--ink:#222}} @media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--ink:#e6e6e6}}}}
:root[data-theme="dark"]{{--bg:#1b1b1b;--ink:#e6e6e6}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.45 system-ui,sans-serif}} main{{max-width:1180px;margin:0 auto;padding:16px}}
h1{{font-size:18px;margin:0 0 4px}} .k{{font-size:12px;opacity:.8;margin:2px 0}}
.wrap{{display:grid;grid-template-columns:1fr 300px;gap:16px;align-items:start}} @media (max-width:800px){{.wrap{{grid-template-columns:1fr}}}}
svg{{width:100%;height:auto;border:1px solid #bbb}} label{{display:flex;align-items:center;gap:6px;margin:4px 0}}
.sw{{display:inline-block;width:22px}} code{{margin-left:auto;font-size:10px;opacity:.7}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: base linework (CAD preview)</h1>
<p class="k">Lines only, one colour per layer, as the DXF would carry them; layer names on the right. 1 km square, EPSG:3776, local metres from the red cross (origin {d['origin'][0]}, {d['origin'][1]}).
City of Calgary Open Data; NRCan HRDEM 1 m DTM (2020). Parcels are assessment parcels, not survey lines. Canopy outlines under 10 m² dropped.</p>
<div class="wrap"><div>{svg}</div><aside>{rows}
<p class="k" style="margin-top:10px"><b>Ground:</b> {i['zmin']}–{i['zmax']} m; contours from the 1 m DTM, lightly smoothed (σ 1.5 m).</p></aside></div></main>
<script>document.querySelectorAll('input[data-l]').forEach(c=>c.onchange=()=>{{const g=document.getElementById('L-'+c.dataset.l);if(g)g.style.display=c.checked?'':'none';
if(c.dataset.l==='contours-maj'){{const t=document.getElementById('L-contour-labels');t.style.display=c.checked?'':'none'}}}})</script>
</body></html>"""


def lines_mode(sid):
    s = SITES[sid]
    d = build(sid, s)
    # re-contour from a smoothed DTM for clean CAD lines
    x0, y0 = d["origin"]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(DTM[sid]) as src, WarpedVRT(src, crs="EPSG:3776", resampling=Resampling.bilinear) as vrt:
            win = rasterio.windows.from_bounds(x0 - HALF, y0 - HALF, x0 + HALF, y0 + HALF, vrt.transform)
            z = vrt.read(1, window=win, masked=True).astype("float64").filled(np.nan)
            tr = vrt.window_transform(win)
    z = smooth(z)
    ny, nx = z.shape
    xs = tr.c + tr.a * (np.arange(nx) + 0.5) - x0
    ys = tr.f + tr.e * (np.arange(ny) + 0.5) - y0
    gen = contourpy.contour_generator(xs, ys, z)
    from shapely.geometry import LineString
    contours = []
    for lev in np.arange(math.floor(np.nanmin(z)), math.ceil(np.nanmax(z)) + 1, 1.0):
        for line in gen.lines(lev):
            if len(line) > 5:
                ls = LineString(line).simplify(0.25)
                contours.append((float(lev), np.asarray(ls.coords)))
    f = OUT / f"site-linework-{s['letter']}-{sid}.html"
    f.write_text(html_lines(sid, s, d, contours), encoding="utf-8")
    print(f, f.stat().st_size // 1024, "KB", len(contours), "contours")


# ---------- Imagery check (2026-10-05): current linework + candidate City impervious-surface lines over Esri imagery ----------
IMPERVIOUS = "rgsu-3v7u"  # City Impervious Surface 2021: paved roads, curbs/sidewalks, lots, pathways, gravel roads
CANDIDATE = [  # (svg id, label, surface_type values, stroke)
    ("imp-road", "Roads paved (edges)", {"Roads Paved"}, "#ff2bd6"),
    ("imp-gravel", "Roads gravel / gravel areas", {"Roads Gravel Or Gravel Areas"}, "#ff9f1c"),
    ("imp-curb", "Curb, gutter, sidewalk", {"Curb Gutter Sidewalk"}, "#00e5ff"),
    ("imp-lot", "Paved areas / parking lots", {"Paved Areas Or Paved Parking Lots", "Parking Pad"}, "#ffe600"),
    ("imp-path", "Pathways", {"Pathways"}, "#7CFC00"),
    ("imp-drive", "Driveways, concrete pads", {"Driveway", "Concrete Pad"}, "#c9a0ff"),
]
TILES = HERE / "_tiles"


def esri_mosaic(x0, y0, z=18):
    """Esri World Imagery tiles warped onto the local EPSG:3776 frame, returned as a base64 JPEG."""
    import io, base64
    from PIL import Image
    from rasterio.warp import reproject
    from rasterio.transform import from_origin
    TILES.mkdir(exist_ok=True)
    lons, lats = to4326.transform([x0 - HALF, x0 + HALF, x0 - HALF, x0 + HALF], [y0 - HALF, y0 - HALF, y0 + HALF, y0 + HALF])
    def tx(lon): return (lon + 180) / 360 * 2 ** z
    def ty(lat): return (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * 2 ** z
    xa, xb = int(tx(min(lons))), int(tx(max(lons)))
    ya, yb = int(ty(max(lats))), int(ty(min(lats)))
    mos = Image.new("RGB", ((xb - xa + 1) * 256, (yb - ya + 1) * 256))
    for X in range(xa, xb + 1):
        for Y in range(ya, yb + 1):
            f = TILES / f"esri_{z}_{X}_{Y}.jpg"
            if not f.exists():
                r = get(f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{Y}/{X}", tries=8)
                f.write_bytes(r.content)
            mos.paste(Image.open(f).convert("RGB"), ((X - xa) * 256, (Y - ya) * 256))
    R = 6378137.0
    res = 2 * math.pi * R / (256 * 2 ** z)
    left = xa * 256 * res - math.pi * R
    top = math.pi * R - ya * 256 * res
    src = np.transpose(np.asarray(mos), (2, 0, 1))
    px = 0.5
    W = int(2 * HALF / px)
    dst = np.zeros((3, W, W), dtype=np.uint8)
    reproject(src, dst, src_transform=from_origin(left, top, res, res), src_crs="EPSG:3857",
              dst_transform=from_origin(x0 - HALF, y0 + HALF, px, px), dst_crs="EPSG:3776", resampling=Resampling.bilinear)
    buf = io.BytesIO()
    Image.fromarray(np.transpose(dst, (1, 2, 0))).save(buf, "JPEG", quality=72)
    return base64.b64encode(buf.getvalue()).decode()


def check_mode(sid):
    s = SITES[sid]
    d = build(sid, s)
    x0, y0 = d["origin"]
    clip = box(x0 - HALF, y0 - HALF, x0 + HALF, y0 + HALF)
    lons, lats = to4326.transform([x0 - HALF - 50, x0 + HALF + 50], [y0 - HALF - 50, y0 + HALF + 50])
    bbox_ll = (min(lons), min(lats), max(lons), max(lats))
    loc = lambda x, y, z=None: (x - x0, y - y0)
    imp = []
    for f in fetch(IMPERVIOUS, bbox_ll):
        if not f.get("geometry"):
            continue
        g = shp_transform(lambda x, y, z=None: to3776.transform(x, y), shape(f["geometry"])).intersection(clip)
        if not g.is_empty:
            imp.append((shp_transform(loc, g), f["properties"].get("surface_type", "")))
    img = esri_mosaic(x0, y0)
    cur = [("cur-roads", "Street centrelines (current)", [g for g, _ in d["layers"]["roads"]], "#ffffff", "10 4 2 4"),
           ("cur-parcels", "Property lines (current)", [outline(g) for g, _ in d["layers"]["parcels"]], "#ff4d4d", "8 3"),
           ("cur-bldg", "Buildings (current)", [outline(g) for g, _ in d["layers"]["buildings"]], "#ffffff", "")]
    parts = [f'<image href="data:image/jpeg;base64,{img}" x="{-HALF}" y="{-HALF}" width="{2*HALF}" height="{2*HALF}"/>']
    rows, counts = [], {}
    for gid, label, geoms, col, dash in cur:
        da = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<g id="L-{gid}" fill="none" stroke="{col}" stroke-width="1"{da} vector-effect="non-scaling-stroke">' +
                     "".join(f'<path d="{path_of(g.simplify(0.15))}"/>' for g in geoms if not g.is_empty) + "</g>")
        rows.append((gid, label, col, len(geoms)))
    for gid, label, types, col in CANDIDATE:
        geoms = [outline(g) for g, t in imp if t in types]
        parts.append(f'<g id="L-{gid}" fill="none" stroke="{col}" stroke-width="1.2" vector-effect="non-scaling-stroke">' +
                     "".join(f'<path d="{path_of(g.simplify(0.15))}"/>' for g in geoms if not g.is_empty) + "</g>")
        rows.append((gid, "NEW: " + label, col, len(geoms)))
    parts.append(f'<g fill="#fff" font-size="10"><path d="M{-HALF+20},{HALF-24}h100" stroke="#fff" stroke-width="2"/>'
                 f'<text x="{-HALF+20}" y="{HALF-30}">0</text><text x="{-HALF+100}" y="{HALF-30}">100 m</text></g>')
    svg = f'<svg viewBox="{-HALF} {-HALF} {2*HALF} {2*HALF}" xmlns="http://www.w3.org/2000/svg">' + "".join(parts) + "</svg>"
    tg = "".join(f'<label><input type="checkbox" {"" if gid == "imp-drive" else "checked"} data-l="{gid}"><span class="sw" style="background:{col}"></span>{lab} <small>({n})</small></label>'
                 for gid, lab, col, n in rows)
    out = OUT / f"site-imagery-check-{s['letter']}-{sid}.html"
    out.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Imagery Check {s['letter']}</title><style>:root{{--bg:#f4f4f2;--ink:#222}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--ink:#e6e6e6}}}} :root[data-theme="dark"]{{--bg:#1b1b1b;--ink:#e6e6e6}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.45 system-ui,sans-serif}} main{{max-width:1240px;margin:0 auto;padding:16px}}
h1{{font-size:18px;margin:0 0 4px}} .k{{font-size:12px;opacity:.8}} .wrap{{display:grid;grid-template-columns:1fr 290px;gap:16px;align-items:start}}
@media (max-width:800px){{.wrap{{grid-template-columns:1fr}}}} svg{{width:100%;height:auto}} label{{display:flex;gap:6px;align-items:center;margin:4px 0}}
.sw{{width:14px;height:4px;display:inline-block}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: linework vs. aerial imagery</h1>
<p class="k">Same 1 km frame and scale as the linework (EPSG:3776). Imagery: Esri World Imagery (Esri, Maxar, Earthstar Geographics), warped to the local frame; date varies.
White and red = what the base has now. Bright colours (NEW) = City Impervious Surface 2021 outlines that would fill the gaps. Driveways off by default.</p>
<div class="wrap"><div>{svg}</div><aside>{tg}</aside></div></main>
<script>document.querySelectorAll('input[data-l]').forEach(c=>{{const g=document.getElementById('L-'+c.dataset.l);if(!c.checked&&g)g.style.display='none';
c.onchange=()=>{{if(g)g.style.display=c.checked?'':'none'}}}})</script></body></html>""", encoding="utf-8")
    print(out, out.stat().st_size // 1024, "KB", {r[0]: r[3] for r in rows})


if __name__ == "__main__":
    import sys
    if "--lines" in sys.argv:
        lines_mode("F")
        raise SystemExit
    if "--check" in sys.argv:
        check_mode("F")
        raise SystemExit
    for sid, s in SITES.items():
        d = build(sid, s)
        f = OUT / f"site-base-{s['letter']}-{sid}.html"
        f.write_text(html(sid, s, d), encoding="utf-8")
        print(sid, s["name"], d["info"], [(p.get("address"), round(g.area)) for g, p in d["focus"]], f.stat().st_size // 1024, "KB")

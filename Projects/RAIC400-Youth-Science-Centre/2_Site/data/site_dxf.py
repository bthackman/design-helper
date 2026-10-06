"""Write the CAD set per site (2026-10-05): a flat site plan DXF and a 3D topo DXF, plus a 5 m points CSV.

Same geometry as the approved HTML previews (site_linework.py). Units: metres. Coordinates: local, origin at
the site anchor (0,0), shared by both DXFs; the real EPSG:3776 (NAD83 / Alberta 3TM 114 W) coordinates of the
origin are written on layer Z-ORIGIN and in README.txt. Topo: 600 m square centred on the site parcel(s), 1 m
contours as 3D polylines at true elevation (HRDEM, CGVD2013), lightly smoothed (sigma 1.5 m).

Run: python site_dxf.py  ->  ../cad/
"""
import math, pathlib, csv
import numpy as np
import ezdxf
from ezdxf.enums import TextEntityAlignment
import rasterio, contourpy
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from shapely.geometry import LineString, box
from shapely.ops import unary_union

import site_linework as SL
from site_base_test import smooth, SITES, DTM

CAD_DIR = pathlib.Path(__file__).parent.parent / "cad"
CAD_DIR.mkdir(exist_ok=True)
TOPO = 600

# layer -> (ACI colour, linetype)
STYLE = {
    "TOPO-CONTOUR-MINOR": (9, "CONTINUOUS"), "TOPO-CONTOUR-MAJOR": (8, "CONTINUOUS"),
    "SITE-TREE-CANOPY": (94, "CONTINUOUS"), "SITE-WATER-EDGE": (5, "CONTINUOUS"),
    "SITE-FLOOD-LIMIT": (5, "DASHED"), "SITE-SETBACK-WATER": (1, "DASHDOT"),
    "SITE-DRIVEWAY": (252, "CONTINUOUS"), "SITE-PATH": (84, "CONTINUOUS"),
    "SITE-PARKING": (250, "CONTINUOUS"), "SITE-ROAD-GRAVEL": (32, "CONTINUOUS"),
    "SITE-ROAD-PAVED": (7, "CONTINUOUS"), "SITE-ROAD-CURB": (7, "CONTINUOUS"),
    "SITE-ROAD-CL": (8, "CENTER"), "SITE-RAIL": (7, "CONTINUOUS"), "SITE-BLDG-EXIST": (7, "CONTINUOUS"),
    "SITE-PROPERTY": (7, "PHANTOM"), "SITE-PROPERTY-SITE": (1, "PHANTOM"),
    "TEXT": (7, "CONTINUOUS"), "TEXT-CONTOUR": (8, "CONTINUOUS"), "Z-ORIGIN": (1, "CONTINUOUS"),
    "TOPO-EXTENT": (3, "DASHED"), "TOPO-REF-SITE": (1, "PHANTOM"),
}
OFF_BY_DEFAULT = {"SITE-DRIVEWAY", "SITE-ROAD-CL"}


def new_doc():
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M
    doc.header["$INSUNITS"] = 6
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 2.0
    for name, (col, lt) in STYLE.items():
        if name not in doc.layers:
            doc.layers.add(name, color=col, linetype=lt)
    for name in OFF_BY_DEFAULT:
        doc.layers.get(name).off()
    return doc


def lines_of(g):
    """Any shapely geometry -> list of coordinate sequences (polylines)."""
    if g.is_empty:
        return []
    t = g.geom_type
    if t == "LineString":
        return [list(g.coords)]
    if t == "LinearRing":
        return [list(g.coords)]
    if t == "Polygon":
        return [list(g.exterior.coords)] + [list(r.coords) for r in g.interiors]
    if hasattr(g, "geoms"):
        return [c for p in g.geoms for c in lines_of(p)]
    return []


def add_2d(msp, layer, geoms, tol=0.1):
    n = 0
    for g in geoms:
        for c in lines_of(g.simplify(tol) if tol else g):
            if len(c) < 2:
                continue
            closed = len(c) > 3 and c[0] == c[-1]
            pts = [(x, y) for x, y, *_ in (c[:-1] if closed else c)]
            msp.add_lwpolyline(pts, close=closed, dxfattribs={"layer": layer})
            n += 1
    return n


def add_origin(msp, x0, y0, name):
    msp.add_line((-5, 0), (5, 0), dxfattribs={"layer": "Z-ORIGIN"})
    msp.add_line((0, -5), (0, 5), dxfattribs={"layer": "Z-ORIGIN"})
    msp.add_circle((0, 0), 1.5, dxfattribs={"layer": "Z-ORIGIN"})
    msp.add_text(f"ORIGIN 0,0 = EPSG:3776 E {x0:.2f} N {y0:.2f} ({name} site anchor)", height=1.5,
                 dxfattribs={"layer": "Z-ORIGIN"}).set_placement((3, 3))


def site_plan(sid):
    SL.main(sid)   # rebuilds the approved HTML preview and fills SL.LAST
    L = SL.LAST
    s = SITES[sid]
    x0, y0 = L["origin"]
    doc = new_doc()
    msp = doc.modelspace()
    counts = {}
    for lname, gs in L["layers"].items():
        counts[lname] = add_2d(msp, lname, gs, tol=0.25 if lname.startswith("TOPO") else 0.1)
    for layer, text, x, y, ang, h in L["texts"]:
        msp.add_text(text, height=h, rotation=ang, dxfattribs={"layer": layer, "style": "OpenSans"}
                     ).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
    add_origin(msp, x0, y0, s["name"])
    xmin, xmax, ymin, ymax = L["frame"]
    doc.set_modelspace_vport(height=(ymax - ymin) * 1.05, center=((xmin + xmax) / 2, (ymin + ymax) / 2))
    f = CAD_DIR / f"{s['letter']}_{s['name'].replace(' ', '-')}_site-plan.dxf"
    doc.saveas(f)
    return f, counts, L


def topo(sid, L):
    s = SITES[sid]
    x0, y0 = L["origin"]
    site = unary_union(L["focus"])
    cx, cy = round(site.centroid.x), round(site.centroid.y)
    h = TOPO / 2
    pad = 10   # read a little wider so the smoothing has no edge effect, then clip
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(DTM[sid]) as r, WarpedVRT(r, crs="EPSG:3776", resampling=Resampling.bilinear) as vrt:
            win = rasterio.windows.from_bounds(x0 + cx - h - pad, y0 + cy - h - pad, x0 + cx + h + pad, y0 + cy + h + pad, vrt.transform)
            raw = vrt.read(1, window=win, masked=True).astype("float64").filled(np.nan)
            tr = vrt.window_transform(win)
    z = smooth(raw)
    ny, nx = z.shape
    xs = tr.c + tr.a * (np.arange(nx) + 0.5) - x0
    ys = tr.f + tr.e * (np.arange(ny) + 0.5) - y0
    sq = box(cx - h, cy - h, cx + h, cy + h)
    gen = contourpy.contour_generator(xs, ys, z)

    doc = new_doc()
    msp = doc.modelspace()
    n_min = n_maj = 0
    for lev in np.arange(math.floor(np.nanmin(z)), math.ceil(np.nanmax(z)) + 1, 1.0):
        layer = "TOPO-CONTOUR-MAJOR" if not lev % 5 else "TOPO-CONTOUR-MINOR"
        for line in gen.lines(lev):
            if len(line) < 6:
                continue
            g = LineString(line).simplify(0.2).intersection(sq)
            for c in lines_of(g):
                if len(c) < 2:
                    continue
                msp.add_polyline3d([(x, y, float(lev)) for x, y, *_ in c], dxfattribs={"layer": layer})
                if layer.endswith("MAJOR"): n_maj += 1
                else: n_min += 1
    # reference only (2D, z=0): leave these layers out when building the Toposolid
    msp.add_lwpolyline([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)], close=True,
                       dxfattribs={"layer": "TOPO-EXTENT"})
    add_2d(msp, "TOPO-REF-SITE", [g.boundary for g in L["focus"]])
    add_origin(msp, x0, y0, s["name"])
    doc.set_modelspace_vport(height=TOPO * 1.1, center=(cx, cy))
    f = CAD_DIR / f"{s['letter']}_{s['name'].replace(' ', '-')}_topo.dxf"
    doc.saveas(f)

    # 5 m points from the raw (unsmoothed) DTM, inside the square
    fc = CAD_DIR / f"{s['letter']}_{s['name'].replace(' ', '-')}_topo-points-5m.csv"
    n_pts = 0
    with open(fc, "w", newline="") as fh:
        w = csv.writer(fh)
        for gy in np.arange(cy - h, cy + h + 0.1, 5.0):
            for gx in np.arange(cx - h, cx + h + 0.1, 5.0):
                i = int(round((y0 + gy - tr.f) / tr.e - 0.5)); j = int(round((x0 + gx - tr.c) / tr.a - 0.5))
                if 0 <= i < ny and 0 <= j < nx and not np.isnan(raw[i, j]):
                    w.writerow([f"{gx:.2f}", f"{gy:.2f}", f"{raw[i, j]:.2f}"]); n_pts += 1
    zr = raw[~np.isnan(raw)]
    return f, fc, dict(minor=n_min, major=n_maj, points=n_pts, centre=(cx, cy), zmin=float(zr.min()), zmax=float(zr.max()))


def readme(rows):
    lines = ["Cairn Youth Centre (RAIC 400): site CAD set, generated 2026-10-05 by 2_Site/data/site_dxf.py", "",
             "UNITS: metres.  COORDINATES: local, origin (0,0) at each site's anchor; both DXFs of a site share it.",
             "REAL POSITION: NAD83 / Alberta 3TM ref. merid. 114 W (EPSG:3776). Origin coordinates below and on layer Z-ORIGIN.",
             "ELEVATIONS (topo): true heights in metres, NRCan HRDEM 1 m DTM, 2020 LiDAR, CGVD2013 datum.", "",
             "FILES PER SITE",
             "  *_site-plan.dxf        flat 2D base: all linework layers (contours flattened, for reference)",
             "  *_topo.dxf             600 m square centred on the site parcel(s): 1 m / 5 m contours as 3D polylines at true elevation",
             "                         TOPO-EXTENT and TOPO-REF-SITE are 2D reference only: leave them out when building the Toposolid",
             "  *_topo-points-5m.csv   x,y,z every 5 m (local metres), raw DTM; backup for Revit 'Toposolid from points' on flat ground", "",
             "SOURCES: City of Calgary Open Data (assessment parcels, street centrelines, buildings, hydrology, regulatory flood map,",
             "tree canopy 2022, Impervious Surface 2021, Tracks - Non-LRT); NRCan HRDEM. Parcels are assessment parcels, not survey lines.",
             "The 50 m water setback is a design assumption drawn from all mapped water. Contours lightly smoothed (sigma 1.5 m).",
             "Layers SITE-DRIVEWAY and SITE-ROAD-CL are switched off. $LTSCALE = 2.", ""]
    for r in rows:
        lines += [f"{r['name']} ({r['letter']}): origin E {r['x0']:.2f}  N {r['y0']:.2f}; frame {r['frame']} m from origin; "
                  f"topo centre {r['centre']} m from origin, {r['zmin']:.1f}-{r['zmax']:.1f} m; "
                  f"{r['minor']} minor + {r['major']} major contours; {r['points']} points"]
    (CAD_DIR / "README.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    rows = []
    for sid in ("F", "C"):
        f1, counts, L = site_plan(sid)
        f2, f3, st = topo(sid, L)
        s = SITES[sid]
        rows.append(dict(name=s["name"], letter=s["letter"], x0=L["origin"][0], y0=L["origin"][1], frame=L["frame"], **st))
        print(f1.name, sum(counts.values()), "polylines;", f2.name, st, ";", f3.name)
        for f in (f1, f2, f3):
            print("   ", f.name, f.stat().st_size // 1024, "KB")
    readme(rows)

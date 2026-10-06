"""Side bar (2026-10-05): the program laid flat, one storey, on each site. Not design, just area on the ground.

Program: brief v0.7 with Ben's 2026-10-05 cuts (hall and dining combined at 300 m2, lab 130 -> 80, separate
dining room removed). Each zone is a double-loaded bar (rooms both sides of a 2.4 m corridor); bars sit in
two columns either side of a 3 m spine. The block is dropped on the buildable part of the site parcel(s)
(parcel minus the 50 m water setback), clear of existing buildings and paved lots, nearest the parcel centre.
Run: python program_flat.py -> ../site-base-test/program-flat-<letter>-<id>.html
"""
import math
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
from shapely import affinity

import site_linework as SL
from site_base_test import SITES, OUT, path_of

ZONES = [  # zone, colour, [(room, count, m2 each)]
    ("Private", "#e8b04a", [("Pod room, 4 beds", 8, 20), ("Node washroom", 4, 18), ("Leader suite", 4, 18.6),
                            ("Lounge", 1, 84), ("Night station", 1, 14), ("Laundry", 1, 20), ("Accessible WC", 2, 6.5), ("Health room", 1, 16)]),
    ("Semi-public", "#6aa2d8", [("Maker and technology lab", 1, 111), ("Science and field lab", 1, 80), ("Classroom", 2, 46.5),
                                ("Office", 4, 14), ("Staff workroom", 1, 45), ("Reception", 1, 19), ("Staff and teachers' room", 1, 35)]),
    ("Public", "#d9694a", [("Hall and dining", 1, 300), ("Entry hub", 1, 56), ("Public washrooms", 1, 28)]),
    ("Service", "#9a9a9a", [("Kitchen and walk-in", 1, 60), ("Shipping and garbage", 1, 21), ("General storage", 1, 50),
                            ("Janitor and IT", 1, 10), ("Staff change room", 1, 15), ("Mechanical and electrical", 1, 70)]),
    ("Expedition", "#5c9a5a", [("Gear store", 1, 60), ("Packing and boot room", 1, 50), ("Drying room", 1, 16),
                               ("Gear wash and repair", 1, 20), ("Garage and vehicle bay", 1, 74)]),
]
CORR, SPINE = 2.4, 3.0
COLUMNS = [["Private", "Semi-public"], ["Public", "Service", "Expedition"]]


def depth(a):
    return 5.0 if a <= 25 else 7.0 if a <= 60 else 9.0


def bar(rooms):
    """Double-loaded bar. Rooms > 150 m2 sit as a block at the east end. Returns (room rects, corridor, w, h)."""
    big = [r for r in rooms if r[1] > 150]
    small = sorted([r for r in rooms if r[1] <= 150], key=lambda r: -r[1])
    sides = [[], []]; lens = [0.0, 0.0]
    for name, a in small:
        i = 0 if lens[0] <= lens[1] else 1
        w = a / depth(a); sides[i].append((name, a, w, depth(a))); lens[i] += w
    L = max(lens)
    dS, dN = max([r[3] for r in sides[0]] or [5]), max([r[3] for r in sides[1]] or [5])
    rects = []
    x = 0
    for name, a, w, d in sides[0]:
        rects.append((name, a, box(x, dS - d, x + w, dS))); x += w
    x = 0
    for name, a, w, d in sides[1]:
        rects.append((name, a, box(x, dS + CORR, x + w, dS + CORR + d))); x += w
    H = dS + CORR + dN
    corr = box(0, dS, L, dS + CORR)
    for name, a in big:   # e.g. the hall: full bar height, off the corridor end
        w = a / H
        rects.append((name, a, box(L, 0, L + w, H))); L += w
    return rects, corr, L, H


def block():
    """Two columns of bars either side of a spine. Returns rooms [(zone, colour, name, m2, rect)], circulation, bbox."""
    zones = {z: (c, [(n, a) for n, k, a in rooms for _ in range(k)]) for z, c, rooms in ZONES}
    out, circ, colw = [], [], []
    built = []
    for col in COLUMNS:
        y, w = 0.0, 0.0
        items = []
        for z in col:
            c, rooms = zones[z]
            rects, corr, L, H = bar(rooms)
            items.append((z, c, rects, corr, y)); y += H; w = max(w, L)
        built.append((items, w, y))
    x = 0.0
    for ci, (items, w, h) in enumerate(built):
        for z, c, rects, corr, y in items:
            dx = x if ci == 0 else x            # column 0 runs west->east to the spine; column 1 starts after it
            for name, a, r in rects:
                out.append((z, c, name, a, affinity.translate(r, dx, y)))
            circ.append(affinity.translate(corr, dx, y))
        x += w + (SPINE if ci == 0 else 0)
    H = max(h for _, _, h in built)
    circ.append(box(built[0][1], 0, built[0][1] + SPINE, H))
    return out, circ


def main(sid):
    SL.main(sid)
    L = SL.LAST
    s = SITES[sid]
    site = unary_union(L["focus"])
    # buildable = parcel minus the 50 m water setback (re-derived from the water layer's polygons)
    water = unary_union([Polygon(c) for g in L["layers"]["SITE-WATER-EDGE"] for c in ([g.coords] if g.geom_type in ("LineString", "LinearRing") else [p.coords for p in g.geoms]) if len(c) > 3])
    buildable = site.difference(water.buffer(50)) if not water.is_empty else site
    obstacles = unary_union([Polygon(g.coords).buffer(3) for g in L["layers"]["SITE-BLDG-EXIST"] if g.geom_type in ("LineString", "LinearRing") and len(g.coords) > 3]
                            + [Polygon(g.coords) for g in L["layers"]["SITE-PARKING"] + L["layers"]["SITE-ROAD-PAVED"] + L["layers"]["SITE-ROAD-GRAVEL"]
                               if g.geom_type in ("LineString", "LinearRing") and len(g.coords) > 3])
    free = buildable.difference(obstacles).buffer(-1)

    rooms, circ = block()
    allg = unary_union([r for *_, r in rooms] + circ)
    minx, miny, maxx, maxy = allg.bounds
    cx0, cy0 = (minx + maxx) / 2, (miny + maxy) / 2
    target = site.centroid
    best = None
    for ang in (0, 90):
        rot = lambda g: affinity.rotate(affinity.translate(g, -cx0, -cy0), ang, origin=(0, 0))
        fp = rot(allg.envelope)
        bx0, by0, bx1, by1 = free.bounds
        y = by0
        while y <= by1:
            x = bx0
            while x <= bx1:
                cand = affinity.translate(fp, x, y)
                if free.contains(cand):
                    d = cand.centroid.distance(target)
                    if best is None or d < best[0]:
                        best = (d, ang, x, y)
                x += 4
            y += 4
    placed_ok = best is not None
    if not placed_ok:   # does not fit clear of everything: put it at the parcel centre and show the clash
        best = (0, 0, target.x, target.y)
    _, ang, tx, ty = best
    place = lambda g: affinity.translate(affinity.rotate(affinity.translate(g, -cx0, -cy0), ang, origin=(0, 0)), tx, ty)
    rooms = [(z, c, n, a, place(r)) for z, c, n, a, r in rooms]
    circ = [place(g) for g in circ]
    foot = unary_union([r for *_, r in rooms] + circ)

    net = sum(a for *_, a, _ in rooms)
    circ_a = sum(g.area for g in circ)
    gross = foot.area
    site_a, build_a = site.area, buildable.area
    zt = {}
    for z, c, n, a, r in rooms:
        zt.setdefault((z, c), 0); zt[(z, c)] += a

    # drawing: faint base, site, buildable, block
    fx0, fy0, fx1, fy1 = foot.buffer(140).bounds
    view = box(fx0, fy0, fx1, fy1)
    base = []
    for lname in ("SITE-ROAD-CURB", "SITE-PARKING", "SITE-ROAD-GRAVEL", "SITE-BLDG-EXIST", "SITE-PROPERTY", "SITE-WATER-EDGE", "SITE-PATH", "SITE-RAIL", "TOPO-CONTOUR-MAJOR"):
        for g in L["layers"].get(lname, []):
            gi = g.intersection(view)
            if not gi.is_empty:
                base.append(f'<path d="{path_of(gi.simplify(0.2))}"/>')
    rp = "".join(f'<path d="{path_of(r)}" fill="{c}" fill-opacity=".75" stroke="#333" stroke-width=".25"><title>{n}: {a:.0f} m²</title></path>' for z, c, n, a, r in rooms)
    labels = "".join(f'<text x="{r.centroid.x:.1f}" y="{-r.centroid.y+0.8:.1f}" font-size="2" text-anchor="middle" fill="#111">{n}</text>'
                     for z, c, n, a, r in rooms if a >= 70)
    for (z, c), _a in zt.items():   # one zone label, beside the zone's bar
        zg = unary_union([r for zz, cc, n, a, r in rooms if zz == z])
        b = zg.bounds
        right = z in COLUMNS[1]   # second-column zones are labelled on their east side, clear of the spine
        lx, anc = (b[2] + 1, "start") if right else (b[0] - 1, "end")
        labels += f'<text x="{lx:.1f}" y="{-(b[1]+b[3])/2+1:.1f}" font-size="3.2" font-weight="700" text-anchor="{anc}" fill="{c}">{z.upper()}</text>'
    cp = "".join(f'<path d="{path_of(g)}" fill="#fff" stroke="none"/>' for g in circ)
    svg = (f'<svg viewBox="{fx0:.1f} {-fy1:.1f} {fx1-fx0:.1f} {fy1-fy0:.1f}" xmlns="http://www.w3.org/2000/svg">'
           f'<rect x="{fx0:.1f}" y="{-fy1:.1f}" width="{fx1-fx0:.1f}" height="{fy1-fy0:.1f}" fill="#fff"/>'
           f'<g fill="none" stroke="#c8c8c8" stroke-width=".4" vector-effect="non-scaling-stroke">{"".join(base)}</g>'
           f'<path d="{path_of(buildable)}" fill="#c0392b" fill-opacity=".05" stroke="none"/>'
           f'<path d="{path_of(site.boundary)}" fill="none" stroke="#c0392b" stroke-width="1.6" stroke-dasharray="14 4 3 4" vector-effect="non-scaling-stroke"/>'
           f'<g>{cp}{rp}</g><g font-family="Arial, sans-serif">{labels}</g>'
           f'<path d="{path_of(foot.boundary)}" fill="none" stroke="#111" stroke-width="1.2" vector-effect="non-scaling-stroke"/>'
           f'<g font-size="6" fill="#222"><path d="M{fx0+15:.1f},{-fy0-12:.1f}h50" stroke="#222" stroke-width="1"/><text x="{fx0+15:.1f}" y="{-fy0-16:.1f}">0</text><text x="{fx0+56:.1f}" y="{-fy0-16:.1f}">50 m</text></g></svg>')
    zrows = "".join(f'<tr><td><span class="sw" style="background:{c}"></span>{z}</td><td>{a:,.0f} m²</td></tr>' for (z, c), a in zt.items())
    fit = ("Fits clear of the water setback, existing buildings and paved lots." if placed_ok
           else "Does NOT fit clear of everything at one storey: shown at the parcel centre so the clash is visible.")
    f = OUT / f"program-flat-{s['letter']}-{sid}.html"
    f.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Program Flat {s['letter']}</title><style>:root{{--bg:#f4f4f2;--ink:#222}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1b1b1b;--ink:#e6e6e6}}}} :root[data-theme="dark"]{{--bg:#1b1b1b;--ink:#e6e6e6}}
body{{margin:0;background:var(--bg);color:var(--ink);font:13px/1.45 system-ui,sans-serif}} main{{max-width:1200px;margin:0 auto;padding:16px}}
h1{{font-size:18px;margin:0 0 4px}} .k{{font-size:12px;opacity:.8}} .wrap{{display:grid;grid-template-columns:1fr 300px;gap:16px;align-items:start}}
@media (max-width:820px){{.wrap{{grid-template-columns:1fr}}}} svg{{width:100%;height:auto;border:1px solid #bbb}}
table{{border-collapse:collapse;width:100%;font-size:12px}} td{{padding:3px 4px;border-bottom:1px solid #ccc}} td:last-child{{text-align:right}}
.big td{{font-size:14px;font-weight:600}} .sw{{display:inline-block;width:10px;height:10px;margin-right:6px;vertical-align:-1px}}</style></head><body><main>
<h1>{s['letter']} {s['name']}: program laid flat, one storey</h1>
<p class="k">Not a design: every room at its brief area, in one double-loaded bar per zone, two columns either side of a spine, dropped on the buildable part of the site.
Program = brief v0.7 with the 2026-10-05 cuts (hall and dining combined 300 m², lab 80 m², separate dining removed). Hover a room for its name and area.</p>
<div class="wrap"><div>{svg}</div><aside><table class="big">
<tr><td>Site (parcel{'s' if len(L['focus']) > 1 else ''})</td><td>{site_a:,.0f} m² ({site_a/1e4:.2f} ha)</td></tr>
<tr><td>Buildable (minus 50 m water setback)</td><td>{build_a:,.0f} m²</td></tr>
<tr><td>Building footprint (1 storey)</td><td>{gross:,.0f} m²</td></tr>
<tr><td>Site coverage</td><td>{100*gross/site_a:.1f}%</td></tr></table>
<p class="k" style="margin:8px 0">{fit}</p>
<table>{zrows}<tr><td><b>Net (rooms)</b></td><td><b>{net:,.0f} m²</b></td></tr>
<tr><td>Corridors and spine</td><td>{circ_a:,.0f} m²</td></tr><tr><td>Footprint ÷ net</td><td>{gross/net:.2f}</td></tr>
<tr><td>Brief target at ×1.30</td><td>{net*1.3:,.0f} m²</td></tr></table>
<p class="k" style="margin-top:8px">Walls, structure and shafts aren't drawn, so the true gross at one storey sits nearer ×1.30 than the corridors alone suggest. Outdoor program (build yard, fire circle, sleep-out ground), parking and coach drop-off are not placed yet.</p>
</aside></div></main></body></html>""", encoding="utf-8")
    print(f.name, dict(net=round(net), circ=round(circ_a), gross=round(gross), site=round(site_a), buildable=round(build_a), fits=placed_ok, ang=ang))


if __name__ == "__main__":
    for sid in ("F", "C"):
        main(sid)

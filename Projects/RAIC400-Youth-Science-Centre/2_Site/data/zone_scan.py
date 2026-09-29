"""Stage 1 zone scan for the RAIC 400 Cairn Youth Centre: reframe version, 2026-09-29.

Client reframe (instructor feedback 2026-09-28, Ben's decisions 2026-09-29): a year-round residential centre for
visiting domestic and international students, 32 beds (4 nodes of 8), about a third of the program outdoors.
Transit and low-income reach no longer drive the search. This version scores every zone, city and rural, on
seven criteria (see CRITERIA). It replaces the 2026-09-25 version, whose output `zone_scan.json` is kept as the
record of the transit-era scan (zones A-E only).

Sources (all free, queried live; cached in `_cache_reframe_raw.json`, rerun with --offline to rescore only):
  - OSRM public demo router (router.project-osrm.org), table service: FREE-FLOW drive minutes, no traffic.
  - OpenStreetMap via Overpass: land cover, trails, water, parks, parking, roads, schools, places, is_in areas.
    OSM coverage is uneven; untagged land is reported, not guessed.
  - Alberta Flood Hazard Identification Program (FHIP) map service, geospatial.alberta.ca (floodway, flood fringe,
    1:500 extent). Covers studied reaches only: "no hit" means "not mapped as hazard", not "no hazard".
  - City of Calgary parcels (4bsw-nn7w) for Ben's two lots, A and B.
Zones are anchor points with a 400 m ring (dot + ring convention), never an outlined retail/club parcel.
Output: scan_2026-09-29_reframe.json (self-contained: per-site scores, raw metrics, why-it-ranks, flags).
"""
import json, math, sys, time
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "scan_2026-09-29_reframe.json"
CACHE = HERE / "_cache_reframe_raw.json"
UA = {"User-Agent": "RAIC400-student-site-search"}
OVERPASS = ["https://overpass-api.de/api/interpreter"] * 3   # busy server: up to 3 tries per query with back-off
OSRM = "https://router.project-osrm.org/table/v1/driving/"
FHIP = ("https://geospatial.alberta.ca/mimas/rest/services/fama_data_distribution/"
        "fama_public_data_distribution/MapServer/{}/query")

# ---------------------------------------------------------------- zones
# setting: city (inside Calgary), edge (town/hamlet edge), rural (open county land)
ZONES = [
    # removed by Ben 2026-09-29: ("A", "Beltline infill, 633 15 Ave SW (Ben lot 1)", 51.038723, -114.076476, "city"),
    # removed by Ben 2026-09-29: ("B", "Eau Claire, 708 1 Ave SW, Prince's Island edge (Ben lot 2)", 51.052571, -114.076107, "city"),
    ("C", "Inglewood, Bird Sanctuary / Bow River edge", 51.027895, -114.006957, "city"),
    ("D", "Fish Creek Park edge at Fish Creek-Lacombe CTrain", 50.923014, -114.07307, "city"),
    # removed by Ben 2026-09-29: ("E", "Forest Lawn, Elliston Park edge", 51.033572, -113.939943, "city"),
    ("F", "Glenmore Landing, Glenmore Reservoir edge", 50.9737, -114.097874, "city"),
    ("G", "Brentwood, Nose Hill / U of C side", 51.0883561, -114.1308072, "city"),
    ("I", "Loch McKinnon north shore, Bowness / Bow River", 51.10090, -114.23840, "city"),
    # removed by Ben 2026-09-29: ("J", "819 32 St SE school reserve, Franklin", 51.04643, -113.99114, "city"),
    # removed by Ben 2026-09-29: ("K", "636 Marlborough Wy NE school reserve", 51.05856, -113.97458, "city"),
    # new 2026-09-29, anchors placed on open ground after an Esri imagery check
    ("L", "Bragg Creek, hamlet east edge across Hwy 22", 50.9493, -114.5594, "edge"),
    ("M", "Cochrane SW edge, Jumping Pound Creek valley rim", 51.1817, -114.5107, "edge"),
    ("N", "Glenbow Ranch gateway, Hwy 1A (Bow valley, Cochrane-Calgary)", 51.1750, -114.3650, "rural"),
    ("O", "Springbank hub, Range Rd 33 / Springbank schools", 51.0782, -114.3449, "rural"),
    ("P", "Hwy 1 corridor at Jumping Pound Creek (west of Hwy 22)", 51.0800, -114.5486, "rural"),
    ("Q", "Hwy 22 north of Bragg Creek, foothill forest meadow", 50.9744, -114.5638, "rural"),
]
PARCELS = {"A": "633 15 AV SW", "B": "708 1 AV SW"}

# ---------------------------------------------------------------- destinations
DEST = {
    "kananaskis_hwy1_hwy40": (51.0850, -115.0010),   # same anchor as the 2026-09-28 scan
    "west_bragg_creek_trailhead": None,              # looked up in OSM, fallback below
    "yyc_airport": (51.1313, -114.0107),             # terminal frontage
    "city_hall_downtown": (51.0453, -114.0581),
    "telus_spark": (51.05387, -114.02444),
    "calgary_zoo": (51.04543, -114.02318),
    "university_of_calgary": (51.07505, -114.13881),
}
WBC_FALLBACK = (50.9486, -114.6933)   # West Bragg Creek PRA centroid (OSM) if no trailhead parking found
CITY_CLUSTER = ["city_hall_downtown", "telus_spark", "calgary_zoo", "university_of_calgary"]


# ---------------------------------------------------------------- helpers
def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


OVP_STATE = {"consecutive_failures": 0}


def overpass(q):
    """Time-boxed: one try per endpoint, 60 s each. After 2 zones fail in a row, Overpass is skipped for the run."""
    if OVP_STATE["consecutive_failures"] >= 4:
        raise RuntimeError("Overpass skipped (public endpoints unresponsive earlier in this run)")
    q = q.replace("[timeout:200]", "[timeout:50]").replace("[timeout:120]", "[timeout:50]")
    last = None
    for url in OVERPASS:
        try:
            r = requests.post(url, data={"data": q}, headers=UA, timeout=60)
            if r.status_code == 200 and r.text.lstrip().startswith("{"):
                return r.json()["elements"]
            last = f"{r.status_code} {r.text[:120]}"
        except requests.RequestException as e:
            last = str(e)[:160]
        time.sleep(20)
    raise RuntimeError(f"Overpass failed: {last}")


def fhip(layer, lon, lat, dist_m):
    p = {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": "Multi_Zone,Two_Zone,RiverName",
         "returnGeometry": "false", "f": "json"}
    if dist_m:
        p.update(distance=dist_m, units="esriSRUnit_Meter")
    r = requests.get(FHIP.format(layer), params=p, timeout=60)
    r.raise_for_status()
    j = r.json()
    if "error" in j:
        raise RuntimeError(j["error"])
    return j.get("features", [])


class Local:
    """Equirectangular metres around an anchor."""
    def __init__(self, lat, lon):
        self.lat0, self.lon0 = lat, lon
        self.kx = 111320.0 * math.cos(math.radians(lat))
        self.ky = 111320.0

    def xy(self, lat, lon):
        return ((lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky)


def pip(x, y, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def assemble(chains):
    """Join way chains into rings by matching endpoints; close leftovers straight (approximation)."""
    chains = [list(c) for c in chains if len(c) >= 2]
    rings = []
    while chains:
        cur = chains.pop(0)
        changed = True
        while cur[0] != cur[-1] and changed:
            changed = False
            for i, c in enumerate(chains):
                if c[0] == cur[-1]:
                    cur += c[1:]
                elif c[-1] == cur[-1]:
                    cur += c[::-1][1:]
                elif c[-1] == cur[0]:
                    cur = c + cur[1:]
                elif c[0] == cur[0]:
                    cur = c[::-1] + cur[1:]
                else:
                    continue
                chains.pop(i); changed = True
                break
        if len(cur) >= 4:
            rings.append(cur)
    return rings


def classify(tags):
    """Map OSM tags to cover classes used by the scoring."""
    c = set()
    nat, lu, le, am = tags.get("natural"), tags.get("landuse"), tags.get("leisure"), tags.get("amenity")
    if nat == "water" or tags.get("waterway") == "riverbank" or lu in ("reservoir", "basin"):
        c.add("water")
    if nat == "wood" or lu == "forest":
        c.add("wood")
    if nat in ("scrub", "grassland", "heath", "wetland") or lu == "meadow":
        c.add("natural_open")
    if lu == "farmland":
        c.add("farmland")
    if lu in ("grass", "recreation_ground", "village_green"):
        c.add("grass")
    if lu in ("greenfield", "brownfield", "construction"):
        c.add("vacant")
    if am == "parking":
        c.add("parking")
    if le in ("park", "nature_reserve") or tags.get("boundary") == "protected_area":
        c.add("park")
    if le == "golf_course":
        c.add("golf")
    if lu in ("residential", "commercial", "retail", "industrial", "railway", "cemetery", "military") or "building" in tags:
        c.add("built")
    return c


def polygons_from(elements, loc):
    polys = []   # (classes, outer_rings, inner_rings, bbox, tags)
    for e in elements:
        tags = e.get("tags", {})
        cls = classify(tags)
        if not cls:
            continue
        outers, inners = [], []
        if e["type"] == "way" and e.get("geometry"):
            g = [(p["lat"], p["lon"]) for p in e["geometry"]]
            if g[0] == g[-1]:
                outers = [g]
        elif e["type"] == "relation":
            o = [[(p["lat"], p["lon"]) for p in m["geometry"]] for m in e.get("members", [])
                 if m.get("type") == "way" and m.get("geometry") and m.get("role", "outer") in ("outer", "")]
            i = [[(p["lat"], p["lon"]) for p in m["geometry"]] for m in e.get("members", [])
                 if m.get("type") == "way" and m.get("geometry") and m.get("role") == "inner"]
            outers, inners = assemble(o), assemble(i)
        if not outers:
            continue
        o_xy = [[loc.xy(*p) for p in r] for r in outers]
        i_xy = [[loc.xy(*p) for p in r] for r in inners]
        xs = [p[0] for r in o_xy for p in r]; ys = [p[1] for r in o_xy for p in r]
        polys.append((cls, o_xy, i_xy, (min(xs), min(ys), max(xs), max(ys)), tags))
    return polys


def cover(polys, radius, step):
    """Fraction of a disc of `radius` m covered by each class, sampled on a `step` m grid."""
    pts = [(x, y) for x in range(-radius, radius + 1, step) for y in range(-radius, radius + 1, step)
           if x * x + y * y <= radius * radius]
    counts, combos = {}, []
    for x, y in pts:
        hit = set()
        for cls, o, i, bb, _ in polys:
            if not (bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]):
                continue
            if any(pip(x, y, r) for r in o) and not any(pip(x, y, r) for r in i):
                hit |= cls
        combos.append(hit)
        for c in hit:
            counts[c] = counts.get(c, 0) + 1
        if not hit:
            counts["untagged"] = counts.get("untagged", 0) + 1
    n = len(pts)
    frac = {k: round(v / n, 3) for k, v in sorted(counts.items())}
    # derived fractions (each sample point counted once)
    natural = sum(1 for h in combos if h & {"water", "wood", "natural_open", "park"}) / n
    natural_farm = sum(0.5 for h in combos if "farmland" in h and not h & {"water", "wood", "natural_open", "park"}) / n
    open_room = 0.0
    for h in combos:
        if h & {"park", "water", "golf"} or ("built" in h and "parking" not in h):
            continue
        if h & {"parking", "farmland", "natural_open", "grass", "vacant"}:
            open_room += 1
        elif "wood" in h:
            open_room += 0.5          # clearable, at a cost
    return frac, round(natural + natural_farm, 3), round(open_room / n, 3), n


def line_len_in(geom, loc, radius):
    tot = 0.0
    pts = [loc.xy(p["lat"], p["lon"]) for p in geom]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if mx * mx + my * my <= radius * radius:
            tot += math.hypot(x2 - x1, y2 - y1)
    return tot


def min_dist(geom, loc):
    return min(math.hypot(*loc.xy(p["lat"], p["lon"])) for p in geom) if geom else 1e9


# ---------------------------------------------------------------- data collection
def collect():
    raw = {"zones": {}, "dest": {}}
    if CACHE.exists() and "--fresh" not in sys.argv:          # resume: keep zones already collected
        raw["zones"] = json.loads(CACHE.read_text(encoding="utf-8")).get("zones", {})
    # West Bragg Creek trailhead parking
    try:
        els = overpass('[out:json][timeout:60];nwr["amenity"="parking"](50.92,-114.72,50.97,-114.60);out tags center;')
        cand = [(e.get("tags", {}).get("name", ""), e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}) for e in els]
        wbc = [c for c in cand if "west bragg" in c[0].lower()]
        pick = wbc[0] if wbc else min(cand, key=lambda c: km((c[1]["lat"], c[1]["lon"]), WBC_FALLBACK)) if cand else None
        DEST["west_bragg_creek_trailhead"] = (pick[1]["lat"], pick[1]["lon"]) if pick else WBC_FALLBACK
        raw["dest"]["west_bragg_creek_trailhead_source"] = f"OSM parking '{pick[0]}'" if pick else "fallback PRA centroid"
    except Exception as e:
        DEST["west_bragg_creek_trailhead"] = WBC_FALLBACK
        raw["dest"]["west_bragg_creek_trailhead_source"] = f"fallback PRA centroid ({e})"
    raw["dest"]["coords"] = DEST

    # OSRM table, all zones x all destinations
    names = list(DEST)
    coords = [(z[3], z[2]) for z in ZONES] + [(DEST[n][1], DEST[n][0]) for n in names]
    s = ";".join(f"{lon},{lat}" for lon, lat in coords)
    src = ";".join(str(i) for i in range(len(ZONES)))
    dst = ";".join(str(len(ZONES) + i) for i in range(len(names)))
    r = requests.get(OSRM + s, params={"sources": src, "destinations": dst, "annotations": "duration,distance"},
                     headers=UA, timeout=120)
    r.raise_for_status()
    tab = r.json()

    for zi, (zid, name, lat, lon, setting) in enumerate(ZONES):
        rec = {"drive_min": {n: round(tab["durations"][zi][k] / 60) for k, n in enumerate(names)},
               "drive_km": {n: round(tab["distances"][zi][k] / 1000, 1) for k, n in enumerate(names)}}
        if zid in raw["zones"] and "flood_fhip" in raw["zones"][zid] and not raw["zones"][zid].get("osm_error"):
            raw["zones"][zid].update(rec)
            continue
        try:
            q_poly = f"""[out:json][timeout:200];
            ( way(around:1000,{lat},{lon})["natural"~"^(wood|scrub|grassland|heath|wetland|water)$"];
              way(around:1000,{lat},{lon})["landuse"~"^(forest|meadow|grass|farmland|greenfield|brownfield|construction|residential|commercial|retail|industrial|railway|recreation_ground|village_green|reservoir|basin|cemetery|military)$"];
              way(around:1000,{lat},{lon})["leisure"~"^(park|nature_reserve|golf_course)$"];
              way(around:1000,{lat},{lon})["boundary"="protected_area"];
              way(around:1000,{lat},{lon})["waterway"="riverbank"];
              way(around:1000,{lat},{lon})["amenity"="parking"];
              way(around:400,{lat},{lon})["building"];
            ); out tags geom;"""
            q_rel = f"""[out:json][timeout:200];
            ( relation(around:1000,{lat},{lon})["natural"~"^(wood|scrub|grassland|wetland|water)$"];
              relation(around:1000,{lat},{lon})["landuse"~"^(forest|meadow|grass|farmland|residential|commercial|retail|industrial|reservoir)$"];
              relation(around:1000,{lat},{lon})["leisure"~"^(park|nature_reserve|golf_course)$"];
              relation(around:1000,{lat},{lon})["boundary"="protected_area"];
              relation(around:1000,{lat},{lon})["amenity"="parking"];
            ); out tags bb;"""
            q_lines = f"""[out:json][timeout:200];
            ( way(around:400,{lat},{lon})["highway"~"^(path|footway|track|bridleway|cycleway)$"];
              way(around:400,{lat},{lon})["waterway"~"^(river|stream|canal)$"];
              way(around:2000,{lat},{lon})["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"];
            ); out tags geom;
            ( nwr(around:2000,{lat},{lon})["amenity"="school"]; ); out tags center;
            ( node(around:4000,{lat},{lon})["place"~"^(city|town|village|hamlet|suburb|neighbourhood)$"]; ); out tags;
            ( nwr(around:5000,{lat},{lon})["man_made"~"^(works|wastewater_plant|water_works)$"];
              nwr(around:5000,{lat},{lon})["landuse"="industrial"]["name"]; ); out tags center;
            is_in({lat},{lon})->.a;
            ( area.a["boundary"~"^(aboriginal_lands|protected_area|administrative)$"];
              area.a["leisure"~"^(park|nature_reserve)$"]; ); out tags;"""
            polys_el = overpass(q_poly)
            rels = overpass(q_rel)
            big = [e for e in rels if "bounds" in e and km((e["bounds"]["minlat"], e["bounds"]["minlon"]),
                                                           (e["bounds"]["maxlat"], e["bounds"]["maxlon"])) > 60]
            small_ids = [str(e["id"]) for e in rels if e not in big]
            if small_ids:
                polys_el += overpass(f"[out:json][timeout:200];relation(id:{','.join(small_ids)});out tags geom;")
            rec["relations_skipped_too_large"] = [e.get("tags", {}).get("name", e["id"]) for e in big]
            lines = overpass(q_lines)

            loc = Local(lat, lon)
            polys = polygons_from(polys_el, loc)
            f400, nat400, room400, _ = cover(polys, 400, 25)
            f1k, nat1k, _, _ = cover(polys, 1000, 50)
            rec["cover_400m"] = f400
            rec["natural_fraction_400m"] = nat400          # water/wood/natural open/park, + half credit for farmland
            rec["open_room_fraction_400m"] = room400       # parking, farmland, meadow, grass, vacant; wood at half
            rec["cover_1km"] = f1k
            rec["natural_fraction_1km"] = nat1k
            rec["forest_fraction_1km"] = f1k.get("wood", 0.0)
            parks = {}
            for cls, o, i, bb, tags in polys:
                if "park" in cls and tags.get("name"):
                    parks[tags["name"]] = round(sum(abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(r, r[1:])) / 2)
                                                    for r in o) / 10000, 1)
            rec["named_parks_within_1km_ha"] = dict(sorted(parks.items(), key=lambda kv: -kv[1])[:6])

            trail_m = track_m = 0.0
            water = set(); roads = []
            schools, places, works, is_in = [], [], [], []
            for e in lines:
                t = e.get("tags", {})
                if e["type"] == "area":
                    is_in.append({k: t[k] for k in ("name", "boundary", "admin_level", "leisure") if k in t})
                    continue
                hw, ww = t.get("highway"), t.get("waterway")
                if e.get("geometry") and hw in ("path", "footway", "bridleway", "cycleway") and t.get("footway") != "sidewalk":
                    trail_m += line_len_in(e["geometry"], loc, 400)
                elif e.get("geometry") and hw == "track":
                    track_m += line_len_in(e["geometry"], loc, 400)
                elif e.get("geometry") and ww:
                    water.add(t.get("name", f"unnamed {ww}"))
                elif e.get("geometry") and hw in ("motorway", "trunk", "primary", "secondary", "tertiary"):
                    roads.append((hw, t.get("ref") or t.get("name") or f"unnamed {hw}", min_dist(e["geometry"], loc)))
                elif t.get("amenity") == "school":
                    schools.append(t.get("name", "unnamed school"))
                elif "place" in t:
                    places.append(f"{t.get('name')} ({t['place']})")
                elif t.get("man_made") or t.get("landuse") == "industrial":
                    works.append(t.get("name") or t.get("man_made"))
            rank = {"motorway": 5, "trunk": 4, "primary": 4, "secondary": 4, "tertiary": 3}
            near = sorted(roads, key=lambda r: r[2])
            rec["trail_m_400m"] = round(trail_m)
            rec["track_m_400m"] = round(track_m)
            rec["waterways_400m"] = sorted(water)
            rec["nearest_major_road"] = {"class": near[0][0], "name": near[0][1], "m": round(near[0][2])} if near else None
            rec["best_road_within_400m"] = max((r for r in roads if r[2] <= 400 and r[0] != "motorway"),
                                                key=lambda r: rank[r[0]], default=None)
            rec["major_roads_within_2km"] = sorted({r[1] for r in roads})
            rec["schools_within_2km"] = sorted(set(schools))
            rec["places_within_4km"] = sorted(set(places))
            rec["works_industry_within_5km"] = sorted({w for w in works if w})
            rec["is_in"] = is_in
        except Exception as e:
            OVP_STATE["consecutive_failures"] += 1
            rec["osm_error"] = str(e)[:200]
            print(zid, "OSM unavailable:", rec["osm_error"])
        else:
            OVP_STATE["consecutive_failures"] = 0

        # Alberta FHIP flood hazard: layer 1 (floodway/fringe), layer 13 (1:500 open water)
        fl = {}
        # layer 1 carries floodway, flood fringe (incl. high-hazard and protected) and the 1:200 / 1:500 extents
        fl["at_point"] = sorted({f["attributes"]["Multi_Zone"] for f in fhip(1, lon, lat, 0)})
        fl["within_250m"] = sorted({f["attributes"]["Multi_Zone"] for f in fhip(1, lon, lat, 250)})
        fl["rivers"] = sorted({f["attributes"]["RiverName"] or "" for f in fhip(1, lon, lat, 250)} - {""})
        rec["flood_fhip"] = fl

        if zid in PARCELS:
            row = requests.get("https://data.calgary.ca/resource/4bsw-nn7w.json",
                               params={"$where": f"address = '{PARCELS[zid]}'", "$limit": 1}, timeout=60).json()[0]
            rec["parcel"] = {"address": PARCELS[zid], "area_m2": float(row["land_size_sm"]),
                             "land_use": row.get("land_use_designation")}
        raw["zones"][zid] = rec
        CACHE.write_text(json.dumps(raw, indent=1), encoding="utf-8")
        print(zid, json.dumps({k: rec.get(k) for k in ("drive_min", "natural_fraction_400m", "open_room_fraction_400m",
                                                       "forest_fraction_1km", "trail_m_400m", "flood_fhip", "osm_error")}))
        time.sleep(1)
    return raw


# ---------------------------------------------------------------- scoring
CRITERIA = [
    # key, label, weight, rule text
    ("mountains", "Mountains", 2, "Free-flow drive minutes to the nearer of the Hwy 1/Hwy 40 Kananaskis gateway and the "
     "West Bragg Creek trailhead: <=20 = 5, <=32 = 4, <=44 = 3, <=56 = 2, else 1 (same minute bands as City)."),
    ("city", "City & airport", 2, "Mean of (drive to YYC) and (mean drive to City Hall, TELUS Spark, the Zoo and U of C): "
     "<=20 = 5, <=32 = 4, <=44 = 3, <=56 = 2, else 1 (same minute bands as Mountains)."),
    ("landscape", "Landscape at the door", 2, "Points: natural cover in the 400 m ring >=60% +2, >=30% +1 (farmland at half); "
     "trails >=2 km in the ring +1 (tracks at half); a river, stream or lake in the ring +1; natural cover >=40% of the "
     "1 km ring +1. Floor 1, cap 5."),
    ("room", "Room", 1, "Open ground in the 400 m ring (parking, farmland, meadow, grass, vacant; forest at half; parks, "
     "water, golf and built land excluded): >=40% = 5, >=25% = 4, >=15% = 3, >=7% = 2, else 1. Ben's fixed lots scored "
     "on lot area against the ~1 ha need."),
    ("access", "Coach & egress", 1, "4 if a secondary-or-better road is within 400 m, 3 if tertiary within 400 m or "
     "secondary+ within 1 km, else 2; +1 if 3+ distinct major roads within 2 km (routes out), -1 if only 1. Floor 1, cap 5."),
    ("hazards", "Hazards", 1, "Start 5. Flood (Alberta FHIP): floodway at the anchor -3, flood fringe at the anchor -2, "
     "else protected fringe or a 1:200/1:500 extent at the anchor, or floodway/fringe within 250 m, -1. Wildfire (forest share of the 1 km ring): >=40% -2, "
     ">=15% -1. Sour-gas or heavy industrial works within 5 km -1. Floor 1."),
    ("services", "Services & community", 1, "Servicing: inside Calgary or the Town of Cochrane +3; hamlet with a county "
     "water/wastewater utility +2; open county land 0 (well and on-site wastewater). Community: a school within 2 km +1; "
     "a town, hamlet or city neighbourhood within 4 km +1. Floor 1, cap 5."),
]
MAX_W = sum(c[2] for c in CRITERIA) * 5
TRAVEL_BANDS = [(5, 20), (4, 32), (3, 44), (2, 56)]   # one yardstick for both travel criteria, so neither side is favoured

# Imagery-review adjustments (Esri World Imagery, 2026-09-29). Kept visible: formula score and reason stay in the JSON.
OVERRIDES = {
    # zone: {criterion: (score, reason)}
}
SERVICING = {  # jurisdiction note per zone, used by the services score
    "city": (3, "City of Calgary municipal water and sanitary (inside city limits)"),
    "L": (2, "Bragg Creek hamlet: Rocky View County water and wastewater utility serves the hamlet core; capacity "
             "and reach east of Hwy 22 unverified"),
    "M": (3, "Town of Cochrane municipal servicing at the adjacent subdivision; extension to the rim land unverified"),
}
SHORTLIST = [
    {"letter": "L", "role": "rural lead", "why": "Ties F at 38 and wins the tie-break; West Bragg Creek trails 16 min away, forest and the Elbow at the door, a hamlet next door."},
    {"letter": "F", "role": "city lead", "why": "38; reservoir shore and pathway at the door, surface parking to build on, 24 min average to the city and YYC."},
    {"letter": "D", "role": "city alternate", "why": "37; Fish Creek PP at the door; 52 min to West Bragg Creek ties F for the best city mountain time. Chosen over G (little landscape)."},
    {"letter": "M", "role": "edge alternate", "why": "36; town servicing and neighbours with the Jumping Pound Creek valley at the door."},
]
EXTRA_FLAGS = {
    "A": ["Ben's lot: 1,000 m2, a tenth of the ~1 ha need", "Inside the Elbow 1:200/1:500 extents (FHIP)"],
    "B": ["Ben's lot: 3,028 m2; stacked building, no on-site camp", "DC 91D2008 use for a residential youth centre unverified",
          "Bow River floodway/fringe within 250 m (FHIP)"],
    "C": ["Anchor is in the Bow floodway (FHIP); a buildable lot must sit on the 9 Ave SE edge, none identified"],
    "D": ["City use of station-area land unverified", "Macleod Trail and LRT noise"],
    "E": ["Stormwater-lake park; thin ecology"],
    "F": ["Glenmore Landing redevelopment proposal unverified; anchor is on surface parking, not an outlined parcel",
          "Glenmore Reservoir is a drinking-water reservoir: water-contact program limits unverified"],
    "G": ["Nose Hill access across John Laurie Blvd unverified"],
    "I": ["Loch McKinnon is Shriners' land, availability unverified", "Bow River flood mapping nearby"],
    "J": ["School-reserve surplus status unverified"],
    "K": ["School-reserve surplus status unverified"],
    "L": ["Open ground is a narrow meadow beside Hwy 22; the rest is forest to clear (FireSmart defensible space)",
          "Bragg Creek has limited road routes out (Hwy 22 N, Hwy 22/758 S) in a wildfire",
          "Rocky View County water/wastewater capacity east of Hwy 22 unverified",
          "Tsuut'ina Nation 145 lies to the east; anchor believed outside it, unverified"],
    "M": ["Valley-rim land may be environmental or municipal reserve; ownership and developability unverified",
          "Jumping Pound Creek flood mapping near the anchor (FHIP within 250 m)",
          "OSRM snapped the rim anchor to a local road; mountain times may be a few minutes long"],
    "N": ["Whether the hay field is inside Glenbow Ranch Provincial Park is UNVERIFIED (OSM is_in unavailable); if it is, "
          "the zone moves to private land north of Hwy 1A",
          "No services, no neighbours within 4 km: the course's community interface is weakest here",
          "OSRM time to Hwy 40 (58 min) looks long for Hwy 1A; check routing"],
    "O": ["Flat cultivated field: no landscape at the door", "Near Calaway Park and Springbank Airport (noise)"],
    "P": ["No services, no neighbours: well, on-site wastewater, and a weak community interface",
          "Jumping Pound sour-gas field and plant in the area: AER setback check needed, unverified", "Hwy 1 noise"],
    "Q": ["Continuous conifer forest: highest wildfire exposure of the set", "One road (Hwy 22) at the door",
          "Existing ranch/acreage buildings in the ring: the anchor is on the meadow, not the homestead"],
}
WHY = {
    "A": "Downtown access is excellent but a 0.10 ha lot with no landscape can't hold a residential, outdoor-heavy program.",
    "B": "Best city-landscape pairing (Prince's Island, Bow River) and 14 min average to the city, held back by a 0.30 ha lot.",
    "C": "Best urban ecology, but the anchor is in the floodway and no dry lot has been found.",
    "D": "Fish Creek PP at the door and fast road access; 52 min to West Bragg Creek ties F for the best city mountain time.",
    "F": "Ties L for first: reservoir shore and pathway at the door, surface parking to build on, 24 min average to city and YYC.",
    "E": "Far from the mountains (81 min) with thin ecology; no reason to prefer it after the reframe.",
    "G": "Fast to U of C, YYC and downtown with plenty of parking land, but little landscape at the door.",
    "I": "Best city time to the Kananaskis gateway (56 min) and a river edge, but slower to YYC and the land's availability is unknown.",
    "J": "Big school-reserve fields close to Spark, the Zoo and YYC; no landscape.",
    "K": "Same as J: fast to the city, room to build, no landscape.",
    "L": "Top rural: 16 min to West Bragg Creek trails, forest and the Elbow at the door, a hamlet next door; 49 min to the city.",
    "M": "Town servicing and neighbours plus a creek valley at the door; mid-way on both the city and the mountain drive.",
    "N": "Glenbow Ranch and the Bow valley next door with open land, but no services or community and a slow mountain drive.",
    "O": "Room and schools, but flat farmland with no landscape at the door.",
    "P": "Fastest to the Hwy 40 gateway (33 min) with open land and a creek valley, but no services or neighbours.",
    "Q": "Fast to Bragg Creek, but forest all round, little open ground and no services.",
}

# Fallback when Overpass (OSM) is unavailable for a zone: Esri-imagery and map-knowledge judgments, UNVERIFIED.
# (landscape, room, access, forest_share_1km_estimate, school_within_2km, community_within_4km, note)
IMAGERY = {
    "A": (1, None, 4, 0.0, True, True, "dense Beltline blocks; Lougheed House is a formal garden; no trail terrain"),
    "B": (4, None, 4, 0.05, True, True, "Prince's Island, the lagoon and Bow River pathway across 1 Ave; urban edge, not wild"),
    "C": (5, 3, 3, 0.2, True, True, "Bird Sanctuary riparian forest and Bow River; buildable land limited by flood mapping"),
    "D": (4, 3, 5, 0.15, True, True, "Fish Creek PP valley at the door; station-area parking and open land"),
    "E": (3, 3, 4, 0.0, True, True, "stormwater lake and manicured park; thin ecology"),
    "F": (4, 4, 5, 0.1, True, True, "Glenmore Reservoir shore and pathway, Weaselhead ~2 km; large surface parking in ring"),
    "G": (2, 4, 5, 0.0, True, True, "Nose Hill ~1 km across John Laurie Blvd; big surface parking in ring"),
    "I": (4, 3, 3, 0.15, True, True, "Bow River and lagoon edge, riverbank pathway; shoreline residential around it"),
    "J": (2, 4, 4, 0.0, True, True, "school-reserve playing fields; no natural terrain"),
    "K": (2, 4, 4, 0.0, True, True, "school-reserve playing fields; no natural terrain"),
    "L": (5, 2, 3, 0.6, True, True, "Elbow River ~400 m W, forest E, trails to Bragg Creek PP; open ground is a ~100 m meadow "
         "strip beside Hwy 22, the rest is forest to clear"),
    "M": (5, 4, 3, 0.15, True, True, "Jumping Pound Creek valley and escarpment in the ring; open grass terrace next to the "
         "subdivision"),
    "N": (5, 5, 4, 0.1, False, False, "hay field on Hwy 1A beside the Glenbow Ranch PP access road; Bow valley below"),
    "O": (1, 5, 4, 0.0, True, True, "flat cultivated field; schools and Park for All Seasons next door; no natural terrain"),
    "P": (4, 5, 4, 0.1, False, False, "rolling ranchland; Jumping Pound Creek's wooded valley ~300 m W"),
    "Q": (4, 2, 3, 0.7, False, True, "continuous foothill forest with one ranch meadow; Bragg Creek hamlet ~2.5 km S"),
}


def band(v, cuts):
    for s, c in cuts:
        if v <= c:
            return s
    return 1


def score_zone(zid, setting, rec):
    s, m = {}, {}
    dm = rec["drive_min"]
    mt = min(dm["kananaskis_hwy1_hwy40"], dm["west_bragg_creek_trailhead"])
    s["mountains"] = band(mt, TRAVEL_BANDS)
    m["mountains"] = {"min_to_nearer_gateway": mt, "min_to_hwy1_hwy40": dm["kananaskis_hwy1_hwy40"],
                      "min_to_west_bragg_creek": dm["west_bragg_creek_trailhead"]}
    cl = sum(dm[k] for k in CITY_CLUSTER) / len(CITY_CLUSTER)
    cv = (dm["yyc_airport"] + cl) / 2
    s["city"] = band(cv, TRAVEL_BANDS)
    m["city"] = {"min_to_yyc": dm["yyc_airport"], "mean_min_to_city_cluster": round(cl, 1),
                 "combined_min": round(cv, 1), **{f"min_to_{k}": dm[k] for k in CITY_CLUSTER}}

    if rec.get("osm_error"):      # OSM missing: imagery judgments, flagged unverified
        ls, rm, ac, ff, school, comm, note = IMAGERY[zid]
        src = {"source": "imagery judgment (Esri World Imagery) - UNVERIFIED, OSM/Overpass unavailable",
               "osm_error": rec["osm_error"], "note": note}
        s["landscape"] = ls; m["landscape"] = dict(src)
        if "parcel" in rec:
            a = rec["parcel"]["area_m2"]
            s["room"] = 1 if a < 2500 else 2 if a < 5000 else 3 if a < 8000 else 4 if a < 10000 else 5
            m["room"] = {"parcel_area_m2": a, "need_m2_approx": 10000}
        else:
            s["room"] = rm; m["room"] = dict(src)
        s["access"] = ac; m["access"] = dict(src)
        rec = dict(rec, forest_fraction_1km=ff, works_industry_within_5km=[],
                   schools_within_2km=["(imagery/map judgment)"] if school else [],
                   places_within_4km=["(imagery/map judgment)"] if comm else [])
        return finish(zid, setting, rec, s, m)

    untag = rec.get("cover_400m", {}).get("untagged", 0)
    if untag >= 0.5 and zid in IMAGERY:   # OSM land cover too sparse to trust (common on rural land)
        ls, rm, _ac, ff, _sc, _cm, note = IMAGERY[zid]
        src = {"source": f"imagery judgment - UNVERIFIED; OSM land cover only {1 - untag:.0%} tagged in the 400 m ring",
               "note": note, "trail_m_400m": rec["trail_m_400m"], "waterways_400m": rec["waterways_400m"]}
        s["landscape"] = ls; m["landscape"] = dict(src)
        s["room"] = rm; m["room"] = dict(src)
        rec = dict(rec, forest_fraction_1km=ff, land_cover_source="imagery")
        return roads_and_finish(zid, setting, rec, s, m)
    nat, nat1k = rec["natural_fraction_400m"], rec["natural_fraction_1km"]
    trails = rec["trail_m_400m"] + 0.5 * rec["track_m_400m"]
    lake = any(rec["cover_400m"].get(k, 0) > 0 for k in ("water",))
    pts = (2 if nat >= 0.6 else 1 if nat >= 0.3 else 0) + (1 if trails >= 2000 else 0) \
        + (1 if (rec["waterways_400m"] or lake) else 0) + (1 if nat1k >= 0.4 else 0)
    s["landscape"] = max(1, min(5, pts))
    m["landscape"] = {"natural_fraction_400m": nat, "natural_fraction_1km": nat1k, "trail_m_400m": rec["trail_m_400m"],
                      "track_m_400m": rec["track_m_400m"], "waterways_400m": rec["waterways_400m"],
                      "water_polygon_in_ring": lake, "named_parks_within_1km_ha": rec["named_parks_within_1km_ha"]}

    if "parcel" in rec:
        a = rec["parcel"]["area_m2"]
        s["room"] = 1 if a < 2500 else 2 if a < 5000 else 3 if a < 8000 else 4 if a < 10000 else 5
        m["room"] = {"parcel_area_m2": a, "need_m2_approx": 10000, "open_room_fraction_400m": rec["open_room_fraction_400m"]}
    else:
        o = rec["open_room_fraction_400m"]
        s["room"] = 5 if o >= 0.4 else 4 if o >= 0.25 else 3 if o >= 0.15 else 2 if o >= 0.07 else 1
        m["room"] = {"open_room_fraction_400m": o, "untagged_fraction_400m": rec["cover_400m"].get("untagged", 0),
                     "cover_400m": rec["cover_400m"]}

    return roads_and_finish(zid, setting, rec, s, m)


def roads_and_finish(zid, setting, rec, s, m):
    rank = {"motorway": 5, "trunk": 4, "primary": 4, "secondary": 4, "tertiary": 3}
    best = rec["best_road_within_400m"]
    nr = rec["nearest_major_road"]
    base = 4 if best and rank[best[0]] >= 4 else 3 if best or (nr and nr["m"] <= 1000 and rank[nr["class"]] >= 4) else 2
    nroads = len(rec["major_roads_within_2km"])
    s["access"] = max(1, min(5, base + (1 if nroads >= 3 else -1 if nroads <= 1 else 0)))
    m["access"] = {"best_road_within_400m": best[:2] if best else None, "nearest_major_road": nr,
                   "distinct_major_roads_within_2km": nroads, "major_roads_within_2km": rec["major_roads_within_2km"][:12]}
    return finish(zid, setting, rec, s, m)


def finish(zid, setting, rec, s, m):
    """Hazards, services and imagery overrides (shared by the OSM and the imagery-fallback paths)."""
    fl = rec["flood_fhip"]
    h = 5; notes = []
    at, near = fl["at_point"], fl["within_250m"]
    if "Floodway" in at:
        h -= 3; notes.append("floodway at anchor")
    elif any(z in at for z in ("Flood Fringe", "High Hazard Flood Fringe")):
        h -= 2; notes.append("flood fringe at anchor")
    elif at or any(z in near for z in ("Floodway", "Flood Fringe", "High Hazard Flood Fringe")):
        h -= 1; notes.append("protected fringe or 1:200/1:500 extent at anchor, or floodway/fringe within 250 m: "
                             + ", ".join(at or near))
    ff = rec["forest_fraction_1km"]
    if ff >= 0.4:
        h -= 2; notes.append("forest >=40% of 1 km ring (wildland-urban interface)")
    elif ff >= 0.15:
        h -= 1; notes.append("forest >=15% of 1 km ring")
    gas = [w for w in rec["works_industry_within_5km"] if any(k in w.lower() for k in ("gas plant", "sour gas", "refinery"))]
    if gas:
        h -= 1; notes.append("gas/heavy industry within 5 km: " + ", ".join(gas))
    s["hazards"] = max(1, h)
    m["hazards"] = {"flood_fhip": fl, "forest_fraction_1km": ff, "industry_within_5km": rec["works_industry_within_5km"][:8],
                    "deductions": notes}

    sv, note = SERVICING.get(zid, SERVICING.get(setting, (0, "open county land: well and on-site wastewater assumed")))
    sc = sv + (1 if rec["schools_within_2km"] else 0) + (1 if rec["places_within_4km"] or setting == "city" else 0)
    s["services"] = max(1, min(5, sc))
    m["services"] = {"servicing_points": sv, "servicing_note": note, "schools_within_2km": rec["schools_within_2km"][:6],
                     "places_within_4km": rec["places_within_4km"][:6]}

    formula = dict(s)
    over = {}
    for k, (v, why) in OVERRIDES.get(zid, {}).items():
        over[k] = {"formula_score": s[k], "score": v, "reason": why}
        s[k] = v
    return s, formula, over, m


def main():
    offline = "--offline" in sys.argv
    if offline and CACHE.exists():
        raw = json.loads(CACHE.read_text(encoding="utf-8"))
        for k, v in raw["dest"]["coords"].items():
            DEST[k] = tuple(v)
    else:
        raw = collect()
        CACHE.write_text(json.dumps(raw, indent=1), encoding="utf-8")
    weights = {c[0]: c[2] for c in CRITERIA}
    sites = []
    for zid, name, lat, lon, setting in ZONES:
        rec = raw["zones"][zid]
        s, formula, over, m = score_zone(zid, setting, rec)
        wt = sum(s[k] * weights[k] for k in s)
        sens = {"mountains_x3": wt + s["mountains"], "city_x3": wt + s["city"], "equal_weights_of_35": sum(s.values())}
        sites.append({"letter": zid, "name": name, "lat": lat, "lon": lon, "setting": setting,
                      "scores": s, "formula_scores": formula, "overrides": over,
                      "total_weighted": wt, "total_max": MAX_W, "total_unweighted_of_35": sum(s.values()),
                      "sensitivity": sens, "metrics": m, "is_in": rec.get("is_in"),
                      "osm_status": ("unavailable - imagery judgments used (unverified)" if rec.get("osm_error") else "ok, land cover from imagery (OSM too sparse)" if rec.get("cover_400m", {}).get("untagged", 0) >= 0.5 else "ok"),
                      "parcel": rec.get("parcel"), "ring_m": 400,
                      "google_maps": f"https://www.google.com/maps/@{lat},{lon},1200m/data=!3m1!1e3",
                      "why_it_ranks": WHY.get(zid, ""), "flags": EXTRA_FLAGS.get(zid, [])})
    tb = ["mountains", "city", "landscape"]
    sites.sort(key=lambda x: (-x["total_weighted"], -sum(x["scores"][k] for k in tb), -x["scores"]["hazards"]))
    for i, x in enumerate(sites, 1):
        x["rank"] = i
    out = {
        "title": "Cairn Youth Centre: Stage 1 zone scan, reframe (city and rural)",
        "date": "2026-09-29",
        "reframe": "Year-round residential youth centre for visiting domestic and international students; 32 beds "
                   "(4 nodes of 8, one node out camping at a time); academics (science, tech) and making; about 1/3 of the "
                   "program outdoors; summer 2 x 4-week sessions, rest of year 2-week sessions. Transit and low-income "
                   "reach dropped as criteria (instructor feedback 2026-09-28, Ben 2026-09-29).",
        "criteria": [{"key": k, "label": l, "weight": w, "rule": r} for k, l, w, r in CRITERIA],
        "total_max": MAX_W, "tie_break": "sum of Mountains + City + Landscape, then Hazards",
        "destinations": {k: list(v) for k, v in DEST.items()},
        "destination_notes": raw["dest"].get("west_bragg_creek_trailhead_source"),
        "sources": ["OSRM public demo router, table service (free-flow, off-peak; no traffic, no winter conditions)",
                    "OpenStreetMap via Overpass API (land cover, trails, water, parks, parking, roads, schools, places)",
                    "Alberta Flood Hazard Identification Program, geospatial.alberta.ca FAMA map service (layers 1, 13)",
                    "City of Calgary Open Data parcels 4bsw-nn7w (A, B lot areas)",
                    "Esri World Imagery (visual check of anchors; credit Esri, Maxar, Earthstar Geographics, GIS User Community)"],
        "caveats": ["Drive times are free-flow; add 20-40% for peak or winter.",
                    "OSM land cover is incomplete, especially rural; 'untagged' share is reported per site.",
                    "FHIP covers studied reaches only; 'no hit' on an unstudied creek is unverified.",
                    "Wildfire uses forest share as a proxy; no provincial wildfire hazard layer was queried.",
                    "Servicing for rural zones is assumed from jurisdiction, not confirmed with the county or utility.",
                    "Zone anchors are dots + 400 m rings, not parcels; land ownership and land use are unverified."],
        "shortlist": SHORTLIST,
        "sensitivity_note": "Mountains x3 puts L first (43), F second (40); City x3 puts F and G joint first (42), D third (41). Equal weights (/35): F and G 28, D 27, L and M 26. L and F are top-two at the base weights and under Mountains x3; under City x3 the city sites lead.",
        "sites": sites,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for x in sites:
        print(x["rank"], x["letter"], x["setting"], x["scores"], x["total_weighted"], "/", MAX_W)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

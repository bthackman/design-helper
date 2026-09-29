"""Stage 2 four-site study for the RAIC 400 Cairn Youth Centre, 2026-09-29.

Ben's four picks (urban -> rural): C Inglewood, F Glenmore Landing (forest north of the retail), I Loch McKinnon /
Shriners (Bowness), N Glenbow Ranch (Park Foundation building). This script collects the facts, computes the
metrics and scores, draws the Esri clips and sun sections, and writes a self-contained JSON for the canvas.

Steps (each cached in _cache_stage2_raw.json so a rerun is offline unless --fresh):
  collect  : OSRM drive table; Alberta FHIP flood; City of Calgary open data (land use, parcels, parks, natural areas,
             regulatory flood map, NEF contours, land cover, transit stops); NRCan CDEM/CDSM elevation (spot grid,
             horizon rays); OpenStreetMap via Overpass (roads, rail, runways, amenities, nuisances, footprints);
             ECCC 1981-2010 climate normals (Calgary Int'l A); ERA5 hourly wind via Open-Meteo archive (2015-2024).
  figures  : Esri World Imagery clips (dot + 400 m ring + footprint) -> img/stage2_<id>.jpg;
             proportional winter/summer sun sections -> ../diagrams/stage2_sun_<id>.png
  build    : scores, envelope utilization, narrative -> stage2_2026-09-29.json
Usage: python stage2_scan.py [--fresh] [--no-figures]
Sources are free public services; every number in the JSON carries its source. Unverified items are flagged.
"""
import json, math, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import zone_scan as zs                      # reuse Stage 1 helpers (Local, pip, km, band, TRAVEL_BANDS, DEST)

OUT = HERE / "stage2_2026-09-29.json"
CACHE = HERE / "_cache_stage2_raw.json"
IMG = HERE / "img"
DIAG = HERE.parent / "diagrams"
UA = {"User-Agent": "RAIC400-student-site-search"}
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]
FHIP = zs.FHIP
SODA = "https://data.calgary.ca/resource/{}.json"
CDEM = "https://geogratis.gc.ca/services/elevation/{}/profile"
CDEM_PT = "https://geogratis.gc.ca/services/elevation/{}/altitude"

# ---------------------------------------------------------------- the four anchors (see stage2_narrative for why)
SITES = [
    {"id": "C", "name": "Inglewood: Bird Sanctuary entrance (Nature Centre parking lot)", "setting": "city",
     "lat": 51.03070, "lon": -114.01060, "stage1_anchor": (51.027895, -114.006957),
     "footprint": {"kind": "osm_way", "query": 'way(around:40,51.03052,-114.01056)["amenity"="parking"];',
                   "label": "Nature Centre surface lot (OSM)"},
     "parcel_pt": (51.03052, -114.01056), "dry_grid_step": 20},
    {"id": "F", "name": "Glenmore Landing: forest north of the retail (South Glenmore Park)", "setting": "city",
     "lat": None, "lon": None, "stage1_anchor": (50.9737, -114.097874),
     "footprint": {"kind": "osm_ids", "ids": [512148398, 1425733538], "label": "forest patch (OSM natural=wood)"},
     "parcel_pt": None, "dry_grid_step": 40},
    {"id": "I", "name": "Loch McKinnon: Al Azhar Shriners' land, open field NW of the Shrine Centre", "setting": "city",
     "lat": 51.10180, "lon": -114.23950, "stage1_anchor": (51.1009, -114.2384),
     "footprint": {"kind": "city_parcel", "pt": (51.1018, -114.2395), "label": "5225 101 St NW parcel (City open data)"},
     "parcel_pt": (51.1018, -114.2395), "dry_grid_step": 50},
    {"id": "N", "name": "Glenbow Ranch: ranch house at the end of Glenbow Road (park + Foundation office)", "setting": "rural",
     "lat": 51.16697, "lon": -114.39296, "stage1_anchor": (51.1750, -114.3650),
     "footprint": {"kind": "osm_way", "query": 'way(around:25,51.16697,-114.39296)["building"];',
                   "label": "ranch house / 'Information Centre' footprint (OSM)"},
     "parcel_pt": None, "dry_grid_step": None},
]
YYC_BBOX = (51.09, -114.06, 51.16, -113.96)


# ---------------------------------------------------------------- small helpers
def get(url, params=None, timeout=90, tries=3):
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if k == tries - 1:
                raise
            time.sleep(3 + 5 * k)


def overpass(q):
    last = None
    for rnd in range(1):
        for u in OVERPASS:
            try:
                r = requests.post(u, data={"data": q}, headers=UA, timeout=100)
                if r.status_code == 200 and r.text.lstrip().startswith("{"):
                    return r.json()["elements"]
                last = f"{u} {r.status_code}"
            except requests.RequestException as e:
                last = f"{u} {str(e)[:80]}"
            time.sleep(8)
    raise RuntimeError(f"Overpass failed: {last}")


def soda_pt(ds, col, lat, lon, limit=10):
    return get(SODA.format(ds), {"$where": f"intersects({col}, 'POINT ({lon} {lat})')", "$limit": limit}, 60)


def circle_wkt(lat, lon, r, n=24):
    kx, ky = 111320 * math.cos(math.radians(lat)), 111320
    pts = [(lon + r * math.cos(2 * math.pi * i / n) / kx, lat + r * math.sin(2 * math.pi * i / n) / ky) for i in range(n)]
    pts.append(pts[0])
    return "POLYGON ((" + ", ".join(f"{x:.7f} {y:.7f}" for x, y in pts) + "))"


def soda_circle(ds, col, lat, lon, r, limit=200, select=None):
    p = {"$where": f"intersects({col}, '{circle_wkt(lat, lon, r)}')", "$limit": limit}
    if select:
        p["$select"] = select
    return get(SODA.format(ds), p, 120)


def fhip(lat, lon, d=0):
    p = {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": "Multi_Zone,RiverName", "returnGeometry": "false", "f": "json"}
    if d:
        p.update(distance=d, units="esriSRUnit_Meter")
    j = get(FHIP.format(1), p, 60)
    return sorted({f["attributes"]["Multi_Zone"] for f in j.get("features", [])})


def offset(lat, lon, dist, az):
    """Point at `dist` m on azimuth `az` (deg from north)."""
    dy = dist * math.cos(math.radians(az)) / 111320
    dx = dist * math.sin(math.radians(az)) / (111320 * math.cos(math.radians(lat)))
    return lat + dy, lon + dx


def profile(model, lat, lon, dist, az, steps):
    la2, lo2 = offset(lat, lon, dist, az)
    j = get(CDEM.format(model), {"path": f"LINESTRING({lon} {lat},{lo2} {la2})", "steps": steps}, 90)
    return [p["altitude"] for p in j]


def ring_area(ring_ll, lat0, lon0):
    loc = zs.Local(lat0, lon0)
    xy = [loc.xy(la, lo) for la, lo in ring_ll]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2


def centroid(ring_ll):
    lat0, lon0 = ring_ll[0]
    loc = zs.Local(lat0, lon0)
    xy = [loc.xy(la, lo) for la, lo in ring_ll]
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]):
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    a /= 2
    cx /= 6 * a; cy /= 6 * a
    return lat0 + cy / loc.ky, lon0 + cx / loc.kx, abs(a)


def mp_rings(geom):
    """Outer rings (lat, lon) of a GeoJSON (Multi)Polygon."""
    if geom["type"] == "Polygon":
        polys = [geom["coordinates"]]
    else:
        polys = geom["coordinates"]
    return [[(c[1], c[0]) for c in p[0]] for p in polys]


# ---------------------------------------------------------------- collection
_RAW = {}


def checkpoint(step, sid):
    CACHE.write_text(json.dumps(_RAW, indent=0), encoding="utf-8")
    print(f"  {sid} {step} {time.strftime('%H:%M:%S')}", flush=True)


def collect_site(s, raw):
    sid = s["id"]
    rec = raw["sites"].setdefault(sid, {})
    lat, lon = s["lat"], s["lon"]

    # footprint first (F's anchor is the footprint centroid)
    if "footprint" not in rec:
      try:
        fp = s["footprint"]
        if fp["kind"] == "osm_ids":
            els = overpass(f"[out:json][timeout:60];way(id:{','.join(map(str, fp['ids']))});out tags geom;")
            rings = [[(p["lat"], p["lon"]) for p in e["geometry"]] for e in els]
        elif fp["kind"] == "osm_way":
            els = overpass(f"[out:json][timeout:60];{fp['query']}out tags geom;")
            els = sorted(els, key=lambda e: len(e.get("geometry", [])), reverse=True)[:1]
            rings = [[(p["lat"], p["lon"]) for p in e["geometry"]] for e in els]
        else:
            rows = soda_pt("4bsw-nn7w", "multipolygon", *fp["pt"])
            big = max(rows, key=lambda r: float(r["land_size_sm"]))
            g = big["multipolygon"] if isinstance(big["multipolygon"], dict) else json.loads(big["multipolygon"].replace("'", '"'))
            rings = mp_rings(g)
            els = [{"tags": {k: big.get(k) for k in ("address", "land_use_designation", "land_size_sm", "assessment_class_description", "sub_property_use", "roll_number")}}]
        rec["footprint"] = {"label": fp["label"], "rings": rings, "tags": [e.get("tags", {}) for e in els],
                            "area_m2": round(sum(ring_area(r, *r[0]) for r in rings))}
        checkpoint("footprint", sid)
      except Exception as ex:
        print("  footprint failed:", str(ex)[:120], flush=True)
    if lat is None and "footprint" not in rec:
        lat, lon = 50.9768, -114.0978      # fallback: forest centre read off the imagery
    if lat is None:
        # area-weighted centroid of the footprint rings
        cs = [centroid(r) for r in rec["footprint"]["rings"]]
        A = sum(c[2] for c in cs)
        lat = round(sum(c[0] * c[2] for c in cs) / A, 5)
        lon = round(sum(c[1] * c[2] for c in cs) / A, 5)
    s["lat"], s["lon"] = lat, lon
    rec["anchor"] = (lat, lon)

    # flood (Alberta FHIP layer 1)
    if "fhip" not in rec:
        rec["fhip"] = {"at_point": fhip(lat, lon), "within_50m": fhip(lat, lon, 50), "within_100m": fhip(lat, lon, 100),
                       "within_250m": fhip(lat, lon, 250)}
        checkpoint("fhip", sid)

    # City of Calgary open data
    if s["setting"] == "city" and "city" not in rec:
        c = {}
        c["land_use"] = [(x.get("lu_code"), x.get("description"), x.get("lu_bylaw")) for x in soda_pt("qe6k-p9nh", "multipolygon", lat, lon)]
        pa = soda_pt("4bsw-nn7w", "multipolygon", lat, lon)
        c["parcels"] = [{k: x.get(k) for k in ("address", "land_use_designation", "land_size_sm", "assessment_class_description",
                                                 "sub_property_use", "comm_name", "roll_number")} for x in pa]
        c["parks"] = [(x.get("site_name"), x.get("planning_category"), x.get("type_description"), x.get("steward")) for x in soda_pt("kami-qbfh", "the_geom", lat, lon)]
        c["natural_areas"] = [x.get("asset_type") for x in soda_pt("szzc-mugz", "multipolygon", lat, lon)]
        c["city_flood_at"] = [x.get("description") for x in soda_pt("tp6q-x2v7", "multipolygon", lat, lon)]
        c["city_flood_100m"] = sorted({x.get("description") for x in soda_circle("tp6q-x2v7", "multipolygon", lat, lon, 100, select="description")})
        c["city_flood_250m"] = sorted({x.get("description") for x in soda_circle("tp6q-x2v7", "multipolygon", lat, lon, 250, select="description")})
        c["nef_at"] = [x.get("dblevel") for x in soda_pt("g5qu-w8fb", "multipolygon", lat, lon)]
        c["nef_within_1km"] = sorted({x.get("dblevel") for x in soda_circle("g5qu-w8fb", "multipolygon", lat, lon, 1000, select="dblevel")})
        c["land_cover_at"] = [x.get("lc_cat") for x in soda_pt("as2i-6z3n", "the_geom", lat, lon)]
        # transit stops (context only)
        st = get(SODA.format("muzh-c9qc"), {"$where": f"within_circle(point, {lat}, {lon}, 800) AND status='ACTIVE'", "$limit": 200}, 60)
        loc = zs.Local(lat, lon)
        d = sorted((math.hypot(*loc.xy(x["point"]["coordinates"][1], x["point"]["coordinates"][0])), x["stop_name"]) for x in st)
        c["transit_stops_800m"] = len(d)
        c["transit_stops_400m"] = sum(1 for x in d if x[0] <= 400)
        c["nearest_stop"] = {"name": d[0][1], "m": round(d[0][0])} if d else None
        rec["city"] = c
        checkpoint("city", sid)

    # Calgary land cover sample for the 400 m and 1 km rings (city sites): grid of points, one query per polygon batch
    if s["setting"] == "city" and "land_cover" not in rec:
        rec["land_cover"] = land_cover_rings(lat, lon)
        checkpoint("land_cover", sid)

    # dry buildable area: sample the footprint / parcel on a grid against FHIP (floodway/fringe) and the City flood map
    if s["dry_grid_step"] and "dry" not in rec and (s["id"] == "C" or "footprint" in rec):
        rec["dry"] = dry_grid(s, rec)
        checkpoint("dry", sid)

    # elevation: CDEM spot grid (+-150 m cross), slope; horizon rays (CDEM terrain, CDSM surface incl. canopy)
    if "elev" not in rec:
        e = {"anchor_cdem": get(CDEM_PT.format("cdem"), {"lat": lat, "lon": lon})["altitude"],
             "anchor_cdsm": get(CDEM_PT.format("cdsm"), {"lat": lat, "lon": lon})["altitude"]}
        for az, key in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            e[f"prof_{key}_300m"] = profile("cdem", lat, lon, 300, az, 12)
        e["horizon"] = {}
        for model in ("cdem", "cdsm"):
            e["horizon"][model] = {}
            for az in range(90, 271, 15):
                e["horizon"][model][az] = profile(model, lat, lon, 4000, az, 80)   # 50 m steps
        e["near_south_cdsm_400m"] = profile("cdsm", lat, lon, 400, 180, 40)       # 10 m steps
        e["near_south_cdem_400m"] = profile("cdem", lat, lon, 400, 180, 40)
        rec["elev"] = e
        checkpoint("elev", sid)

    # OSM: roads/rail within 3 km, trails/water within 400 m, amenities/nuisances within 2 km
    if "osm_lines" not in rec:
      try:
        rec["osm_lines"] = overpass(f"""[out:json][timeout:120];
          ( way(around:3000,{lat},{lon})["highway"~"^(motorway|trunk|primary|secondary|tertiary|motorway_link|trunk_link)$"];
            way(around:3000,{lat},{lon})["railway"~"^(rail|light_rail)$"];
            way(around:400,{lat},{lon})["highway"~"^(path|footway|track|bridleway|cycleway)$"];
            way(around:400,{lat},{lon})["waterway"~"^(river|stream|canal)$"];
            way(around:2000,{lat},{lon})["power"="line"]; ); out tags geom;""")
        checkpoint("osm_lines", sid)
      except Exception as ex:
        print("  osm_lines failed:", str(ex)[:120], flush=True)
      time.sleep(2)
    if "osm_pois" not in rec:
      try:
        rec["osm_pois"] = overpass(f"""[out:json][timeout:120];
          ( nwr(around:2000,{lat},{lon})["amenity"~"^(school|community_centre|library|hospital|clinic|pharmacy|place_of_worship|fire_station|police|kindergarten|university|college)$"];
            nwr(around:2000,{lat},{lon})["shop"~"^(supermarket|convenience|outdoor|sports|hardware)$"];
            nwr(around:2000,{lat},{lon})["leisure"~"^(park|nature_reserve|sports_centre|swimming_pool|golf_course|stadium|ice_rink|horse_riding|marina)$"]["name"];
            nwr(around:2000,{lat},{lon})["tourism"~"^(museum|zoo|attraction|theme_park|camp_site|information)$"]["name"];
            nwr(around:2000,{lat},{lon})["landuse"~"^(industrial|railway|landfill|quarry)$"];
            nwr(around:2000,{lat},{lon})["man_made"~"^(wastewater_plant|water_works|works|pumping_station)$"];
            nwr(around:2000,{lat},{lon})["power"~"^(substation|plant)$"];
            nwr(around:2000,{lat},{lon})["aeroway"~"^(aerodrome|helipad)$"];
            nwr(around:5000,{lat},{lon})["man_made"~"^(works)$"]["product"~"gas"];
            node(around:4000,{lat},{lon})["place"~"^(city|town|village|hamlet|suburb|neighbourhood)$"]; ); out tags center;""")
        checkpoint("osm_pois", sid)
      except Exception as ex:
        print("  osm_pois failed:", str(ex)[:120], flush=True)
    return rec


def land_cover_rings(lat, lon):
    """Calgary Citywide Land Cover (as2i-6z3n): fetch polygons within 1 km, sample 400 m and 1 km discs locally."""
    rows = []
    off = 0
    while True:
        p = {"$where": f"intersects(the_geom, '{circle_wkt(lat, lon, 1000, 32)}')", "$select": "lc_cat, the_geom",
             "$limit": 2000, "$offset": off}
        b = get(SODA.format("as2i-6z3n"), p, 180)
        rows += b
        if len(b) < 2000:
            break
        off += 2000
    loc = zs.Local(lat, lon)
    polys = []
    for r in rows:
        g = r["the_geom"]
        for ring in mp_rings(g):
            xy = [loc.xy(a, b) for a, b in ring]
            xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
            polys.append((r["lc_cat"], xy, (min(xs), min(ys), max(xs), max(ys))))

    def disc(R, step):
        cnt = {}
        n = 0
        for x in range(-R, R + 1, step):
            for y in range(-R, R + 1, step):
                if x * x + y * y > R * R:
                    continue
                n += 1
                hit = "unclassified"
                for cat, xy, bb in polys:
                    if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and zs.pip(x, y, xy):
                        hit = cat; break
                cnt[hit] = cnt.get(hit, 0) + 1
        return {k: round(v / n, 3) for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])}
    return {"source": "City of Calgary Citywide Land Cover (as2i-6z3n)", "ring_400m": disc(400, 20), "ring_1km": disc(1000, 50),
            "polygons": len(rows)}


def dry_grid(s, rec):
    """Share of the footprint/parcel outside FHIP floodway/fringe AND outside the City regulatory flood map."""
    step = s["dry_grid_step"]
    if s["id"] == "C":   # C: test the whole Nature Centre parcel, not just the lot
        rows = soda_pt("4bsw-nn7w", "multipolygon", *s["parcel_pt"])
        g = rows[0]["multipolygon"]
        rings = mp_rings(g)
        label = f"parcel {rows[0]['address']}"
    elif s["id"] == "F":
        rings = rec["footprint"]["rings"]; label = "forest patch"
    else:
        rings = rec["footprint"]["rings"]; label = "Shriners' parcel"
    lat0, lon0 = rings[0][0]
    loc = zs.Local(lat0, lon0)
    pts = []
    for ring in rings:
        xy = [loc.xy(a, b) for a, b in ring]
        xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
        x = min(xs)
        while x <= max(xs):
            y = min(ys)
            while y <= max(ys):
                if zs.pip(x, y, xy):
                    pts.append((lat0 + y / loc.ky, lon0 + x / loc.kx))
                y += step
            x += step

    def one(p):
        la, lo = p
        f = fhip(la, lo)
        cty = [x.get("description") for x in soda_pt("tp6q-x2v7", "multipolygon", la, lo)] if s["setting"] == "city" else []
        return {"lat": round(la, 6), "lon": round(lo, 6), "fhip": f, "city": cty}
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, pts))
    bad = {"Floodway", "Flood Fringe", "High Hazard Flood Fringe"}
    dry = [r for r in res if not (set(r["fhip"]) & bad) and not (set(r["city"]) & {"Floodway", "Flood Fringe"})]
    clear = [r for r in dry if not r["fhip"] and not r["city"]]
    cell = step * step
    return {"tested": label, "grid_m": step, "points": len(res), "area_m2_sampled": len(res) * cell,
            "dry_m2": len(dry) * cell, "dry_and_clear_of_1in200_1in500_m2": len(clear) * cell, "samples": res}


def collect(fresh=False):
    raw = _RAW
    raw["sites"] = {}
    if CACHE.exists() and not fresh:
        raw.update(json.loads(CACHE.read_text(encoding="utf-8")))
    for s in SITES:
        print("collect", s["id"], flush=True)
        try:
            collect_site(s, raw)
        finally:
            CACHE.write_text(json.dumps(raw, indent=0), encoding="utf-8")
    # OSRM drive table (free-flow)
    scan1 = json.loads((HERE / "scan_2026-09-29_reframe.json").read_text(encoding="utf-8"))
    dest = {k: tuple(v) for k, v in scan1["destinations"].items()}
    if "osrm" not in raw or fresh:
        names = list(dest)
        coords = [(s["lon"], s["lat"]) for s in SITES] + [(dest[n][1], dest[n][0]) for n in names]
        url = zs.OSRM + ";".join(f"{a},{b}" for a, b in coords)
        j = get(url, {"sources": ";".join(str(i) for i in range(len(SITES))),
                      "destinations": ";".join(str(len(SITES) + i) for i in range(len(names))),
                      "annotations": "duration,distance"}, 120)
        raw["osrm"] = {"dest": dest, "snap": {s["id"]: {"m": round(j["sources"][i]["distance"]), "name": j["sources"][i].get("name")}
                                              for i, s in enumerate(SITES)},
                       "min": {s["id"]: {n: round(j["durations"][i][k] / 60) for k, n in enumerate(names)} for i, s in enumerate(SITES)},
                       "km": {s["id"]: {n: round(j["distances"][i][k] / 1000, 1) for k, n in enumerate(names)} for i, s in enumerate(SITES)}}
    # YYC runways
    if "runways" not in raw:
        b = YYC_BBOX
        try:
            raw["runways"] = overpass(f'[out:json][timeout:60];way({b[0]},{b[1]},{b[2]},{b[3]})["aeroway"="runway"];out tags geom;')
        except Exception as ex:
            print("  runways failed:", str(ex)[:120], flush=True)
    # ECCC climate normals, Calgary Int'l A (3031093), 1981-2010
    if "normals" not in raw:
        j = get("https://api.weather.gc.ca/collections/climate-normals/items",
                {"CLIMATE_IDENTIFIER": "3031093", "f": "json", "limit": 2000}, 120)
        keep = {1: "mean_temp_c", 5: "mean_max_c", 8: "mean_min_c", 54: "snowfall_cm", 90: "wind_speed_kmh", 91: "wind_dir_deg",
                100: "days_hourly_wind_gt_40kmh", 141: "days_wind_ge_52kmh", 49: "days_windchill_lt_m20", 89: "days_blowing_snow"}
        n = {}
        for f in j["features"]:
            p = f["properties"]
            if p["NORMAL_ID"] in keep:
                n.setdefault(keep[p["NORMAL_ID"]], {})[p["MONTH"]] = p["VALUE"]
        raw["normals"] = {"station": "CALGARY INT'L A (Climate ID 3031093)", "period": "1981-2010", "values": n}
    # ERA5 hourly wind per site (Open-Meteo archive), 2015-2024
    raw.setdefault("era5", {})
    for s in SITES:
        if s["id"] in raw["era5"]:
            continue
        j = get("https://archive-api.open-meteo.com/v1/archive",
                {"latitude": s["lat"], "longitude": s["lon"], "start_date": "2015-01-01", "end_date": "2024-12-31",
                 "hourly": "wind_speed_10m,wind_direction_10m,temperature_2m", "timezone": "America/Edmonton"}, 300)
        raw["era5"][s["id"]] = wind_summary(j)
        CACHE.write_text(json.dumps(raw, indent=0), encoding="utf-8")
        time.sleep(2)
    CACHE.write_text(json.dumps(raw, indent=0), encoding="utf-8")
    return raw


def wind_summary(j):
    h = j["hourly"]
    secs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    seasons = {"DJF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
    out = {"grid_lat": j.get("latitude"), "grid_lon": j.get("longitude"), "grid_elev_m": j.get("elevation"), "seasons": {}}
    days = {}
    for t, sp, di, te in zip(h["time"], h["wind_speed_10m"], h["wind_direction_10m"], h["temperature_2m"]):
        if sp is None or di is None:
            continue
        m = int(t[5:7])
        for k, ms in seasons.items():
            if m in ms:
                d = out["seasons"].setdefault(k, {"n": 0, "speed_sum": 0.0, "sectors": {x: 0 for x in secs}, "calm_lt_5": 0, "strong_ge_30": 0})
                d["n"] += 1; d["speed_sum"] += sp
                d["sectors"][secs[int(((di + 22.5) % 360) // 45)]] += 1
                d["calm_lt_5"] += sp < 5
                d["strong_ge_30"] += sp >= 30
        day = t[:10]
        dd = days.setdefault(day, {"tmax": -99, "w": 0, "n": 0, "m": m})
        dd["tmax"] = max(dd["tmax"], te if te is not None else -99)
        dd["n"] += 1
        dd["w"] += 1 if (di is not None and 200 <= di <= 290 and sp >= 15) else 0
    for k, d in out["seasons"].items():
        n = d.pop("n")
        d["mean_speed_kmh"] = round(d.pop("speed_sum") / n, 1)
        d["sectors_pct"] = {x: round(100 * v / n, 1) for x, v in d.pop("sectors").items()}
        d["calm_lt_5_pct"] = round(100 * d.pop("calm_lt_5") / n, 1)
        d["strong_ge_30_pct"] = round(100 * d.pop("strong_ge_30") / n, 1)
    winter = [d for d in days.values() if d["m"] in (12, 1, 2)]
    chin = [d for d in winter if d["tmax"] >= 5 and d["w"] >= 6]
    out["winter_warm_westerly_days_per_winter"] = round(len(chin) / 10, 1)
    out["chinook_proxy_rule"] = "Dec-Feb days with ERA5 max temperature >= 5 C and >= 6 h of 200-290 deg wind >= 15 km/h; 10 winters"
    return out


# ---------------------------------------------------------------- metrics
def sun_geometry(lat):
    out = {}
    for key, dec in (("winter_solstice", -23.44), ("equinox", 0.0), ("summer_solstice", 23.44)):
        noon = 90 - lat + dec
        cosH = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
        H0 = math.degrees(math.acos(max(-1, min(1, cosH))))
        az_rise = math.degrees(math.acos(math.sin(math.radians(dec)) / math.cos(math.radians(lat))))
        out[key] = {"declination": dec, "noon_altitude_deg": round(noon, 1), "day_length_h": round(2 * H0 / 15, 1),
                    "sunrise_azimuth_deg": round(az_rise), "sunset_azimuth_deg": round(360 - az_rise),
                    "path": sun_path(lat, dec)}
    return out


def sun_path(lat, dec):
    pts = []
    for hh in range(-8 * 4, 8 * 4 + 1):
        H = hh * 3.75   # 15 min steps, hour angle deg
        la, d, h = map(math.radians, (lat, dec, H))
        alt = math.asin(math.sin(la) * math.sin(d) + math.cos(la) * math.cos(d) * math.cos(h))
        if alt <= 0:
            continue
        az = math.degrees(math.atan2(math.sin(h), math.cos(h) * math.sin(la) - math.tan(d) * math.cos(la))) + 180
        pts.append((round(H / 15, 2), round(math.degrees(alt), 1), round(az % 360, 1)))
    return pts


def horizon_angles(prof, z0, eye=1.6, step=50.0):
    best, at = -90.0, None
    for i, z in enumerate(prof[1:], 1):
        a = math.degrees(math.atan2(z - (z0 + eye), i * step))
        if a > best:
            best, at = a, i * step
    return round(best, 1), at


def acoustic(rec, lat, lon):
    loc = zs.Local(lat, lon)
    roads, rail, power = {}, {}, []
    for e in rec["osm_lines"]:
        t = e.get("tags", {})
        g = e.get("geometry") or []
        if not g:
            continue
        d = zs.min_dist(g, loc)
        hw, rw = t.get("highway"), t.get("railway")
        if hw in ("motorway", "trunk", "primary", "secondary", "tertiary", "motorway_link", "trunk_link"):
            nm = t.get("name") or t.get("ref") or f"unnamed {hw}"
            cls = hw.replace("_link", "")
            if nm not in roads or d < roads[nm]["m"]:
                roads[nm] = {"class": cls, "m": round(d), "ref": t.get("ref"), "bearing": bearing_to(g, loc)}
        elif rw:
            nm = t.get("name") or t.get("operator") or rw
            if nm not in rail or d < rail[nm]["m"]:
                rail[nm] = {"type": rw, "operator": t.get("operator"), "m": round(d), "bearing": bearing_to(g, loc)}
        elif t.get("power") == "line":
            power.append(round(d))
    roads = dict(sorted(roads.items(), key=lambda kv: kv[1]["m"]))
    rail = dict(sorted(rail.items(), key=lambda kv: kv[1]["m"]))
    return {"roads_within_3km": roads, "rail_within_3km": rail, "nearest_power_line_m": min(power) if power else None}


def bearing_to(g, loc):
    x, y = min((loc.xy(p["lat"], p["lon"]) for p in g), key=lambda q: math.hypot(*q))
    b = (math.degrees(math.atan2(x, y)) + 360) % 360
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][int(((b + 22.5) % 360) // 45)]


def runway_exposure(runways, lat, lon):
    """For each YYC runway end, lateral offset of the site from the extended centreline and distance from threshold;
    height on a 3-degree glide path is indicative only (real procedures vary)."""
    out = []
    for e in runways:
        g = e.get("geometry") or []
        if len(g) < 2:
            continue
        ref = e.get("tags", {}).get("ref", "?")
        a, b = g[0], g[-1]
        loc = zs.Local(a["lat"], a["lon"])
        bx, by = loc.xy(b["lat"], b["lon"])
        L = math.hypot(bx, by)
        ux, uy = bx / L, by / L
        sx, sy = loc.xy(lat, lon)
        for end, (ex, ey), sign in (("a", (0, 0), -1), ("b", (bx, by), 1)):
            # extension beyond this end: direction outward = sign * u
            dx, dy = sx - ex, sy - ey
            along = (dx * ux + dy * uy) * sign
            lateral = abs(dx * uy - dy * ux)
            if along > 0 and along < 20000:
                ends = ref.split("/")
                name = ends[0] if end == "a" else ends[-1]
                out.append({"runway": ref, "approach_to_end": name, "km_from_threshold": round(along / 1000, 1),
                            "lateral_offset_m": round(lateral), "glidepath_height_m_3deg": round(along * math.tan(math.radians(3)))})
    return sorted(out, key=lambda r: r["lateral_offset_m"])


def pois(rec, lat, lon):
    loc = zs.Local(lat, lon)
    out = []
    for e in rec["osm_pois"]:
        t = e.get("tags", {})
        c = e.get("center") or ({"lat": e.get("lat"), "lon": e.get("lon")} if "lat" in e else None)
        if not c:
            continue
        d = math.hypot(*loc.xy(c["lat"], c["lon"]))
        kind = next((f"{k}={t[k]}" for k in ("amenity", "shop", "leisure", "tourism", "landuse", "man_made", "power", "aeroway", "place") if k in t), "?")
        out.append({"name": t.get("name") or t.get("operator") or "", "kind": kind, "m": round(d)})
    return sorted(out, key=lambda r: r["m"])


def landscape_metrics(rec, lat, lon, setting):
    loc = zs.Local(lat, lon)
    trail = track = 0.0
    water = set()
    for e in rec["osm_lines"]:
        t = e.get("tags", {}); g = e.get("geometry") or []
        if not g:
            continue
        hw, ww = t.get("highway"), t.get("waterway")
        if hw in ("path", "footway", "bridleway", "cycleway") and t.get("footway") != "sidewalk":
            trail += zs.line_len_in(g, loc, 400)
        elif hw == "track":
            track += zs.line_len_in(g, loc, 400)
        elif ww and zs.min_dist(g, loc) <= 400:
            water.add(t.get("name", f"unnamed {ww}"))
    return {"trail_m_400m": round(trail), "track_m_400m": round(track), "waterways_400m": sorted(water)}


NATURAL_LC = ("Grassland", "Forest", "Shrubland", "Wetland", "Stream/Rivers", "Water", "Riparian", "Lakes", "Natural", "Reservoir")


def natural_share(dist):
    return round(sum(v for k, v in dist.items() if any(n.lower() in k.lower() for n in NATURAL_LC)), 3)


# ---------------------------------------------------------------- build
def build(raw):
    import stage2_narrative as NARR   # per-site narrative written after reading the collected data
    sites_out = []
    weights = {c[0]: c[2] for c in zs.CRITERIA}
    for s in SITES:
        sid = s["id"]
        rec = raw["sites"][sid]
        lat, lon = rec["anchor"]
        dm = raw["osrm"]["min"][sid]
        m = {}
        mt = min(dm["kananaskis_hwy1_hwy40"], dm["west_bragg_creek_trailhead"])
        cl = sum(dm[k] for k in zs.CITY_CLUSTER) / 4
        cv = (dm["yyc_airport"] + cl) / 2
        m["drive"] = {"minutes_free_flow": dm, "km": raw["osrm"]["km"][sid], "osrm_snap": raw["osrm"]["snap"][sid],
                      "nearer_mountain_gateway_min": mt, "city_cluster_mean_min": round(cl, 1), "city_combined_min": round(cv, 1)}
        e = rec["elev"]
        slopes = {}
        for k in ("N", "E", "S", "W"):
            p = e[f"prof_{k}_300m"]
            slopes[k] = {"drop_to_300m_m": round(p[-1] - p[0], 1), "grade_pct_first_100m": round(100 * (p[4] - p[0]) / 100, 1),
                         "profile_25m": p}
        hz = {}
        for model in ("cdem",):   # CDSM read ~5 m below CDEM on flat open ground at every site (datum/vintage offset): not used
            z0 = e["anchor_cdem"] if model == "cdem" else e["anchor_cdem"]   # eye at ground (bare earth) + 1.6 m
            hz[model] = {int(az): horizon_angles(p, z0) for az, p in e["horizon"][model].items()}
        m["elevation"] = {"source": "NRCan CDEM (bare-earth DEM, concept grade, too coarse for micro-grading), geogratis API",
                          "anchor_cdem_m": e["anchor_cdem"],
                          "cdsm_note": "CDSM (surface model) sampled but not used: it reads ~5 m below CDEM on open ground here",
                          "profiles_300m": slopes, "horizon_deg_by_azimuth": hz}
        sun = sun_geometry(lat)
        # sun hours blocked by terrain/surface at winter solstice (interpolate horizon at azimuth)
        for model in ("cdem",):
            blocked = 0
            tot = 0
            for H, alt, az in sun["winter_solstice"]["path"]:
                tot += 1
                azs = sorted(hz[model])
                if az < azs[0] or az > azs[-1]:
                    continue
                lo = max(a for a in azs if a <= az); hi = min(a for a in azs if a >= az)
                h = hz[model][lo][0] if lo == hi else hz[model][lo][0] + (hz[model][hi][0] - hz[model][lo][0]) * (az - lo) / (hi - lo)
                blocked += alt < h
            sun["winter_solstice"][f"quarter_hours_blocked_{model}"] = f"{blocked}/{tot}"
        m["sun"] = sun
        m["flood_fhip"] = rec["fhip"]
        if "city" in rec:
            m["city_open_data"] = rec["city"]
        if "land_cover" in rec:
            lc = rec["land_cover"]
            m["land_cover"] = {"source": lc["source"], "ring_400m": lc["ring_400m"], "ring_1km": lc["ring_1km"],
                               "natural_share_400m": natural_share(lc["ring_400m"]), "natural_share_1km": natural_share(lc["ring_1km"]),
                               "forest_share_1km": round(sum(v for k, v in lc["ring_1km"].items() if "forest" in k.lower()), 3)}
        if "dry" in rec:
            d = dict(rec["dry"]); d.pop("samples")
            m["dry_area"] = d
        m["footprint"] = {k: rec["footprint"][k] for k in ("label", "area_m2", "tags")}
        m["acoustic"] = acoustic(rec, lat, lon)
        m["acoustic"]["yyc_runway_extended_centrelines"] = [r for r in runway_exposure(raw["runways"], lat, lon) if r["lateral_offset_m"] <= 3000]
        seen, pl = set(), []
        for q in pois(rec, lat, lon):
            if (q["name"], q["kind"]) in seen or not q["name"]:
                continue
            seen.add((q["name"], q["kind"])); pl.append(q)
        m["pois_2km"] = pl[:70]
        m["landscape_osm"] = landscape_metrics(rec, lat, lon, s["setting"])
        m["wind_era5"] = raw["era5"][sid]
        n = NARR.SITE[sid]
        scores = {"mountains": zs.band(mt, zs.TRAVEL_BANDS), "city": zs.band(cv, zs.TRAVEL_BANDS)}
        for k in ("landscape", "room", "access", "hazards", "services"):
            scores[k] = n["scores"][k][0]
        wt = sum(scores[k] * weights[k] for k in scores)
        sens = {"mountains_x3": wt + scores["mountains"], "city_x3": wt + scores["city"], "equal_weights_of_35": sum(scores.values())}
        scan1 = {x["letter"]: x for x in json.loads((HERE / "scan_2026-09-29_reframe.json").read_text(encoding="utf-8"))["sites"]}
        s1 = scan1[sid]
        changes = [{"criterion": k, "stage1": s1["scores"][k], "stage2": scores[k],
                    "why": (n["scores"][k][1] if k in n["scores"] else
                            f"OSRM from the Stage 2 anchor: {mt} min to the nearer gateway" if k == "mountains" else
                            f"OSRM from the Stage 2 anchor: {cv:.1f} min combined (YYC {dm['yyc_airport']}, cluster {cl:.1f})")}
                   for k in scores if scores[k] != s1["scores"][k]]
        sites_out.append({
            "id": sid, "name": s["name"], "setting": s["setting"], "anchor": {"lat": lat, "lon": lon, "ring_m": 400,
            "google_maps": f"https://www.google.com/maps/@{lat},{lon},800m/data=!3m1!1e3"},
            "stage1_anchor": {"lat": s["stage1_anchor"][0], "lon": s["stage1_anchor"][1]},
            "anchor_rationale": n["anchor_rationale"],
            "footprint": {"label": rec["footprint"]["label"], "area_m2": rec["footprint"]["area_m2"],
                          "rings_latlon": [[[round(a, 6), round(b, 6)] for a, b in r] for r in rec["footprint"]["rings"]]},
            "image": f"img/stage2_{sid}.jpg", "sun_section": f"../diagrams/stage2_sun_{sid}.png",
            "facts": n["facts"], "envelope": n["envelope"], "battery": n["battery"], "context": n["context"],
            "scores": scores, "score_reasons": {k: v[1] for k, v in n["scores"].items()},
            "total_weighted": wt, "total_max": zs.MAX_W, "sensitivity": sens,
            "stage1": {"scores": s1["scores"], "total_weighted": s1["total_weighted"], "rank": s1["rank"]},
            "changes_from_stage1": changes,
            "talking_points": n["talking_points"], "visit_checklist": n["visit_checklist"], "flags": n["flags"],
            "metrics": m})
    tb = ["mountains", "city", "landscape"]
    sites_out.sort(key=lambda x: (-x["total_weighted"], -sum(x["scores"][k] for k in tb), -x["scores"]["hazards"]))
    for i, x in enumerate(sites_out, 1):
        x["rank"] = i
    out = {"title": "Cairn Youth Centre: Stage 2 four-site study (C, F, I, N)", "date": "2026-09-29",
           "program": {"net_m2": 1904, "gross_m2": 2475, "beds": 32, "nodes": 4, "gym_m": [24, 15],
                       "site_need_m2": {"city": 6600, "rural": 10000}},
           "criteria": [{"key": k, "label": l, "weight": w, "rule": r} for k, l, w, r in zs.CRITERIA],
           "stage2_column": NARR.ENVELOPE_RULE, "total_max": zs.MAX_W, "tie_break": "Mountains + City + Landscape, then Hazards",
           "climate_normals": raw["normals"], "destinations": raw["osrm"]["dest"],
           "sources": NARR.SOURCES, "caveats": NARR.CAVEATS, "ranking_summary": NARR.RANKING, "sites": sites_out}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for x in sites_out:
        print(x["rank"], x["id"], x["scores"], x["total_weighted"], x["sensitivity"])
    print("wrote", OUT)
    return out


# ---------------------------------------------------------------- figures
def figures(raw):
    import stage2_figures
    stage2_figures.draw_all(SITES, raw, IMG, DIAG)


if __name__ == "__main__":
    raw = collect("--fresh" in sys.argv)
    if "--collect-only" in sys.argv:
        sys.exit()
    if "--no-figures" not in sys.argv:
        figures(raw)
    build(raw)

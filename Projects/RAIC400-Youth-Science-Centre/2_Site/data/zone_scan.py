"""Stage 1 zone scan for the RAIC 400 youth centre: live City of Calgary open data per zone.

Per zone reference point: land-use district, community, regulatory flood-map hit, nearest
CTrain station, transit stops within 400 m, and straight-line distances to downtown and Kananaskis.
Ben's two parcels use their real polygon centroids; other zones use an OSM-geocoded anchor.
Writes zone_scan.json next to this file. Concept-grade: straight-line distances, not walk/drive routes.

Datasets (data.calgary.ca, Socrata): 4bsw-nn7w assessments/parcels, qe6k-p9nh land-use districts,
2axz-xm4q LRT stations, muzh-c9qc transit stops, tp6q-x2v7 regulatory flood map (bylaw flood hazard).
"""
import json, math, time
from pathlib import Path
import requests

HERE = Path(__file__).resolve().parent
SOC = "https://data.calgary.ca/resource/{}.json"
UA = {"User-Agent": "RAIC400-student-site-search"}
CITY_HALL = (51.0453, -114.0581)
BARRIER_LAKE = (51.0270, -115.0330)   # Kananaskis gateway, Hwy 40 (approximate anchor)


def soc(ds, **params):
    r = requests.get(SOC.format(ds), params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def parcel(addr):
    row = soc("4bsw-nn7w", **{"$where": f"address = '{addr}'", "$limit": 1})[0]
    ring = row["multipolygon"]["coordinates"][0][0]
    lon = sum(p[0] for p in ring) / len(ring)
    lat = sum(p[1] for p in ring) / len(ring)
    (HERE / f"parcel_{addr.replace(' ', '-')}.geojson").write_text(json.dumps(
        {"type": "Feature", "properties": {k: v for k, v in row.items() if k != "multipolygon"},
         "geometry": row["multipolygon"]}, indent=1))
    return (lat, lon), float(row["land_size_sm"]), row


def geocode(q):
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": q, "format": "json", "limit": 1}, headers=UA, timeout=60)
    r.raise_for_status()
    time.sleep(1.1)   # Nominatim usage policy: max 1 request/second
    j = r.json()[0]
    return (float(j["lat"]), float(j["lon"])), j["display_name"]


def point_wkt(p):
    return f"POINT ({p[1]} {p[0]})"


def circle_wkt(p, r_m, n=24):
    """Polygon approximating a circle of radius r_m around p (lat, lon)."""
    dlat = r_m / 111320.0
    dlon = r_m / (111320.0 * math.cos(math.radians(p[0])))
    pts = [(p[1] + dlon * math.cos(2 * math.pi * i / n), p[0] + dlat * math.sin(2 * math.pi * i / n))
           for i in range(n)]
    pts.append(pts[0])
    return "POLYGON ((" + ", ".join(f"{x} {y}" for x, y in pts) + "))"


ZONES = [
    ("A", "Beltline infill (Ben idea 1)", {"parcel": "633 15 AV SW"}),
    ("B", "Eau Claire, Prince's Island edge (Ben idea 2)", {"parcel": "708 1 AV SW"}),
    ("C", "Inglewood, Bow River / Bird Sanctuary edge", {"geo": "Inglewood Bird Sanctuary, Calgary"}),
    ("D", "Fish Creek Park edge at Fish Creek-Lacombe CTrain", {"geo": "Fish Creek-Lacombe Station, Calgary"}),
    ("E", "Forest Lawn, Elliston Park edge (International Ave)", {"geo": "Elliston Park, Calgary"}),
]

stations = [(s["stationnam"], (s["the_geom"]["coordinates"][1], s["the_geom"]["coordinates"][0]), s["status"])
            for s in soc("2axz-xm4q", **{"$limit": 500})]

out = []
for zid, name, how in ZONES:
    rec = {"zone": zid, "name": name}
    if "parcel" in how:
        pt, area, row = parcel(how["parcel"])
        rec.update(anchor=how["parcel"], parcel_area_m2=area, assessed_land_use=row["land_use_designation"])
    else:
        pt, disp = geocode(how["geo"])
        rec.update(anchor=disp)
    rec["lat"], rec["lon"] = round(pt[0], 6), round(pt[1], 6)
    lu = soc("qe6k-p9nh", **{"$where": f"intersects(multipolygon, '{point_wkt(pt)}')", "$limit": 3})
    rec["land_use_at_point"] = [f"{x.get('lu_code')} ({x.get('description')})" for x in lu]
    fl = soc("tp6q-x2v7", **{"$where": f"intersects(multipolygon, '{point_wkt(pt)}')", "$limit": 5})
    rec["flood_at_point"] = sorted({f["description"] for f in fl})
    fl = soc("tp6q-x2v7", **{"$where": f"intersects(multipolygon, '{circle_wkt(pt, 250)}')", "$limit": 20})
    rec["flood_within_250m"] = sorted({f["description"] for f in fl})
    near = sorted((km(pt, s[1]), s[0], s[2]) for s in stations if s[2] == "Current")[:2]
    rec["nearest_ctrain"] = [{"station": n, "km": round(d, 2)} for d, n, _ in near]
    stops = soc("muzh-c9qc", **{"$where": f"within_circle(point, {pt[0]}, {pt[1]}, 800) AND status = 'ACTIVE'",
                                "$limit": 2000})
    d = sorted(km(pt, (float(x["point"]["coordinates"][1]), float(x["point"]["coordinates"][0]))) * 1000
               for x in stops)
    rec["stops_within_400m"] = sum(1 for v in d if v <= 400)
    rec["stops_within_800m"] = len(d)
    rec["nearest_stop_m"] = round(d[0]) if d else None
    w = soc("wj3a-wgmh", **{"$where": f"intersects(polygon, '{point_wkt(pt)}')", "$limit": 1})
    if w:
        w = w[0]
        tot = float(w["total_household_total_income"])
        low = float(w["under_20_000"]) + float(w["_20_000_to_39_999"])
        rec["ward"] = w["ward"]
        rec["ward_pct_households_under_40k_2016"] = round(100 * low / tot, 1)
    rec["km_to_city_hall"] = round(km(pt, CITY_HALL), 1)
    rec["km_to_kananaskis_gateway"] = round(km(pt, BARRIER_LAKE), 1)
    out.append(rec)
    print(json.dumps(rec))

(HERE / "zone_scan.json").write_text(json.dumps(out, indent=1))
print("wrote", HERE / "zone_scan.json")

"""Site presentation preview (HTML, 11x17 sheets at 100 px/in) for the four Stage 2 sites.
Deliberately general (2026-10-02, per Ben): no weights, scores 1-5 out of 35, words instead of measured values,
drive times rounded to 5 min. Inputs: ../data/stage2_2026-09-29.json (Stage 2 facts), mountain_drive.json (OSRM to
Wildhorn and Kananaskis Village), img/terrain_<id>.json (relative elevation). P below holds the rescored criteria
(Room now includes flexibility, Hazards now includes busy roads/rail at the door) and the plain-word labels.
Writes site-presentation.html (images in img/, from make_slide_maps.py and make_terrain.py)."""
import json, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE.parent / "data" / "stage2_2026-09-29.json").read_text(encoding="utf-8"))
SITES = {s["id"]: s for s in D["sites"]}
MTN = json.loads((HERE / "mountain_drive.json").read_text())["osrm_table"]
PINS = json.loads((HERE / "img" / "city_plan_pins.json").read_text())["pins"]
TERR = {k: json.loads((HERE / "img" / f"terrain_{k}.json").read_text()) for k in SITES}
ORDER = ["C", "F", "I", "N"]  # urban -> rural (Stage 2 ids; image files keep these)
LET = {"C": "A", "F": "B", "I": "C", "N": "D"}  # presentation letters
DATE = "October 2026"
TOTAL = 2 + 3 * len(ORDER)

CRIT = [("mountains", "Mountains"), ("city", "City & airport"), ("landscape", "Landscape"), ("room", "Room & flexibility"),
        ("access", "Coach & egress"), ("hazards", "Hazards"), ("services", "Services")]
DEFS = {
    "mountains": "Distance to the mountains",
    "city": "Distance to city amenities and the airport",
    "landscape": "Nature at the door",
    "room": "Space to build, and freedom to place it",
    "access": "Coach access and ways out",
    "hazards": "Flood, fire, industry and busy roads",
    "services": "Water, sewer, schools and neighbours",
}

# Presentation rescore. Same as Stage 2 except: mountains (new destinations; all four are ~60-75 min, so all 3),
# room (-1 where neighbours or the forest fix the building's position/orientation), hazards (-1 for a divided
# arterial or a rail line within ~150 m).
P = {
    "C": {"name": "Inglewood", "where": "Bird Sanctuary entrance, Nature Centre lot", "setting": "Inner city",
          "scores": {"mountains": 3, "city": 5, "landscape": 4, "room": 4, "access": 4, "hazards": 3, "services": 5},
          "notes": {"mountains": "Furthest from Wildhorn", "city": "Closest of the four", "landscape": "Sanctuary and river",
                    "room": "Lot plus the lawn around it", "access": "Local road, many routes", "hazards": "Flood edge; rail next door",
                    "services": "City serviced"},
          "character": "Riverside grassland", "land": "City park", "roomw": "Ample (lot plus lawn)", "flex": "Some limits (rail W, flood edge E)", "transit": "Bus within walking distance",
          "flood": "Medium", "edge": "Rail line next door", "terrain": "Flat river terrace; the ground barely changes around the lot"},
    "F": {"name": "Glenmore Landing", "where": "Forest north of the retail, South Glenmore Park", "setting": "Suburban edge",
          "scores": {"mountains": 3, "city": 4, "landscape": 3, "room": 4, "access": 5, "hazards": 3, "services": 5},
          "notes": {"mountains": "Nearest to Wildhorn", "city": "Close", "landscape": "Forest and reservoir",
                    "room": "Ample; boxed in by parking and retail", "access": "Arterial, many routes", "hazards": "Arterial road next door",
                    "services": "City serviced, shops"},
          "character": "Wooded, reservoir shore", "land": "City park", "roomw": "Ample", "flex": "Some limits (boxed in by parking and commercial area)", "transit": "MAX Yellow BRT on 14 St SW",
          "flood": "Low", "edge": "Arterial road next door", "terrain": "Nearly level, with a gentle fall west to the reservoir shore"},
    "I": {"name": "Loch McKinnon", "where": "Shriners' field, NW of the Shrine Centre", "setting": "City's western gate",
          "scores": {"mountains": 3, "city": 4, "landscape": 3, "room": 5, "access": 4, "hazards": 3, "services": 5},
          "notes": {"mountains": "About an hour", "city": "Moderate", "landscape": "Lake and river",
                    "room": "Large open field", "access": "Highway close by", "hazards": "Rail next door; level crossing",
                    "services": "City; servicing to extend"},
          "character": "Lakeside field", "land": "Private, future development", "roomw": "Ample", "flex": "Open", "transit": "Bus within walking distance",
          "flood": "Low", "edge": "Rail siding next door", "terrain": "Level terrace above the lake, with gentle slopes nearby"},
    "N": {"name": "Glenbow Ranch", "where": "Ranch house at the end of Glenbow Road", "setting": "Rural, provincial park",
          "scores": {"mountains": 3, "city": 3, "landscape": 4, "room": 5, "access": 2, "hazards": 5, "services": 1},
          "notes": {"mountains": "About 70 min", "city": "Furthest", "landscape": "Native prairie park",
                    "room": "Open bench", "access": "One road in", "hazards": "Low (grass fire not scored)",
                    "services": "Well and septic"},
          "character": "Native prairie", "land": "Provincial park", "roomw": "Ample", "flex": "Open", "transit": "None",
          "flood": "Low", "edge": "None", "terrain": "Sloping bench that falls south toward the Bow"},
}
for k in P:
    P[k]["total"] = sum(P[k]["scores"].values())
TOTALS = [P[k]["total"] for k in ORDER]


def rank(sid):
    t = P[sid]["total"]
    r = 1 + sum(x > t for x in TOTALS)
    return f"{r}=" if TOTALS.count(t) > 1 else str(r)


IMG_CREDIT = "Imagery: Esri, Maxar, Earthstar Geographics, and the GIS User Community."
GRAY_CREDIT = "Basemap: Esri World Light Gray Canvas, darkened, with hill shading from AWS Terrain Tiles."
e = html.escape


def r5(x):
    return f"~{max(5, int(5 * round(x / 5)))} min"


def drives(sid):
    m = SITES[sid]["metrics"]["drive"]["minutes_free_flow"]
    return [("YYC airport", m["yyc_airport"]), ("Downtown", m["city_hall_downtown"]), ("U of C", m["university_of_calgary"]),
            ("Wildhorn (Forgetmenot Ridge)", MTN[sid]["wildhorn"]["min"]), ("Kananaskis Village", MTN[sid]["kananaskis_village"]["min"])]


def city_min(sid):
    m = SITES[sid]["metrics"]["drive"]["minutes_free_flow"]
    cl = sum(m[k] for k in ("city_hall_downtown", "telus_spark", "calgary_zoo", "university_of_calgary")) / 4
    return (m["yyc_airport"] + cl) / 2


def footer(n, note):
    return (f'<div class="foot"><div>Ben Hackman · RAIC 400 · {DATE}</div><div class="foot-note">{note}</div>'
            f'<div class="sheetno">SHEET {n:02d}/{TOTAL:02d}</div></div>')


def head(eyebrow, title, sub, num=None, right=""):
    badge = f'<div class="badge">{num}</div>' if num is not None else ""
    return (f'<div class="head"><div class="head-l">{badge}<div><div class="eyebrow">{e(eyebrow)}</div>'
            f'<h1>{e(title)}</h1><div class="sub">{e(sub)}</div></div></div>{right}</div>')


def pins():
    out = []
    for i, sid in enumerate(ORDER, 1):
        x, y = PINS[sid]
        left = "left" if sid in ("C", "F") else ""
        out.append(f'<div class="pin" style="left:{x*100:.2f}%;top:{y*100:.2f}%"><span class="pin-dot">{i}</span>'
                   f'<span class="pin-lab {left}">{LET[sid]} · {e(P[sid]["name"])}</span></div>')
    return "".join(out)


def kv(k, v):
    return f'<div class="kv"><span>{e(k)}</span><b>{e(v)}</b></div>'


def sheet_cover():
    rows = "".join(
        f'<div class="legend-row"><span class="pin-dot">{i}</span><div><b>{LET[sid]} · {e(P[sid]["name"])}</b>'
        f'<div class="small">{e(P[sid]["setting"])} · {e(P[sid]["character"].lower())}</div></div></div>' for i, sid in enumerate(ORDER, 1))
    pr = D["program"]
    return f'''<section class="sheet" data-label="City plan">
{head("RAIC 400 · Assignment · Site selection", "Four candidate sites", "Cairn Youth Centre: a year-round residential centre for visiting students aged 12 to 15. Calgary and the western foothills.")}
<div class="body cover">
  <figure class="map city"><div class="mapbox"><img src="img/city_plan.png" alt="Plan of Calgary west to Kananaskis Village with the four candidate sites numbered">{pins()}</div>
    <figcaption>Fig. 1. The four sites, numbered urban to rural, with reference destinations (black squares). {GRAY_CREDIT}</figcaption></figure>
  <aside class="side">
    <div class="label">The sites</div>{rows}
    <div class="label gap">Why these four</div>
    <p>A range from inner city to provincial park, narrowed from 11 zones for spread, talking points and the chance to visit each one.</p>
    <div class="label gap">Programme</div>
    {kv("Beds", f'{pr["beds"]}, in {pr["nodes"]} nodes of 8, pods of 4')}
    {kv("Building", f'about {round(pr["gross_m2"], -2):,.0f} m²')}
    {kv("Land needed", "about 1 ha")}
  </aside>
</div>
{footer(1, "Early site analysis: values are approximate and for comparison only.")}
</section>'''


def sheet_zone(i, sid, n):
    s, t = SITES[sid], P[sid]

    def cap(x):
        x = x.strip()
        return x[:1].upper() + x[1:]
    adj = "".join(f'<div class="kv adj"><span>{e(a.split(":")[0])}</span><div>{e(cap(a.split(":", 1)[1]))}</div></div>'
                  for a in s["context"]["adjacent"])
    extra = ["MAX Yellow bus rapid transit on 14 St SW, beside the site"] if sid == "F" else []
    am = "".join(f"<li>{e(a)}</li>" for a in (extra + s["context"]["ring_amenities"])[:5])
    nu = "".join(f"<li>{e(a)}</li>" for a in s["context"]["ring_nuisances"][:4])
    return f'''<section class="sheet" data-label="{i} {sid} context">
{head(f"Site {i} of 4 · Context · {t['setting']}", f"{LET[sid]} · {t['name']}", t["where"], i)}
<div class="body zone">
  <figure class="map"><img src="img/zone_{sid}.jpg" alt="Aerial view of the area around site {LET[sid]} with the site dot and 400 m ring">
    <figcaption>Fig. {n}.1. Neighbourhood context, about 10 km across. Yellow dot: site. Dashed ring: 400 m. {IMG_CREDIT}</figcaption></figure>
  <aside class="side">
    <div class="label">Next to the site</div>{adj}
    <div class="label gap">Within reach</div><ul>{am}</ul>
    <div class="label gap">Nuisances</div><ul>{nu}</ul>
  </aside>
</div>
{footer(n, "Context from OpenStreetMap and City of Calgary open data, checked against aerial imagery.")}
</section>'''


def score_right(sid):
    return (f'<div class="score"><div class="score-n"><span>{P[sid]["total"]}</span><small>/ 35</small></div>'
            f'<div class="tag">Rank {rank(sid)} of 4</div></div>')


def sheet_site(i, sid, n):
    t = P[sid]
    sc = "".join(f'<tr><td>{e(lab)}</td><td class="c b">{t["scores"][k]}</td><td class="note">{e(t["notes"][k])}</td></tr>' for k, lab in CRIT)
    dr = "".join(kv(lab, r5(mn)) for lab, mn in drives(sid))
    return f'''<section class="sheet" data-label="{i} {sid} site">
{head(f"Site {i} of 4 · Site · {t['setting']}", f"{LET[sid]} · {t['name']}", t["where"], i, score_right(sid))}
<div class="body site">
  <figure class="map"><img src="img/site_{sid}.jpg" alt="Aerial view of site {LET[sid]} with the site outline, 400 m ring, sun path and prevailing wind">
    <figcaption>Fig. {n}.1. The site, about 2.4 km across. Cyan: the site chosen. Arcs: sunrise to sunset at the summer and winter solstices (schematic). Arrow: prevailing wind. {IMG_CREDIT}</figcaption></figure>
  <aside class="stats">
    <div class="col">
      <div class="label">Scores (1 to 5)</div>
      <table><tbody>{sc}</tbody><tfoot><tr><td>Total</td><td class="c">{t["total"]}</td><td class="note">out of 35</td></tr></tfoot></table>
      <div class="label gap">The site</div>
      {kv("Character", t["character"])}{kv("Land", t["land"])}{kv("Room", t["roomw"])}{kv("Flexibility", t["flex"])}
      {kv("Transit", t["transit"])}{kv("Flood risk", t["flood"])}{kv("Busy edge", t["edge"])}
      <div class="label gap">Drive times (off-peak)</div>{dr}
    </div>
  </aside>
</div>
{footer(n, "Drive times rounded to 5 min, off-peak; allow more at rush hour or in winter. Flood risk from the Alberta flood hazard maps.")}
</section>'''


def sheet_terrain(i, sid, n):
    t, f = P[sid], TERR[sid]

    def rnd(x):
        return f"about {max(5, int(5 * round(x / 5)))} m"
    return f'''<section class="sheet" data-label="{i} {sid} terrain">
{head(f"Site {i} of 4 · Terrain · {t['setting']}", f"{LET[sid]} · {t['name']}", t["terrain"], i)}
<div class="body terrain">
  <figure class="map"><img src="img/terrain_{sid}.jpg" alt="Oblique 3D view of the terrain around site {LET[sid]}, looking north, height exaggerated four times">
    <figcaption>Fig. {n}.1. Looking north over the site, about 2.4 km across, heights exaggerated ×5. Yellow pin: site. Elevation: AWS Terrain Tiles (CDEM-derived). {IMG_CREDIT}</figcaption></figure>
  <aside class="side">
    <div class="label">Where it sits</div>
    <p>{e(t["terrain"])}.</p>
    <div class="label gap">Within 500 m</div>
    {kv("Above the lowest ground", rnd(f["above_low_m"]))}
    {kv("Below the highest ground", rnd(f["below_high_m"]))}
  </aside>
</div>
{footer(n, "Elevation model is about 20–30 m resolution: reads the landform, not the fine grading. A site survey comes later.")}
</section>'''


LANDS = ("<b>A · Inglewood</b> leads by a point: the closest to the city, with room on the lawn beside the lot, "
         "but a medium flood risk and rail next door. <b>B · Glenmore Landing</b> and <b>C · Loch McKinnon</b> tie just behind: "
         "B keeps the city close; C has the most room and is private land rather than park. <b>D · Glenbow Ranch</b> trails on services and access.")


def sheet_summary():
    rows = ""
    top = max(TOTALS)
    for sid in ORDER:
        t = P[sid]
        mtn = min(MTN[sid]["wildhorn"]["min"], MTN[sid]["kananaskis_village"]["min"])
        rows += (f'<tr class="{"lead" if t["total"] == top else ""}"><td><span class="pin-dot sm">{ORDER.index(sid)+1}</span></td>'
                 f'<td class="nw"><b>{LET[sid]} · {e(t["name"])}</b></td><td class="r b">{t["total"]}</td>'
                 f'<td>{e(t["character"])}</td><td class="r nw">{r5(city_min(sid))}</td><td class="r nw">{r5(mtn)}</td>'
                 f'<td>{e(t["roomw"])}</td><td>{e(t["flood"])}</td><td>{e(t["land"])}</td></tr>')
    defs = "".join(f'<div class="def"><b>{e(lab)}</b><span>{e(DEFS[k])}</span></div>' for k, lab in CRIT)
    return f'''<section class="sheet" data-label="Summary">
{head("RAIC 400 · Site selection · Summary", "Four sites compared", "Seven criteria, each scored 1 to 5, out of 35.")}
<div class="body summary">
  <figure class="map city"><div class="mapbox"><img src="img/city_plan.png" alt="Plan with the four sites numbered">{pins()}</div>
    <figcaption>Fig. {TOTAL}.1. The four sites. {GRAY_CREDIT}</figcaption></figure>
  <aside class="stats one">
    <div class="label">Overall</div>
    <table class="sum"><thead><tr><th></th><th>Site</th><th class="r">/35</th><th>Character</th><th class="r">City</th><th class="r">Mountains</th><th>Room</th><th>Flood</th><th>Land</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <div class="label gap">How the sites were scored</div>
    <div class="defs">{defs}</div>
    <div class="label gap">Where it lands</div>
    <p>{LANDS}</p>
  </aside>
</div>
{footer(TOTAL, "Early site analysis: scores are judgments for comparison, not measurements.")}
</section>'''


CSS = r"""
:root{--bg:#E9E5DB;--chrome:#1B1B1B;--chrome-2:#5C574E;--paper:#F5F2EA;--ink:#1B1B1B;--red:#A63A26;--panel:#E8E3D6;--rule:#8D877C}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141414;--chrome:#EDEAE2;--chrome-2:#A9A397}}
:root[data-theme="dark"]{--bg:#141414;--chrome:#EDEAE2;--chrome-2:#A9A397}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--chrome);font-family:"Source Serif 4",Georgia,serif}
.top{max-width:1240px;margin:0 auto;padding:28px 16px 8px}
.top h2{font-family:"Barlow Condensed",sans-serif;font-weight:700;font-size:30px;margin:0 0 4px;text-transform:uppercase;letter-spacing:.02em}
.top p{margin:0;color:var(--chrome-2);font-size:15px;line-height:1.5}
.deck{max-width:1240px;margin:0 auto;padding:12px 16px 60px;display:flex;flex-direction:column;gap:22px}
.frame-label{font-family:"Barlow Condensed",sans-serif;font-weight:600;font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:var(--chrome-2);margin-bottom:6px}
.wrap{width:100%;aspect-ratio:17/11;position:relative;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.18)}
.sheet{position:absolute;left:0;top:0;width:1700px;height:1100px;transform-origin:0 0;background:var(--paper);color:var(--ink);
  padding:44px 62px 30px;display:flex;flex-direction:column;gap:22px;font-family:"Source Serif 4",Georgia,serif}
.head{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;border-bottom:2px solid var(--ink);padding-bottom:16px}
.head-l{display:flex;gap:22px;align-items:flex-end}
.badge{width:92px;height:92px;background:var(--ink);color:var(--paper);display:flex;align-items:center;justify-content:center;font:700 64px/1 "Barlow Condensed",sans-serif;flex-shrink:0}
.eyebrow,.label{font:600 15px/1.2 "Barlow Condensed",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--red)}
h1{margin:4px 0 2px;font:700 60px/1 "Barlow Condensed",sans-serif;text-transform:uppercase;letter-spacing:.01em}
.sub{font-size:18px;line-height:1.35}
.score{display:flex;flex-direction:column;align-items:flex-end;gap:8px}
.score-n{display:flex;align-items:baseline;gap:6px;font-family:"Barlow Condensed",sans-serif;font-weight:700}
.score-n span{font-size:76px;line-height:.9;color:var(--red)}.score-n small{font-size:26px}
.tag{background:var(--ink);color:var(--paper);font:600 15px/1 "Barlow Condensed",sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:6px 10px}
.body{flex:1;display:grid;gap:36px;min-height:0}
.cover{grid-template-columns:1160px 1fr}
.zone{grid-template-columns:1180px 1fr}
.site{grid-template-columns:1000px 1fr}
.terrain{grid-template-columns:1220px 1fr}
.terrain figure img{max-height:800px;width:auto;max-width:100%}
.summary{grid-template-columns:780px 1fr}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
figure img{width:100%;display:block}
figcaption{font-style:italic;font-size:13px;line-height:1.4}
.mapbox{position:relative}.mapbox img{border:1px solid var(--rule)}
.pin{position:absolute;transform:translate(-50%,-50%);display:flex;align-items:center}
.pin-dot{width:36px;height:36px;border-radius:50%;background:var(--red);color:#fff;border:3px solid #fff;display:flex;align-items:center;justify-content:center;
  font:700 21px/1 "Barlow Condensed",sans-serif;box-shadow:0 0 0 1px var(--red);flex-shrink:0}
.pin-dot.sm{width:28px;height:28px;font-size:17px;border-width:2px}
.pin-lab{position:absolute;left:44px;white-space:nowrap;font:700 20px/1 "Barlow Condensed",sans-serif;color:var(--red);
  text-shadow:0 0 4px #fff,0 0 4px #fff,0 0 3px #fff,0 0 2px #fff}
.pin-lab.left{left:auto;right:44px}
.side,.stats{display:flex;flex-direction:column;font-size:16px;line-height:1.4;min-width:0}
.stats{flex-direction:row;gap:30px}.stats.one{flex-direction:column;gap:0}
.col{flex:1;display:flex;flex-direction:column;min-width:0}
.label{border-bottom:2px solid var(--ink);padding-bottom:6px;margin-bottom:4px}
.label.gap{margin-top:16px}
.kv{display:flex;justify-content:space-between;gap:14px;padding:4px 0;border-bottom:1px solid var(--rule);font-size:16px}
.kv b{font-family:"Barlow Condensed",sans-serif;font-weight:600;font-size:19px;text-align:right}
.kv.adj{justify-content:flex-start}.kv.adj span{font:600 17px/1.3 "Barlow Condensed",sans-serif;width:22px;flex-shrink:0}
.legend-row{display:flex;gap:14px;align-items:center;padding:9px 0;border-bottom:1px solid var(--rule);font-size:16px}
.legend-row b{font:700 22px/1.1 "Barlow Condensed",sans-serif;text-transform:uppercase}
.small{font-size:14px;line-height:1.4}
ul{margin:4px 0 0;padding-left:18px}li{padding:3px 0}
p{margin:6px 0 0;font-size:17px;line-height:1.45}
table{width:100%;border-collapse:collapse;font-size:16px}
th{font:600 14px/1.2 "Barlow Condensed",sans-serif;letter-spacing:.08em;text-transform:uppercase;text-align:left;padding:6px 4px;border-bottom:1px solid var(--ink)}
td{padding:4px 4px;border-bottom:1px solid var(--rule)}
td.b,tfoot td.c{font-family:"Barlow Condensed",sans-serif;font-weight:700;font-size:20px}
td.note{font-size:14px}
tfoot td{border-bottom:2px solid var(--ink);font-weight:600}
.nw{white-space:nowrap}.c{text-align:center}.r{text-align:right}
table.sum td{font-size:15px}table.sum td.r{font-family:"Barlow Condensed",sans-serif;font-weight:600;font-size:18px}
tr.lead td{background:var(--panel)}
.defs{display:flex;flex-direction:column}
.def{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:4px 0;border-bottom:1px solid var(--rule);font-size:14.5px;line-height:1.35}
.def b{font:600 17px/1.3 "Barlow Condensed",sans-serif}
.foot{display:flex;justify-content:space-between;gap:30px;font-size:13px;line-height:1.4;border-top:1px solid var(--rule);padding-top:10px}
.foot-note{flex:1;text-align:center}.sheetno{font:600 14px/1.4 "Barlow Condensed",sans-serif;letter-spacing:.1em}
"""

JS = r"""
function fit(){document.querySelectorAll('.wrap').forEach(w=>{const s=w.clientWidth/1700;w.firstElementChild.style.transform='scale('+s+')'})}
new ResizeObserver(fit).observe(document.body);window.addEventListener('load',fit);fit();
"""


def build():
    sheets = [sheet_cover()]
    n = 2
    for i, sid in enumerate(ORDER, 1):
        sheets += [sheet_zone(i, sid, n), sheet_site(i, sid, n + 1), sheet_terrain(i, sid, n + 2)]
        n += 3
    sheets.append(sheet_summary())
    frames = "".join(
        f'<div><div class="frame-label">Sheet {k:02d} · {s.split("data-label=")[1].split(chr(34))[1]}</div><div class="wrap">{s}</div></div>'
        for k, s in enumerate(sheets, 1))
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Site Selection Deck</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header class="top"><h2>Site selection deck: layout preview</h2>
<p>Cairn Youth Centre, RAIC 400. {TOTAL} sheets at 11x17: the city plan, then context, site and terrain for each site (urban to rural), then a summary. Kept general on purpose for early site analysis. Once the layout's approved, it moves into the PDF template.</p></header>
<main class="deck">{frames}</main><script>{JS}</script></body></html>'''
    (HERE / "site-presentation.html").write_text(page, encoding="utf-8")
    print("wrote site-presentation.html", len(sheets), "sheets", {k: P[k]["total"] for k in ORDER})


if __name__ == "__main__":
    build()

# Site search — Cairn Youth Centre (RAIC 400)

*Stage 1 re-run 2026-09-29 after the client reframe. It covers 16 zones: the 10 city zones A–K plus 6 new rural/edge zones L–Q. Stage 2 (parcel drill-down) hasn't started; it waits on Ben's pick from the shortlist below. The transit-era scan (2026-09-25, zones A–E) is kept at the bottom as superseded.*

## Reframe, 2026-09-29

Instructor feedback on 2026-09-28, and Ben's decisions on 2026-09-29:
- **Out:** the low-income / social-services focus, the sanctuary suite, counselling and after-school care. Transit access and nearness to low-income kids **no longer drive site selection**, so M3 (transit), M4 (near the kids served) and the scorecard's "reach" criterion are retired.
- **In:** a **year-round residential youth centre** for visiting **domestic and international students**. Academics (science and tech) and making (workshop), with about **a third of the program outdoors** in the mountains and foothills.
- **32 beds** in 4 nodes of 8. One node (8 kids) is out camping at a time. Summer runs two 4-week sessions; the rest of the year runs 2-week sessions.
- The instructor suggested rural sites: Bragg Creek, Cochrane, or en route to those. **Ben keeps the city in the running** for logistics, the airport, museums, the Zoo, the university and science institutions, and because Calgary is itself a city day or two for visiting students.

**Data provenance.** Every number comes from `data/zone_scan.py` → `data/scan_2026-09-29_reframe.json`. That JSON is self-contained: per site it holds scores, the raw metrics behind them, a "why it ranks" line and flags. Sources:
- **OSRM** public router: free-flow drive times, i.e. off-peak with no traffic or winter conditions. Add 20–40% for peak or winter.
- **Alberta Flood Hazard Identification Program** map service (geospatial.alberta.ca): floodway, flood fringe, and the 1:200 / 1:500 extents, applied the same way to city and rural zones.
- **City of Calgary** parcels, for Ben's lots A and B.
- **Esri World Imagery**, for a visual check of every new anchor.

**First run (16 zones): OpenStreetMap (Overpass) timed out on both public endpoints.** Superseded by the 11-zone re-run below. Only zone A has OSM-measured land cover, trails and roads. For the other 15 zones, Landscape, Room and Coach & egress, plus the forest share used in Hazards, are **imagery judgments, marked unverified** (`osm_status` in the JSON). A live rerun of `zone_scan.py` replaces them with measured values when Overpass responds.

## Land need (rough, 32 beds)

The program isn't re-issued yet; the gross area below is an estimate.

| Item | m² |
|---|---|
| Building footprint (≈ 2,600 m² gross; single-storey gym, the rest on 2 storeys) | ~1,550 |
| Parking: 15 staff + 5 visitor + 8 vans | ~840 |
| Coach lay-by and turnaround (56-seat coach) | ~900 |
| Service yard and loading | ~150 |
| On-site camp and outdoor teaching yard (tent platforms, fire circle) | ~2,000 |
| Trailhead lot, ~10 stalls | ~300 |
| **City subtotal + 15%** | **≈ 6,600 (0.66 ha)** |
| Rural adds: well and on-site wastewater field (~2,000), FireSmart defensible space | **≈ 1.0 ha** |

Room is scored against **~1 ha**.

## Criteria (7, each /5, weighted; max 50)

| # | Criterion | Weight | Measure → score | Why |
|---|---|---|---|---|
| 1 | **Mountains** | ×2 | Free-flow minutes to the nearer of the Hwy 1/Hwy 40 Kananaskis gateway or West Bragg Creek. ≤20 = 5, ≤32 = 4, ≤44 = 3, ≤56 = 2, else 1 | Every camping node starts with a van run. A third of the program is out there. |
| 2 | **City & airport** | ×2 | Mean of (minutes to YYC) and (mean minutes to City Hall, TELUS Spark, the Zoo and U of C). **Same bands as Mountains** | International arrivals, city days, and science partners. Ben's reason for keeping the city. |
| 3 | **Landscape at the door** | ×2 | Natural cover in the 400 m ring, trails, a river/stream/lake in the ring, natural cover in the 1 km ring (see JSON rule) | Day hikes and field science straight from the building. |
| 4 | **Room** | ×1 | Open ground in the 400 m ring (parking, field, meadow; forest at half). ≥40% = 5 … <7% = 1. Ben's lots scored on lot area vs ~1 ha | A new build on a parking lot, demolition site or greenfield. |
| 5 | **Coach & egress** | ×1 | Road class at the door, plus distinct major roads within 2 km (routes out) | Every cohort arrives by coach. Two ways out in a fire. |
| 6 | **Hazards** | ×1 | Start at 5. Floodway −3, fringe −2, protected fringe / 1:200–1:500 extent / hazard within 250 m −1 (FHIP). Forest share of the 1 km ring ≥40% −2, ≥15% −1. Sour gas / heavy industry within 5 km −1 | Kids sleep here. The 2013 floods hit the Bow and Elbow valleys. Foothill forest is wildland-urban interface. |
| 7 | **Services & community** | ×1 | Municipal servicing +3 (hamlet utility +2, open county land 0); a school within 2 km +1; a community within 4 km +1 | Well and septic drive the site plan. The course requires an interface with the community. |

**How the criteria stay fair to both city and rural.**
- Mountains and City use **one minute yardstick at equal weight**. Each side is judged by the drive it imposes on the other: the city's run to West Bragg Creek (52–81 min) against the rural sites' run to the city (33–54 min).
- Landscape is weighted with the two travel criteria because the reframe makes the outdoors a third of the program.
- **Double counting to note:** Services & community also favours the city and town edges, and it overlaps with City. A sensitivity check follows the ranking.
- **Dropped:** transit and reach (moot after the reframe) and "kid-friendly context" (it no longer discriminates). M6 "two approaches" now sits inside Coach & egress, and Room covers the road side / trail side split.

## Zones

City zones A–K (history: A–E 2026-09-25; F, G, I, J, K added 2026-09-28; McKinnon Flats dropped). Rural/edge zones L–Q are new 2026-09-29. All are **anchor dot + 400 m ring**. None is an outlined retail or club parcel, and projects are new builds.

| Zone | Name | Setting | Anchor (lat, lon) | Note |
|---|---|---|---|---|
| A | Beltline infill, 633 15 Ave SW (Ben lot 1) | city | 51.038723, −114.076476 | parcel centroid, 1,000 m² |
| B | Eau Claire, 708 1 Ave SW (Ben lot 2) | city | 51.052571, −114.076107 | parcel centroid, 3,028 m² |
| C | Inglewood, Bird Sanctuary / Bow River | city | 51.027895, −114.006957 | |
| D | Fish Creek Park edge, Fish Creek–Lacombe | city | 50.923014, −114.073070 | |
| E | Forest Lawn, Elliston Park edge | city | 51.033572, −113.939943 | |
| F | Glenmore Landing, reservoir edge | city | 50.973700, −114.097874 | on surface parking |
| G | Brentwood (Nose Hill / U of C side) | city | 51.088356, −114.130807 | |
| I | Loch McKinnon north shore, Bowness | city | 51.100900, −114.238400 | |
| J | 819 32 St SE school reserve | city | 51.046430, −113.991140 | |
| K | 636 Marlborough Wy NE school reserve | city | 51.058560, −113.974580 | |
| **L** | **Bragg Creek, hamlet east edge across Hwy 22** | edge | **50.9493, −114.5594** | meadow strip + forest, hamlet core across the highway |
| **M** | **Cochrane SW edge, Jumping Pound Creek valley rim** | edge | **51.1817, −114.5107** | grass terrace south of the newest subdivision |
| **N** | **Glenbow Ranch gateway, Hwy 1A** | rural | **51.1750, −114.3650** | hay field beside the park access road |
| **O** | **Springbank hub, Range Rd 33** | rural | **51.0782, −114.3449** | cultivated field next to the Springbank schools |
| **P** | **Hwy 1 at Jumping Pound Creek (west of Hwy 22)** | rural | **51.0800, −114.5486** | ranchland, creek valley ~300 m W |
| **Q** | **Hwy 22 north of Bragg Creek** | rural | **50.9744, −114.5638** | ranch meadow in continuous forest |

Scouted and not proposed:
- **The Hwy 22 / Hwy 8 junction:** its Elbow crossing is the Springbank Off-stream Reservoir (SR1) diversion works.
- **Cochrane's Spray Lakes Sawmills / SLS Centre area:** an operating mill and a recreation centre.
- **The Hwy 22 midpoint:** flat farmland with no landscape.
- **Tsuut'ina Nation 145 land** east of Bragg Creek is not a candidate.

## Ranking (2026-09-29, 11 zones)

**Ben cut A, B, E, J and K on 2026-09-29** (kept in the zone table as a record). Re-run the same day: OpenStreetMap answered for 9 of 11 zones. Roads and trails are measured wherever OSM answered. Where OSM tags under half the land in the 400 m ring (most rural zones, and D and I), Landscape, Room and the forest share come from the imagery judgments instead. F and G are still all imagery (OSM timed out).

| Rank | Zone | Setting | Mtn | City | Land | Room | Coach | Haz | Serv | **/50** | OSM data | Why it ranks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **L** Bragg Creek | edge | 5 | 2 | 5 | 2 | 5 | 3 | 4 | **38** | land cover: imagery | Top rural: 16 min to West Bragg Creek trails, forest and the Elbow at the door, a hamlet next door; 49 min to the city. |
| 2 | **F** Glenmore Landing | city | 2 | 4 | 4 | 4 | 5 | 4 | 5 | **38** | imagery | Ties L for first: reservoir shore and pathway at the door, surface parking to build on, 24 min average to city and YYC. |
| 3 | **D** Fish Creek–Lacombe | city | 2 | 4 | 4 | 3 | 5 | 4 | 5 | **37** | land cover: imagery | Fish Creek PP at the door and fast road access; 52 min to West Bragg Creek ties F for the best city mountain time. |
| 4 | G Brentwood | city | 2 | 5 | 2 | 4 | 5 | 5 | 5 | 37 | imagery | Fast to U of C, YYC and downtown with plenty of parking land, but little landscape at the door. |
| 5 | **M** Cochrane SW | edge | 3 | 2 | 5 | 4 | 4 | 3 | 5 | **36** | land cover: imagery | Town servicing and neighbours plus a creek valley at the door; mid-way on both the city and the mountain drive. |
| 6 | I Loch McKinnon | city | 2 | 4 | 4 | 3 | 4 | 3 | 5 | 35 | land cover: imagery | Best city time to the Kananaskis gateway (56 min) and a river edge, but slower to YYC and the land's availability is unknown. |
| 7 | P Hwy 1 / Jumping Pound Cr. | rural | 3 | 3 | 4 | 5 | 2 | 5 | 1 | 33 | land cover: imagery | Fastest to the Hwy 40 gateway (33 min) with open land and a creek valley, but no services or neighbours. |
| 8 | Q Hwy 22 N of Bragg Creek | rural | 5 | 2 | 4 | 2 | 4 | 3 | 1 | 32 | land cover: imagery | Fast to Bragg Creek, but forest all round, little open ground and no services. |
| 9 | C Inglewood | city | 1 | 5 | 4 | 1 | 4 | 2 | 5 | 32 | measured | Best urban ecology, but the anchor is in the floodway and no dry lot has been found. |
| 10 | N Glenbow Ranch gateway | rural | 1 | 3 | 5 | 5 | 3 | 5 | 1 | 32 | land cover: imagery | Glenbow Ranch and the Bow valley next door with open land, but no services or community and a slow mountain drive. |
| 11 | O Springbank hub | rural | 3 | 3 | 1 | 5 | 4 | 5 | 2 | 30 | measured | Room and schools, but flat farmland with no landscape at the door. |

Tie-break: Mountains + City + Landscape, then Hazards.

Key travel metrics (free-flow minutes: nearer mountain gateway / YYC / city-cluster mean):

| Zone | Mountains | YYC | City cluster |
|---|---|---|---|
| L | 16 | 53 | 45.8 |
| F | 52 | 28 | 19.5 |
| D | 52 | 31 | 24.5 |
| G | 56 | 21 | 15.2 |
| M | 43 | 44 | 44.2 |
| I | 54 | 30 | 27.5 |
| P | 33 | 46 | 40.8 |
| Q | 19 | 58 | 50.8 |
| C | 61 | 19 | 13.5 |
| N | 57 | 33 | 33.2 |
| O | 40 | 36 | 31.8 |

**Sensitivity.**
- Mountains ×3 puts **L first (43)**, F second (40).
- City ×3 puts F and G joint first (42), D third (41), L at 40.
- Equal weights (/35): F and G 28, D 27, L and M 26.
- **L and F share the top at the base weights.** Which leads turns on how Ben values the mountain drive against the city drive.

## Shortlist for Stage 2 (2–4)

| Zone | Role | Why |
|---|---|---|
| **L** Bragg Creek | rural lead | Ties F at 38 and wins the tie-break. Measured roads lifted Coach & egress from 3 to 5 (Hwy 22 at the door, several routes out). The mountain-camp answer, with a real hamlet as its community. |
| **F** Glenmore Landing | city lead | 38. The only city zone with both landscape and room; 24 min average to the city and YYC. Scores are still all imagery. |
| **D** Fish Creek–Lacombe | city alternate | 37. Provincial park at the door; 52 min to West Bragg Creek ties F for the best city mountain time. Preferred over G (little landscape). |
| **M** Cochrane SW | edge alternate | 36. Town servicing and neighbours with a creek valley at the door. |

**Changes from the 16-zone run:** L +2 (Coach 3→5), M +1 (Coach 3→4), I +1 (Coach 3→4), Q +1 (Coach 3→4), P −2 (Coach 4→2: one minor road at the door), N −1 (Coach 4→3), C −2 (measured: Landscape 5→4, Room 3→1 because the ring is park, river and built land; Coach 3→4 and Hazards 1→2 offset part of it). F, D, G, O unchanged.

**Named trade-off.** F gives the city, airport and partners in under 30 min but asks every camping node to drive 52 min. L gives the mountains in 16 min but puts YYC 53 min away and every city day about 45 min each way. M sits in the middle on both drives and adds a town. Stage 2 should test whether the camping cadence (one node out at a time, weekly) or city logistics (arrivals, city days, partners) generates more trips per year. That count would settle the Mountains vs City weight.

## Unverified (carry into Stage 2)

- **F and G are still all imagery judgments** (OSM timed out on the re-run). Landscape, Room and forest share for D, I, L, M, N, P and Q are imagery too, because OSM tags under half of their land. Rerun `zone_scan.py` for F and G when Overpass responds.
- West Bragg Creek destination: the PRA centroid was used, not the trailhead lot (the OSM lookup failed). The OSRM snap point is unverified.
- N: whether the hay field is inside Glenbow Ranch Provincial Park. The OSRM Hwy 40 time (58 min) looks long.
- L: Rocky View County water and wastewater capacity east of Hwy 22. Tsuut'ina boundary clearance. Wildfire egress routes.
- M: whether the rim land is environmental or municipal reserve. Town servicing extension.
- P: sour-gas facilities and AER setbacks in the Jumping Pound field.
- F: the Glenmore Landing redevelopment proposal. Reservoir water-contact limits.
- D: City use of the station-area land. I: Shriners' land.
- Land ownership and land use for every zone. Wildfire uses forest share as a proxy; no provincial wildfire hazard layer was queried.

## Stage 2 — parcel drill-down

**2026-09-29: four-site study done → [`Stage-2_Four-Site-Study.md`](Stage-2_Four-Site-Study.md)** on Ben's picks C Inglewood, F Glenmore Landing (forest north of the retail), I Loch McKinnon (Shriners' land) and N Glenbow Ranch (Park Foundation building). Result at the Stage 1 weights: F 37, C 36, I 36, N 29. The recommendation is F, built on the forest's north-edge gravel lots; I is the runner-up. Data: `data/stage2_scan.py` → `data/stage2_2026-09-29.json`. The template below is kept for later parcels.

*Template (original note): For each shortlisted zone: find the actual parcel (a parking lot, a demolition site or greenfield; land use, area, owner type); run envelope utilization against ≈ 2,600 m² gross and ~1 ha of site; confirm servicing and hazards at the parcel; check the adjacency and the trail door.*

| Parcel | Land use verified? | Mtn | City | Land | Room | Coach | Haz | Serv | Envelope utilization | Caveats | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

Recommendation + runner-up: *(after Stage 2)*

---

<details>
<summary><strong>Superseded: transit-era Stage 1, 2026-09-25 (zones A–E) and the 2026-09-28 scorecard</strong></summary>

*Superseded 2026-09-29 by the client reframe above. Kept as the record. The 2026-09-28 scorecard (10 sites, 6 criteria incl. reach and transit, /30) ranked F 24, G 24 (F on tie-break), B 23, D 22 (drill down) · J 21, I 19, K 19 (hold) · A 18 (cut) · C 17, E 16 (hold). Its drive times are in `data/scan_2026-09-28_mountains_reach.json`, and the A–E open-data scan is in `data/zone_scan.json`.*

*Stage 1 (zone scan) drafted 2026-09-25, "light" pass. Stage 2 (parcel drill-down) not started — it waits on Ben's pick of zones below. City: Calgary (confirmed by Ben 2026-09-25).*

**Data provenance.** Every number in the zone table comes from `data/zone_scan.py` → `data/zone_scan.json`, queried live from City of Calgary Open Data (Socrata): assessments/parcels `4bsw-nn7w`, land-use districts `qe6k-p9nh`, CTrain stations `2axz-xm4q`, transit stops `muzh-c9qc`, regulatory flood map `tp6q-x2v7`, 2016 census household income by ward `wj3a-wgmh`. Ben's two parcels are stored as GeoJSON in `data/`. Distances are **straight-line**; walking is roughly 1.3× longer. Cells marked `[proxy, unverified]` are informed impressions, not checked facts. *(2026-09-29: `zone_scan.py` has since been rewritten for the reframe; the 2026-09-25 script's output is `zone_scan.json`.)*

### Selection criteria (from client motives + brief)

| # | Motive | Weight | Source |
|---|---|---|---|
| M1 | **Land for the program:** enough ground for the building plus parking, bus drop-off, service yard, play yard and outdoor basecamp, ideally with room for a cluster/courtyard parti | **H** | `00_Brief.md` site requirements; precedent Lesson 2; OQ 6 |
| M2 | **Real ecology on or next to the site** for the field-science ground (W2's fail test) | **H** | Driver W2; OQ 6 |
| M3 | **Transit:** kids arrive on their own, some staff and families don't drive | **H** | Client profile ("inside Calgary, reachable by transit") |
| M4 | **Near the kids Cairn serves** (kids facing hard circumstances, low-income families) | M | Client profile; mission |
| M5 | **Flood risk** kept off the building footprint | M | Calgary 2013 flood; residential use, overnight sanctuary |
| M6 | **Two separable approaches** (public front plus a discreet sanctuary intake) and a calm acoustic setting | M | Driver W3; OQ 9 |
| — | Drive to Kananaskis for expedition weeks | dropped | Every zone is 67–76 km straight-line from the Barrier Lake gateway. It doesn't discriminate, so it gets no column. |

#### How much land the program needs (M1)

| Item | Basis | m² |
|---|---|---|
| Building footprint, 2 storeys | Gym single-storey double-height: 360 × 1.30 = 468. Rest: (2,480 − 468) ÷ 2 = 1,006 | ~1,475 |
| Parking | 15 staff + 5 visitor + 8 vans (brief says 5–10) = 28 stalls × ~30 m² incl. aisle | ~840 |
| Bus lay-by + pull-through drop-off loop | estimate | ~450 |
| Service yard, loading, waste enclosure | estimate | ~150 |
| Play yard for one day-camp class | ~40 × 30 m | ~1,200 |
| Outdoor basecamp (fire circle, low ropes, teaching yard) | estimate | ~800 |
| Subtotal | | 4,915 |
| **Total with 15% for setbacks and landscape** | | **≈ 5,650 m² (0.57 ha)** |
| Compact floor: 3 storeys, underground parking, smaller yard, same basecamp | 1,140 + 450 + 150 + 600 + 800, +10% | ≈ 3,450 m² (0.35 ha) |

A cluster/courtyard parti (precedent Lesson 2) wants more than the 0.57 ha, roughly 0.8–1.0 ha. The field-science ground itself can be **borrowed** from an adjacent park rather than counted on the lot.

### Stage 1 — zone scan

Glyphs: ✓ meets · ~ partial · ✗ fails. Units in each cell.

| Zone | M1 Land (lot or zone) | M2 Ecology | M3 Transit | M4 Near the kids served | M5 Flood | M6 Approaches / calm | Land use at anchor | Verdict |
|---|---|---|---|---|---|---|---|---|
| **A. Beltline infill** — Ben's idea 1, 633 15 Ave SW | ✗ **1,000 m² (0.10 ha)**: less than a third of even the compact floor; the building alone would need 3+ storeys and no yard | ✗ Beaulieu Gardens / Lougheed House is a formal garden, not field ecology | ✓ nearest stop 105 m; 13 stops within 400 m; CTrain 6 St SW 0.90 km | ~ Ward 8: 22.1% of households under $40k (2016) | ✓ not in the regulatory flood map; "Overland Flow" within 250 m | ~ corner lot plus lane gives two approaches; dense and noisy (17 Ave, one-ways) `[proxy, unverified]` | CC-MH (Centre City Multi-Residential High Rise) | **Cut** |
| **B. Eau Claire, Prince's Island edge** — Ben's idea 2, 708 1 Ave SW | ~ **3,028 m² (0.30 ha)**: fits only the compact floor (3 storeys, underground parking); no cluster parti | ✓ Prince's Island Park, the lagoon and the Bow River riparian edge are across the street | ✓ nearest stop 123 m; 75 stops within 800 m; CTrain 7 St SW 0.63 km | ~ Ward 7: 25.8% under $40k; the immediate context is high-end condos `[proxy, unverified]` | ~ parcel polygon is clear of the regulatory flood map; floodway and floodplain within 250 m. Ben's screenshot shows the lot inside the "larger floods" (1:200 / 1:500) extent | ✓ multiple frontages; park festivals and events are a double-signed noise source `[proxy, unverified]` | DC 91D2008 (Direct Control, site-specific rules) | **Drill down** |
| **C. Inglewood, Bird Sanctuary / Bow River edge** | ~ larger lots exist on the Inglewood side, but much of the land by the sanctuary is floodway or flood fringe `[proxy, unverified]` | ✓✓ Inglewood Bird Sanctuary: the best field-science setting of the five | ✗ at the sanctuary anchor: no stops within 800 m; CTrain Barlow/Max Bell 1.96 km. The 9 Ave SE edge will score better (Stage 2) | ~ Ward 9: 24.7% under $40k | ✗ floodway at the anchor; flood fringe within 250 m. A buildable lot must sit outside both | ~ rail and industry nearby `[proxy, unverified]` | S-UN (Special Purpose – Urban Nature) at the sanctuary | **Hold**: drill down only if a 9 Ave SE lot outside the flood fringe turns up |
| **D. Fish Creek Park edge at Fish Creek–Lacombe CTrain** | ✓ station-area and park-edge land in the 0.5–1.0 ha range is plausible `[proxy, unverified]` | ✓✓ Fish Creek Provincial Park: large, real ecology, and a natural fit for the client's "parks agency" partner | ✓✓ station 20 m from the anchor; 11 stops within 400 m; Red Line direct to downtown | ✗ Ward 13: 11.0% under $40k, the lowest of the five. Kids would ride the CTrain in from other parts of the city | ✓ no regulatory flood mapping within 250 m of the anchor | ✓ room for two approaches; Macleod Trail and the LRT are the noise sources `[proxy, unverified]` | S-CRI (City and Regional Infrastructure) at the station | **Drill down** |
| **E. Forest Lawn, Elliston Park edge** | ✓ large, lower-cost parcels in East Calgary `[proxy, unverified]` | ~ Elliston Park is a stormwater lake with manicured parkland: usable, but thinner ecology than B, C or D | ~ nearest stop 488 m; 11 stops within 800 m; nearest CTrain 4.0 km. The 17 Ave SE MAX Purple BRT is close `[proxy, unverified]` | ✓ Ward 9: 24.7% under $40k. Forest Lawn itself is one of the city's lower-income communities, so it is closest to the mission `[proxy, unverified]` | ✓ only the lake itself shows as "Normal River Channel" | ✓ room for two approaches; 17 Ave SE traffic `[proxy, unverified]` | S-CRI at the park anchor | **Hold**: mission-first runner-up |

How to read the anchors: A and B are Ben's actual parcels, measured at the parcel centroid. C, D and E use an OSM-geocoded point (the sanctuary, the station, the park), so their land-use and flood cells describe the landmark, not a lot. A lot at the edge will differ; Stage 2 fixes that.

**Map views** (satellite, links only per the imagery convention):
- [A](https://www.google.com/maps/@51.038723,-114.076476,300m/data=!3m1!1e3)
- [B](https://www.google.com/maps/@51.052571,-114.076107,400m/data=!3m1!1e3)
- [C](https://www.google.com/maps/@51.027895,-114.006957,1200m/data=!3m1!1e3)
- [D](https://www.google.com/maps/@50.923014,-114.07307,1200m/data=!3m1!1e3)
- [E](https://www.google.com/maps/@51.033572,-113.939943,1200m/data=!3m1!1e3)

#### Named trade-off

The course sample asks for a **central location**, and the client needs **transit** for kids who arrive alone. The precedents (Lesson 2, OQ 6) argue for **land with real ecology**. No central lot has both.
- **B** is the best central option. It borrows its ecology from Prince's Island but pays for it with a stacked building, underground parking and no cluster parti.
- **D** keeps transit at full strength and gains land and a provincial park, but it moves the centre 13.6 km south into the most affluent ward of the five. The kids travel to it rather than it sitting among them.
- **E** is the mission-first answer: nearest to the kids, cheap land, weaker ecology, bus rather than CTrain.

The defensible reading is that transit, not centrality, is the real client need. That makes D a legitimate answer to "central" and keeps B as the downtown test.

#### Cuts, documented

- **A (Beltline) is cut.** At 0.10 ha it can't hold the compact floor (0.35 ha), let alone the brief's outdoor program, and it has no ecology. It still earns a place in the final argument as the urban control: it shows why the youth centre can't be a downtown infill tower.

</details>

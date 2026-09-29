# Site search — Cairn Youth Centre (RAIC 400)

*Stage 1 (zone scan) drafted 2026-09-25, "light" pass. Stage 2 (parcel drill-down) not started — it waits on Ben's pick of zones below. City: Calgary (confirmed by Ben 2026-09-25).*

**Data provenance.** Every number in the zone table comes from `data/zone_scan.py` → `data/zone_scan.json`, queried live from City of Calgary Open Data (Socrata): assessments/parcels `4bsw-nn7w`, land-use districts `qe6k-p9nh`, CTrain stations `2axz-xm4q`, transit stops `muzh-c9qc`, regulatory flood map `tp6q-x2v7`, 2016 census household income by ward `wj3a-wgmh`. Ben's two parcels are stored as GeoJSON in `data/`. Distances are **straight-line**; walking is roughly 1.3× longer. Cells marked `[proxy, unverified]` are informed impressions, not checked facts.

## Selection criteria (from client motives + brief)

| # | Motive | Weight | Source |
|---|---|---|---|
| M1 | **Land for the program:** enough ground for the building plus parking, bus drop-off, service yard, play yard and outdoor basecamp, ideally with room for a cluster/courtyard parti | **H** | `00_Brief.md` site requirements; precedent Lesson 2; OQ 6 |
| M2 | **Real ecology on or next to the site** for the field-science ground (W2's fail test) | **H** | Driver W2; OQ 6 |
| M3 | **Transit:** kids arrive on their own, some staff and families don't drive | **H** | Client profile ("inside Calgary, reachable by transit") |
| M4 | **Near the kids Cairn serves** (kids facing hard circumstances, low-income families) | M | Client profile; mission |
| M5 | **Flood risk** kept off the building footprint | M | Calgary 2013 flood; residential use, overnight sanctuary |
| M6 | **Two separable approaches** (public front plus a discreet sanctuary intake) and a calm acoustic setting | M | Driver W3; OQ 9 |
| — | Drive to Kananaskis for expedition weeks | dropped | Every zone is 67–76 km straight-line from the Barrier Lake gateway. It doesn't discriminate, so it gets no column. |

### How much land the program needs (M1)

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

## Stage 1 — zone scan

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

### Named trade-off

The course sample asks for a **central location**, and the client needs **transit** for kids who arrive alone. The precedents (Lesson 2, OQ 6) argue for **land with real ecology**. No central lot has both.
- **B** is the best central option. It borrows its ecology from Prince's Island but pays for it with a stacked building, underground parking and no cluster parti.
- **D** keeps transit at full strength and gains land and a provincial park, but it moves the centre 13.6 km south into the most affluent ward of the five. The kids travel to it rather than it sitting among them.
- **E** is the mission-first answer: nearest to the kids, cheap land, weaker ecology, bus rather than CTrain.

The defensible reading is that transit, not centrality, is the real client need. That makes D a legitimate answer to "central" and keeps B as the downtown test.

### Cuts, documented

- **A (Beltline) is cut.** At 0.10 ha it can't hold the compact floor (0.35 ha), let alone the brief's outdoor program, and it has no ecology. It still earns a place in the final argument as the urban control: it shows why the youth centre can't be a downtown infill tower.

## Stage 2 — parcel drill-down

*Not started. Proposed scope, pending Ben's call:*

1. **B:** read DC bylaw 91D2008 (permitted uses, height, density) and check whether a youth centre with overnight rooms fits it. Pull the provincial 1:200 / 1:500 flood extents. Run the envelope-utilization math on 3,028 m².
2. **D:** find the actual parcels at the Fish Creek–Lacombe station edge (land use, area, owner type), and check the park-edge adjacency per the adjacency rule.
3. **E (if kept):** the same parcel search along the 17 Ave SE / Elliston edge, and confirm the MAX Purple stop distances.
4. For each parcel: the Stage 2 scorecard plus envelope-utilization (target 2,480 m² gross ÷ buildable GFA).

| Parcel | Land-use verified? | M1 | M2 | M3 | M4 | M5 | M6 | Envelope-utilization | Caveats | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

Recommendation + runner-up: *(after Stage 2)*

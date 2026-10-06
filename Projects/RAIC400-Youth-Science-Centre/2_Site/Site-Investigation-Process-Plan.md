# Site investigation process plan: two-site test fit

*Cairn Youth Centre, RAIC 400. Drafted 2026-10-05 as a plan only. Nothing here has been run, and no spine files have been changed. Student coursework with a fictional client: "verified" means a public dataset was checked on 2026-10-05, not a survey, title search or conversation with the City.*

**Purpose.** For each of the two favourite sites, get accurate linework and topography, draw the land we can actually build on, then put the program on it to answer one question: does it fit, and at how many storeys? The instructor's point (OQ 25) is that this test may decide which site is viable.

**Worked examples.** Deck **A Inglewood** (data id **C**) and deck **C Loch McKinnon / Shriners** (data id **I**). The process is the same for B Glenmore Landing (F) and D Glenbow Ranch (N); notes on those two are in the source table.

---

## 1. What we already have, and what's missing

| Already in `2_Site/` | Good for | Not good enough for |
|---|---|---|
| `data/stage2_scan.py` + `_cache_stage2_raw.json` (City SODA, Overpass, FHIP, CDEM, with retry and caching) | Site facts, flood at points, dry-area grids (20–50 m) | Linework. The dry grid is 20–50 m cells, not lines |
| `presentation/make_terrain.py` (AWS Terrarium DEM, z14/z15, ~10–20 m effective in Canada, CDEM/SRTM based) | Oblique slide views | Siting. It can't show a 1 m step or a top of bank |
| NRCan CDEM spot heights and 300 m profiles | "Flat" or "slopes 3% to the lake" | Contours, grading, a stepped section |
| `4_Space-Planning/room-squares/Cairn_Room-Squares.dxf` (1:1, metres, one layer per zone, v0.7) | Paper and AutoCAD space planning | Outdoor program (not in it yet) |
| `data/parcel_633-15-AV-SW.geojson`, `parcel_708-1-AV-SW.geojson` | Nothing here. These are Beltline lots from an earlier scan | Don't reuse them |

**Tool status for this project.** Cairn has no `Massing-Studio.html`, `Test-Fit-Studio.html` or `Design-Studio.html` instance yet (Nonimuss has all three). Use the existing generators and receivers: the skill's Massing Studio spec already carries `site.lotPolygon`, `site.setbackPolygon`, `site.latLong` and `site.origin` in `massing-interchange/v1`. We feed those fields from the new site base rather than building a separate site tool.

---

## 2. Data sources per site

Checked 2026-10-05 against the live catalogues (City Socrata catalogue API, NRCan STAC search, point-in-polygon tests at both anchors).

**Jurisdiction.** Both worked examples are inside the City of Calgary. Loch McKinnon (51.1018, -114.2395) falls inside the City Boundary polygon (`erra-cqp9`), on parcel 5225 101 St NW, S-FUD. It is **not** Rocky View County. Inglewood is on parcel 2405 9 Av SE, S-R. So one set of City sources covers both. Glenbow Ranch (N) is outside the City (point test returns nothing): Rocky View County and Alberta Parks.

| Layer | Source (dataset id) | Resolution / currency | C Inglewood | I Loch McKinnon | Limits |
|---|---|---|---|---|---|
| Property lines | City Current Year Property Assessments (Parcel) `4bsw-nn7w`, multipolygon | Assessment parcels, updated 2026-10-01 | verified (2405 9 Av SE, 4,419 m²) | verified (5225 101 St NW, 414,022 + 12,140 m²) | Assessment parcels, not legal survey lines. Fine for coursework; say so on the sheet |
| Land use | Land Use Districts `qe6k-p9nh` | Current | verified S-R | verified S-FUD | Neither district lists this use (see §4) |
| Roads | Street Centreline `4dx8-rtm5` (centrelines); OSM via Overpass for curbs, paths, rail | Current | verified (81 features in the 1.3 km box) | verified (62) | Centrelines only. Road edges come from OSM or are traced off imagery |
| Buildings | Buildings `uc4c-6kbd` (2D roof outlines); 3D Buildings – Citywide `cchr-krqg` (2023) | Outlines 2026; 3D 2023 | verified | verified (17 within 400 m) | Roof outlines, not walls. Fine at 1:500 |
| Water edges | Hydrology `47bt-eefd` (polygons), Hydrology – Line `5fk8-xqeu` (2016), Parks Water Bodies `d3xr-mc4m` | Mixed | likely (Bow, sanctuary lagoon) | verified (2 features in 400 m) | Water edge moves; check against imagery and the DTM |
| Riparian / ER setback | Riparian Areas – Variable Width `7mc8-zqjc`; Riparian Management Zones `fyid-twcw`; Rivers and Streams – ER Setback Guideline `8xc4-74f9` | City riparian mapping | verified (303 / 54 / 2 features) | verified (89 / 15 / **0**: no ER guideline line on the lake) | ER policy widths are variable (base + slope modifiers). The lake has no guideline line, so we assume one (§4) |
| Flood | City Regulatory Flood Map `tp6q-x2v7`; 1:1000 Flood Map `65h7-2au2`; Flood Hazard Steplines `mngv-ufjz` (design flood elevations, 2017); Alberta FHIP via geospatial.alberta.ca (already in `stage2_scan.py`) | Regulatory, 2017–2026 | verified (fringe/floodway within 250 m; 1:500 at the lot) | verified (fringe within 250 m) | Steplines give an elevation to set the ground floor against. Check the vertical datum (§6 risks) |
| Trees | Tree Canopy 2022 `mn2n-4z98` (polygons); Public Trees `tfs4-3wwa` (points, City-managed only); Citywide Land Cover `as2i-6z3n` | 2022–2026 | verified (3,226 canopy / 2,109 trees) | verified (2,103 / 133) | Public Trees misses private trees (most of I). Canopy polygons cover all ownership. Heights come from the DSM (below) |
| Natural areas | Natural Areas `szzc-mugz`, Habitat `7tax-5vsg` | Current | used in Stage 2 | used in Stage 2 | |
| **Terrain, primary** | **NRCan HRDEM, LiDAR project "NRCAN-Calgary_West_utm11_2020-1m"**, DTM and DSM, cloud-optimized GeoTIFF on `canelevation-dem.s3.ca-central-1.amazonaws.com` | **1 m, 2020**, EPSG:3979 | verified (tile covers anchor) | verified | Range requests work (HTTP 206), so a windowed read pulls only ~2 km² per site, a few MB. No big download. 2020 surface: misses anything graded since |
| Terrain, cross-check | City Digital Elevation Model (DEM) – ASCII 2m `eink-tu9p`, LiDAR 2022–2024, EPSG:3776 | 2 m, newer | covers (citywide) | covers | **1.2–1.5 GB zip, no windowed access.** Only if Ben approves the download. 1 m and 20 cm versions are on CityOnline, not the open portal |
| Imagery underlay | Esri World Imagery tiles (already cached by `make_slide_maps.py`) | ~0.3–0.5 m | yes | yes | Credit line required. arcgisonline drops; tile cache + retry already exists |
| Fallback | OpenStreetMap (Overpass, three mirrors already coded) | Varies | yes | yes | Use for paths, rail, curbs; never for property lines |

**Other two sites.** F Glenmore Landing: same City sources. N Glenbow Ranch: Rocky View County publishes an online Atlas only; parcel data is bought from County GIS Solutions (unverified price). For N, the park boundary would come from Alberta Parks open data (unverified), and HRDEM coverage is likely (a test point 3.5 km north of N is inside the same Calgary_West tile; N itself not tested).

---

## 3. Outputs: what Ben gets, in which software

**Coordinate system: NAD83 / Alberta 3TM 114 W (EPSG:3776), metres.** Why:
- The City's own CAD and the 2 m DEM are delivered in it, so City data needs no reprojection and any City drawing Ben finds will line up.
- Its central meridian is 114°W. Both sites sit within 0.25° of it, so scale distortion is negligible.
- UTM 11N works too (scale error ~0.1 mm/m here), but Inglewood is 0.01° from the UTM 11/12 line. NRCan itself splits Calgary into "West utm11" and "East utm12" tiles there. 3TM 114 avoids the zone edge for every site, N included.
- Catch: northings are ~5.65 million m. AutoCAD and Revit lose precision far from the origin. Keep the DXF in true 3TM coordinates, and record a **site origin** (a round 3TM point near each anchor). Revit's survey point and the tool's `site.origin` both use that origin, so the model works in small local numbers.

**Per site, written to `2_Site/base/<id>/`:**

| File | Contents | Opens in |
|---|---|---|
| `Cairn_Base_<id>.dxf` | Layers: `PROP-LINE`, `LANDUSE`, `ROAD-CL`, `ROAD-EDGE` (OSM), `BLDG-EXIST`, `WATER-EDGE`, `FLOOD-FLOODWAY`, `FLOOD-FRINGE`, `FLOOD-1-500`, `RIPARIAN`, `TREE-CANOPY`, `CONTOUR-MAJOR` (5 m), `CONTOUR-MINOR` (1 m; 0.5 m on flat C), `SLOPE-OVER-15`, `ENV-*` (one per envelope constraint, §4), `ENV-BUILDABLE`, `SITE-ORIGIN`, `NORTH`, text with source and date | AutoCAD (base for room squares), Bluebeam (PDF plot for markups), Revit (Link CAD) |
| `dtm_<id>.tif`, `dsm_<id>.tif` | HRDEM 1 m windows, reprojected to 3TM | QGIS if wanted; source for everything below |
| `terrain_<id>.obj` (+ `.png` imagery drape) | Ground mesh, ~600 × 600 m at 2 m spacing, local metres from the site origin | Blender (via blender-mcp), Revit (as a fallback) |
| `envelope_<id>.geojson` | Buildable polygon, lot polygon, per-constraint polygons, areas | Massing Studio `site.lotPolygon` / `site.setbackPolygon` |
| `fit_<id>.json` + a section in the write-up | Storeys vs footprint vs site need, per gross area | Ben's review; slides |

**Scripts.** No parallel pipeline. One new script, `2_Site/data/site_base.py`, imports the helpers that already exist: `stage2_scan.get / soda / overpass / fhip` (caching and retry), `make_slide_maps` (tile cache and imagery). It writes everything above, with raw responses cached so a rerun works offline. Same pattern `make_terrain.py` already uses. Libraries: `ezdxf` (installed), plus `shapely`, `pyproj`, `rasterio`, `contourpy` (not installed; small pip install, wheels for Python 3.14 to confirm). The mesh is written with numpy as plain OBJ, so `trimesh` isn't needed. Site rules live in one editable block, `ENVELOPE_RULES` per site, so Ben can change a setback and rerun.

**Outdoor program squares.** Add an `OUTDOOR` zone to the existing `make_room_squares.py`, which writes into the existing DXF. Don't start a second room-squares file.

---

## 4. Buildable envelope

Each constraint is its own layer and its own line in an "area lost" table, so Ben can see which rule bites. The buildable area is what's left after all of them. **Everything marked A is a course assumption.** No bylaw permits this use on either site (S-R and S-FUD both need a redesignation to S-CI or Direct Control), so the rules below are what we choose to argue, stated plainly on the sheet.

| Constraint | Rule | Basis | C Inglewood effect | I Loch McKinnon effect |
|---|---|---|---|---|
| **Site boundary** | C: lot parcel 2405 9 Av SE + the dry, mown lawn of 2425 9 Av SE outside the sanctuary forest. I: a **1.5–2.0 ha carve-out** from the 41 ha parcel, on the upper terrace between rail and lake | **A.** A design decision, not data. On I the boundary *is* the first site move | ~0.7 ha (Stage 2 estimate) | Set by Ben |
| Property setbacks | 6 m from all property lines; 10 m from any road right-of-way | **A** (camp-scale stand-in for S-CI; check LUB 1P2007 Part 9 Div 5 if the instructor wants the bylaw) | Bites hard on a 0.44 ha lot | Negligible |
| Flood: building | No building footprint in floodway or flood fringe (City map or FHIP, whichever is larger). Ground floor ≥ 0.5 m above the 1:100 design flood elevation (Steplines). Beds above the 1:500 level | Regulatory map + **A** freeboard | Lot is inside FHIP 1:500: raise the ground floor, no basement, beds upstairs | Fringe within 250 m; keep nodes on the terrace |
| Flood: outdoor | Sleep-out ground and fire circle outside the 1:100 extent; build yard may sit in the 1:500 | **A** | Sleep-out must stay on the lot side | Sleep-out on the terrace, not the lakeshore |
| Riparian | City ER Setback Guideline where mapped; elsewhere 30 m from the water edge or top of bank, whichever is further | City data + **A** (ER policy is variable width; 6 m is a common minimum, 30 m is our conservative stand-in) | Bow and lagoon edges | **No mapped ER line on the lake**: the 30 m assumption governs |
| **Water hazard for kids** (OQ 24) | No door, bedroom window or unsupervised outdoor room within **50 m of the river** or **30 m of still water**; fenced, gated edge between program and water; raft launch only on **still water**, supervised, reached by one controlled path | **A**, from the instructor's crit. The raft launch is only possible where the water is still | **River site: no raft launch.** Lagoon access stays a supervised field-science visit | Raft launch possible on the lake; gate it from the basecamp |
| Slope | > 15%: no building, no outdoor rooms. 8–15%: building may step (trail door one level down). Coach loop, parking and accessible routes ≤ 5% | **A** (common practice thresholds) | Flat (< 1%): no effect | Terrace falls 3% then steeper to the lake: check the 8–15% band at the trail door |
| Trees to keep | No building within the drip line + 3 m of canopy polygons over 8 m tall (DSM − DTM) | **A** | Keep out of the sanctuary forest | Lakeshore tree row stays |
| Rail | No bedrooms within 75 m of the CPKC track; nodes on the far side of the building | **A** (noise and vibration; check FCM/RAC guidelines if challenged) | Rail at 65 m: bites | Siding at ~140 m: OK |
| Height / coverage | Max 3 storeys, 13 m; max 50% coverage of the carve-out | **A** (Stage 2 assumed 2 storeys, driver W5) | Decision 4 below | Decision 4 below |

**C only: parking replacement.** The C lot is the sanctuary's only public parking. Whatever the building takes, the plan has to give back as shared parking or a coach bay the sanctuary can use. This goes into the site need in §5 as a separate line, not hidden.

---

## 5. Fit and storeys

### 5a. Arithmetic first (`fit_<id>.json`)

Gross area is a parameter: **G = 1,800 / 2,200 / 2,500 m²** (v0.7 today is 2,475).

- The gym (360 m² net, ~400 m² gross, double height) sits on the ground and leaves a void above it.
- **Ground-bound program** has to touch the ground whatever the storey count: gym, entry, public washrooms, reception, dining and kitchen, shipping, the whole expedition zone, garage, mechanical, janitor. That's ~916 m² net, **≈ 1,190 m² gross** at 1.30 (≈ 1,100 if mechanical goes to a basement, which can't happen at C).
- Footprint F for n storeys: F = max( (G + (n−1) × 400) / n , ground-bound gross ).

| Gross G | 1 storey | 2 storeys | 3 storeys |
|---|---|---|---|
| 1,800 | 1,800 | 1,190 (ground-bound limit) | 1,190 |
| 2,200 | 2,200 | 1,300 | 1,190 |
| 2,500 | 2,500 | 1,450 | 1,190 |

**What the table says:** above two storeys the footprint barely shrinks, because the gym and the ground-floor program set a floor of ~1,100–1,200 m². Condensing the program shrinks the upper floors, not the footprint, unless the gym shrinks. On a tight site the storey count matters less than the gym and the outdoor ground. (This is an estimate; Ben confirms the ground-bound list at Gate 3.)

**Outdoor gradient and arrival** (all **A**, concept-grade, refined at Gate 3):

| Item | m² | Note |
|---|---|---|
| Coach drive-through bay + turnaround (12–14 m coach) | ~600 | Drive-through, since a coach can't turn in a full lot |
| Parking: ~15 staff, ~8 visitors, 5–10 vans next to the garage | ~850 | ~28 m² per stall with aisle |
| Service drive and loading | ~250 | Never crosses arrival or play |
| Build / test yard | ~400 | Next to the maker lab |
| Fire circle (with clearance) | ~250 | FireSmart clearance to building and canopy |
| On-site sleep-out ground (one node + leader) | ~400 | Outside the 1:100 flood extent |
| Outdoor kitchen | ~80 | |
| Bike storage (covered, ~40 bikes) | ~80 | |
| Basecamp teaching yard | ~300 | |
| **Outdoor total** | **≈ 3,200** | Raft launch is linear (path + landing), not area |

**Site need** = F + outdoor + 25% for paths, grading and planting. At G = 2,500 on two storeys: (1,450 + 3,200) × 1.25 ≈ **5,800 m²**, plus at C the replaced sanctuary parking (Stage 2: the lot holds ~3,170 m² of asphalt; replace whatever count Ben assumes). Verdict bands as in Stage 2: need / buildable < 0.5 comfortable, 0.5–0.9 fits, 0.9–1.1 tight, > 1.1 doesn't fit.

### 5b. The honest test: squares on the base, then a stack

1. **Room squares on the base (AutoCAD).** XREF `Cairn_Room-Squares.dxf` (already 1:1 metres) into `Cairn_Base_<id>.dxf`. Ben arranges a ground floor inside `ENV-BUILDABLE` and an upper floor beside it (offset in model space, labelled). Outdoor squares go outside the building but inside the boundary. Coach and parking go on ≤ 5% ground. Ben plots to PDF and marks up in Bluebeam. The arithmetic says "fits"; the squares show whether it fits *in that shape*. (Nonimuss proved the gap: area fit, shape didn't.)
2. **Massing stack (Massing Studio).** Generate Cairn's Massing Studio instance through the skill, with `site.lotPolygon`, `site.setbackPolygon` (= `ENV-BUILDABLE`), `site.latLong` and `site.origin` from `envelope_<id>.geojson`. The **cap meter** is set to G, so the same file tests 1,800 / 2,200 / 2,500 by changing one number. The sun section uses the DTM profile instead of a flat ground. Make one scheme per site, two to three volumes (gym block, learning block, node wing), using the arrangement from step 1.
3. **Test-Fit Studio** (optional at this stage). Seed from v0.7 to refine one floor. Note: the Massing x,z ↔ Test-Fit x,y axis match is still unverified in the tool. Check it on this first real site use.
4. **Revit (Ben).** Link the DXF (shared coordinates from `SITE-ORIGIN`). Make a Toposolid from the imported contour layers (Revit 2024+ "Create from Import"; confirm Ben's version). Run the existing receiver (`_Export-Receivers/Revit/Massing-Import.dyn` + `MassBox.rfa`) on the Studio's Export JSON. The receiver reads only `volumes[]` and `site.storeys[]`, so terrain comes from the DXF link, not the JSON. No Dynamo wiring needed for this step.
5. **Blender (Claude via blender-mcp).** Import `terrain_<id>.obj` with the imagery drape. Run `_Export-Receivers/Blender/import_massing.py` on the same JSON (`site.latLong` now filled, which closes the receiver's known gap). Use it for a sun study and two views from the trail door and the arrival road. Blender stays for views; the fit is decided in AutoCAD and the Studio.

---

## 6. Sequence, gates, effort

| Step | Who | What | Effort | Gate: Ben checks |
|---|---|---|---|---|
| 0 | Ben | Answer the decisions in §7 | 15 min | — |
| 1 | Claude | Install the four libraries (ask first); write `site_base.py`; pull and cache C and I; write DXF, DTM/DSM, mesh | 3–4 h for the first site, ~30 min for the second | **Gate 1:** open the DXF in AutoCAD. Layers present? Property line sits on the imagery? One spot height matches CDEM (1,037 m at C, 1,084 m at I, within ~1 m) |
| 2 | Claude | Envelope layers and the area-lost table, from `ENVELOPE_RULES` | 1–2 h | **Gate 2:** read the assumptions table. Change any rule, rerun (minutes) |
| 3 | Claude | `fit_<id>.json` and the §5a tables per site; add `OUTDOOR` squares to `make_room_squares.py` | 1 h | **Gate 3:** confirm the ground-bound list and the outdoor sizes. First verdict per site |
| 4 | Ben | Room squares on each base in AutoCAD; PDF to Bluebeam | 1–2 h per site | **Gate 4:** does the ground floor fit inside `ENV-BUILDABLE` with the coach loop and sleep-out ground? Pin-up ready |
| 5 | Claude, then Ben | Generate the Massing Studio instance with site fields; one stack per site; Export JSON → Revit receiver (Ben) and Blender (Claude) | 2–3 h Claude, 1 h Ben | **Gate 5:** storeys chosen per site; section and sun read right on real ground |
| 6 | Claude drafts, Ben approves | `2_Site/Stage-3_Two-Site-Test-Fit.md`, decision-log row, OQ 25 update (spine edits only with Ben's OK) | 1 h | **Gate 6:** site viability call for the instructor |

Total: about one working day of Claude time, and half to one day of Ben time, across both sites.

**Risks.**

| Risk | Effect | Mitigation |
|---|---|---|
| CRS mix-up (HRDEM is EPSG:3979; City is 3776; OSM is lat/long) | Linework off by metres or kilometres | Reproject everything to 3776 in the script, then check at Gate 1 against imagery and a known building corner |
| Datum: NAD83 (original) vs NAD83(CSRS); vertical CGVD28 vs CGVD2013 | Horizontal ~1 m; flood elevations vs DTM off by tens of cm | Record the datum on each layer. Compare the stepline elevation with the DTM at a flat spot; state the offset on the sheet |
| DEM age (HRDEM 2020) | Misses recent grading | Cross-check with the City 2 m DEM (2022–24) only if Ben accepts the 1.5 GB download |
| Water edge and canopy drift | Buffers measured from the wrong line | Draw the water edge from the DTM (water surface is flat in LiDAR) and compare with the Hydrology polygon |
| Assessment parcels aren't legal lines | Setback numbers slightly off | Coursework label on the sheet: "assessment parcel, not surveyed" |
| Network drops (arcgisonline tiles, Overpass, SODA) | Script stalls mid-run | Reuse existing retry and cache; imagery is optional (linework comes from the City and NRCan, not Esri) |
| Python 3.14 wheels for rasterio/shapely | Install fails | Fall back to a Python 3.12/3.13 venv; ezdxf and numpy are already in place |
| Big rasters in a public repo | Repo bloat (licences allow sharing with attribution: Open Government Licence – Canada; City of Calgary Open Data terms) | Keep `dtm/dsm/*.tif` and `_raw/` out of git; ask Ben before touching `.gitignore` |
| Program changes after the dream session | Fit numbers go stale | Gross is a parameter; rerun step 3 in minutes |

---

## 7. Decisions Ben needs to make first

> **Ben's answers, 2026-10-05:** (1) sites are **B Glenmore Landing (F) and A Inglewood (C)**, not A and C; (2) boundary = the general property lines of the lot for now; (3) gross 2,250–2,500 m²; (4) up to 3 storeys; (5) 50 m / 30 m water setbacks accepted to start; (6) main entrance on the ground; also study site access and approach; (7) **no parking replaced at Inglewood: place the building beside the lot, in the field areas** (supersedes the C-parking paragraph in section 4 and the parking allowance in section 5a); (8) installs and downloads: not approved yet, ask first; (9) deliverable is a **flat site DXF plus a separate topo file**; Ben builds the Revit topo himself. **Nothing starts without Ben's go-ahead.**

1. **Confirm the two sites**: A Inglewood (C) and C Loch McKinnon (I)?
2. **Site boundary**: for C, lot only or lot + lawn? For I, how big a carve-out, and where on the terrace?
3. **Gross area range**: keep 1,800 / 2,200 / 2,500, or wait for the dream session's number?
4. **Height cap**: 2 storeys (Stage 2's assumption) or allow 3?
5. **Water-hazard distances**: accept 50 m from river, 30 m from still water, raft launch only on still water?
6. **Which rooms must be on the ground?** The list in §5a sets the minimum footprint.
7. ~~**Parking at C**: how many sanctuary stalls to replace?~~ None (Ben, 2026-10-05).
8. **Approve** the pip install (shapely, pyproj, rasterio, contourpy), and say yes or no to the 1.5 GB City DEM download.
9. **Software for the stack**: Massing Studio first, Revit first, or both? Also confirm your Revit version for Toposolid.

---

*Sources checked 2026-10-05: City of Calgary Open Data catalogue (data.calgary.ca) for dataset ids above; City Boundary and Parcel point tests at both anchors; NRCan datacube STAC (`hrdem-lidar`, `hrdem-mosaic-1m/2m`) item search at each anchor and an HTTP range test on the Calgary_West DTM; City Environmental Reserve Setback Policy and Riparian Areas pages (calgary.ca/riparian); Rocky View County Atlas (rockyview.ca/maps).*

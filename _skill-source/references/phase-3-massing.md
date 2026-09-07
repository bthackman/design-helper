# Phase 3 — Building massing

Output: `3_Massing/Massing-Options.md` — minimum three genuinely different options, scored, with a recommended direction logged as a decision — **plus an interactive Massing Studio** (`3_Massing/Massing-Studio.html`) that instruments the options so the architect can steer them, not just pick one.

## Generate wide first
Propose massing partis for the user to react to — bar, courtyard, tower-on-podium, terraced, split/linked volumes — filtered by the envelope from phase 2 and lessons from phase 1. Three options that share one parti are one option; force real difference (different section, different ground relationship, different organization).

## For every option, run the numbers
Footprint × storeys → GFA; compare to required GSF from the brief (with grossing factor); check against envelope (setbacks, height, FAR). Compute, don't estimate. An option that doesn't fit the program or the envelope is either dead or requires a logged decision to change the brief/seek variance.

## Score against drivers
Each option gets a driver scorecard (✓ / ~ / ✗ with one line of why per driver). This is where drivers earn their keep — if every option scores identically, the drivers are too vague, and that's worth surfacing. Where a score rests on the geometric proxy rather than a real test — the same honesty already required of the Studio's driver proxies — the rationale line carries `[proxy, unverified]` too, so the scorecard doesn't look more certain than the proxy behind it.

## Converge
Recommend a direction (an option or a named hybrid) with rationale. The user decides; the decision — including rejected options and why — goes to the decision log. Park, don't delete, the losers: mark status parked/dead so they're recoverable when the client asks "did you consider...?" Log the same call to `Library/Parked-Ideas.md` (project, option, why it died, reconsider-if) — that's what makes "have we tried this anywhere before" answerable across projects, not just within one.

## The Massing Studio (interactive instrument) — evolves the phase from *pick* to *steer*

Build a single self-contained HTML tool (`Massing-Studio.html`, Three.js + Chart.js from CDN) so the architect works the massing, not just reviews it. **Cost principle that governs what's built-in vs. on-request: anything that runs client-side in the browser is a one-time build then free forever; anything that needs the model in the loop on every use costs tokens each time.** Build the first kind in by default; gate the second kind behind an explicit ask.

### ALWAYS build in (client-side — one-time cost, then free)
1. **Steerable volumes + live driver read-out.** Volumes adjustable by sliders (E–W, N–S, width, depth, height, rotate-90, **base-elevation for stacking a room on a room**, and a **glazing % slider** 0/25/50/75/100). Glazing must feed the thermal proxies (glass ≈ 3.5× a wall's loss) — **but which way that cuts is climate-conditional, not universal.** In a temperate climate (this proxy's default assumption): a winter-thermal driver falls and a daylight driver rises with more glass — the real tension, live. Near the equator, that relationship inverts or goes flat: there's no winter heat-loss season to trade against, and more glazing (especially E/W-facing) is more often a *cooling/glare* liability than a winter-gain benefit — check `phase-2-site.md`'s latitude-conditional sun-study branch before trusting the default proxy direction on a non-temperate site, and flag the proxy `[proxy, unverified]` if the climate regime hasn't actually been confirmed. Support multi-storey via base-elevation with per-storey cap accounting (footprint-only coverage). On every change, recompute and display: a **cap meter** (dwelling floor vs. the hard program cap, red when over), coverage %, enclosed volume, façade/envelope area, build-simplicity (volume count), and **concept-grade driver proxies** (a geometric heuristic per driver + any project-specific gate like a cap-safety score). Label the proxies honestly as a live gut-check, not analysis — but wire them to the real drivers so the model *talks back*.
2. **Mandatory sun-tested section.** A 2D section cut (movable, both principal axes) drawn from the same geometry, with summer/winter noon sun rays at the site's computed altitudes and the key obstruction (neighbour ridge, forest wall) shown — so the sectional lessons from phase 1 (buffer-zone, roof daylight) are worked at massing, not deferred. Section is not optional; a massing with no section is half-done.
3. **Trade-space plot.** A small scatter/bubble chart placing every option on the two or three competing objectives the project actually trades (e.g. cap-safety × a signature driver, bubble = winter energy), with a **live point** that moves as the architect edits — so hybrids are seen relative to A/B/C and no driver is traded away invisibly.
4. **⤓ Export JSON — neutral interchange for downstream tools.** Beside the existing share-edits/export button, a button that emits `massing-interchange/v1` (schema of record: `Massing-Export-Roadmap.md` at the tool root) — the current scheme's boxes plus site header, structured for the Rhino/Revit/Blender receivers to consume without touching the Studio itself. Fixed shape, one-time build, no ongoing cost:
   - `axes`: x=East(+), z=South(+), y=Up, north is −z; box `x,z` = **SW corner** in plan (any rotation baked into `w`/`d`, not a separate flag).
   - `volumes[]`: `{id, type, x, z, w, d, h, base, glaz}` (+ `clerestory:true` where set).
   - `site`: `{origin, northDeg, latLong, lotPolygon, setbackPolygon, lotArea, storeys}`. **`latLong` is required, not optional** — pull it as the site polygon's centroid (or the geocoded site point, if the site phase already produced one) from `2_Site/data/*.geojson`; downstream solar/sun-study receivers (e.g. the Blender template+import pair under `_Export-Receivers/Blender/`) need real coordinates and have no other source for them. `storeys` is inferred from the distinct base elevations present in the current scheme, not fixed.
   - `program`/`metrics`: whatever the Studio already computes for the cap meter/coverage — pass the live numbers through, don't recompute.

### OPTIONAL — offer, but run only on request (model-in-the-loop — real recurring token cost)
- **Sketch / napkin → option.** Architect uploads a hand parti; reconstruct it as measured geometry, score and critique it. Costs a vision ingest + reasoning every time — worth it, but ask first.
- **Architect-collaborator (multi-voice) mode.** Beyond the standard one-shot gate below: convene the standing three-voice roster — **Design Collaborator** (generative protagonist; calibrated to MacKay-Lyons + Safdie as sensibilities, not pastiche), **Client** (from the client profile), **Studio Critic** (~75% RAIC review / 25% DP+Code) — in escalating rounds that *always end with the Design Collaborator turning critique into dimensioned, testable moves*. Full spec in `references/collaborator-voices.md`. On-request / token-taxing; usable in any phase, not just massing.
- **Real-drawing precedent overlay.** Fetch and overlay actual precedent plans/sections at scale beside an option. Fetch + image ingest per precedent = expensive; a cheap *schematic* overlay redrawn from saved precedent cards is the low-cost substitute.

### Studio hygiene
Self-contained single file; syntax-check the script before delivery; sanity-check that the driver proxies reproduce the written narrative for each option (the strong option should score strong on the drivers you claimed). Keep a simpler orbit-only viewer if useful. Link the Studio from `Massing-Options.md`.

## Gate questions worth asking (standard, always run)
What breaks if the program grows 15%? Which option is most resilient to the top open question? Is the recommended option the best one or the safest one — and is that the right trade here? Plus the hardest question a reviewer will ask about the recommended parti.

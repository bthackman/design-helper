# Handoff — Design Process Tool

Read this to pick up work **on the tool itself** (not any specific project) after time away. It's the
honest current-state read — what's solid, what's genuinely unfinished, and where to look for more detail.

## What's solid

Client discovery, Site (open-data pipeline + mandatory assessment battery), the Drivers-lock gate,
Precedents (two-layer search + source-dialect discovery + fetch-before-cite verification), and Massing
(interactive Studio + driver scorecards + sun-tested section) are built, folded into `SKILL.md`, and
pressure-tested end-to-end on a full pilot project — with real failures caught and fixed along the way
(dead source links, a phantom lot geometry error, a first precedent board that turned out to be
memory-biased toward international canon rather than actually searched).

## What's genuinely unfinished

1. **Materiality has a protocol now, run once, on an academic project.** `phase-5-materiality.md`
   was rewritten 2026-08-28 (candidate palettes, driver scorecard, value-engineering test, lock) and
   run for real on Nonimuss — see `Projects/Nonimuss-Residence/5_Materiality/Material-Palette.md`.
   Real finding from that run: the protocol's "promote back to the library" step assumes a built
   project confirms a material choice held up; an academic/hypothetical project never reaches that
   gate, so nothing has actually been promoted into `Library/Materials/` yet, and the starter set
   seeded that day is still exactly as drafted — `[proxy, unverified]`, not yet earned by a real
   failure the way every other phase's reference has been.
2. **Space planning has no interactive tool.** Massing got a full client-side Studio (live cap meter,
   sun-section, trade-space plot); space planning is still hand-drawn diagrams + prose. A "Test-Fit
   Studio" (place → steer, with a live doorway/clearance collision check) is the named next tooling
   target — not yet built.
3. **Exports don't exist.** Program → `.xlsx`, brief/drivers → `.docx`, boards/decision log → `.pdf` are
   all speced in `00_Tool-Concept-Spec.md`, none built.
4. **Export receivers are uneven.** Blender (`_Export-Receivers/Blender/`) is built and tested end-to-end
   — but only against a synthetic fixture, not yet a real project's massing. Revit is paused at a
   Dynamo-graph MVP (Autodesk's own API is read-only for now, so there's no near-term reason to push
   further). Rhino hasn't been started at all.
5. **Precedents check a personal Obsidian vault as their source of truth, not a folder in this repo.**
   `_skill-source/references/phase-1-precedents.md` points phase 1 at an external vault path
   (`Architecture/Architecture Design/` tree) before running a fresh web search. That integration is
   specific to the tool author's own setup — running this tool elsewhere means either pointing that step
   at your own reference library in the same way, or skipping it and relying on fresh web search only.
6. **Never tested against a real client engagement.** Every run so far has been an academic/hypothetical
   project. Real-regulatory cap arguments (arguing floor-area exclusions to an actual development
   authority, not a course instructor), real budget-as-a-driver workflows, multi-disciplinary
   consultant-team coordination, and confidentiality handling for real client data are all identified
   gaps — none yet exercised. See the backlog in `00_Tool-Concept-Spec.md` for the full list and reasoning.

## Session handoff — 2026-09-09, continued (Stage 0 built and verified — the existing sync is now visible, not just numeric)

Same day, immediately after the architecture-dream pass below. Ben agreed to a staged build-out of that pass's recommendation, broken into 8 checkpointed stages after a token/session-budget discussion; this is **Stage 0** — the cheap, independent fallback the dream pass recommended building regardless of whether the bigger merge (Stages 1–6b) ever happens: upgrade the *existing* file-based sync from a text-only advisory to something actually visible, without touching the underlying two-document architecture at all.

**Massing → Test-Fit direction** (`syncFromMassing()`, `Test-Fit-Studio.html`): now also captures each dwelling volume's real `w`×`d` per level (not just a derived area) from the interchange JSON, into `massingSync.volumesByLevel`. `render()` draws it as a dashed amber rectangle in the SVG plan — **deliberately centered on this level's own on-cap room bounding box**, not on any invented cross-tool site coordinate, since the Massing-`x,z` ↔ Test-Fit-`x,y` axis correspondence is still unverified (flagged in both existing sync functions and the dream pass) and a wrong position claim would be worse than today's safe text-only comparison. The label says so explicitly. New helper: `onCapBBox(level)`.

**Test-Fit → Massing direction** (`syncFromTestFit()`/`renderTestFitSync()`, `Massing-Studio.html`): new `ghostGroup` in the Three.js scene; `rebuildGhosts()` draws Test-Fit's per-level bbox (already computed by the existing advisory) as a dashed wireframe outline **anchored at the real Massing box's own (x,z) position** — same origin, drawn at the size Test-Fit's rooms actually need instead of the box's current size, for the same axis-correspondence reason as above. A floating label (reusing the existing `makeLabel()` helper) names the level and needed dimensions. Called from `refresh()`, so it stays live as other volumes are steered, same as everything else in that function.

Both directions: purely additive, advisory-only — nothing writes back into `state`/`rooms`; the existing text advisories are untouched, just no longer the only signal.

**Verified for real, not just balance-checked:** resized House to 13×10m in Massing, saved, synced in a fresh Test-Fit tab — the dashed rectangle rendered correctly labeled "13×10 m," zero console/page errors (screenshot `_UI/_playwright/qa-scratch/dir1_testfit_ghost.png`). Moved room `GU` to Upper in Test-Fit, saved, synced in a fresh Massing tab — two wireframe outlines rendered (Ground and Upper), `ghostGroup` correctly held 4 children (2 levels × line+label), zero console/page errors (screenshot `dir2_massing_ghost.png`). Both round trips used `_UI/_playwright/qa-scratch/` files, never the real project's canonical interchange files.

**Not addressed here, by design:** this is Stage 0 only. The deeper issue — two independently-authored data models with no live relationship, only a manual save/sync ritual — is unchanged; Stages 1+ (get both models into one runtime, then a truly live containment layer) are the actual fix for that, per the dream pass. This just makes the *current* mechanism's output visible instead of textual, which was cheap and worth doing regardless of what happens next.

## Session handoff — 2026-09-09, continued (a Fable "dream" pass on the Massing↔Test-Fit architecture itself — no code changed, a real recommendation made)

Same day, immediately after Ben's pushback on "sync confirmed working" (two entries below) — asked for a genuine first-principles dream session on whether the two-Studio architecture is fighting itself, mirroring the 2026-09-06 "dream pass" pattern but aimed at architecture, not vocabulary. Full report: `Architecture-Dream-2026-09-09.md`.

**The verdict: wrong data architecture, not wrong platform — and the fix is smaller than a shared geometry kernel, bigger than a save button.** Research into Blender (`bpy.data` + dependency graph), SketchUp (2D plans are just camera Scenes over one 3D model), Revit (views are computed projections of one parametric database — and even there, massing and Room elements stay distinct-but-live-linked, never merged into one geometry), and Grasshopper (one definition, many derived outputs) all converge on the same mechanism: one live document, many computed views, recomputed automatically — never a hand-triggered export/import ritual. Both existing Studios already prove this pattern works *within* themselves (Massing Studio's 3D scene/section/trade-space-plot/cap-meter are four live views over one `state` array; Test-Fit's SVG/room-list/adjacency-table/hub-clearance are five live views over one `rooms` graph) — the sync gap is the one seam where the tool never applied its own best idea.

**Recommendation: build toward one page holding both live object graphs (volumes + rooms), related by a live containment/derivation layer, staged — starting with a read-only ghost-overlay (Massing's footprint drawn live inside Test-Fit's plan from the same in-memory object, no file) verified end-to-end with today's new Playwright harness before attempting bidirectional editing.** Also recommends building a smaller, real fallback regardless: make the *existing* file-based sync draw a visible dashed-outline overlay instead of a text delta — cheap, real, ships in one session, improves the current mechanism even if the bigger merge takes longer.

**Reassesses the 2026-09-08 "Fable take" honestly, as asked:** its diagnosis was right (a literal shared geometry kernel both a Three.js scene and an SVG canvas draw from is genuinely too big a project, built the way this tool gets built) but its counter-proposal under-solved the complaint — it treated "merge everything" and "keep two files" as the only two options and picked the safer one, missing the middle path of two distinct data shapes in one running session with a live derivation function. Explicitly says this wasn't wrong given what it had evidence for that day (no Playwright harness yet, no concrete "deleted a volume, saw nothing" demonstration yet) — both of which are new today.

**Explicitly recommends against extending Blender into the room-layout role** — the 2026-07-29 call to keep Blender for form/massing only stays correct; the only proven Claude↔Blender interaction pattern (`execute_blender_code` → screenshot) is generate-then-render, not live mouse-driven drag-and-check, and pushing test-fit there would trade away the offline-first `file://` property the 2026-09-07 review called "exactly right" for a heavyweight desktop dependency, without fixing the actual liveness gap.

**Honest about what's at risk under its own top pick:** a real multi-session build (bigger than anything shipped in one sitting so far), a genuine UI-layout problem (3D viewport + SVG plan + both tools' side panels in one page), and a real change to the per-project generation method in `SKILL.md`/`phase-3-massing.md`/`phase-4-space-planning.md` (seeding one cross-referenced file instead of two independent ones). Explicitly not at risk: cap math, driver-proxy formulas, the sun-section, the trade-space plot, adjacency/hub-clearance/casework-violation logic (all pure functions of the live model, lifted not rewritten), and the Rhino/Revit `massing-interchange/v1` export pipeline (untouched, arguably more trustworthy once exported from one coherent object graph). **Nothing built yet — a recommendation, not a build session.** No browser was opened; the read-only ghost-overlay slice should be the first thing verified with the harness before anything bigger is attempted.

## Session handoff — 2026-09-09, continued (both QA-found bugs fixed and verified with the Playwright harness — no more balance-check-only "verification")

Same day, immediately after the QA pass below. Ben, reasonably, pushed back on this session calling Test-Fit→Massing sync "confirmed working" when it only moves two numbers and never shows a visible change — fair: a sync a user can't see isn't "working" in any sense that matters, and that framing should have been sharper the first time. Both real bugs the QA pass found are now fixed, and — for the first time in this tool's history — actually verified by driving the fix through the real harness rather than a brace-count and a hope:

- **`Test-Fit-Studio.html`'s `adjacencyResults()` crash, fixed.** Added a `.filter(([a,b])=>rooms[a]&&rooms[b])` guard before the pair-by-pair lookup — a pair naming a deleted room is now silently omitted rather than throwing. Verified live: deleted room `GB` (the exact QA repro), adjacency pairs went 37→27 (GB's 10 pairs correctly dropped), `buildExportData()` (what Save calls) returned clean, zero page errors.
- **`Massing-Studio.html`'s 1440×900 topbar/panel overlap, fixed.** Added `layoutPanels()`, which measures `#topbar`'s real rendered height and repositions `#left`/`#right` below it (was a hardcoded `top:64px` sized only for the single-row case), called on boot and on every `resize`. Verified live at a real 1440×900 viewport: topbar measured 86px (was invisible to a hand read), `#left` correctly repositioned to top:110px, and a real Playwright click on "↻ Sync from Test-Fit" — the exact click that failed during QA — succeeded.

**The open, harder question — not fixed, deliberately, pending discussion:** the underlying complaint behind Ben's pushback goes beyond the two bugs. Today's sync mechanism, even working exactly as designed, moves numbers/labels, not geometry — deleting a whole Massing volume produces zero visible change in Test-Fit's plan. Whether to build toward something more visible (a floor-outline overlay, actual geometry propagation, something else) is a real product decision, not a bug fix, and stays open rather than getting quietly redesigned mid-bugfix.

## Session handoff — 2026-09-09, continued (first real QA pass on both Studios via the new Playwright harness — sync confirmed mostly numbers-only, two real bugs found)

Same day, using the Playwright harness built two entries below. First genuine click-through QA pass
on both Studios (not just the one round-trip that proved the harness works) — full report at
`_UI/_playwright/QA-2026-09-09.md`. Four things tested:

**Massing→Test-Fit sync (Task 1):** deleted a volume (Office — no UI control exists, fell back to
direct state edit) and moved another (Gym) to a new level (via the real base slider). Confirmed via
`syncFromMassing()`'s own code that Test-Fit's sync reads exactly two fields — `program.dwellingCap`
(a fixed constant) and the House box's ground footprint — so a major Massing change that doesn't
touch House produces **zero visual change** in Test-Fit's room layout, only one passive status-text
number. Matches what was already documented, now confirmed for real rather than by inspection.

**Test-Fit→Massing sync (Task 2):** confirmed genuinely advisory-only — box dims (House, Office)
were byte-identical before/after a sync, even against a dramatic "+96.3 m² short" mismatch. But
**found a real, unconditional crash bug** getting there: `adjacencyResults()` in
`Test-Fit-Studio.html` (line 248) reads `rooms[a].level` with no existence guard, and the hardcoded
`ADJ_PAIRS` list references every seeded room — so deleting *any* room (the only way to delete one
at all, since there's no UI control) throws a `TypeError` that crashes both `render()` and the Save
button's own `buildExportData()` call. Not fixed (QA pass, not a build session) — flagged here for
whoever picks up a delete-room feature next: guard that function first.

**Open-ended use (Task 3):** no console/page errors anywhere across extensive real clicking —
scheme-switch persistence, rotate, driver-proxy bars, room drag/resize, the add-opening palette, the
real on-canvas delete ×, pan/zoom, level tabs, and the scenario toggle all work as designed. One more
real bug found: at 1440×900 (common laptop width) Massing Studio's topbar wraps to a second row that
the `#left` panel's hardcoded `top:64px` renders underneath, making "↻ Sync from Test-Fit"
unclickable — confirmed via measured topbar height (86px at 1440px vs 49px at ≥1600px). Also: the
3D orbit-drag is very sensitive (a ~220px drag rotates >90°) — the one recovery, clicking any
Plan/Iso/Persp button, does fully reset the camera, just isn't signposted as doing that.

**Doors/windows → Massing glazing (Task 4, investigation only, nothing built):** the real gap isn't
data — it's that neither tool has a concept of "which wall is actually exterior," and any position
mapping would inherit the already-unverified Massing-x,z / Test-Fit-x,y axis-correspondence
assumption. Recommended against full per-opening geometry (would re-open the already-settled
"don't merge the two tools' geometry" call from two entries below); a coarse per-cardinal-wall
glazing-% addition to the existing advisory sync is the only version worth it, and only after that
axis-correspondence assumption is actually checked by hand once, not built blind on top of it.

## Session handoff — 2026-09-09 (Nonimuss: Massing Studio's House footprint updated to match Test-Fit's refined plate)

Fixed the specific drift flagged at the end of the 2026-09-08 "Save/Load/Sync" entry below: `3_Massing/Massing-Studio.html`'s scheme-B House box was still the original schematic bar (14×7 m, 98 m²), while `4_Space-Planning/Program-Test-Fit.md` refined the house plate to a squarer 11.6×9.3 m (~108 m²) back on 2026-07-25 and explicitly asked for it to be fed back — never done until now.

**What changed, `3_Massing/Massing-Studio.html` only** (scheme B's `DEFAULTS`, the values a fresh load or reset starts from — a session with unsaved slider edits in its own browser's `localStorage` won't see this until it resets/reloads that scheme):
- House box: `w:14,d:7` → `w:11.6,d:9.3`, matching Program-Test-Fit.md's settled figure exactly.
- Office box: `w:5,d:3` (15 m²) → `w:3.7,d:3` (~11.1 m²). **This wasn't in the original ask, but was necessary, not optional:** Program-Test-Fit.md's own reconciled program table, functional-area verification, and driver scorecard all settle on an ~11 m² office (trimmed down from the massing phase's earlier 11–15 m² placeholder range specifically to make room for the larger house plate without breaking the 120 m² hard cap — see Program-Test-Fit.md's "Net dwelling ≈ 120 m²" line). Leaving Office at the stale 15 m² after growing House to 108 m² would have pushed the live dwelling total to ~123 m², *over* the cap the Massing Studio's whole cap-meter exists to protect — the same class of never-fed-back drift as the House number itself, just not the one HANDOFF happened to name.
- Result: scheme B's default dwelling total is now 118.98/120 m² (house 107.88 + office 11.1), ~1 m² of slack, consistent with Program-Test-Fit.md's own rounded "~120 m²."

**Not touched:** `Massing-Options.md` (never hardcoded the 14×7/98 figure — only states the generic "house ~120 m²" dwelling cap, so nothing there was stale). No `massing-interchange.json` exists on disk for this project yet (the Save-for-Test-Fit-sync feature uses the File System Access API's save picker, and no browser has been used against this instance), so there was nothing to regenerate.

**A separate, pre-existing discrepancy found but deliberately left alone — Ben's call, not fixed:** `3_Massing/Massing-3D.html` (the "simpler orbit-only viewer" Massing-Options.md keeps as a secondary reference) has its *own*, independently hardcoded scheme-B House box at `w:15,d:8` (120 m², no separate Office box — it models a single-storey dwelling, not the two-storey house+office split Massing-Studio.html and Program-Test-Fit.md both use). This doesn't match either the old 98 m² or the new 108 m² figure, and predates the two-storey office decision entirely. Fixing it would mean deciding whether to also add an Office box and split the 120 m² between two volumes the way the primary tool does — a real modeling decision, not a numeric typo, and out of scope for what was asked here.

**Verification — no browser available in this session either**, same pattern as every prior entry: confirmed brace/paren/bracket balance unchanged (214/214, 740/740, 106/106) after the edit, and hand-recomputed the dwelling-cap arithmetic in a throwaway script (house 107.88 + office 11.1 = 118.98, under the 120 m² `CAP` constant with room to spare). Did not trace `metrics()`/`drivers()`'s other live-computed values (coverage, D1–D5, OQ-6) by hand beyond confirming no box now overlaps another (Link/House still touch at x=18 as before, just with House's z-extent grown from 12→14.3, which doesn't intersect Link's z=9–13 range in a new way). **Still unverified in an actual browser** — worth opening Massing Studio for real and confirming the cap meter and section both read sensibly against the new House box before trusting this further.

## Session handoff — 2026-09-09 (Test-Fit Studio embedded into Project Window's Space-planning phase)

Same day, prompted by Ben actually opening `_UI/Project-Window.html` in a real browser for the first time and asking where to find Test-Fit Studio — it wasn't embedded anywhere; `Program-Test-Fit.md`'s link was the only way in, same as it's been since the Studio was built on 2026-09-07. Fixed to match Massing's existing pattern exactly: `openPhase()` in `_UI/Project-Window.html` now checks for `4_Space-Planning/Test-Fit-Studio.html` and, if found, swaps the phase view for a toolbar + `<iframe>` (same `pw:theme`/`pw:files-changed` best-effort `postMessage` bridge, scoped to `4_Space-Planning/`), falling back to the plain doc list when no Studio instance exists for a project — same as Massing does for projects without a Massing Studio.

**Not touched:** the doc list is now hidden whenever a Studio instance exists, same trade-off Massing already made (no code changes there, just following precedent rather than inventing a different behavior for the second Studio).

**Verification:** brace/paren/bracket balance re-checked after this edit (see the fork's numbers two entries above — this session's own edit is a straight copy of the Massing branch's structure with paths swapped, so it carries the same balance). **This is the first real, live opportunity this tool has had to verify anything in an actual browser** — Ben has Chrome open against this file right now. First thing to confirm: does the Space-planning tab actually show the iframe, does the Studio render inside it, and does the in-app link inside `Program-Test-Fit.md` still work as a fallback.

## Session handoff — 2026-09-09, continued (Massing Studio gains "Sync from Test-Fit" — the missing reverse direction)

Same day, immediately after embedding Test-Fit Studio into Project Window: Ben, testing live in a real browser for the first time, asked why Massing Studio has no way to sync data the other direction — Test-Fit Studio can already "↻ Sync from massing" (read-only), but Massing had no equivalent read of Test-Fit's output. This is exactly the missing link that let the 98 m²/108 m² House-footprint drift (fixed earlier today) happen silently in the first place — Test-Fit refined a footprint and there was no path back for Massing to notice.

**Built, `3_Massing/Massing-Studio.html` only:** a new "↻ Sync from Test-Fit" button, mirroring Test-Fit's `syncFromMassing()` exactly (same File System Access `showOpenFilePicker` + IndexedDB-persisted-handle pattern, reusing the existing `idbGetMS`/`idbSetMS` helpers with a new `testfit-file-handle` key). Reads a `test-fit-interchange/v1` save (the file Test-Fit's own "💾 Save" button writes), computes the bounding box + net program area of each level's on-cap, non-illustrative rooms, and compares that against whichever box in the *current* scheme matches that level (House for Ground, Office for Upper) — rendered as a live advisory note under the cap meter, recomputed on every `refresh()` so it stays current as boxes are steered.

**Deliberately advisory, not auto-applied — same judgment-call principle as the fix earlier today.** The note reports the delta (e.g. "+3.2 m² short — box may need to grow") but never writes new `w`/`d` values itself: growing House to match Test-Fit's actual layout can force Office to shrink to hold the dwelling cap, exactly what happened this morning — a call that needs a human, not a formula, each time. Also flagged plainly in the UI's own text: axis correspondence between the two tools' coordinate systems (Massing's `x,z` vs Test-Fit's `x,y`) is assumed, not verified — worth confirming the first time this is actually used against real synced data.

**Verification:** brace/paren/bracket balance confirmed 236/236, 807/807, 118/118 after the edit (all balanced). Logic not yet exercised against a real `testfit-interchange.json` file — Test-Fit Studio's own Save button has to be clicked first to produce one. **Ben has both tools open in a real browser right now** — next real test is clicking Test-Fit's Save, then Massing's new Sync button, and confirming the readout matches hand-checked numbers.

## Session handoff — 2026-09-09, continued (real browser automation, at last — Playwright harness built; first-ever verified click-through; a real geometric finding from it)

Same day, prompted by Ben asking for a way to keep building without being the live tester every round (the Chrome-extension connector never worked this session despite repeated attempts on both sides). Built a **reusable Playwright-for-Python test harness** at `_UI/_playwright/` (`fs-mock.js` + `harness.py`) — not part of the shipped tool, dev tooling only. It mocks `showDirectoryPicker`/`showOpenFilePicker`/`showSaveFilePicker` (which exist in headless Chromium but hang forever waiting for a native OS dialog that can't appear under automation) against the **real filesystem** via exposed Python bridge functions, so every read/write during a test is a real file, not a synthetic fixture. Known gap, documented in the harness's own comments: storing a picked handle in IndexedDB relies on structured-clone preserving native methods, which these mock objects can't survive — so the reconnect-from-IndexedDB path isn't exercised, only first-connect.

**This is the actual first time any part of this tool has been driven in a real (headless) browser, ever**, closing out the single most repeated caveat in every prior session's verification section. Confirmed working end-to-end: Project Window's connect gate, project load, the new Space-planning→Test-Fit-Studio iframe embed (both built earlier today), Massing Studio's 3D isometric render (trees, volumes, sun-section, trade-space plot all draw correctly), and the full Test-Fit Save → Massing "Sync from Test-Fit" round trip — no console errors, no page errors, both built earlier today with zero prior verification.

**A real, useful finding surfaced by that round trip, not a bug:** synced against Nonimuss's actual Ground-level room layout, the advisory note reported the on-cap rooms need a **13×12.3 m (159.9 m²) bounding rectangle** to contain them as currently placed — vs. the House box's 107.9 m² (11.6×9.3 m). Net program area (102.2 m²) fits fine under 108 m² — the areas were never the problem. The gap is *shape*: the real rooms sprawl in an L (GR/MB along one edge, GU/GB offset above MU/ML) that a single rectangle can't contain, something no prior area-only comparison in this tool would ever have caught. **Not resolved — a real design tension for Ben**, not something to silently pick a side on: either the room layout needs to pack more rectangularly, or the House volume needs to stop being a single box. Logged here rather than guessed at.

**One real bug caught and fixed in the harness itself while getting here:** an early repro attempt threw `ReferenceError: syncFromTestFit is not defined` — not a bug in Massing Studio (confirmed by direct `typeof` check: the function was defined) but a race in the test script, which read `page.frames` for the newly-swapped iframe before its scripts had finished executing. Fixed by using `frame.wait_for_function("typeof <fn> === 'function'")` before evaluating into a freshly-swapped iframe — now a documented pattern in the harness for future sessions to reuse, not something to rediscover each time.

## Session handoff — 2026-09-08 (Test-Fit Studio: multi-floor via tabs, windows, pan/zoom — from real feedback on the first instance)

Built the first-ever Test-Fit Studio instance for a *second* project (Nonimuss, alongside Nyando's from the weekend), seeded from Nonimuss's real `Program-Test-Fit.md`. Ben's first real feedback on it, in his own words — "needs a bit more love," "windows are also critical," "I don't like that I can't zoom out," "how does this deal with multiple floors? we need a tab" — changed what "Test-Fit Studio v1" means, so `phase-4-space-planning.md`'s spec was updated to match rather than treating the fixes as one project's local patch:

- **Multi-floor moved from "deferred" to "built," via level tabs** — a flat room registry tagged per-room with a level; a tab switcher rescopes rendering/dragging/cap-accounting to the active level and re-fits the view on switch. Adjacency pairs spanning two levels display but are explicitly **not** distance-checked (a 2D per-level tool can't measure cross-floor distance meaningfully) — shown as "different levels, not evaluated" rather than a fabricated number. This is a flat tab switch, not true 3D stacking — that's still the Massing Studio's job; logged as a real, narrower deferred item now (`phase-4-space-planning.md`'s deferred list).
- **Windows/exterior openings**, a new type distinct from doors — no swing arc, draggable along their wall like a door, seeded only from driver language already in the project's own docs (not invented freely). Fixed casework overlapping a window gets a *soft* note ("may block daylight/view"), separate in both logic and styling from the hard door-circulation violation.
- **Pan/zoom + collapsible side panels** — mouse-wheel zoom toward the cursor, drag-empty-canvas-to-pan, a "fit view" reset (also fires on level switch), collapse toggles on both panels. The root cause of "can't zoom out, panels block objects" was that v1 shipped a fixed viewBox with fixed-position panels over it — geometry near the canvas edges had no way to be seen. Panel repackaged; `design-process.skill` rebuilt via the Python-zipfile method (still avoiding `Compress-Archive`'s backslash-path bug).

**Verification, same honesty pattern as everything else this tool builds:** no browser available again this session, and this machine turned out to have **no Node.js either** (checked PATH and common install locations, found none) — every prior "Node-level" verification claim in this tool's history should be read as having actually run on whatever machine/cloud sandbox had Node, not necessarily this one. This session's check was a line-for-line Python port of the pure geometry/adjacency/clearance functions, run against the real seeded data: confirmed the combined on-cap dwelling total lands at 113.2/120 m² (matching Nonimuss's own "~120 m²" figure), all required-adjacency pairs pass, cross-level pairs correctly show as unevaluated rather than computing a meaningless number, and both scenario buttons (clean vs. constructed-violation) produce the expected casework/door and casework/window results. Caught and fixed one real bug this way, not by running anything: the left panel's help text claimed casework re-snaps to the nearest wall on drop, which the drag code never implemented — corrected the text rather than leave a false claim in a tool whose whole premise is not doing that. **The interaction code itself — drag, resize, pan, zoom, level-tab switching — has still never been clicked through in a real browser**, for either project's instance.

## Session handoff — 2026-09-08, continued (file-based Save/Load/Sync between the two Studios — the Fable take, acted on)

Same day, after the stair-drag work and a Fable-model product-direction take (spawned mid-session at Ben's request, prompted by him losing a Test-Fit editing session to a closed tab, then asking a genuinely good architecture question: "could these two Studios not just be one tool, like Revit/SketchUp deriving a plan from a section cut through a 3D model?"). **The Fable take recommended against merging** — a real shared geometry kernel that both a Three.js scene and an SVG canvas subscribe to is a fundamentally bigger, differently-shaped project than either Studio has been, built by a Claude Code session one round of hand-edits at a time, and it inverts the single-file/cheap-incremental-edit model that's made this tool workable at all. It also named the actual, narrower pain correctly: a hand-typed number drifting, and lost work on tab-close — neither needs unifying the two tools' geometry. Its counter-proposal, built this session:

- **Massing Studio gained a "💾 Save for Test-Fit sync" button**, additive next to the existing Export JSON (which the Rhino/Revit Dynamo pipeline already depends on and was deliberately left untouched). Writes the same `massing-interchange/v1` payload to a real file via the File System Access API, with the handle persisted in IndexedDB so repeat saves overwrite the same file without re-prompting. Falls back to the existing download behavior on non-Chromium browsers.
- **Test-Fit Studio gained three things**: a **Save**/**Load** pair that read/write its *own* full state to a real file the same way (this is what actually fixes "closed the tab, lost my work" — the old clipboard-based Export/share-state button never did, since it required remembering to paste it somewhere before closing); and **Sync from massing**, a separate read-only file connection that reads `program.dwellingCap` and the ground-level House volume's footprint out of whatever Massing Studio's save wrote, replacing the two previously hand-typed cap constants with live-read ones and showing a "synced: scheme B, 2:41pm" status rather than claiming to be continuously live.
- **Deliberately not a live link.** Both tools remain two separate self-contained files with no shared runtime or server — the fix is making the existing manual step (export → paste → hand-edit back in) cheap and visible instead of a lossy clipboard ritual, not eliminating the step itself. Folded into both `phase-3-massing.md` and `phase-4-space-planning.md`; skill repackaged.

**A real, live discrepancy this surfaces, not yet fixed:** Massing Studio's own scheme-B House volume is still 14×7 m (98 m²) — the *original* schematic massing bar. `Program-Test-Fit.md` refined the house-plate footprint to ~108 m² (11.6×9.3 m) back on 2026-07-25 and explicitly said "feed this footprint back to the Massing Studio" — which never happened. The first real sync from Test-Fit Studio will show this live (108 m² hand-typed placeholder → 98 m² actual synced value), which is exactly the kind of drift this feature exists to catch. Not fixed this session — flagged for Ben rather than silently edited, since it's real project content, not plumbing.

**Verification, same pattern as always.** No browser on this machine, so this was checked by careful reading plus brace/paren/bracket balance checks on both files after each edit (330+ braces in Test-Fit Studio alone by this point), and by tracing the data shapes by hand against the existing, working `buildInterchange()`/`exportJSON()` functions in both files rather than inventing a new schema. The File System Access API itself (`showSaveFilePicker`/`showOpenFilePicker`, IndexedDB-persisted handles) is the same mechanism Project Window already uses for its folder-handle reconnect — established, not new — but this is the first time it's been used for *writing*, not just reading, and none of it has been exercised in a real browser yet, on either file.

## Session handoff — 2026-09-08, continued (stretchable/deletable openings, an add-opening palette, a schematic stair marker)

Same day, second round of feedback on Nonimuss's Test-Fit Studio, again in Ben's own words: "needs a bit more love"; "make windows stretchable"; "add a palette that allows placement of new windows and doors"; "delete doors and windows that are currently placed"; "add a schematic stair... just so its kinda clear where that is." All four built, again promoted into `phase-4-space-planning.md` rather than left as one file's local patch:

- **Stretch handles.** Every door/window now renders three handles: the existing round one slides the whole opening along its wall (unchanged), plus two new square ones at its ends — drag either to change its width while the other end stays fixed. Implemented by always recomputing both endpoints fresh from the drag delta and clamping each independently to the wall's extent and a 0.3 m minimum width, rather than deriving one end from the other algebraically — simpler to get right and easier to verify by hand.
- **Delete.** A small red × next to each door/window's handles removes it from the live array and re-renders; no confirmation step, matches how casual a sketchpad tool should be about undo (nothing here is destructive at the level of a real document).
- **Add-opening palette.** A new left-panel section: pick door/window/entry, a room, and a wall (both dropdowns scoped to whichever level tab is currently open), then "+ Add" drops a new one at that wall's midpoint with a sensible default width, ready to slide/stretch into place. This is what actually makes the Studio a sketchpad rather than a fixed read-only rendering of whatever the program doc happened to specify — closes a real gap the first build left open.
- **Schematic stair marker.** A room can carry a `hasStair` flag; when set, it renders simple perpendicular tread hatching plus a "STAIR" label, oriented along whichever of the room's two dimensions is longer. Explicitly a location marker only — no rise/run/going/headroom calculation, logged as a new, narrower deferred item (a real calculated stair, if ever wanted, is Massing Studio section territory, not this 2D plan tool's).

**Verification, same pattern, one real limit found in the process.** Still no browser and no Node on this machine, so this round's check was by hand rather than by running anything: traced the resize math's edge cases directly (confirmed width can approach but never cross below the 0.3 m minimum, and can never go negative, even under repeated extreme dragging near a wall's boundary — a soft limit, not a crash) and re-ran the brace/paren/bracket/backtick balance check on the full script after each batch of edits. The interaction code — including this session's new handles, palette, and stair rendering — has **still never been clicked through in a real browser**, now three rounds of features deep on this instance alone.

## Session handoff — 2026-09-07 (Project Window: redesign + UX fixes from the review below, applied)

Same day, immediately after the Test-Fit Studio build below: went back to the four-agent UI
review and actually built what it recommended, rather than leaving it as four inputs for later.
`_UI/Project-Window.html` was rewritten in full; `_UI/spine-parse.js` and `_UI/audit.js` got small
additive changes. **No browser was available this session** (Chrome extension not connected) —
verification was static (JS syntax check via `new Function()`, every `getElementById` target
confirmed present in markup, every CSS `var(--x)` confirmed defined, div-tag balance, a
throwaway-script check of the two new `spine-parse.js`/`audit.js` functions). This is real risk:
none of the interactive behavior (drag, IndexedDB permission flow, keyboard shortcuts, the
conflict overlay) has actually been clicked through. **First thing worth doing next time a browser
is available: open this for real, ideally against a real project, before trusting it further.**

**Visual redesign — the Claude Design mockup, ported for real.** Pulled the actual mockup content
(not just the review's prose summary) by reading the published artifact's `Main.dc.html`/
`Gate.dc.html` source directly, and re-implemented its dark warm-charcoal/bronze palette, IBM
Plex type pairing (see below), inline-SVG icon set (lock/check/warning/x/chevron/external-link —
replacing every raw Unicode glyph: `▮▯✓⚠▼`), the drivers-lock gate's dashed-rule-plus-chip
treatment, the IDE-problems-panel conscience style, and the header's real-app-chrome layout
(brand mark, mono breadcrumb path). **Made dark the tool's one theme** rather than inventing a
matching light palette — the mockup only ever designed dark, and the review explicitly left that
decision for Ben; light mode is gone, not hidden, and can be revisited on request. **Kept IBM Plex
named in the font stack but never loaded it from Google Fonts** — the UX review called this tool's
"offline-first, dependency-free architecture" a real strength ("exactly right for this tool"), and
a CDN font would cut against that for a `file://` tool meant to open with no network; system
mono/sans fill in as the fallback, so the look is close but not pixel-identical to the mockup.
Also did the graphic-design pass's own list: collapsed the previous 8 uncoordinated font sizes to
7 governed `--fs-*` tokens and scattered spacing to a 4px `--sp-*` scale; gave the project title
real heading weight (17px, was 14px+bold-only); restyled the native `<select>` as an invisible
full-row overlay behind a custom title+chevron trigger (`showPicker()`) instead of bare OS chrome;
extended chip/badge treatment to the header's stale/dormant/changed indicators; added left-border+
icon backing to every severity/blocking signal that used to be color-only.

**UX/tool-builder fixes — all 15 numbered recommendations, at least at a working level:**
1–2. `alert()`/`confirm()` gone — replaced with a toast system (save success/error) and an in-app
   conflict overlay (Overwrite / Discard & reload / Cancel) for the raw-markdown save conflict.
3. **Directory handle now persists via IndexedDB.** On load, a stored handle offers "Reconnect to
   this folder" (calls `requestPermission` from a real click, satisfying the browser's user-gesture
   requirement) instead of always re-prompting with the native picker — the review's own
   "highest-leverage fix." Unverified end-to-end (no browser), but the IndexedDB
   structured-clone-of-a-FileSystemDirectoryHandle pattern this uses is Chrome's documented one.
4. Phase-rail highlight now tracks `selectedPhaseKey` (set in `openPhase()`/`openCloseOut()`),
   separate from the workflow's `currentPhase` — both render, distinctly (fill vs. left-border).
5. Decision log un-clipped entirely (was `.slice(0,8)` rows / `.slice(0,140)` chars) — safe now
   that the rail splits into a pinned Phases zone plus one independently-scrolling zone for
   Drivers/Open-Questions/Decisions/Close-out, so a long log can't push navigation off-screen.
6. Conscience-panel collapse state is now keyed per-project (`pw-conscience-collapsed:<name>`,
   was one global key), and force-expands on a real high-severity finding unless the user has
   already manually toggled it this session.
7. Conscience findings are click-through (via a `target` field now attached in `audit.js` — best
   effort, maps to a phase or a rail section) and per-finding mutable (× button, stored per
   project, with a "N muted — show" recall).
8. **Decision-append divider bug fixed at the root**, not just in the UI: `spine-parse.js` gained
   `findTableLineRange()`, reusing `readDecisions()`'s own column-matching rule instead of "the
   first pipe-table divider in the file" — verified with a throwaway script that it finds the
   *decisions* table specifically even when a second table exists earlier in the file.
9. Baseline keyboard support: Esc backs out of whatever's open (search/conflict/decision-form/
   editor), Ctrl/Cmd+S saves the focused raw-markdown editor, Ctrl/Cmd+K opens search, Alt+Up/Down
   steps through phases.
10. Cross-project search was scoped down to **project search** (Ctrl/Cmd+K) — drivers, decisions,
    open questions, and phase text within the currently open project only. Indexing every project
    up front for true cross-project search was judged disproportionate to this pass; logged here
    as a deliberate reduction, not an oversight.
11. **`looping-back` reachability confirmed, not changed.** It's real and reachable through a valid
    `state.json` — `SKILL.md`'s spine section already instructs the skill to write it "whenever a
    phase loops back." The only path that can't produce it is the `inferState()` fallback used
    when `state.json` is missing/malformed, which is inherent to what inference can know from file
    contents alone, not a bug. Left a code comment in `spine-parse.js` recording this.
12. Status dots now carry a `title` tooltip with the human-readable status name.
13. Massing Studio iframe gets a best-effort `postMessage` bridge (theme + changed-file paths) on
    load — **unverified**, since no Massing Studio instance exists on this machine to round-trip
    against (Nyando skipped building one; Nonimuss's is gone). Degrades to a no-op if unheard.
14. A successful raw-markdown save now returns to rendered view instead of staying in the editor.
15. The last-opened project is now remembered globally (`pw-last-project`) and reselected on
    reconnect, not just per-project last-opened timestamps.

Also fixed a small bug introduced while wiring Ctrl/Cmd+S and Esc: the first draft left
`activeEditorSave`/`activeEditorCancel` pointing at a just-closed editor's buttons whenever the
editor was closed via its own Save/Cancel click rather than via Esc, so a stale shortcut could
re-fire against removed DOM. Fixed by clearing both at the top of `openPhase()`/`openCloseOut()`,
the single choke point every close path already funnels through.

**Not done / left as-is:** the search-result ordering has no relevance ranking (first-match order
only); the conflict overlay's "Overwrite" and "Discard & reload" don't show an actual diff, just
the review's minimum bar of "not a bare confirm()"; per-section independent scroll inside the rail
was simplified to one pinned zone (Phases) + one scrolling zone (everything else) rather than each
subsection scrolling independently, which was judged sufficient to fix the actual complaint (Phases
disappearing) without the added complexity.

## Session handoff — 2026-09-07 (Test-Fit Studio built — the pick from the review below)

Same day, immediately following the four-agent review below: built the **Test-Fit Studio**, the
tool this session's own product-direction pick named as the highest-leverage next build. Two
things changed, following the same split the Massing Studio already established — method in the
skill, artifact generated per-project (never a checked-in template):

- **`_skill-source/references/phase-4-space-planning.md`** gained a new "The Test-Fit Studio
  (interactive instrument)" section, mirroring `phase-3-massing.md`'s Massing Studio section in
  structure and cost principle (client-side/one-time-build always-in; model-in-the-loop
  on-request). `design-process.skill` repackaged (`python3 -m zipfile`, per the 2026-09-06 note
  about `Compress-Archive` silently writing backslash paths).
- **A real generated instance** — `Projects/Nyando-Maternity-Waiting-Home/4_Space-Planning/
  Test-Fit-Studio.html`, seeded with that project's actual `Program-Test-Fit.md` data (12
  program-table rows expanded into placed room blocks, the real 10×10 adjacency matrix, the real
  7-opening veranda loop). Linked from `Program-Test-Fit.md`.

**Freeform, not massing-dependent — a deliberate v1 scope call.** Nyando's own massing was run as
a text option table (`Massing-Options.md` explicitly skipped building the interactive Massing
Studio as disproportionately expensive for that exercise), so no `massing-interchange/v1` JSON
exists to overlay. The Studio works as a pure sketchpad against the program table alone; an
outline overlay is optional infrastructure for later, not a dependency.

**What it does, live:** room blocks sized to program NSF (draggable/resizable, grouped by
cluster) with a running cap meter against the massing GFA; click-to-place doors with clear-swing
arcs; a fixed-casework check (crosses-a-doorway test); a live adjacency panel reading the real
matrix; a veranda/hub-loop clearance panel merging keep-clear bands and reporting residual
furniture pockets per arc; a `test-fit-interchange/v1` JSON export mirroring the massing export's
pattern.

**Verification — the "done" bar from the review below, met, with an honest caveat.** No browser
was available this session (the Chrome extension tool reported not connected), so verification
was Node-level only, same caveat pattern as the 2026-09-06 Project-Window fixes: the pure
geometry/adjacency/veranda-coverage functions were copied into a throwaway script and run against
the same embedded Nyando data. Both real findings from `Program-Test-Fit.md`'s manual pass
reproduce: the newborn-nook/night-nurse required-adjacency violation (the two clusters are
genuinely spatially separated — the check isn't rigged to fire) and the Cluster-1 veranda's
busiest arc showing exactly 0.00 m residual once its 5 closest-spaced openings' 1.2 m keep-clear
bands are merged, matching the doc's "no residual pocket left for even a bench." A first attempt
at the initial room layout used loose, evenly-spaced placement and flagged nearly every
required-adjacency pair as a violation, not just the real one — noise that would have buried the
actual signal; fixed by packing each cluster's required-linked rooms into a touching chain (0 m
gaps) before re-verifying, since the adjacency check is type-level (minimum gap across all
instances of a type), not instance-level — a limitation worth knowing, documented as an honesty
note in the new phase-4-space-planning.md section. **Not yet exercised in an actual browser** —
next time this project (or a new one) is open on a machine with Chrome available, click through it
for real rather than trusting the Node-level check alone, the same way `_selftest.html` doesn't
substitute for a real click-through of the Project Window.

## Session handoff — 2026-09-07 (four-agent UI review + a redesign mockup, no code changes)

Ben asked for the Project Window UI reviewed from a graphic-design lens and a UI/UX-and-tool-builder lens
(two Fable-model agents, text critiques), plus a Fable pick on the single highest-leverage next build for
the tool overall, plus a fourth Fable agent using Claude Code's `design` skill to produce an actual
redesigned mockup rather than more prose. Full reports (verbatim) in **`UI-Review-2026-09-07.md`** at the
repo root. This session made no code changes — it's four inputs for a future build session, not a build
itself.

**Mockup:** https://claude.ai/code/artifact/28ebd6a2-52b6-47b9-9c46-a8b321bd4cb7 — dark-first warm-charcoal
palette, bronze accent, IBM Plex Mono/Sans pairing, header rebuilt as real app chrome, conscience panel
styled like an IDE problems panel. Static, dark-only, sample content only — not wired to real data.

**Where the two text critiques agreed:** severity/status signaling is color-only with no icon/border/fill
backup; the native `<select>` project switcher and raw Unicode glyphs (▮▯✓⚠▼) are the clearest "unfinished"
tells; the drivers-lock gate is visually under-weighted relative to how central it is to the workflow.

**Graphic-design review, top items:** no governed type scale (8 sizes in a 4px band) or spacing scale;
project title barely reads as a heading; dark-mode semantic colors (`--red/--amber/--green/--accent`)
reuse light-tuned hex values unchecked in the dark media block (`Project-Window.html:12-14`).

**UX/tool-builder review, top items — the sharper of the two:** `alert()`/`confirm()` block the UI for
routine saves and conflicts (`:487,492`) — the single biggest "form, not tool" tell; no persisted
`FileSystemDirectoryHandle` (re-picks the folder every session); zero keyboard shortcuts; the phase-rail
"current" highlight never tracks what's actually open (`:337` vs. `openPhase()` at `:435-455` never
updating a selected state); decision log silently truncates to 8 rows (`:381,383`) with no escape hatch;
`looping-back` status may be practically unreachable since `inferState()`'s fallback never produces it
(`spine-parse.js:243-252`) — worth confirming the skill side always writes it correctly.

**Product-direction pick: build the Test-Fit Studio next**, not exports/Rhino/materiality-library work.
Case rests on real evidence already on disk: `Projects/Nyando-Maternity-Waiting-Home/4_Space-Planning/
Program-Test-Fit.md`'s manual pass caught a cross-cluster required-adjacency violation and an undersized
veranda only *after* massing was already locked — exactly what a live clearance/adjacency check would
catch during placement. Also cheaper to build than Massing Studio (2D canvas/SVG, no Three.js). v1 scope,
what to read/write, and a concrete "done" bar (validate against Nyando's real files) are in the full report.

## Session handoff — 2026-09-06 (Project Window: fixed a real crash, five smaller bugs)

A Fable-model pass finally code-reviewed `_UI/` directly (every earlier pass this session reviewed
method/backlog/strategy, never the actual UI code) — and it ran the real parser/audit pipeline in
Node against the one real project on this machine to check rather than guess. Verdict: **opening
that project threw and blanked the whole window.** Its `state.json` uses a `phaseStatus` key with
narrative string values, not the `phases: {key:{status,updated}}` shape `reconcile()`/`missingGates()`
assumed — `Object.entries(undefined)` in `audit.js` threw before `render()` ever ran.

Fixed, each verified afterward with a small throwaway Node script reproducing the exact malformed
shape found (not a claim this substitutes for real browser testing — just confirming the diff itself
doesn't have a logic bug, since neither `testproj/` nor Nonimuss exist on this machine to run the
real `_UI/runtest.js`/`_UI/audittest.js` suites or `_selftest.html`):

- **The crash itself** — `spine-parse.js`'s `reconcile()` now validates `phases` before trusting it;
  a malformed/legacy shape degrades to `inferState()`'s inferred phases instead of throwing, flagged
  `schemaMismatch: true` so the UI can say so rather than presenting inferred data as authoritative.
  `audit.js`'s `missingGates()` also hardened defensively (belt and suspenders — one choke point
  shouldn't be the only thing standing between a bad file and a blank window).
- **Decision-log append had no concurrent-write protection** (the raw markdown editor's Save button
  did, per the original plan's own explicit requirement; the append form skipped it). Fixed by
  re-reading the file fresh from disk before inserting, rather than trusting the in-memory copy —
  stronger than a re-read-and-confirm pattern, since an append never actually needs to overwrite.
- **`esc()` didn't escape quotes** despite building HTML attributes (`img src=`, `a href=`, `option
  value=`) from file content — fixed; a stray `"` in a URL or folder name could break out of an
  attribute before this.
- **`state.stale`** (a project file newer than `state.json`) **was computed and never shown anywhere**
  — now surfaced in a header badge, along with the new `status`/`dormantReason` field added earlier
  today (which nothing in the UI read at all until now) and the `schemaMismatch` flag above.
- **Driver cards rendered raw asterisks** instead of bold — `**text**` in `01_Design-Drivers.md` was
  passed through `esc()` only. Fixed by factoring the markdown renderer's inline formatter out into
  a standalone `mdInline()` both call.
- **`0_Spine/05_Close-Out.md`** (added earlier today) was getting silently swept into the
  "Client discovery" phase view along with every other spine file. Given its own rail entry instead.
- **The site-phase status probe only checked `Site-Details*.md`**, so a project deep into Site-Search
  scoring but not yet at Site-Details could read as "not started" in the phase rail (the raw content
  was still visible — `openPhase()` shows all `.md` files in the dir regardless of probe — just the
  status dot was wrong). Probe now matches `Site-Search.md` too.
- **`_selftest.html` is stale on two dimensions**, not fixed (would require guessing): its hardcoded
  `Nonimuss-Residence` path doesn't exist here, and its fixture file list separately references
  `Site-Shortlist.md`, a name that matches no version of the site templates, past or current. Left a
  clear comment flagging both rather than guessing a replacement; needs regenerating against the real
  project's actual current file inventory next time someone has access to it.

Still unverified: none of this has been opened in an actual browser against the real project since
the fix (only the Node-level logic was checked). First thing worth doing next time the Window is
opened for real: confirm `Nyando-Maternity-Waiting-Home` (or a fresh project) now renders instead of
red-banner-erroring.

## Session handoff — 2026-09-06 (full backlog swept — one real build, twelve bookkeeping fixes)

Same day, one more pass: went through every row in `00_Tool-Concept-Spec.md`'s backlog, oldest to
newest, looking for anything fixable without a real project. Two kinds of thing turned up.

**One genuinely unbuilt, buildable item — #22, the "system learns" close-out loop.** New spine file
`0_Spine/05_Close-Out.md` (phase timing expected-vs-actual, driver-proxy-vs-reality deltas, which
promoted `Library/`/vault items got reused by a later project), written once when a project goes
`complete` or `dormant` — the same transition #24 added earlier today. Kept deliberately cheap (one
table per section) on the MASIV research's own caution that this tool's project volume won't produce
statistically meaningful calibration for years. The spine is now seven files, not six; `SKILL.md`,
`GLOSSARY.md`, and the project-structure block all updated to match. `design-process.skill`
repackaged.

**Twelve stale status cells — rows #1–4, #6–13 — were bookkeeping, not builds.** The 2026-07-25
re-package's own summary paragraph (top of `00_Tool-Concept-Spec.md`) already claimed these were
folded into `SKILL.md`; checked `SKILL.md` directly and confirmed every one of them genuinely is
(the client-discovery matrix, the 04a/04b fork, the process reorder, units/imagery hygiene, the
SITE SEARCH/DETAILS split, the municipal+NRCan data pipeline, parcel adjacency verification, the
full drivers-lock consolidation method, the mandatory assessment battery, the sun-section method,
diagram verification + the OneDrive sync-damage note, and geometry provenance). Their status cells
just never got updated after that re-package to say so — corrected to `✅` with a pointer to where
each lives in `SKILL.md`, no content changes needed since the work was real.

**Two items confirmed correctly still open, not fixable without a real project:**
- **#20** (space-planning circulation-first rule) is folded into `phase-4-space-planning.md` but
  deliberately *not* yet into `SKILL.md`'s main body — `SKILL.md` has no "Phase 4" or "Phase 5"
  section at all, only Phase 1 and Phase 3 (matching the top-of-file note: those two phases haven't
  been pilot-tested for real yet, and the established convention here is not to promote a phase's
  method into the main skill body until it has been). Left alone rather than promoted early, since
  today's synthetic solo pilot explicitly doesn't meet that bar per its own stated caveat.
- **#27** (fetch-before-cite's domain-dependent coverage) stays a logged observation — the pilot that
  found it proposed no concrete fix, so there was nothing to build.

`design-process.skill` repackaged once more to include the close-out spine file. Nothing in this pass
required Nonimuss, the vault, or any project data — it was file-reading and cross-referencing within
the repo itself.

## Session handoff — 2026-09-06 (all 7 fixable pilot findings built)

Same day, immediately following the pilot debrief below. All 7 of that pilot's "specific, actionable
fixes" (backlog rows #28–34) were built in one pass — only #27 (fetch-before-cite's domain-dependent
coverage) stays a logged observation, since the pilot itself proposed no fix for it. What changed:

- **#28** — `phase-2-site.md`'s Output line now says `Site-Details_<address>.md`, matching `SKILL.md`
  and the template's own rename instruction. The stale `Site-Strategy.md` name is gone.
- **#29** — `_templates/0_Spine/state.json` now exists (trimmed shape: project status, per-phase
  status, drivers-lock state) — `SKILL.md` and `GLOSSARY.md` point to it instead of describing the
  fields in prose alone.
- **#30** — `Site-Search.md`'s Stage 2 scorecard note now says to add/remove motive columns, matching
  Stage 1 (previously hard-coded at M1–M3).
- **#31** — `config.local.json` (gitignored, per-machine) + `config.local.example.json` (the shape,
  committed) added at the repo root. `SKILL.md`'s vault-path instruction now names the concrete
  check-then-ask-then-offer-to-save mechanism instead of the aspirational "resolve it once per
  environment" line the pilot found nothing behind.
- **#32** — `phase-2-site.md`'s sun-study battery and `phase-3-massing.md`'s glazing proxy both gained
  an explicit temperate-vs-near-equatorial branch, naming which worst-case condition and section cut
  applies in each regime instead of assuming the temperate one silently.
- **#33** — all three `Library/Materials/` files (+ `Library/README.md`) now carry an explicit
  cold-climate-of-origin warning. No non-cold-climate example was seeded — that part of the finding
  stays open.
- **#34** — `01_Design-Drivers.md` template gained a "Consolidation workshop" section (the CONFIRM /
  SPECIFY / DEFLATE-REFRAME / DEMOTE verdict table + full-disposition record + site-volunteered-drivers
  prompt), which previously existed only as prose in `phase-0-drivers.md` with no template home.

`design-process.skill` repackaged (SKILL.md + phase-2-site.md + phase-3-massing.md all changed).
**None of these 7 fixes have been exercised on a real (or even a second synthetic) project yet** —
same caveat as everything else built today: this closes the gap the pilot found in the *instructions*,
it doesn't yet prove the fixed instructions hold up in a second real run.

## Session handoff — 2026-09-06 (first full five-phase dry run — synthetic, solo, one sitting)

Fifth pass the same day: a Fable-model agent invented its own project from scratch (deliberately
picked something the tool had never been pointed at — equatorial, non-Canadian, a multi-organization
coalition client, no Nonimuss reuse) and ran it through client discovery → site search → drivers
lock → precedents → massing → space planning → materiality, writing real files into
`Projects/Nyando-Maternity-Waiting-Home/` (gitignored, local only — never committed). Full method in
`_skill-source/SKILL.md` was followed as written, not summarized or assumed.

**Read the scope honestly, the same way the agent itself insisted on framing it:** this is real
evidence the tool's *instructions* are followable and internally consistent when someone actually
does what they say — including in a context the tool had never faced before. It is **not** the same
kind of evidence as a real multi-week project with an independent human pushing back, and it does
**not** mean the 13 SKILL patches applied earlier today are now "pilot-tested" in the sense the rest
of this file uses that phrase. The two gates that most need a second, independent party — the
precedent Search-Plan sign-off, and every phase-gate skeptic pass — were self-reviewed by the same
agent that proposed the work, which is a fundamentally weaker check than a human catching a bad plan.

**Depth per phase:** full depth on client discovery (re-scoped the 04b organization fork for a
four-party coalition, which the template assumes is one org's internal politics), the brand-new
site-search scorecard (the main event — a real two-stage zone/parcel cull), site details (real
hand-computed sun-geometry math, not estimated), and drivers-lock (full consolidation workshop,
including a site-volunteered driver and one client–site contradiction resolved via the protocol).
Compressed: precedents (4 verified cards vs. the reference's 6–12, one campaign skipped). Massing was
run as a text-based option table with real computed geometry — **the interactive Massing Studio HTML
was deliberately not built**, judged disproportionately expensive relative to what it would teach
about the tool's instructions specifically. Space planning ran at full depth (a real circulation-first
clearance check caught a genuine undersized-veranda problem); materiality's analysis was full depth,
material sourcing shallow.

**What held up well:** the drivers-lock consolidation workshop, judgment flags working cleanly inside
scorecard cells (not just prose — validates the same-day earlier change), the massing driver scorecard
catching a real cross-phase conflict the two phases' outputs would otherwise have shipped silently,
fetch-before-cite producing a more honest board even when it meant dropping good sources, and
circulation-first furnishing catching a real numeric problem.

**Real friction, now logged as backlog rows #27–34** in `00_Tool-Concept-Spec.md`: three conflicting
names for the same site-phase output file across `SKILL.md`/the template/`phase-2-site.md` itself; no
`state.json` template exists anywhere despite `SKILL.md` describing its shape in prose; Site-Search
Stage 2's scorecard table ships hard-coded at 3 motive columns even though Stage 1 says to add/remove
to match; the vault-path "config, not hard-coded" language in `SKILL.md` describes a mechanism that
doesn't actually exist; the sun-study/glazing-proxy method silently assumes a temperate climate and
scores backwards near the equator; `Library/Materials/`'s starter set was 0% usable outside a
cold-climate context (its first real test outside the one context it was seeded in); the drivers-lock
workshop has no template section of its own, only prose describing it; and fetch-before-cite's real
coverage is bottlenecked by which domains the fetch tool can reach, not source quality (logged as an
observation, not yet a proposed fix).

**None of the eight backlog rows from this pass have been fixed yet** — this session logged the
findings; the fixes themselves are still pending.

## Session handoff — 2026-09-06 (three ideas from a Fable "dream" pass, built same-day)

Fourth pass the same day — this one deliberately not a structured review. A Fable-model agent was
asked to free-associate on the tool's own texture (its vocabulary, rituals, and honesty conventions)
rather than audit it, landed on reading the whole thing as a hospital chart (spine = chart,
drivers-lock = anesthesia induction, judgment flags = patient-reported vs. lab-confirmed, parking a
rejected option = differential-diagnosis discipline), and used that lens to surface three backlog
items (now #24, #25, #26 in `00_Tool-Concept-Spec.md`) plus a fourth roster voice, all actioned the
same session on the user's go-ahead:

- **`Library/Parked-Ideas.md`** (#25) — a new cross-project register for demoted drivers, dead
  massing options, and cut site candidates, so "has this been tried before, anywhere" is answerable
  outside the one project that rejected the idea. Wired into the phase-gate promotion step in
  `phase-0-drivers.md`, `phase-2-site.md`, and `phase-3-massing.md`.
- **`state.json`'s new `status` field** (#24) — `active`/`dormant`/`complete` at the project level,
  with a one-line reason when dormant, closing the gap where a stalled project looked identical to a
  finished one.
- **The Archive, a fourth collaborator-roster voice** (#26) — retrieves the user's own cross-project
  decision-log patterns rather than arguing an opinion, added to both `collaborator-voices.md` and the
  standalone `design-collaborator-roster` skill. Both `.skill` packages repackaged.

The dream also flagged one gap it called non-speculative — `Projects/*/` is gitignored, so every real
project's spine has no version history, and the corpus already records one silent-corruption incident
(the OneDrive brief v0.3 loss) — but the user chose not to action that one this session, only the
three speculative ideas plus the Archive voice out of curiosity. **None of the four are exercised
against real project data yet** — same honesty caveat as the site-search scorecard: drafted from the
dream's reasoning, not from an earned failure.

## Session handoff — 2026-09-06 (SITE SEARCH scorecard drafted)

Third pass the same day, from a third Fable-model review specifically scoped to "what's workable on
a machine with no access to Ben's Obsidian vault and no access to the Nonimuss pilot project." Its
finding: backlog row #23 (the MASIV-inspired driver-weighted parcel scorecard) turned out to have
zero dependency on either missing resource — `phase-2-site.md` and `Site-Search.md` never touch the
vault, and the method can be authored the same way materiality's protocol was, from method rather
than an earned failure.

Drafted: a new "Site search — scoring candidates" section in `phase-2-site.md` describing the same
two-layer pattern as precedent search (visible SCORE layer over a pooled candidate long-list), run
against **weighted client motives** rather than drivers, since drivers don't exist yet at this point
in the process. `Site-Search.md`'s template gained real tables at both stages — a criteria/weight
list, a Stage 1 zone scorecard, a Stage 2 parcel scorecard — plus **envelope-utilization** (target
GSF ÷ buildable envelope GFA) folded into Stage 2 as a scored row, computed per-candidate before
selection rather than only after it. `SKILL.md`'s SITE SEARCH one-liner, `GLOSSARY.md` (new
`Envelope-utilization` entry, updated `Site search` and `Scorecard` entries), and the backlog row in
`00_Tool-Concept-Spec.md` were all updated to match.

**Not yet run** — like materiality when its protocol was first written, this is drafted from method,
not from a real search's failure. First real site-search run should be read against it the way every
other phase's reference got sharpened by an actual mistake; don't treat this as validated until then.

## Session handoff — 2026-09-06 (judgment flag extended to scorecard cells)

Small follow-on the same day, from two Fable-model reviews (one researching MASIV, a Calgary
housing-developer proptech company, for portable ideas; one an outside expert review of the tool
against the ambition of it becoming a design assistant other architects could use). Of the ranked
list that came out of that, the one actionable without a new pilot project: the existing
judgment-flag convention (`[invented]` / `[proxy, unverified]`) covered prose claims but not
scorecard cells, so a driver score resting on assumption could sit next to one resting on a
fetched fact with no visible difference. Extended the rule in `SKILL.md`'s common-rules list, the
`GLOSSARY.md` entry, all three phase references that define a scorecard (`phase-1-precedents.md`,
`phase-3-massing.md`, `phase-5-materiality.md`), and the three templates whose scorecard line
already carried inline instructions (`Precedent-Board.md`, `Massing-Options.md`,
`Material-Palette.md`). `design-process.skill` repackaged — note the repackage script now goes
through Python's `zipfile` rather than PowerShell's `Compress-Archive`, which had silently written
backslash path separators into the archive (`design-process\SKILL.md` instead of
`design-process/SKILL.md`) — harmless on Windows, but would break extraction on Mac/Linux.

Full rest of that ranked list (not yet actioned): pilot-test the 13 patches below, get a real
client engagement running, decide the Claude-Code-vs-GUI product-shape question, a site-search
driver-weighted scorecard ported from the precedent phase's pattern, making the vault/regional
coupling explicit config, and a cheap per-project close-out/calibration log. Also logged as
backlog rows #22/#23 in `00_Tool-Concept-Spec.md`.

## Session handoff — 2026-09-06 (all 13 pending SKILL-patches applied)

All 13 patches drafted in `SKILL-patches.md` on 2026-08-27/28 are now applied to
`_skill-source/SKILL.md`, `design-process.skill` was repackaged (only `SKILL.md` changed inside
the zip — the `references/` files were untouched by any patch), and `GLOSSARY.md` picked up a
sixth spine entry (`state.json`) plus new terms for the awards ladder, the open slot, and the
judgment flag. `SKILL-patches.md` itself is now empty (no patches pending).

Three patches (4, 7, 8) amended each other on the same section — the vault-path handling — and
were synthesized into one final version rather than applied as three literal sequential diffs;
likewise patches 6 and 9 (the Canadian awards ladder) were merged into one ring 0–4 list. Patch 13
(the `04a`/`04b` → `04_Client-Profile.md` filename fix) turned out to be half-done already: the
`_templates/0_Spine/04a_*`/`04b_*` files already carried the "save as `04_Client-Profile.md`
regardless of fork" header comment, but `SKILL.md`'s own spine list, project-structure tree, and
intake step 2 still said `04a`/`04b` as the filename — those three spots are now fixed to match.

**Not yet run since the change:** no test project has exercised the new rules (parallel
vault/search, the open slot, the awards ladder, the judgment flag, the phase-gate Studio Critic
question, `state.json` maintenance) — the patches were reviewed and applied, not pilot-tested
the way the earlier Project Window work was against real Nonimuss files. Worth a light sanity
check the next time a phase actually runs, rather than trusting the prose alone.

## Session handoff — 2026-08-28 (Project Window built; materiality run once)

The Project Window planned 2026-08-27 is now **built and working**: `_UI/Project-Window.html`,
a `file://`-openable page (verified — `showDirectoryPicker` works with no server) with a folder
picker, phase rail with the drivers-lock gate, pinned driver cards, open questions/decisions
panels, a collapsible/resizable conscience panel, a dependency-free markdown renderer, raw-doc
editing, decision-log append, and a Massing Studio iframe. `_UI/_selftest.html` is a repeatable
headless-Chrome regression check against the real Nonimuss files — rerun it after any change to
`spine-parse.js`/`audit.js` rather than trusting a manual click-through alone.

Building it against the real pilot (not a synthetic fixture) surfaced real bugs the synthetic test
suite hadn't: the client-discovery file probe and the drivers-table column matching both silently
failed against Nonimuss's actual files (the real drivers table uses `Test`/`Origin`, not the
template's `Why it matters here`/`How we'll know it's working`); a top-level `ORDER`/`API`
identifier collision between `spine-parse.js` and `audit.js` (both load as classic `<script>` tags
sharing one global scope) silently killed `audit.js` entirely; precedent cards encode driver
coverage in the heading text, not a field, so orphan-card detection false-flagged every card.
Templates were updated to match what real practice already does rather than what the schema still
claimed. `SKILL-patches.md` gained three more drafted (still unapplied) patches from a whole-corpus
synthesis pass — generalizing fetch-before-cite to judgment-only content, pointing the Phase Gate
at the Collaborator Roster, and fixing an internal disagreement in `SKILL.md` about the
client-profile filename.

Read **`SESSION-HANDOFF-2026-08-27.md`** for the original plan and the reasoning behind it — still
accurate for *why* the Window is shaped the way it is, just no longer accurate about build status.

## Where to look for more detail

- **`00_Tool-Concept-Spec.md`** — the full improvement backlog: every method decision, numbered, dated,
  with a status per item (folded into the skill / reference-only / still pending).
- **`Tool-Strategy-Map.md`** (+ `.svg`) — the whole tool as one map: method (true run order + the
  drivers-lock gate), tooling (grouped by type), and the roadmap, with a built / designed-pending /
  not-started legend.
- **`Massing-Export-Roadmap.md`** — the Studio → Rhino/Revit/Blender export architecture: what's shipped
  per target app, what's deliberately out of scope, and why.

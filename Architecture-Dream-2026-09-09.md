# Architecture Dream — 2026-09-09

A first-principles pass, requested by Ben after real Playwright-driven testing proved that Massing↔Test-Fit
"sync" moves two numbers and never geometry — deleting a whole volume in Massing Studio produces zero
visible change in Test-Fit's plan. His words: *"if the user can visually see the plan or mass change - then
its not working... maybe moving to HTML was a bad idea. OR we need a different way to make the visual
portion of the UI more responsive to updates."* This is a thinking session, not a build session — no code
changed. Written the way a domain expert who has actually shipped visual/spatial tools (game engines,
Revit, SketchUp, Blender, Rhino/Grasshopper) would argue it, with a real opinion at the end, not a menu.

**Read in full before forming a view:** `Projects/Nonimuss-Residence/3_Massing/Massing-Studio.html` (642
lines), `Projects/Nonimuss-Residence/4_Space-Planning/Test-Fit-Studio.html` (870 lines), `HANDOFF.md` in
full (all 2026-09-09 and 2026-09-08 entries, plus the 2026-09-06 "dream pass" entry this session mirrors),
`Tool-Strategy-Map.md`, `UI-Review-2026-09-07.md`, `_UI/_playwright/harness.py`, and `_skill-source/SKILL.md`
(spine/per-project structure). Researched externally: Blender's `bpy.data`/dependency-graph model, SketchUp's
scene-camera architecture, Revit's parametric single-model-many-views claim, Grasshopper's data-flow
pattern, and JS shared-reactive-state patterns (sources at the end).

---

## 1. What the two tools' architecture actually is (not what the names suggest)

This matters because the diagnosis depends on it, and it's easy to get wrong from the summary alone.

**Massing Studio is *not* "a 3D view of a data file."** It is one JS module holding a single live array,
`state` (an array of box objects — `{id,type,x,z,w,d,h,base,glaz}`, `Massing-Studio.html:137-156`), and
**four independent live views computed directly from that one array on every edit**: the Three.js scene
(`rebuild()`, `:277-290`), the hand-drawn sun-section canvas (`drawSection()`, `:353-414`), the Chart.js
"trade-space" bubble plot (`updateTrade()`, `:420-436`), and the driver-proxy/cap-meter panel
(`refresh()`, `:331-349`). A slider's `oninput` mutates one field on one box, then calls `rebuild()` and
`refresh()` (`:318`) — every view re-derives itself from the same object, synchronously, in the same tab.
No file, no serialization, no round trip.

**Test-Fit Studio is built the same way.** `rooms`/`doors`/`windows_`/`furniture` (`:197-201`) are the one
live model; dragging a room calls `render()` (`:634`), which redraws the SVG *and* recomputes the room
list, cap meter, adjacency table, hub-clearance panel, and violation list, all from the same objects
(`renderPanels()`, `:509-576`).

**This is, at the scale of one tool, already exactly the pattern Ben is asking about** — a single shared
data model with several synchronized views subscribing to it, no export/import step between them. It works,
it's proven (Playwright confirmed zero console errors across extensive live interaction with both — QA
report, `_UI/_playwright/QA-2026-09-09.md`), and it's the reason both Studios *feel* alive when you use them
inside their own boundary.

**The sync problem lives specifically at the seam between the two tools, and only there.** `saveForSync()`
(`Massing-Studio.html:527-550`) and `syncFromTestFit()` (`:557-596`) write/read a JSON snapshot through the
File System Access API — a real file on disk, opened by explicit button click, read by a separate explicit
button click in the other tab. `syncFromTestFit()` extracts exactly two derived numbers per level (a
bounding-box area and a net program area, `:576-589`) and renders them as advisory text
(`renderTestFitSync()`, `:597-614`) — it never touches `state`'s `w`/`d` fields. `syncFromMassing()`
(`Test-Fit-Studio.html:836-862`) is the mirror: reads `program.dwellingCap` and one box's footprint, writes
them into two module-level numbers (`GROUND_CAP`, `DWELLING_CAP_FULL`, `:150-152`) that only ever feed a
cap-bar percentage — never a room position, wall, or door. **Both sync functions are advisory-only by
explicit design** (comment at `Massing-Studio.html:552-555` says so directly, citing the 2026-09-09
House/Office drift as the reason a mechanical write would be unsafe). That design choice is defensible on
its own merits (see §4) — but it is why Ben's volume-delete test produced nothing visible: the mechanism was
never built to move geometry, only two summary numbers, and it does that correctly.

**So the real question is not "why doesn't the sync work" — it works exactly as specified. It's "why are
there two live models with no live relationship between them, when the tool's own two instruments already
prove that one live model with several views is buildable and does feel right."**

---

## 2. What real tools actually do (researched, not assumed)

**Blender.** `bpy.data` is one document-wide data-block store (scenes, objects, meshes, materials) that
every editor — 3D viewport, Outliner, Properties panel, N-panel — reads and writes directly; there is no
per-editor copy. Blender additionally runs a **dependency graph** (`developer.blender.org/docs/features/core/depsgraph`)
that recomputes derived/evaluated data (modifiers, constraints, drivers) from the same original data blocks
whenever an upstream value changes, so "final" and "original" data stay reconciled through one evaluation
graph rather than through hand-triggered exports. The mechanism that makes multi-editor liveness possible is
not cleverness in the UI layer — it's that every editor is a view into the *same in-memory document*, full
stop, plus a graph that knows what to recompute when something upstream changes.

**SketchUp.** There is no separate "2D plan" data structure at all. A plan, section, or elevation is a
camera set to parallel projection, saved as a **Scene** — a bookmark of camera + visibility state over the
*same* one 3D model. LayOut (SketchUp's 2D drawing-production tool) is architecturally a different
document that *references* a `.skp` file and re-renders whenever that file changes — the closest real-world
analogue to what this tool's Massing/Test-Fit pair already tried to be, and worth noting precisely because
it *is* a separate document with a live reference, not a static export.

**Revit / BIM.** Every drawing view (plan, section, schedule) is a computed projection of one parametric
model database; there is no independent "plan file" to keep in sync — editing the model *is* editing every
view simultaneously, because views are queries/cuts over one source of truth, not separate authored
artifacts. Crucially for this tool's specific seam: Revit does **not** merge a conceptual mass and a Room
element into one object either — a mass and a room are distinct element types, linked by geometric
containment and updated through the parametric engine when one changes near the other. Even real BIM
software keeps "envelope volume" and "room polygon" as related-but-distinct data, associated within one
live document — it does not literally collapse them into a single geometric entity.

**Rhino + Grasshopper.** One parametric definition (nodes/wires, left-to-right data flow) drives however
many geometric outputs are wired from it; changing an upstream slider recomputes every downstream output
automatically. The relevant lesson here isn't the visual-programming UI — it's that outputs are *derived*,
recomputed on every input change, never hand-copied between two independently-authored files.

**Shared-reactive-state (web-native).** The vanilla/modern-framework version of the same idea: a single
JS object (or a reactive proxy over one) that N components subscribe to and re-render from; components never
talk to each other directly, only through the one store. This is functionally what Massing Studio and
Test-Fit Studio each already do *internally*, just with hand-written imperative `refresh()`/`render()` calls
instead of a subscribe/notify library — which, at this tool's scale (a handful of boxes, a dozen rooms), is
the right amount of machinery, not under-built.

**The one property every one of these has, that this tool's current cross-tool sync lacks:** the dependent
view/data recomputes automatically, in the same running session, the instant the upstream thing changes —
never through a save-a-file/open-a-file ritual initiated by the user. That gap is the actual bug, not the
choice of Three.js, SVG, or even having two conceptually distinct data shapes (volumes vs. rooms) in the
first place.

**Sources:** [Blender `bpy.data` API docs](https://docs.blender.org/api/current/bpy.types.BlendData.html) ·
[Blender dependency graph docs](https://developer.blender.org/docs/features/core/depsgraph/) ·
[SketchUp Blog — creating a 2D plan in LayOut from a model](https://blog.sketchup.com/article/creating-plan-your-sketchup-model-layout) ·
[general BIM/Revit single-source-of-truth summaries — bluentcad, virtualbuildingstudio, archilabs] ·
[Rhino developer docs — Grasshopper algorithms & data](https://developer.rhino3d.com/en/guides/grasshopper/gh-algorithms-and-data-structures/algorithms-data/) ·
[Vue.js state-management guide](https://vuejs.org/guide/scaling-up/state-management.html).
General-web-summary caveat: the Revit/BIM and JS-reactive-state search results were vendor-blog-level
summaries, not primary API docs the way the Blender and Rhino links are — treat those two as directionally
correct, not authoritative citations.

---

## 3. The actual diagnosis: wrong platform, or wrong data architecture?

**Wrong data architecture — not wrong platform, and not even "wrong to have two data shapes."** Three
separate pieces of evidence converge on this, not just one:

1. Both tools already *prove*, on this exact platform (plain HTML/JS, no framework, no build step), that a
   single live model with several synchronized views works and feels responsive — that's items 1–2 above.
   If HTML/JS itself were the obstacle, neither Studio would feel alive even on its own.
2. Every real precedent researched keeps **one live document, many computed/derived views** — none of them
   solve this by exporting a file and re-importing it into a second, independently-running document. The
   File-System-Access save/load mechanism this tool built on 2026-09-08 is architecturally closer to two
   separate Word documents with a "paste updates here" convention than to anything Blender, SketchUp, or
   Revit actually do.
3. Even Revit — the most "everything in one model" of the four researched — keeps massing and room-boundary
   as **distinct but co-resident, live-linked element types**, not one merged geometry. So the fix this tool
   needs is not "make volumes and rooms the same object" (that would be over-correcting, and is closer to
   what the 2026-09-08 pass rightly worried was too big a project). The fix is "put both live object graphs
   in one running session, with a real derivation/containment relationship between them that recomputes
   automatically" — which is a smaller, more precedented move than a shared geometry kernel, and a bigger,
   more real move than a save/load button.

---

## 4. Was the 2026-09-08 "Fable take" right?

Worth being honest, since Ben asked directly. **Its diagnosis of the risk was correct; its counter-proposal
under-solved the actual complaint.**

It was right that a **literal shared geometry kernel** — one mesh/vertex representation that both a Three.js
WebGL renderer and an SVG DOM renderer draw from — is a real, disproportionate undertaking relative to how
this tool gets built (one Claude Code session, one file, one round of hand edits at a time), and right that
merging box-steering and room-steering into one editing surface risks losing what makes each Studio good at
its own job (Massing's sun-section and driver trade-space plot; Test-Fit's per-wall clearance/adjacency
checking — neither generalizes cleanly onto the other's geometry).

It was **not** right that the only smaller alternative to a full merge was a hand-triggered file round trip.
There's a real middle option it didn't consider: **two distinct data shapes, in one page, in one JS runtime,
related by an explicit containment/derivation function that runs on every edit** — not one geometry kernel,
not two files. That's a bigger lift than a Save button, but a much smaller one than "the tools become the
same tool." The 2026-09-08 take reasoned as if the only two options were "merge everything" or "keep two
files," and picked the safer of those two — reasonably, given what it had evidence for at the time. It did
not have today's evidence (a real Playwright harness that can drive and verify a two-pane page end-to-end)
and did not have today's clarifying signal (Ben watching a whole-volume deletion produce literally nothing
visible, and calling that "not working"). Both are new information that changes the correct call.

---

## 5. Options, ranked

### (A) One page, one shared live model, two synchronized renderers — RECOMMENDED

A single page (could stay as separate `<script>`-module-scoped objects, or literally one file, matching
this tool's existing single-file idiom) holding:
- `volumes` — the same shape Massing Studio's `state` already is.
- `rooms`/`doors`/`windows` — the same shape Test-Fit's model already is.
- One explicit **containment/derivation layer**: which rooms live inside which volume (by level, the way
  `syncFromTestFit()` already groups by `Ground`/`Upper`), computing the same bbox/net-area comparison the
  advisory note computes today — except live, on every drag, not on a save/open click. Whether a volume
  literally resizes to fit its rooms should stay a judgment call the user makes (not auto-applied — this
  preserves the real, hard-won 2026-09-09 lesson that growing House can force Office to shrink), **but the
  *mismatch itself* should render immediately as a visible ghost outline in both views**, not just a text
  delta: the room bbox drawn as a dashed overlay inside the 3D scene, the volume's plan footprint drawn as a
  dashed reference layer under the SVG rooms. That single change — from "advisory number" to "visible ghost
  geometry, live" — is what actually satisfies Ben's stated bar.

**Why this is the real answer, the reasoning a domain expert would use:** this tool's own founding thesis —
Massing Studio and Test-Fit Studio both exist because "steer, don't just pick" beats a static option table —
only holds up across the massing↔room-layout boundary if steering one is visible from the other, the same
way it's already visible within each tool. Every precedent researched confirms the mechanism (one live
session, computed views) rather than the medium (any specific renderer or file format). And this tool has
already built the muscle for it twice, at smaller scope — this is not a new pattern, it's the existing
pattern applied one level up.

**What's genuinely at risk / what it costs, honestly:**
- Real, multi-session build — bigger than anything this tool has shipped in one sitting. Should be staged:
  start with a **one-way, read-only ghost overlay** (Massing volume outline drawn inside Test-Fit's SVG,
  sourced from the same in-memory object, not a file) before attempting bidirectional live editing — exactly
  the smaller first slice the 2026-09-08 take never got to consider.
- The **per-project generation step changes**: today `phase-3-massing.md` and `phase-4-space-planning.md`
  each independently seed a project's own hardcoded `DEFAULTS`/`ROOMS` into two separate files. Under (A),
  seeding has to produce one file (or one linked pair) with volumes and rooms cross-referenced by level/
  containment from the start — a real change to the generation method in `SKILL.md`, not just to one
  project's HTML.
- Real UI-layout cost: a 3D viewport, an SVG plan, and every existing side panel (cap meter, driver proxies,
  section, trade-space, adjacency, hub-clearance) sharing one page is a genuinely harder layout problem than
  either Studio alone — this is real design work, not a footnote.
- **What is NOT at risk, and shouldn't be treated as if it were:** the cap math, driver-proxy formulas
  (`drivers()`, `Massing-Studio.html:193-226`), the sun-section, the trade-space plot, and Test-Fit's
  adjacency/hub-clearance/casework-violation logic (`Test-Fit-Studio.html:246-304`) are all pure functions
  of the live in-memory model already — none of that logic changes meaning under (A); it gets lifted, not
  rewritten. The Rhino/Revit export pipeline (`buildInterchange()`/`exportJSON()`) also doesn't need to
  change — if anything, exporting from one coherent, cross-checked object graph instead of two
  independently-drifting ones should make that pipeline *more* trustworthy, not less, which matters given
  this tool runs alongside Ben's real Revit/Rhino work at DIALOG.
- The Playwright harness (`_UI/_playwright/harness.py`, built today) is what makes this a responsible bet
  now rather than six weeks ago: a merge attempt can be driven and verified end-to-end in a real headless
  browser before being called done, instead of trusting brace-balance checks the way every prior session in
  `HANDOFF.md` had to.

### (D) Keep two documents, but make the sync itself geometry-visible — legitimate, smaller, real fallback

If (A)'s layout/build cost proves worse than expected once actually attempted, or as a deliberate first
increment: keep the current Save/Sync file mechanism exactly as built, but change what gets drawn when a
sync happens — a real dashed silhouette of the other tool's footprint, not a text delta. This is buildable
in one session, doesn't touch the per-project generation method, and directly answers "can I see the
geometry change" for the *sync moment* specifically. Its honest limit: it only ever updates on an explicit
save-then-open click — it will never feel "alive" the way dragging a room and watching a driver proxy score
move in the same instant already feels in both existing Studios. It fixes visibility, not liveness. Worth
building regardless of whether (A) gets attempted, since it's a real, cheap improvement either way — but
it is not, on its own, the answer to what real tools do.

### (B) Move the canonical model into Blender — wrong tool for this half of the problem

Blender is real and already correctly scoped: the 2026-07-29 decision to do real *form* exploration there
(twisted volumes, folded roofs, real sun-angle studies) via the working `blender-mcp` connection was right,
and nothing here argues against it. But extending Blender to also own room-level test-fit is a step backward
specifically on the property Ben is complaining about:

- The only proven interaction pattern this tool has with Blender is `execute_blender_code` → screenshot,
  which is generate-then-render, not live mouse-driven drag/resize with instant rule feedback. Making that
  feel like dragging a room wall in Test-Fit today would mean building a real Blender **addon** (Python UI
  panels, custom operators, persistent widget state) — a different skillset than vanilla JS, with zero
  established Claude Code competence in this tool's history building *interactive* Blender UI (every prior
  use has been generate/render, never live-drag).
- It would trade away the offline-first, dependency-free, `file://`-openable property the 2026-09-07 review
  explicitly called "exactly right for this tool" — Blender is a heavyweight desktop dependency, not
  something any future reader of this tool (or Ben on a machine without it configured) can just open.
- Verdict: keep Blender exactly where it already is (massing/form), don't push the room-adjacency instrument
  onto it. This would be solving the wrong half of the problem with the right tool.

### (C) Any other precedented pattern

Nothing researched beats (A) as a genuinely different, better-fitting pattern — Blender/SketchUp/Revit all
point the same direction, and (A) is the correctly-scoped translation of that direction into this tool's own
idiom. A full entity-component-system or a formal reactive-store library (Vue-style `reactive()`) would be
solving a scale problem this tool doesn't have (a handful of volumes, a dozen rooms) at the cost of a real
dependency this tool has deliberately avoided everywhere else. The existing "mutate the object, then call
the render functions" pattern already proven in both Studios is the right amount of machinery for (A) too —
no framework needed.

---

## 6. Recommendation, plainly

**Build toward (A): one page, one shared live model, two synchronized renderers — staged, starting with a
read-only live ghost-overlay of Massing's footprint drawn inside Test-Fit's plan from the same in-memory
object (no file, no button), verified end-to-end with the Playwright harness before attempting the reverse
direction or any bidirectional editing.** Build (D)'s geometry-visible sync improvement regardless, in
parallel or as the very first increment — it's cheap, real, and improves the current two-file mechanism even
if (A) takes several sessions to land. Do not extend Blender into the room-layout role.

The single strongest piece of reasoning behind this: **this tool has already proven, twice, at smaller
scope, that "one live model, several synchronized views, no export step" is buildable in exactly this
tool's own idiom and feels right when it exists — Massing Studio's four views over one `state` array, and
Test-Fit's five views over one `rooms` graph.** The sync problem is not evidence that pattern doesn't work
here; it's evidence of the one place the tool never actually applied its own best idea.

The most honest risk of taking this advice: it's a real, multi-session engineering project — bigger than
anything built in one sitting so far — with genuine UI-layout difficulty (fitting a 3D viewport and an SVG
plan and both tools' side panels into one coherent page) and a real change to the per-project generation
method in `SKILL.md`, not just to one project's HTML. It should be staged small and verified with the
Playwright harness at each step, exactly because the 2026-09-08 take was right to worry about scope — it
just under-shot the smaller option that scope-consciousness should have led to instead.

---

## 7. What stays exactly as it is

- The Rhino/Revit `massing-interchange/v1` export pipeline (`exportJSON()`, `buildInterchange()`) — untouched
  by any of this; if anything it gets more trustworthy under (A).
- Every pure-function driver/cap/adjacency/clearance calculation in both files — lifted, not rewritten.
- The offline-first, dependency-free, `file://`-openable property — (A) keeps this by staying inside plain
  HTML/JS with no server and no build step; (B) would have broken it.
- The per-project generated-file workflow's *spirit* (Claude Code seeds a project-specific instrument from
  that project's own spine documents) — only the seeding step's *shape* changes, from two independent seeds
  to one cross-referenced seed.

## 8. Explicitly unverified

- No browser has been opened during this session — everything above about Three.js/SVG-in-one-page
  feasibility is reasoned from reading both files' full source, not from a working prototype. First real
  test of (A) should be the smallest possible slice (the read-only ghost overlay), verified with the
  Playwright harness before anything bigger is attempted.
- The axis-correspondence assumption between Massing's `x,z` and Test-Fit's `x,y` (flagged as unverified in
  both existing sync functions) has still never been checked by hand — worth doing once, independent of
  which direction gets built next, since (A) inherits the same coordinate mapping the current sync assumes.

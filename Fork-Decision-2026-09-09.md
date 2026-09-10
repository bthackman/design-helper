# Fork Decision — 2026-09-09

Ben asked for a decision, not a menu. This file makes one. It also verifies the hand-analysis I already
reported to him, engages the strongest objection head-on rather than around it, and ends with a staged
build plan for the option that wins.

**Read in full before this was written:** `Architecture-Dream-2026-09-09.md`, `Modality-Dream-2026-09-09.md`,
`Merge-Stages-2026-09-09.md`, `HANDOFF.md` (all 2026-09-09 and 2026-09-08 entries), both projects' full
`Massing-Studio.html`/`Test-Fit-Studio.html`/`Program-Test-Fit.md`, `_skill-source/references/phase-3-massing.md`
and `phase-4-space-planning.md`, `GLOSSARY.md`. One targeted external check (Revit's actual Room/Mass
relationship — cited in §4, since it became load-bearing for the decision, more so than in the prior passes).

---

## 1. Verdict on the four hand-analysis findings

All four **confirmed**, one with an added precision, one with more evidence than originally claimed.

**Finding 1 (axis transposition) — confirmed.** Re-derived independently from the two files' actual
`DEFAULTS.B.boxes` (`Massing-Studio.html:143-149`) and `ROOMS` (`Test-Fit-Studio.html:137-149`):

- Test-Fit `PL` is `w:14.0, h:6.0` (x-extent 14, y-extent 6). Massing `Pool` is `w:6, d:14` (x/E-W-extent
  6, z/N-S-extent 14). Test-Fit's x-extent matches Massing's **d**, not its `w`.
- Test-Fit `OF` is `w:3.0, h:3.67`. Massing `Office` is `w:3.7, d:3`. Same pattern: Test-Fit's x-extent
  (3.0) matches Massing's `d` (3), Test-Fit's y-extent (3.67) matches Massing's `w` (3.7).

Both examples agree: **Test-Fit.x ↔ Massing.z, Test-Fit.y ↔ Massing.x** — a genuine transposition, not a
mirror (no sign flip; see below). This directly contradicts `Merge-Stages-2026-09-09.md`'s Stage 1
working hypothesis (`x→x, y→z`, same handedness) — confirmed as stated in the brief.

**Finding 2 (per-room-inconsistent offsets) — confirmed, and worse than the two examples given.** Solving
for the constant in `Massing.z = Test-Fit.x + c` and `Massing.x = Test-Fit.y + c'`:

| Room→Volume | z-offset (Massing.z − TestFit.x) | x-offset (Massing.x − TestFit.y) |
|---|---|---|
| PL → Pool | +23 (consistent at both edges: 6=-17+23, 20=-3+23) | +4 (8=4+4, 14=10+4) |
| OF → Office | +13 (10=-3+13, 13=0+13) | +4 (8=4+4, 11.7≈7.67+4) |
| GR-cluster → House | +5 at one edge only (not a clean fit — see below) | **does not fit at all**: House.x is 18–29.6; the GR-cluster's own y-range (0–12.3) + 4 gives 4–16.3, no overlap |

PL and OF share the same x-offset (+4) by what looks like local internal consistency (they sit adjacent
in Test-Fit's own frame, same as Pool/Link/Office cluster in Massing's), but the House cluster uses a
*different* mapping entirely — not even the same additive constant on the same axis. This is stronger
evidence for "eyeballed cluster by cluster, not derived from one transform" than the brief's original two
examples alone show. It also means Ben's own recorded HANDOFF finding — the on-cap Ground rooms needing a
**13×12.3 m bbox** against House's **11.6×9.3 m** box — is a real shape mismatch, not an artifact of a
wrong axis guess on my part.

**Finding 3 (rooms cluster one-to-one with volumes) — confirmed.** Verified all six mappings by reading
`level`/`cluster`/`onCap` on every `ROOMS` entry and cross-referencing `DEFAULTS.B.boxes`: PL→Pool,
LK(Ground)/LKU(Upper)→Link (Link's own `h:7.5` genuinely spans both storeys — House `h:4` at `base:0`,
Office `base:4.5` — so a box tall enough to bridge both floors is real, not asserted), OF→Office
(`base:4.5`, `level:'Upper'`, matches), GR/MB/GU/GB/MU/ML→House (all six are `level:'Ground'`, `onCap:true`,
and no other Ground volume exists to hold them).

**Finding 4 (VOID would become derived) — confirmed, with one precision worth stating exactly.** Massing
doesn't model floor slabs at all — it models solid boxes. Office sits at `base:4.5` (its floor is at
elevation 4.5 m); Pool is one box from elevation 0 to `h:4.5` — i.e., its top face sits at exactly the same
elevation the Upper level's floor starts. So cutting a horizontal plan-slice at ~4.5 m finds the Office box
over the House footprint, and **finds nothing** — no box at all — over the Pool footprint. That is
literally what `VOID` (`illustrative:true`, "open-to-below, over pool") asserts today by hand. Calling
Pool "double-height" is a fair characterization (4.5 m is taller than one storey, shorter than House+Office
stacked at 7.5 m) rather than a precise term — the real mechanism is "no volume occupies this plan region at
this elevation," which is exactly what a derived cut would compute, not an approximation of it. This is the
most rhetorically attractive of the four findings and it holds up under a second, independent derivation.

---

## 2. Option 2 (the live bridge) — one paragraph, as instructed

Dead, and Ben's own clarification is sufficient reason without re-litigating the CDP/`claude-in-chrome`
machinery `Modality-Dream-2026-09-09.md` built stages B0–B5 around. "Chat with it" meant the ordinary
Claude Code loop — seed a concept, Ben plays with it by hand, tells Claude what happened, Claude responds —
which is exactly what already happens across every other phase of this tool and needs no live wire into a
running browser tab. The reference tools (Revit/SketchUp/Blender) were cited for *behaviour* (masses and
plans staying in sync), not as a platform shortlist, and not as a request for Claude to reach into Ben's
open tab mid-session. Nothing about Options 1 or 3 below depends on a live bridge existing, and nothing in
this file resurrects it.

---

## 3. The Nyando objection — engaged directly, not waved off

This is real, and it is the crux. `Projects/Nyando-Maternity-Waiting-Home/3_Massing/` contains only
`Massing-Options.md` (a text option table) — no `Massing-Studio.html` at all, confirmed by directory
listing. `4_Space-Planning/Test-Fit-Studio.html` exists and is a real, working freeform sketchpad against
that project's own program table. `_skill-source/references/phase-4-space-planning.md:26` states the
principle plainly: *"Freeform by default — don't hard-require a massing export... overlay a floor outline
from the Massing Studio's `massing-interchange/v1` JSON only if that file actually exists for this
project (it often won't — Massing Studio itself is only built on request...)."* Nyando's own
`Massing-Options.md` explicitly skipped building the interactive Studio as disproportionate for that
exercise. So a literal reading of Option 3 — "a floor plan is a horizontal section through the masses" —
makes the plan a view of something that, on real evidence from a real second project, frequently doesn't
exist. Taken literally, Option 3 breaks Nyando's tool today, not hypothetically.

**The resolution I'd actually build, and why it's cheap:** `onCapBBox(level)`
(`Test-Fit-Studio.html:307-313`) already computes, today, the exact thing an "implicit volume" would need —
the bounding box of a level's on-cap rooms. A Test-Fit instance with no sibling Massing Studio doesn't need
a real steered mass to participate in a shared-coordinate architecture; it needs a **degenerate single box
per level, generated from the rooms themselves** (literally `onCapBBox`'s output, promoted from a read-only
advisory number into the trivial "volume" that level's rooms sit in). When a real Massing Studio exists and
gets built, its real steered volumes *replace* the auto-generated boxes as the authoritative envelope for
levels they cover; where no massing exists, the tool behaves exactly as Nyando's does today — freeform,
no external dependency, nothing hard-required. This is not a new mechanism bolted on as a special case; it's
the same function the tool already has, just given a name and a role instead of only appearing in an
advisory string. It preserves the phase-4 principle's *intent* (never hard-require massing) while giving
Option 1/3's shared architecture something to anchor rooms to even in Nyando's situation.

---

## 4. The decision: Option 1, amended by Option 3's strongest idea — not a hybrid dodge

**I'm recommending Merge-Stages' architecture (Option 1) as the winner, with one specific, load-bearing
amendment to how its Stage 1 gets solved — an amendment that comes directly from Ben's proposal.** This is
not "a bit of both, unresolved" — it is a single architecture, and I'm naming exactly which piece of Option
3 gets absorbed into it and why the rest of Option 3, taken literally, doesn't survive contact with this
tool's own ground rules.

**What Option 3, read literally, actually requires, and why that's the problem.** Ben's phrasing —
"expand the massing tool into also having the test fit functionality by cutting views of the 3D masses" —
and the elaboration that rooms become "children of a volume, positioned in that volume's own coordinate
space" — has two readable versions:

1. **The room's plan geometry is *computed* from a horizontal slice through the volume** (the exterior
   boundary of a room-set literally is the cut). Dragging the Massing slider that resizes House would, by
   construction, instantly reshape what a room's boundary is — no intermediate step, no judgment call.
2. **Rooms are independently authored and steered, but live in the *same coordinate frame* as the volumes**
   (no separate origin, no per-project translation), with containment/mismatch computed and shown, never
   auto-applied.

Reading (1) is a direct violation of this tool's own hardest-earned ground rule: **nothing auto-applies
geometry** (the House/Office drift lesson — growing one volume can silently force another to shrink;
`Massing-Studio.html:552-557`'s own code comment names this explicitly). A section cut *is* an automatic
application of the mass's geometry onto the room layer, by definition, the instant the mass changes. That's
not a hypothetical risk to manage later — it's what "the plan is a section through the mass" *means*, and
it reintroduces exactly the class of bug this tool spent real effort learning to avoid.

**This is also not what the real precedents actually do**, checked directly rather than assumed. I searched
Autodesk's own documentation on Room-bounding elements and the Mass-to-Floor workflow (see sources below).
Revit Rooms are **not** geometric children of a Mass and are **not** derived by cutting mass geometry.
A Room is its own placed element; its extent is computed by finding the nearest *room-bounding* elements
(walls, floors, roofs — a raw Mass is explicitly not one, you must convert Mass Floors to real Floor
elements first) in each direction, and it recomputes automatically **when those bounding elements change**
— not when an unrelated Mass changes shape. Rooms and Masses share one coordinate system and are related by
a computed, live query — but they remain **distinct, independently-existing objects**. This is exactly what
`Architecture-Dream-2026-09-09.md` §2 already found and what `Merge-Stages-2026-09-09.md`'s whole shape
already assumes (`volumes` and `rooms` as two live object graphs, related by a computed containment
function, never merged). Reading (1) of Option 3 has *no real precedent*, even in the tool Ben named as the
example to follow.

**What does survive from Option 3, and it's the best idea in this whole exercise:** the reason a translation
layer (Merge-Stages Stage 1) exists at all is that Test-Fit was authored in its *own* arbitrary local frame,
independent of Massing's site coordinates, from day one. Ben's instinct — stop having two separate origins —
is correct, and it's a better fix than "compute an offset and maintain it forever." **The amendment: retire
Stage 1's framing as "verify a persistent translation" and replace it with "re-anchor Test-Fit's room
authoring directly into Massing's existing site coordinate frame" — a one-time migration, not an ongoing
runtime mapping.** Once that's done, there is only one coordinate system in the tool, full stop — the same
one `LOT`/`LAT_LONG`/`buildInterchange()` already use. That structurally removes the axis-correspondence
problem rather than solving it once and hoping it doesn't drift again the way the House/Office footprint
already did once.

**The reasoning a domain expert would actually use, stated plainly:** the goal isn't "one tool" for its own
sake, and it isn't "keep two tools" for its own sake either — it's "one coordinate system, distinct-but-
linked object types, computed relationships, nothing auto-applied," because that is what every real
precedent researched (Blender's `bpy.data` + depsgraph, SketchUp's Scene-over-one-model, Revit's
room-bounding computation, Rhino/Grasshopper's derived-not-copied outputs) actually converges on, and it is
the only reading that doesn't reopen a bug this tool already paid to learn about. Option 1, amended this
way, gets there. Option 3 read literally does not.

**Where the SVG plan "lives" under this decision** (Merge-Stages Stage 3's open question, answered rather
than left open): not as a rendered Three.js camera slice, and not as a fully independent canvas either.
`drawSection()` (`Massing-Studio.html:355-416`) already proves the right-shaped mechanism — a pure function
that reads the `state` array and draws a *vertical* 2D slice onto a 2D canvas, no WebGL involved. The plan
view is the same family of function, cutting *horizontally* instead: a `drawPlanCut(elevation)` sibling that
produces the volumes' footprint outlines (background context, replacing the Stage 0 ghost's "advisory
overlay" role with a live one) onto which the SVG's independently-steered room rectangles are drawn on top,
exactly as they are today. This is a genuinely small addition, not a new rendering architecture — the tool
already has the pattern proven at Ground level, in Massing's own section code.

**Sources checked for this section:** [Room-Bounding Elements — Autodesk Knowledge Network](https://knowledge.autodesk.com/support/revit/learn-explore/caas/CloudHelp/cloudhelp/2014/ENU/Revit/files/GUID-241430FC-8084-43A1-AA3A-681B2883B0FC-htm.html) ·
[About Rooms — Autodesk Help](https://help.autodesk.com/view/RVT/2024/ENU/?guid=GUID-DD74A51D-A0B0-4461-A4BA-0F9CCC191CDB) ·
[Revit Massing Pt. III: Applying Geometry to Masses — ARKANCE](https://arkance.world/global/resources/read/blogs/revit-massing-applying-geometry-to-masses-part-3)
(confirms Mass Floors must be converted to real Floor elements before they room-bound anything — a Mass
alone doesn't bound a Room). Treat these as vendor/knowledge-base-level, same caveat `Architecture-Dream`
already logged for its own Revit research — directionally reliable, not a primary spec document.

---

## 5. What's genuinely at risk under this decision, and what isn't

**At risk, honestly:**
- **A real, one-time migration of Nonimuss's existing rooms.** §1's own findings show the current
  hand-eyeballed positions don't reduce to one clean global transform (House's cluster doesn't even share
  PL/OF's x-offset) — re-anchoring rooms into Massing's site frame means *deciding*, room by room, where
  each one actually sits relative to its volume, not running a formula. This is real hand-work on a real
  project's content, not a mechanical script.
- **Nonimuss's own room-vs-volume shape mismatch stays a real, unresolved design problem** (13×12.3 m
  actual room bbox vs. House's 11.6×9.3 m box) — this decision makes that mismatch *visible and live*
  (Stage 4/5's whole point), it does not resolve it. Resolving it is still Ben's call (Stage 6), same
  ground rule as always.
- **Stage 3's layout problem is real** (3D viewport + SVG plan + every side panel from both tools in one
  page) — smaller than it looked before §4's "plan-cut is a `drawSection()` sibling" answer, but not zero.
- **The per-project generation method changes** (`phase-3-massing.md`/`phase-4-space-planning.md` seed one
  cross-referenced instrument instead of two independent ones) — a real change to what ships, not just to
  one project's HTML, and it has to preserve Nyando's freeform default per §3's resolution.
- **This is a multi-session build.** Saying it in those words, as asked: this is not a one-sitting project,
  the same honest expectation `Merge-Stages-2026-09-09.md` already carried before this amendment.

**Explicitly NOT at risk:**
- Every pure function on either side — `metrics()`/`drivers()`/`drawSection()`/`updateTrade()`
  (Massing) and `adjacencyResults()`/`hubClearance()`/`caseworkDoorViolations()`/`caseworkWindowNotes()`/
  `onCapBBox()` (Test-Fit) — lifted, not rewritten, same as Merge-Stages already committed to.
- The `massing-interchange/v1` export pipeline (`buildInterchange()`/`exportJSON()`) — untouched; if
  anything it gets more trustworthy exported from one coherent, cross-checked graph.
- Nyando's freeform-without-massing workflow — preserved by design via §3's degenerate-volume resolution,
  not broken by adopting a shared coordinate system elsewhere.
- The "nothing auto-applies geometry" rule itself — this decision exists specifically *because* it protects
  that rule better than Option 3's literal reading would have.
- The offline-first, `file://`-openable, no-build-step, no-CDN property — nothing here needs a server, a
  bridge, or Option 2's machinery.

---

## 6. The staged plan — Merge-Stages, amended

This replaces `Merge-Stages-2026-09-09.md`'s Stage 1 and sharpens Stage 3's open question; Stages 0, 2, 4,
5, 6, 6b keep their shape and their ground rules (nothing auto-applies geometry; `file://`-openable, no
build step, no CDN; nothing verified on a brace-count — every checkpoint runs through
`_UI/_playwright/harness.py` against `_UI/_playwright/qa-scratch/` files; pure functions lifted not
rewritten; `massing-interchange/v1` untouched). Stage 0 is already done. Each stage below is
independently valuable and independently abandonable — stopping at any point leaves the tool better than
it found it, same safety property Merge-Stages already named.

### Stage 1 (amended) — Retire the second coordinate frame, once, by hand
Not "verify then maintain a translation." For each existing project with both a Massing Studio and a
Test-Fit Studio (today, only Nonimuss), decide by hand where each Test-Fit room actually sits relative to
its containing volume's real site coordinates, and rewrite `ROOMS`' `x`/`y` values directly in that frame
— no formula, since §1 shows no single formula fits (House's cluster alone needs its own decision, separate
from PL/OF's). Write down the reasoning, room by room, in this file or a successor note.
**Checkpoint:** Nonimuss's `ROOMS` values are expressed in Massing's site coordinate system; Stage 0's two
ghost overlays lose their "position not mapped" hedge and can show a real site position; re-run the
harness's existing round trip and confirm zero console/page errors with the new coordinates.

### Stage 1b (new) — The Nyando resolution: an implicit per-level volume when no Massing Studio exists
Promote `onCapBBox(level)` from an advisory-only helper into the thing a level's rooms are considered to
"sit in" when no sibling `Massing-Studio.html`/`massing-interchange.json` exists for the project — a
degenerate single box per level, regenerated live from the rooms themselves, never hand-authored, never
presented as a real massing decision. This is what keeps Option 1 from requiring Nyando to build a Massing
Studio it explicitly judged not worth building.
**Checkpoint:** open Nyando's Test-Fit Studio (no massing sibling), confirm it renders and behaves exactly
as it does today — zero regression — while internally reporting a per-level implicit volume a future
Stage 4 could draw against if this project ever gets a real Massing Studio.

### Stage 2 — unchanged from Merge-Stages
Separate model from renderers in place, in both files, no behaviour change. Checkpoint: byte-identical
`buildExportData()`/`buildInterchange()` output for the same inputs, full QA-2026-09-09 task set re-run.

### Stage 3 (sharpened) — One page, one coordinate system; the plan is a horizontal cut, rooms overlay it
Both Studios' JS in one runtime. The open question Merge-Stages left unresolved is answered here, not
deferred again: the SVG plan's background layer is `drawPlanCut(elevation)` — a horizontal sibling of
`drawSection()` (`Massing-Studio.html:355-416`), producing the volumes' footprint outlines at the current
level's elevation — with the independently-steered room rectangles drawn on top, unchanged from how
Test-Fit already draws them. Still decide, with reasoning recorded, whether this is one file or two files
plus a host page.
**Checkpoint:** at 1440×900 and ≥1600px, every control in both Studios is reachable and clickable via a
real Playwright click; the plan view visibly shows the cut volume outline under the rooms; both models
still export their own interchange JSON unchanged.

### Stage 4 — unchanged in intent, cheaper in practice
The containment layer + one-way live ghost, now positioned at a real site coordinate (Stage 1 solved this
for real, not with a hedge). Checkpoint: drag a Massing slider, the SVG plan's cut outline (now real
geometry, not just a bbox-derived ghost) moves in the same frame.

### Stage 5 — unchanged
The reverse live ghost (room bbox as a live wireframe in the 3D scene). Checkpoint, including the "honest
one" Merge-Stages already specified: delete a whole Massing volume and confirm the plan now shows a
visible change, closing out the original complaint that started this whole exercise.

### Stage 6 — unchanged
Reconciliation as a proposed, previewable, undoable action — never automatic. Same warning Merge-Stages
already carries: if this drifts toward auto-apply, stop and re-read `Massing-Studio.html:552-557`.

### Stage 6b (amended) — Propagate to the generation method, including the Nyando principle
`phase-3-massing.md`/`phase-4-space-planning.md` change to seed one cross-referenced instrument — **and
explicitly keep and restate the "freeform by default" principle from `phase-4-space-planning.md:26`**,
now implemented via Stage 1b's implicit volume rather than by keeping two independent files. Rewrite
`phase-4-space-planning.md:39`'s "deliberately not a live link" line honestly, the way Merge-Stages already
flagged it needs to be — recording that the 2026-09-08 call was defensible on what it had, and that today's
evidence (this file, the Playwright harness, the volume-delete test) is what changed the call, not that the
earlier reasoning was wrong on its own terms.
**Checkpoint:** seed a *fresh* project's instrument from the updated references (with no massing sibling,
exercising Stage 1b) and drive it through the harness — the real test being whether the method reproduces.

**Honest read on the whole plan, restated:** Stage 4 is still the natural place to stop and reassess
whether the rest is worth it. Everything through Stage 5 stays read-only and reversible. Stopping after
Stage 5 would leave a genuinely better tool than exists today, and that should not be traded for momentum —
same safety property `Merge-Stages-2026-09-09.md` already named, unchanged by this amendment.

# Two-stage massing — merging it into the system (2026-09-09)

**What this is.** A thinking pass, in this project's established sense (`Architecture-Dream-2026-09-09.md`,
`Fork-Decision-2026-09-09.md`, `Two-Stage-Massing-2026-09-09.md`). No production code touched, no Studio
changed, no commit made, no `HANDOFF.md` entry written. Ben asked how to merge the two-stage idea across
the existing system and for staged integration steps — this is the design and the path, not the build.

**Read in full before this was written:** `Two-Stage-Massing-2026-09-09.md`, `Fork-Decision-2026-09-09.md`,
`Review-Steps-1-4-2026-09-09.md`, `Step-5-Report-2026-09-09.md`, `Containment-And-TradeSpace-2026-09-09.md`,
`GLOSSARY.md`, `HANDOFF.md`'s tail, `_skill-source/SKILL.md`, `_skill-source/references/phase-3-massing.md`
and `phase-4-space-planning.md`, `_templates/0_Spine/state.json`, `Library/Parked-Ideas.md`. Read directly
from the live files, not summarized: `Massing-Studio.html`'s `metrics()`/`drivers()`/`updateTrade()`
(`:183-227`, `:462-494`) and its scheme/view switcher markup (`:50-59`); `Test-Fit-Studio.html`'s
`startDrag()`/`onDrag()` (`:879-972`, including the 2026-09-09 code comment confirming the containment
clamp is already reversed) and `addRoom()`/`deleteRoom()` (`:1023-1056`); `_UI/build-design-studio.js`'s
header and its `Layout` switcher (`:152-156`); Nonimuss's real `0_Spine/state.json` and `02_Decision-Log.md`;
Nyando's `0_Spine/state.json` and its `3_Massing/`/`4_Space-Planning/` directory contents. Two external
searches, cited in §5.

**One correction to the brief's own premise, found live.** The brief describes Stage 0 (clamp reversal) as
recently done and asks this pass to build on it — confirmed exactly: `Test-Fit-Studio.html:885-896` is now
a code comment, not clamp logic, reading *"NO CONTAINMENT CLAMP — deliberately removed 2026-09-09 (Stage 0
of the two-stage massing work)... Under the two-stage model, Stage 1 massing sites coarse volumes and
Stage 2 lets the rooms articulate them — so a room extending past its volume is not an error to be
prevented, it is the SIGNAL that the volume is the wrong shape."` `containmentResults()`/`roomContainer()`/
`isRoomCompliant()` are confirmed still present and called. This is Stage 0 and Stage 1 of
`Two-Stage-Massing-2026-09-09.md` §12, both done, exactly as the brief said.

---

## 1. The two stages, named the way Ben would actually say them

**Stage 1 — siting.** A coarse, axis-aligned box per functional volume (House/Office/Pool/Link/Gym), sized
and positioned to prove the program fits the envelope and the cap, pick a parti, and pass a sun-tested
section. This is `Massing-Studio.html` exactly as it exists today — nothing about it changes.

**Stage 2 — articulation.** Once Test-Fit has placed real rooms against a Stage-1 volume, that volume can be
**promoted** — its box reshaped, on request, to the rooms' actual bounding box — via a one-time, previewable,
undoable action ("Reshape to fit"), never a live binding. This is `Two-Stage-Massing-2026-09-09.md` §12
Stages 2-3, not yet built.

**The vocabulary to hand Ben.** These two names — *siting* and *articulation* — are already coined in
`Two-Stage-Massing-2026-09-09.md` and shouldn't be replaced; `GLOSSARY.md` has no competing term, so this is
new vocabulary, not a collision. But for talking to a client or a licensure reviewer, there's a published,
defensible anchor worth citing directly: the **AIA/BIMForum Level of Development (LOD) framework**
([BIMForum LOD Specification](https://bimforum.org/resource/lod-level-of-development-lod-specification/);
AIA Contract Document E201). LOD 100 = "conceptual mass" — a box that establishes overall volume, area,
height, and location. LOD 200 = "approximate geometry" — quantities, sizes, shape, and orientation are
generalized but still not exact assemblies. LOD 300 = "specific assemblies" — accurate geometry, real
walls, real dimensions. **Stage 1 is LOD 100; Stage 2, as this pass and the prior one both scope it (a
resized box, not a real hull), is LOD 200, not LOD 300** — worth being precise about this with Ben, because
LOD 300 is a materially bigger build (real polygon geometry, a new volume type) that `Two-Stage-Massing`
§8 Q1 already recommended against building speculatively. The reason LOD is a *better* fit than borrowing
AIA's SD/DD (Schematic Design/Design Development) phase language: LOD is explicitly designed to be
**independent of project phase** — a LOD 100 mass can exist inside SD or DD, and BIMForum's own point in
publishing it was that phase and model-maturity don't line up 1:1. That is precisely Ben's stated problem
(two sub-stages living *inside* one phase, `Massing`, not aligned to a phase boundary), so citing LOD to a
reviewer is citing the exact concept, not an adjacent one. Recommend: keep "Stage 1 (siting)" / "Stage 2
(articulation)" as the tool's own working names (they're already used in two documents), and note the LOD
100/200 correspondence once, in the glossary entry, as the citable anchor — not as a wholesale rename.

---

## 2. Question 1 — stage-scoped metrics, the full extent

Ben's ruling stands: façade computes at Stage 1 only. This section works out what that ruling actually
touches, checked against `metrics()`/`drivers()` (`Massing-Studio.html:183-227`) as they exist today —
**not** against the hypothetical "one box per room" scenario `Two-Stage-Massing-2026-09-09.md` §8 Q2 used
to find the problem, because that scenario was explicitly rejected (§8 Q1 recommends aggregate hull +
bbox-grow promotion, not one-box-per-room). That distinction matters: under the **actual recommended
design**, several of §8 Q2's findings don't apply the way they were originally stated, and a couple of new,
narrower problems appear in their place. Read metric by metric.

### Broken at Stage 2, needs gating (Ben's ruling extends here)

**`facade`** (`:188`) and everything computed from it — **`effLoss`/`glazedPct`** (`:189-190`) and **`D3`**
(`:211`, `D3=clamp(100-0.05*(m.effLoss-360)-(m.nVol-2)*4,0,100)`). Under bbox-grow, House stays one box, so
`facade` no longer double-counts shared interior walls the way §8 Q2's one-box-per-room scenario found —
that specific failure doesn't happen. But a promoted box has a **different, real problem**: `Two-Stage-
Massing` §8 Q1 already named it as an honest limitation of bbox-grow — "a bbox-grow can silently include
area that isn't actually program (e.g. an L-shaped room cluster's bbox includes the notch)." A non-
rectangular room cluster's *real* wall perimeter is longer than its bounding rectangle's perimeter (a notch
adds wall length the rectangle doesn't have); the promoted box's `2*(w+d)*h` therefore **understates** real
exterior wall once a room layout is articulated — the opposite direction of error from the one-box-per-room
case, but still wrong, and wrong in the input `D3` reads directly through `effLoss`. **D3's `nVol` term is
separately safe** (see below) — the double penalty §8 Q2 warned about is real but comes entirely from the
`effLoss` half now, not from `nVol`. Recommendation: gate `facade`/`effLoss`/`glazedPct`/`D3` together, the
moment any `COND`-type volume (`house/office/pool/link`, `:176`) in the current scheme carries a promotion.

### Real problem, but softer — needs a caption, not a gate

**`coverage`** (`:185`). Same mechanism as facade: a promoted box's footprint includes non-program notch
area, so `coverage` reads as a **conservative upper bound** on real ground coverage after a promotion, not
an exact number — but it's still one honest number from one box (no double-counting, no gap-tiling
distortion — that specific §8 Q2 failure mode was a one-box-per-room artifact and doesn't happen here
either). Because `coverage` maps to a real regulatory question (site coverage, FAR) Ben needs *some* answer
to even at Stage 2, hiding it would be worse than labeling it. Recommendation: keep it visible and
computed at both stages; change its caption at Stage 2 to say what it now measures ("box coverage —
conservative, includes non-program notch area" or similar, echoing the same honesty the promotion preview's
own ghost text should already carry per `Two-Stage-Massing` §8 Q1's closing line).

### Confirmed protected by the granularity decision already made — but the label is now doing less than it claims

**`nVol`/build-simplicity** (`:191`, `:348`) and **`D5`** (`:218-220`). Under bbox-grow (not one-box-per-
room), `nVol` does **not** inflate — House stays 1 volume no matter how many rooms sit inside it once
promoted. This means the specific failure §8 Q2 found ("every articulated scheme reads as complex
regardless of design quality," `:348`'s `m.nVol<=4?'moderate':'complex'` threshold) **does not happen**
under the design this tool has actually committed to — provided Stage 2 is built as box-grow, never as
one-box-per-room. **This is a load-bearing constraint on the build, not a detail**: the moment a future
session lets a Test-Fit room become its own Massing volume, `nVol` (and through it `D3`'s second term and
`D5`) break for real, exactly as §8 Q2 described. As long as promotion stays box-grow, `D5` needs **no
gating at all** — it's genuinely safe at both stages, correcting §8 Q2's original worry about it.

There is a real, different gap worth naming, though: `nVol` now measures *box count*, which at Stage 2
silently under-represents complexity rather than over-representing it. A highly articulated six-room
cluster and a simple rectangular one both read `nVol=1` for that volume once box-grown — the box hides the
articulation happening inside it. Recommendation: same treatment as `coverage` — keep computing and
showing it at both stages, change the caption at Stage 2 to make clear what it's actually counting
("N schematic volumes — see Test-Fit plan for real room articulation").

### Confirmed safe at both stages, no change needed

**Cap meter** (`m.dwell`, `:184`, `:348`'s label context) — filters by `type`, not by box count or shape, so
it's arithmetically identical at both stages. This was already the one metric §8 Q2 found clean; re-checked
against the actual (not hypothetical) design, it's still the one metric that needs zero stage-awareness of
any kind. **D1** (forest proximity, box-position-weighted, `:196-198`), **D2** (wellness continuity,
box-gap-based, `:199-205`), **D4** (sun, box-position + glazing average, `:213-216`), **CAP6** (cap-safety,
box-gap + link-size threshold, `:222-226`) — none reads `facade`/`effLoss` or `nVol`, so none inherits the
Stage-2 problem. **D2 legitimately changes** when a promoted House box moves or grows (`gapBetween(house,
pool)` is now measuring the real, bigger box) — that's the metric correctly reacting to real geometry, not
a distortion, and it should stay live and untagged.

### The trade-space plot and driver-proxy bars

Only **D3's bar** and **the bubble's radius** (`updateTrade()`, `:462-494`; `r:8+live.D3/10` at `:467`) need
the greyed treatment — the plot's **x/y position** (`CAP6`, `D2`) stays honest and live through a promotion.
The sharper trap, worth stating to Ben directly: **the A/B/C reference bubbles are permanently Stage-1-
grade.** They're computed from `DEFAULTS.A/B/C.boxes` (`updateTrade()`'s `schemePoint()` calls, `:463-466`),
which never change regardless of anything Ben edits or promotes on the live ★. Once the ★ has been promoted
and its bubble radius reflects a Stage-2-tainted `D3`, comparing its size against A/B/C's permanently-
Stage-1 bubbles is comparing two different kinds of number that happen to render the same way. The fix
isn't recomputing A/B/C (they're reference points, not live schemes) — it's the same greyed/tagged
treatment on the live bubble, plus a one-line caption under the chart clarifying A/B/C stay schematic-grade
always. `nVol`'s caption change (above) belongs in the same neighbourhood as this note.

### The mechanism, and the constraint it puts on the build

Two implementation points worth deciding now rather than discovering mid-build:

1. **Don't hide, don't silently compute wrong — reuse the tool's own existing convention for exactly this
   problem.** `GLOSSARY.md`'s `Judgment flag` entry already exists for "a claim, proxy, or invented
   position that isn't traceable to something verified" — a bracketed `[proxy, unverified]` tag used in
   scorecards and prose throughout the method. A Stage-2-tainted `facade`/`D3` number is the same category
   of problem (a number that looks as certain as its neighbours but isn't) at a different layer (a live
   computed value, not a written judgment call) — reusing that visual/textual convention (`[schematic-only
   — see Stage 2]` or similar) rather than inventing a new greyed-state language keeps this consistent
   with vocabulary the tool already has, per this pass's own instruction to prefer it.
2. **Don't edit `metrics()`/`drivers()` themselves — wrap them.** Every prior stage of this build has held
   "pure functions lifted, not rewritten" as a hard rule. Reading a new `state[i].promoted` flag inside
   `metrics()`'s own arithmetic would be a real, if narrow, exception to that rule. The cleaner design:
   keep `metrics()`/`drivers()` computing exactly what they compute today, byte-identical, and add a
   **new, thin, additional pure function** — something like `metricsDisplay(m, state)` — that decides,
   per field, whether to show the raw number or the tagged sentinel, based on whether any relevant volume
   in `state` carries a promotion flag. This is new code, but it's *additive* new code sitting beside the
   existing pure functions rather than inside them, which is the honest way to satisfy "lifted, not
   rewritten" when the display logic genuinely needs new judgment the old function never had to make.

---

## 3. Question 2 — how the two stages introduce themselves in the UI

**Ben's own instinct — two tabs — doesn't survive testing it against what a stage actually changes, and
testing it is what surfaces the right answer.** Walk through each of the constraints the brief named:

- **Which metrics show** — gated per §2, at the level of individual numbers inside the existing metrics
  panel and trade-space chart, not at the level of "which page is showing."
- **Whether room-derived articulation is visible** — already always visible, at both stages, in both cases.
  Test-Fit's own rendering of rooms is never stage-gated; nothing about "Stage 2" turns room detail on or
  off. Promotion is the *mass* catching up to the rooms, not the rooms becoming visible.
- **What the plan cut draws** — `drawPlanCut()`/`levelElevations()`/`liveMassingCut()` (Step 5,
  `Massing-Studio.html`'s plan-cut pair + `Test-Fit-Studio.html`'s consumer) read `state[i]`'s current
  `w/d/x/z` and draw whatever that is, promoted or not, through the exact same code path as any ordinary
  slider edit. **This needs zero changes for the whole two-stage scheme** — a promoted box just draws
  bigger/repositioned, like any other edit ever has. Worth flagging as a genuine "nothing to build here."
- **What can be edited** — nothing changes. A promoted box is still an ordinary box with live sliders;
  promotion is a provenance fact (where this size came from), not a lock.

Given that, **stage is not a page-level mode at all — it is a per-volume provenance flag**, and the
honest answer to the brief's own sharpest question (*is a stage a property of the whole project, of one
scheme, or of one volume?*) is: **of one volume.** Could House be detailed while Pool stays schematic? Yes
— and that's arguably the honest common case, not an edge case: House is what gets rooms placed against it
first and most precisely; Pool/Link/Office may never need promoting if Step 1's re-anchor already sized
them correctly (`Fork-Decision-2026-09-09.md` §1 Finding 3 confirms PL/OF were already set to their massing
box's exact footprint). A single global toggle would have to lie about at least one volume's real state the
moment even one gets promoted and others don't.

**Why a tab is the wrong-shaped control for this, stated plainly.** `Massing-Studio.html` already has a
scheme switcher (A/B/C, `:50-52`) and a view switcher (Plan/Iso/Persp, `:55-57`); `Design-Studio.html`
already has a pane-layout switcher (Side by side/Massing only/Plan only, `_UI/build-design-studio.js:152-
156`). Those three axes are all "how do I *look at* the same underlying data" — orthogonal, genuinely
independent, safely stackable (today already a 3×3×3 = 27-way space). A stage toggle would be a *fourth*
control in that family, but it isn't the same kind of thing: it doesn't change how you look at the data,
it changes **which numbers are currently trustworthy for one specific volume** — a narrower, per-object
fact, not a page-wide rendering mode. Adding a fourth *mode* control for something that is actually a
per-volume *property* would both under- and over-serve the need: over-serve, because switching the whole
page's "mode" implies more changes than a promotion actually causes (§2 already showed almost nothing else
changes); under-serve, because a single project-wide toggle literally cannot represent "House is Stage 2,
Pool is Stage 1" at the same time — the one case most worth representing correctly.

**What to build instead — a badge, not a tab.** A small label next to each volume's name in the volume
picker/slider panel (e.g. "House — LOD 200" vs. "Pool — LOD 100", or the tool's own Stage 1/Stage 2
language) reading `state[i].promoted`. No new top-level control. Cheaper to build, and it's the version
that survives the "could House be detailed while Pool stays schematic" test that a tab fails outright.

**Going back — is there a "demote" action?** No, and there shouldn't be one built as new machinery. A
promotion writes `state[i].w/d/x/z` the same way any slider edit does — reversible the same way any slider
edit already is (drag it back by hand, or reload from `WORK`'s pre-promotion save, per `Fork-Decision-2026-
09-09.md` §3's own reasoning, unchanged here). The one addition worth making: since `Two-Stage-Massing`
§6 already asks that every promotion log its before/after dims to `02_Decision-Log.md` (see §4 below), that
log entry **is** the practical undo record — a person reading it and re-typing the old numbers back is the
same weight of act as reversing any other logged decision in this tool (a parked massing option, a demoted
driver), not a gap needing a button.

**Should this get a lighter version of Ben's tab idea eventually?** Possibly — a "show promoted volumes"
highlight/legend toggle is cheap and might earn its place once the badges are in real use and Ben finds
them hard to scan at a glance. Recommend not building it speculatively (same "don't build until an earned
failure asks for it" discipline the tool already applies to the hull question, materiality, and the
collaborator roster) — put it behind Stage 4's checkpoint pause (§6) instead of building it now.

---

## 4. Question 3 — how the two stages introduce themselves in the process

**This is a loop between phases 3 and 4, not two sequential sub-phases of phase 3, and the method
documentation should say so in both places, not just one.** Mechanically: Stage 1 (siting) is just phase 3
as it already exists, unchanged. Stage 2 (articulation/promotion) is *triggered* by work done in phase 4
(rooms placed, a containment breach reported live) and *writes back* into phase 3's own artifact
(`Massing-Studio.html`'s `state`). `Two-Stage-Massing-2026-09-09.md` §6 already drafted the phase-3-massing.md
side of this correctly (a Stage 1/Stage 2 split inside the existing structure) but its propagation plan
stopped there — **phase-4-space-planning.md needs a matching cross-reference it doesn't currently have**:
something naming that a live containment breach (`containmentResults()`, still live and correct per this
pass's own re-verification) is the *signal* to consider triggering a promotion back in phase 3, not just a
thing to notice. Without that, a future session reading only `phase-4-space-planning.md` — which is exactly
what happens when a per-project Studio gets hand-authored from these references — would never learn the
loop exists from the phase-4 side at all.

**The drivers-lock gate does not move and does not reopen** — confirmed correct, unchanged from `Two-Stage-
Massing` §6's own reasoning. A promotion sharpens a box's precision; it does not re-argue the drivers. The
one real wrinkle, sharpened by §2's finding: **`coverage` is the metric most likely to actually matter here**
— it's the one Stage-2-affected number still meaningfully computed (with its conservative-upper-bound
caveat) rather than gated off entirely, and it maps to a real bylaw limit. If a promotion pushes reported
coverage over a hard site-coverage number that was fine at drivers-lock time, that's a decision-log-worthy
finding — the gate's own existing language ("everything after is tested against them") already anticipates
exactly this kind of post-lock discovery; it is not a reason to treat the gate as reopened.

**What the decision log needs.** `02_Decision-Log.md`'s existing shape (Date | Phase | Decision | Rationale
| Rejected alternatives, confirmed from Nonimuss's real file) needs no new columns — a promotion fits as an
ordinary row, content per `Two-Stage-Massing` §6 (volume, before/after dims, triggering room-level
conflict). One addition worth making: since a promotion is genuinely cross-phase (it originates in phase 4,
lands in phase 3), write its **Phase** cell as `"Space planning → Massing"` rather than a single phase name
— every other row in the real log names exactly one phase, so a promotion needs its own convention to stay
legible as the loop it actually is, the same way the brief asked.

**Does a promotion need a register the way demoted drivers/parked options do?** Checked `Library/Parked-
Ideas.md`'s actual purpose — it registers things that got *killed*, so a future project can ask "has this
been tried before." A promotion is the opposite: something that got *more* resolved, not dropped. It
doesn't belong there. But there is a real cross-project value in tracking **how far off Stage 1's guess
typically is** — that's exactly what `05_Close-Out.md`'s existing "driver-proxy-vs-reality deltas" field
already exists to hold (`GLOSSARY.md`'s `Close-out` entry). Recommendation: a promotion whose before/after
delta is large enough to be worth remembering feeds `05_Close-Out.md` at project close, not a new register
— this reuses a mechanism the tool already has rather than adding a third place decisions get logged.

**How does a project declare which stage it's in — is that in `state.json`?** Checked both the template
(`_templates/0_Spine/state.json`) and Nonimuss's real file directly: **no.** `state.json` tracks
phase-level completion (`currentPhase`, `driversLocked`, a status per phase, project `status`) — per
`SKILL.md`'s own rule, "store only what can't be derived from" the other spine docs. Per-volume promotion
provenance is Massing's own live data (`state[i]`, inside the Studio file itself), not a spine fact — it
doesn't belong in `state.json` any more than `coverage` or `facade`'s current numeric value does. The one
piece that *does* belong there, and needs **zero new schema**: `SKILL.md` already defines a per-phase
status value of `looping-back` for exactly this situation (a phase reopened by later work). A promotion is
a loop-back on the `massing` phase entry — set it, same as any other loop-back gets recorded.

**A live gap worth naming while checking this, unrelated to today's build but real.** Nonimuss's actual
decision log already records a genuine phase-3→phase-4→phase-3 loop (2026-07-25 massing lock →
2026-07-26 space-planning entry explicitly says "This LOOPS BACK on the 2026-07-25 two-storey decision" →
carries forward as OQ-18) — but Nonimuss's real `0_Spine/state.json`, read directly, shows `massing:
{"status":"complete", ...}`, never `looping-back`, despite that already-logged loop. The schema has the
field; current practice doesn't populate it, even for a loop that already happened and is on record. Not
this pass's job to fix, but worth Ben knowing the mechanism isn't self-enforcing — it needs the field
actually set, which today's practice hasn't been doing.

**Also worth noting in the same breath:** Nyando's `0_Spine/state.json`, read directly, is a self-invented
shape with its own note admitting as much ("No state.json template exists in _templates/0_Spine/ (checked
— only 00-04 .md files ship)") — which is now stale; the template does exist (read directly, confirmed
above) and Nonimuss's file follows it closely. Nyando's file predates that template or was written without
checking for it. Not a two-stage-massing problem, but a second, independent `state.json`-hygiene gap
surfaced by reading both files directly for this question.

**Nyando stays clean by construction, re-confirmed.** Since stage is a per-volume flag inside
`Massing-Studio.html`'s own `state` array (§3), and Nyando has no such file at all (`3_Massing/` contains
only `Massing-Options.md`, confirmed by directory listing), there is nowhere for a stage concept to attach
— same conclusion `Two-Stage-Massing` §10 already reached for the promotion button generally, re-derived
here rather than assumed. Worth one more precision: even Fork-Decision's proposed Stage-1b fallback for
Nyando-like projects (`onCapBBox()` promoted into a degenerate implicit volume) is explicitly **not** a
Stage-1-in-the-promotable-sense box — it's auto-derived from the rooms on every render, never hand-
authored, so there's no hand-guess to promote *from*. A project using that fallback never has a Stage-1/
Stage-2 distinction to make in the first place, which is the cleanest possible version of "must not be
forced to have a stage."

---

## 5. Research — LOD and the mass-to-model precedent, checked directly

**BIMForum LOD Specification** ([bimforum.org](https://bimforum.org/resource/lod-level-of-development-lod-specification/)),
cross-referenced with a 2024/2025 edition summary
([United-BIM — LOD 100–500](https://www.united-bim.com/bim-level-of-development-lod-100-200-300-350-400-500/)):
LOD 100 = conceptual mass (overall volume/area/height/location, generic); LOD 200 = approximate geometry
(generalized systems, still not exact assemblies); LOD 300 = specific assemblies (accurate geometry, real
dimensions, coordinatable). LOD is defined jointly by AIA E201 (100/200/300/400/500) and BIMForum's own
spec (adds 350, the practical 500 interpretation). This confirms §1's mapping: Stage 1 = LOD 100 cleanly;
Stage 2, as scoped by the bbox-grow recommendation (still an axis-aligned box, just resized from rooms), is
LOD 200 — approximate, generalized, still not a real assembly — **not** LOD 300, which would require the
rejected-for-now real-hull branch of `Two-Stage-Massing` §8 Q1.

**Revit's conceptual-mass-to-model workflow** ([Novedge — Mass-to-Model Workflow](https://novedge.com/blogs/design-news/revit-tip-mass-to-model-workflow-converting-conceptual-masses-into-constructible-revit-elements);
[Autodesk Knowledge Network — Workflow: Conceptual Masses](https://knowledge.autodesk.com/support/revit/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/Revit-Model/files/GUID-261D36E7-9AAC-4A56-BCCE-0F963354027F-htm.html)),
re-checked for this pass rather than re-cited from the prior one: real practice explicitly recommends
**"stabilize the form... before conversion, as... wholesale reshaping after conversion creates rework"** and
keeping alternates in a Design Option while still testing — i.e., don't convert (promote) prematurely,
converge the mass first, same discipline this tool's own drivers-lock-before-massing sequence already
enforces. This corroborates the *timing* half of Ben's two-stage idea (convergence happens before precision
work) on top of what `Fork-Decision-2026-09-09.md` §4 already established about the *direction* (a one-time,
explicit, human-triggered conversion, not a live two-way sync).

---

## 6. Where this lands in the existing plan

**This pass does not add a new numbered stage or step to either the 8-step plan (`Fork-Decision-2026-09-09.md`
§6) or `Two-Stage-Massing-2026-09-09.md` §12's own staging.** It is a load-bearing amendment to §12's
Stages 2-4, worked out in enough detail that Stage 3 as originally scoped would have shipped incomplete
without it:

- **§12 Stage 2 (promotion preview)** — absorbed, unchanged in mechanism, gains one new requirement: the
  ghost/preview text must also name which metrics will go stale on commit (§2's list), not just the box
  delta. This is new content for an existing stage, not a new stage.
- **§12 Stage 3 (the commit — "Reshape to fit")** — **this is the one place this pass changes what Stage 3
  actually has to build, not just what it says.** As originally scoped, Stage 3 was "write the ghost's bbox
  into `state[i].w/d/x/z`, run `rebuild()`/`refresh()`." Writing only the new dimensions — with no
  provenance flag — would leave `facade`/`D3` silently continuing to compute on the promoted box as if
  still Stage-1-trustworthy, which is exactly the "computes on the wrong model, silently" failure this
  pass's own brief warned is its own kind of lying. Stage 3 must now also write `state[i].promoted` (or
  equivalent) as part of the same commit, and the `metricsDisplay()` wrapper from §2 must exist before
  Stage 3 ships, not after. **This is a correction to already-planned work, surfaced before the build, not
  a new item appended to the list.**
- **§12 Stage 4 (method propagation)** — absorbed and substantially expanded. Originally scoped as "the
  Stage 1/Stage 2 split + the room-creation tool in phase-4's build list." Now also carries: the metric-
  gating rule and its captions (§2), the per-volume-not-per-project stage model and the badge-not-tab UI
  call (§3), the phase-4 cross-reference to the promotion trigger this pass found missing (§4), and the
  decision-log/Close-Out conventions (§4). Given how much this grew, it's worth a checkpoint pause before
  it's written (§7 Stage 5) rather than folding it silently into what was a one-line item before.

**A new item this pass adds that §12 didn't have at all: the UI badge (§3).** §12's staging never
addressed how a promoted volume gets surfaced visually — it stopped at the commit. This pass's §3 is new
scope, inserted between the old Stage 3 (commit) and Stage 4 (method propagation).

**Nothing here touches Steps 1, 2, 4, 5 of the 8-step plan, or §12 Stages 0-1 — all stand exactly as built
and verified**, per `Review-Steps-1-4-2026-09-09.md` and `Step-5-Report-2026-09-09.md`'s own live
verification, re-confirmed by this pass's own direct reads (§0 above).

---

## 7. Staged integration path

Continuing `Two-Stage-Massing-2026-09-09.md` §12's own numbering — Stages 0 and 1 are done; this renumbers
and absorbs its old Stages 2-4 into Stages 2-5 below, per §6's mapping. Each stage independently valuable,
independently abandonable, same property every prior stage of this plan has committed to. Checkpoints run
through the real Playwright harness (`C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe`,
Playwright 1.62.0) against `_UI/_playwright/qa-scratch/` files — a claim isn't done until it's been driven
through headless Chromium, not read from the code.

**Stage 2 — Promotion preview, carrying its own honesty message.** Extend the existing per-volume ghost
(§12's original Stage 2 scope: `rebuildGhosts()`'s advisory pattern, made live per Step 6) so its preview
text also names which metrics will go stale on commit — a static list keyed to `COND`-type volumes
(façade, effLoss, glazedPct, D3's bar and bubble). No write to `state` yet; no provenance flag yet (that's
meaningless before a commit exists). **Checkpoint:** drag a room past its container in `Design-Studio.html`;
read the ghost/preview panel's DOM text; confirm it names the stale-metric list alongside the box delta;
confirm `state` is provably unchanged (same read-only pattern `Step-5-Report-2026-09-09.md` already used).

**Stage 3 — The commit, with the provenance flag load-bearing from the start.** The "Reshape to fit" button
writes new `w/d/x/z` **and** sets `state[i].promoted` (or a small object: `{promoted:true, from:'test-fit',
date}`) as one atomic commit. Add the new `metricsDisplay(m, state)` wrapper (§2) — `metrics()`/`drivers()`
themselves stay byte-identical, untouched. Wire the trade-space chart's bubble radius and D3's bar through
the same wrapper. **Checkpoint:** promote House per `Two-Stage-Massing`'s own conflict #1 (box becomes
~13.0×12.3 m); read `metrics()`'s raw output directly and confirm it's unchanged in *shape* from today
(still computes `facade` etc. — the raw function is untouched); read `metricsDisplay()`'s output and confirm
`facade`/`effLoss`/`glazedPct`/`D3` now render as the tagged/greyed state while `coverage`/`nVol` render
with their new captions and `D1/D2/D4/D5/CAP6` render live and unflagged; pixel-check the trade-space
bubble radius freezes/greys the same way `Containment-And-TradeSpace-2026-09-09.md`'s own star-visibility
fix was verified (`getImageData`, not a screenshot guess); re-run export byte-identity (Step 4's own bar).

**Stage 4 — The badge, not a tab.** A small label on each volume's entry in Massing's volume picker/slider
panel reading `state[i].promoted` — no new page-level mode control. **Checkpoint:** promote House in the
merged page; confirm its badge changes and Pool/Office/Link's (unpromoted) don't; confirm zero new console
errors; confirm the existing scheme/view/pane-layout switchers are unaffected by the new markup (the same
class of check `Review-Steps-1-4-2026-09-09.md` used to catch the export-modal pane-leak bug). **Pause
here, deliberately, before Stage 5** — have Ben actually look at the badges in the real Studio before
they're written into the reference files as the canonical instruction every future project gets seeded
from; a UI call baked into method docs is expensive to unwind later, and this is exactly where his own
"two tabs" instinct should get a real chance to disagree with what got built.

**Stage 5 — Method propagation.** `_skill-source/references/phase-3-massing.md`: the Stage 1/Stage 2 split
(per `Two-Stage-Massing` §6) plus the metric-gating rule and captions (§2) plus the per-volume stage model
and badge-not-tab UI guidance (§3). `phase-4-space-planning.md`: the cross-reference this pass found
missing — a live containment breach is the signal to consider a promotion back into phase 3 (§4).
`_skill-source/SKILL.md`: its condensed "Phase 3 — Massing (folded-in method)" section gains the same
Stage 1/Stage 2 one-liner (its condensed phase-4 pointer needs no edit — it carries no folded content to
update, confirmed by reading the full file). `GLOSSARY.md`: new entries for Stage 1/Stage 2 (with the LOD
100/200 cross-reference), Promotion, and the decision-log `"Space planning → Massing"` convention.
`02_Decision-Log.md`'s documented convention (wherever it's described — `phase-3-massing.md`'s "Converge"
section is the natural home) gains the promotion row shape. Repackage `design-process.skill` via
`python -m zipfile`, never PowerShell's `Compress-Archive` (per `HANDOFF.md`'s own 2026-09-06 note on why).
**Checkpoint:** seed a fresh test project's Massing/Test-Fit instruments from the updated references (same
bar `Two-Stage-Massing` §12 Stage 4 and `Fork-Decision`'s Stage 6b already specified) and confirm: a
promotion action is describable and buildable from the reference text alone; Nyando-style freeform-without-
massing language still reads correctly, uncontradicted, next to the new prose; `GLOSSARY.md`'s new terms
don't collide with existing ones (grep clean).

---

## 8. What's genuinely at risk, and what explicitly is not

**At risk, honestly, additive to `Two-Stage-Massing-2026-09-09.md` §11's list (which still holds — the
write path, the containment reversal, the bbox-grow limitation, the multi-session scope — all restated
there, not repeated here):**

- **The provenance flag is new schema on `state[i]`**, the first field on Massing's live objects that isn't
  pure geometry/type/glazing. This pass recommends **deferring** any export-side reflection of it — don't
  add `stage`/`promoted` to `massing-interchange/v1`'s `volumes[]` shape until a real downstream consumer
  asks for it, same "don't build until an earned failure" discipline the tool already applies elsewhere.
  But flag the sharper risk plainly: `massing-interchange/v1` already carries a `program`/`metrics` field
  ("whatever the Studio already computes... pass the live numbers through," `phase-3-massing.md` item 4) —
  if that field is ever populated from a promoted scheme's `facade`/`D3`, it must carry the same tagged/
  sentinel value the UI shows, not the silently-wrong raw number, or the dishonesty this whole pass exists
  to fix would leak one layer downstream into a file a Rhino/Revit user trusts blindly.
- **`metricsDisplay()` is new code, genuinely new judgment, not a lift.** §2/§7 name the design (wrap, don't
  edit `metrics()`/`drivers()`) specifically so the "pure functions lifted, not rewritten" rule is honored
  everywhere it can be — but the wrapper itself is a real, new piece of logic this pass is introducing, not
  disguising as a lift.
- **The `[schematic-only]`-style tag stretches the existing judgment-flag convention** (`GLOSSARY.md`'s
  `Judgment flag`, originally for prose/scorecard judgment calls) to cover a live-computed, gone-stale
  number — a related but not identical use. Worth Ben's explicit sign-off before it's written into
  `GLOSSARY.md` as an extension of that term, not assumed.
- **Stage 4's badge is a real bet that could be wrong** — Ben asked for tabs; this pass recommends against
  them on reasoned grounds (§3), but the checkpoint pause before Stage 5 exists specifically because that
  disagreement should be tested against the real thing, not settled on paper.
- **Two pre-existing, unrelated gaps this pass found while checking §4's questions, not fixed by it:**
  `state.json`'s `looping-back` status isn't populated even for an already-logged real loop in Nonimuss's
  own decision log; Nyando's `state.json` is a self-invented shape whose own note is now stale (the
  template it says doesn't exist, does). Neither is this pass's job to fix — flagged so they don't get
  mistaken for something this pass already handled.
- **This is a multi-session project, said in those words** — a new schema field, new wrapper-function
  logic, a new UI element, and rewrites to two reference files plus the glossary and a skill repackage is
  clearly more than one sitting, the same honest expectation every prior pass in this thread has already
  carried.

**Explicitly NOT at risk:**

- **Steps 1, 2, 4, 5 of the 8-step plan, and §12 Stages 0-1** — untouched by this pass, re-confirmed by
  direct reads (§0) rather than assumed from the prior passes' own claims.
- **The cap meter** — confirmed clean twice now (§8 Q2's original derivation, this pass's re-check against
  the actual bbox-grow design) — the one metric that never needs stage-awareness of any kind.
- **D1, D2, D4, D5, CAP6** — confirmed safe at both stages under the design this tool has actually
  committed to (D5 specifically clears the doubt §8 Q2 originally raised about it, now that one-box-per-
  room is off the table). D2 legitimately reacting to a promoted box's new size is correct behavior, not a
  distortion, and needs no flag.
- **`drawPlanCut()`/`levelElevations()`/`liveMassingCut()` (Step 5's whole mechanism)** — needs zero
  changes; a promoted box draws through the exact same code path any slider edit already uses.
- **What's editable, in either Studio, at either stage** — sliders stay live everywhere; a promotion is a
  provenance fact, never a lock.
- **Nyando's freeform-without-massing workflow** — confirmed unaffected by construction (§4), twice now.
- **The `massing-interchange/v1` schema as it exists today** — this pass recommends no changes to it; any
  future provenance field is additive-only and explicitly deferred, not a breaking change.
- **The drivers-lock gate** — does not move, does not reopen, re-confirmed with one sharpened caveat
  (coverage is the metric worth actually watching for a post-lock finding).
- **The offline-first, `file://`-openable, no-build-step, no-server property** — nothing proposed here
  needs any of that to change.

---

**This is a multi-session project.** Stage 2 (preview text) is small and cheap and stands alone even if
nothing past it ships. Stage 3 (the commit) is where the real new risk concentrates — the provenance flag
and the metrics wrapper both need to exist together, correctly, before the button ships, not as a fast
follow. Stage 4's pause is deliberate: Ben should see the badge before Stage 5 writes it into the method
docs every future project inherits. Stopping at any point after Stage 2 leaves the tool better than it
found it — same safety property every prior stage of this plan has already named.

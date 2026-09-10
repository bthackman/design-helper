# Massing ↔ Test-Fit merge — 8-stage checkpoint plan

**Status: RECONSTRUCTED 2026-09-09 (later session), not recovered.** The original 8-stage split was
agreed in conversation during the Stage 0 session and never written to a file — only Stage 0 itself is
described, in `HANDOFF.md`. That conversation's context is gone. What follows is rebuilt from three
things that *are* on disk: the recommendation and staging guidance in `Architecture-Dream-2026-09-09.md`
§5(A)/§6, the Stage 0 entry in `HANDOFF.md`, and a fresh read of both Studios' current source. The
stage *count and numbering* are constrained by the Stage 0 entry's own phrasing ("8 checkpointed
stages", "Stages 1–6b"), which gives exactly 0, 1, 2, 3, 4, 5, 6, 6b — so the shape is real even where
the contents are inference. **Treat the contents as a proposal to correct, not as a record of what was
agreed.** Where this version differs from what Ben remembers, Ben's memory wins; amend this file rather
than arguing from it.

## Ground rules carried from the dream pass

These are not stages; they constrain every stage.

- **Nothing auto-applies geometry.** The 2026-09-09 House/Office drift lesson stands: growing one
  volume can force another to shrink, so whether a volume resizes to fit its rooms stays a judgment
  the architect makes. Every stage below renders *mismatch*, never resolves it silently.
- **Offline-first, `file://`-openable, no build step, no CDN.** Plain HTML/JS throughout. This is the
  property the 2026-09-07 UI review called "exactly right"; the dream pass rejected option (B) partly
  to keep it.
- **Nothing ships called "verified" on a brace-count.** Every checkpoint is driven through
  `_UI/_playwright/harness.py` in a real headless browser, against `_UI/_playwright/qa-scratch/`
  files — never the real project's canonical interchange files.
- **Each stage is independently valuable and independently abandonable.** If the plan dies at Stage 3,
  what exists at Stage 3 is still better than what existed at Stage 2. No stage leaves the tool in a
  worse state than it found it.
- **Pure functions get lifted, not rewritten.** `drivers()`, `metrics()`, `drawSection()`,
  `updateTrade()` on the Massing side; `adjacencyResults()`, `hubClearance()`,
  `caseworkDoorViolations()`, `caseworkWindowNotes()`, `onCapArea()`/`onCapBBox()` on the Test-Fit
  side. If a stage finds itself rewriting one of these, that stage has gone wrong.
- **The `massing-interchange/v1` export pipeline is untouched.** `buildInterchange()`/`exportJSON()`
  keep working identically at every stage — the Rhino/Revit path runs alongside real DIALOG work and
  does not get destabilized by this.

---

## Stage 0 — Make the *existing* file sync visible ✅ DONE (2026-09-09)

The dream pass's option (D), built as the cheap fallback that was worth doing regardless of whether
Stages 1+ ever happen. Both directions now draw dashed ghost geometry instead of only a text delta:
`rebuildGhosts()` + `ghostGroup` in `Massing-Studio.html:624`, and the `massingSync.volumesByLevel`
branch in `Test-Fit-Studio.html:521-538` drawing an amber dashed rectangle in the SVG plan.

Both deliberately anchor to each tool's *own* local bounding box rather than claiming a cross-tool
site position — because the axis correspondence is unverified. Stage 1 is what removes that hedge.

**Checkpoint (met):** both directions round-tripped live through the harness, zero console/page
errors, screenshots `dir1_testfit_ghost.png` / `dir2_massing_ghost.png`.

---

## Stage 1 — Verify the axis correspondence by hand, once

**Why first:** `Architecture-Dream-2026-09-09.md` §8 names this as still never checked, and flags that
option (A) *inherits the same coordinate mapping the current sync assumes*. Every ghost overlay from
Stage 4 onward is positionally meaningless until this is settled. It is also the cheapest stage in the
plan and the only one that pays off even if everything after it is abandoned — Stage 0's two overlays
can drop their "centered on local bbox, not a site position" hedge the moment this lands.

**The concrete question**, from the current source: Massing scheme B places House at
`x:18, z:5, w:11.6, d:9.3` in what appear to be site coordinates (`LOT` shoelace, parcel centroid at
`LAT_LONG`). Test-Fit's on-cap Ground rooms span roughly `x 0→13, y 0→12.3` — a local origin at some
house corner, with off-cap rooms (`LK` at `x:-3`, `PL` at `x:-17`) running negative. So the working
hypothesis is `TestFit.x → Massing.x + offset`, `TestFit.y → Massing.z + offset`, same handedness,
same metre units. That is a *hypothesis*, not a fact — nobody has checked whether the axes are even
the same handedness, whether Test-Fit's y grows in the same direction as Massing's z, or which corner
the local origin actually sits on.

**Do:** work it out by hand against the two files and `Program-Test-Fit.md` — no code first. Confirm
or refute handedness, direction, origin corner, and offset. Then write the answer down as a named
mapping (a short section in this file or its own note), including what remains uncertain.

**Checkpoint:** a written mapping, plus — if the mapping holds — Stage 0's two overlays repositioned
to the real corresponding location and their hedging labels rewritten to say what is now known. If the
mapping *doesn't* hold (e.g. the axes turn out mirrored), that is a genuine finding and Stages 4–6
inherit a correction rather than a bug.

---

## Stage 2 — Separate model from renderers, in place, in both files

No merge yet, no behaviour change. Inside each Studio *as it stands today*, pull the live model and
the pure functions apart from the code that draws. Massing: `state` + `metrics()`/`drivers()` on one
side, `rebuild()`/`drawSection()`/`updateTrade()`/`refresh()` on the other. Test-Fit: `rooms`/`doors`/
`windows_`/`furniture` + `adjacencyResults()`/`hubClearance()`/`onCapBBox()` on one side, `render()`/
`renderPanels()` on the other.

**Why this stage exists:** Stage 3 puts both files' JS into one document. Doing that while the model
and the drawing code are interleaved is how name collisions and accidental shared globals get
introduced silently. Doing it in two separate files first, where each Studio can still be verified
against its own known-good behaviour, is what makes Stage 3 a mechanical move instead of a rewrite.

**Explicitly not in scope:** changing any formula, any UI, or any file format. A reader diffing this
stage should see code moved, not code altered.

**Checkpoint:** both Studios drive identically through the harness — the full QA-2026-09-09 task set
re-run, same numbers out, zero console/page errors. Byte-identical `buildExportData()` and
`buildInterchange()` output for the same inputs is the strongest available proof and should be the
actual assertion.

---

## Stage 3 — One page, two panes, two models, no relationship

Both Studios in one document: the Three.js viewport and the SVG plan side by side, both models live in
the same runtime, every existing side panel still reachable. **They still do not know about each
other.** The file sync from Stage 0 keeps working, unchanged, as the only link.

**This is the stage the dream pass called "a genuinely harder layout problem than either Studio
alone"** — 3D viewport + SVG plan + cap meter + driver proxies + sun-section + trade-space plot +
adjacency + hub-clearance, in one coherent page. Treat it as real design work with a real chance of
needing a second pass. The 2026-09-09 QA finding about Massing's topbar wrapping at 1440×900 is a
warning about exactly this class of problem; `layoutPanels()` measures rather than hardcodes, and
whatever this stage builds should measure too.

**Open question this stage must answer, not dodge:** does one page mean one file, or two files and a
host page? The tool's single-file idiom argues for one file (~1,600 lines combined today, which is
large but not unreasonable); the per-project generation step in Stage 6b is simpler with one seed.
Decide it here, with reasoning, rather than letting it happen by default.

**Checkpoint:** at 1440×900 *and* at ≥1600px, every control in both Studios is reachable and clickable
via a real Playwright click — not merely present in the DOM. Both models still export their own
interchange JSON unchanged.

---

## Stage 4 — The containment layer + the one-way live ghost

**This is the slice the dream pass named as the first thing to build and verify.** A pure function —
call it `containment(volumes, rooms)` — computing, per level, which rooms sit inside which volume, and
the same bbox/net-area comparison the Stage 0 advisory computes today. Then: Massing's footprint drawn
live inside Test-Fit's SVG plan, sourced from the same in-memory object, **on every drag, with no file
and no button**.

**The bar this stage has to clear** is the one Ben set: drag a volume in the 3D pane, and the dashed
footprint under the rooms moves in the same instant. Not on save. Not on sync. That is the whole
difference between Stage 0 and the point of this exercise.

Read-only, one direction. Rooms do not move. Nothing writes back into `state`.

**Depends on Stage 1** for where the footprint actually goes.

**Checkpoint:** a harness run that programmatically drags a Massing slider and asserts the SVG ghost's
coordinates changed correspondingly within the same frame — the assertion being on *geometry*, not on
status text.

---

## Stage 5 — The reverse live ghost

The mirror: the room bounding box drawn as a live dashed wireframe in the Three.js scene, from the same
in-memory object, updating as rooms are dragged. Reuses Stage 0's `rebuildGhosts()` machinery, but fed
from the live model instead of a parsed file, and called from wherever Stage 3 put the shared refresh
rather than from a sync button.

Still read-only both ways. At the end of this stage, mismatch in either direction is *visible and
live*, and nothing has been auto-resolved — which is the state the dream pass argued actually satisfies
the founding "steer, don't just pick" thesis across the massing↔layout boundary.

**Checkpoint:** drag a room in the SVG pane, assert the 3D wireframe's dimensions changed in the same
frame. Then the honest one: delete a whole Massing volume — the exact test that produced *zero* visible
change and started all of this — and confirm it now produces a visible change in the plan.

---

## Stage 6 — Reconciliation as a proposed action, never an automatic one

The only stage that writes across the boundary, and it writes only when the architect says so. "Fit
this volume to its rooms" / "fit these rooms to this volume" as an explicit, previewable, undoable
action — showing what else it would knock out of tolerance *before* it applies, because that is the
House/Office lesson in tool form.

**The design risk here is real and should be named up front:** the moment this exists, the temptation
is to make it automatic, and automatic is the one thing the dream pass and the existing sync comments
(`Massing-Studio.html:552-555`) both explicitly warn against. If this stage starts drifting toward
auto-apply, stop and re-read that comment.

**Checkpoint:** apply a reconciliation, assert both models updated coherently, assert undo restores
both exactly, assert cap math and driver proxies recomputed to the values the pure functions would give
for the new state.

---

## Stage 6b — Propagate to the generation method, and repackage

The stage that turns this from one project's HTML into the tool. Today `phase-3-massing.md` and
`phase-4-space-planning.md` each independently seed a project's own hardcoded `DEFAULTS`/`ROOMS` into
two separate files. Under (A), seeding produces one cross-referenced instrument.

**Specifically:**
- `_skill-source/references/phase-3-massing.md` and `phase-4-space-planning.md`: the Studio-building
  method changes from two independent seeds to one seed with volumes and rooms cross-referenced by
  level/containment from the start.
- **`phase-4-space-planning.md:39` currently encodes the superseded call** — it states in the shipped
  skill that the two Studios are "deliberately not a live link," citing the 2026-09-08 Fable take. The
  2026-09-09 dream pass supersedes that reasoning (§4 reassesses it explicitly and fairly). This line
  has to be rewritten, and rewritten *honestly* — recording that the earlier call was defensible on
  what it had, not pretending it was never made.
- `SKILL.md`: whatever the phase-boundary language needs, given one instrument now spans two phases.
- **Repackage `design-process.skill` via `python -m zipfile`** — never PowerShell's `Compress-Archive`,
  which silently writes backslash separators that break extraction on Mac/Linux.
- `HANDOFF.md`: a dated entry in the usual voice. `00_Tool-Concept-Spec.md`: backlog rows closed.

**Checkpoint:** seed a *fresh* project's instrument from the updated references and drive it through
the harness — the real test being whether the method reproduces, not whether Nonimuss still works.

---

## Honest read on the whole plan

The dream pass called (A) "a real, multi-session engineering project — bigger than anything built in
one sitting so far," and that is still the right expectation. Stages 1 and 2 are small. Stage 3 is the
one most likely to need a second attempt. Stage 4 is where the payoff first becomes visible, and is
the natural place to stop and reassess whether the rest is worth it — everything through Stage 5 is
read-only and reversible; Stage 6 is the first stage that changes what the tool *does* rather than
what it *shows*, and Stage 6b is the first that changes what ships.

Stopping after Stage 5 would leave a genuinely better tool. That is the plan's main safety property
and it should not be traded away for momentum.

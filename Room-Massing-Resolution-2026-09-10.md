# Room massing, resolved — 2026-09-10

**What this is.** A build session, not a thinking pass — the thing Ben asked for is built, in the
working tree, uncommitted. It reopens ground `Fork-Decision-2026-09-09.md` §5 deliberately covered
("Promotion is box-grow only — never one-box-per-room"), engages the reason that rule exists head-on,
and explains exactly how this build honors it anyway. Read `Fork-Decision-2026-09-09.md`,
`Merge-Stages-2026-09-09.md`, `Two-Stage-Massing-2026-09-09.md`, `Two-Stage-Integration-2026-09-09.md`
and `Two-Stage-Build-2026-09-09.md` first if you haven't — this document assumes you have.

**No browser or Node.js exists on this machine.** Every verification claim below says exactly what
method was used instead (static reading, brace/paren/bracket/div balance counts, cross-referencing every
new DOM id against every `getElementById` call, grepping both source files for name collisions, a
byte-identity check on the Python port of the build script). None of it is a substitute for actually
clicking the buttons in a real browser — that is named as the open item it is, not glossed over.

---

## 1. What Ben asked for, and what was built and rejected first

Earlier the same session (uncommitted, still in the working tree, described in the harness prompt),
a "3D room massing" tab was added *inside* `Test-Fit-Studio.html` itself: a second, self-contained
Three.js scene (`rmScene`/`rmCamera`/`rebuildRoomMass()`, all `rm`-prefixed) rendering one live box per
room, auto-rebuilding on every `render()` call. Ben's own words on seeing it:

> "Still not quite what i meant - because i wanted it to go back into the massing studio where sections
> and sun study etc is visible with the new massing."

Confirmed separately, before this build, in his own words: (a) one box per room, not grouped by
type/cluster; (b) reachable as a second, clearly distinct view, not a buried toggle; (c) live/automatic,
no click, no "reshape"/"promote" step for this view specifically.

The gap in the first attempt wasn't the geometry — it was genuinely one box per room, correctly derived,
correctly live. The gap was that it was a *bare 3D box viewer* with none of Massing Studio's own
instruments (section cut, sun-study, cap meter, driver proxies, trade-space plot) working against it.
Ben's ask is specifically that those instruments — the ones that already exist, that he already trusts —
run against the room-derived geometry too.

## 2. The tension, engaged directly

`Fork-Decision-2026-09-09.md` §5 states: *"Promotion is box-grow only — never one-box-per-room. Load-
bearing, not stylistic: the moment a room becomes its own volume, nVol, D3 and D5 break for real."*
`Two-Stage-Massing-2026-09-09.md` §8 Q2 worked this out in numeric, checked detail against the real
Nonimuss data: one-box-per-room inflates `nVol` from 5–6 to 11+ (every articulated scheme reads
"complex" regardless of design quality — a threshold in the code, not a guess), and `facade`/`effLoss`
(and through them `D3`) **double-count every shared interior wall** between adjacent rooms, because the
formula sums `2*(w+d)*h` over every box with no concept of "this face is interior, not envelope."

Found new, while building this feature, and not in either prior document: `drivers()` itself calls
`findBox('house')`/`findBox('pool')`/`findBox('link')` for `D2`, `D4`, `OQ-6`, and the link-aspect term
of `D5` — a **single-box lookup**. With several house-type rooms, `Array.find()` would silently return
whichever one it hits first — a wrong number with no visible tell, worse than a number that's merely
imprecise, because it looks exactly as authoritative as a real one.

None of this is hypothetical risk to manage later. It is exactly what would happen if Test-Fit's rooms
were fed into `state`, `metrics()`, or `drivers()` directly. **They never are.** Nothing about this build
touches `state`, `metrics()`, `drivers()`, `DEFAULTS`, or `WORK`. Those stay byte-identical to before this
session (verified the same way `metricsDisplay()`/`schemeDrivers()` already had to be verified: the
function bodies are untouched; only new code sits beside them).

## 3. The resolution actually built

**A second mode of Massing Studio itself** — "Schematic (Stage 1)" / "Room massing (live)" — a real
button pair in `Massing-Studio.html`'s own topbar, not a hidden toggle inside another tool. It:

- Builds `roomBoxes()`: one Massing-shaped box (`{id,type,x,z,w,d,h,base,glaz}`) **per Test-Fit room**,
  not aggregated by type — box-per-room is exactly what `promoteVolume()` is deliberately forbidden from
  writing into `state`; this function never writes into `state` at all, so building it doesn't reopen
  that rule. Feature-detects Test-Fit's `rooms`/`roomVolumeType` exactly like `testFitBBoxFor()` already
  does for promotion (same contract: real only inside the generated `Design-Studio.html`, a safe no-op
  in a standalone open of either file).
- Feeds those boxes into **the same `drawSection()`** Stage 1 already uses — section cut and sun-study,
  completely unchanged code, via a swap-and-restore trick (`withBoxes(boxes, fn)`) that generalizes the
  exact idiom `schemeDrivers()` already used for `drivers()` one screen up in the same file. `drawSection`
  itself is not edited, not touched, not forked — it is called with a different `state` momentarily
  swapped in, then restored, the same "lifted, not rewritten" discipline `metricsDisplay()` already set
  the precedent for.
- Feeds those boxes into **the same `metrics()`**, same trick, but shows only the subset that's honest at
  this grain: **cap meter** (`areaOfTypes()` sums `w*d` filtered by type — arithmetically identical for 1
  box or 12, the one metric both prior documents already found clean at every granularity), **lot
  coverage** (shown, captioned as a literal room-grain sum rather than Stage 1's single-box figure — more
  literal, not less, since real rooms exclude the notch/gap area a bounding-box would include), and
  **enclosed volume** (floor area × height has no perimeter/double-count problem the way façade does).
- **Does not compute or show** façade, glazed façade, build-simplicity, the driver-proxy panel (D1–D5,
  OQ-6), or the trade-space plot in this mode — not tagged/greyed the way a Stage-2 promotion is (there is
  no single promoted volume to caption here; the whole grain changed), just hidden, replaced by one plain
  note: *"Façade, glazing, build-simplicity and the driver-proxy scores aren't shown here — see Schematic
  (Stage 1) for those."* This is the prompt's own second option, taken deliberately: the cap meter and
  section/sun-study are real and useful at this grain; the driver-proxy formulas were calibrated for
  Stage 1's few large volumes and were never asked to mean anything at this one.
- Renders one live 3D box per room in a **separate Three.js group** (`roomBoxGroup`, visibility toggled
  against Stage 1's own `bgroup`) — colored by type (falling back to a neutral grey for an unmapped
  cluster, the same honest gap `roomVolumeType()` already has for a fresh Wellness-cluster room), each
  room's own height/base pulled from whichever Stage-1 box of that type already exists (so the two views
  agree on storey height where they can), same construction pattern the superseded Test-Fit tab already
  proved (see §4).
- **Live, no click**: Test-Fit's own `render()` — already called on every room drag/add/resize — now
  also calls a new, narrow `refreshMassingRoomMode()` in Massing Studio, mirroring the exact asymmetric
  shape `refreshPromotionPreview()` already established (a reverse-direction cross-call that never calls
  back into Test-Fit's own `render()`, so there is no mutual-recursion loop). Dragging a room in Test-Fit
  updates Massing's room-mode view in the same instant, the same bar Step 5's live plan-cut already set
  ("not on save, not on sync").

## 4. What was kept from the earlier attempt, and why

Test-Fit's own "3D room massing" tab (`rmScene`/`rmCamera`/`rebuildRoomMass()`, `Test-Fit-Studio.html`)
is **kept, not deleted**. Its box-per-room geometry construction and its live-rebuild-on-`render()`
pattern were the direct model for `roomBoxes()`/`rebuildRoomBoxes()` above — lifted and re-shaped into
Massing's own box format and rendering conventions, not shared by reference (the same per-file-copy
convention every other cross-Studio read in this codebase already uses, e.g. `drawPlanCut()`/
`levelElevations()`).

It stays valuable in exactly one real case: a project with **no Massing Studio at all** (Nyando-style —
`phase-4-space-planning.md:26`'s own "freeform by default" principle). There, Massing's new mode has
nothing to attach to — no `Design-Studio.html` merge exists, so the room-derived section/sun-study/cap
meter can't be reached at all. Test-Fit's own standalone tab is the only room-massing view such a project
can have, and it still works exactly as built. Its button was relabeled "3D room massing (standalone)"
and its tooltip now says plainly that the integrated view (section/sun-study/cap-meter) lives in Massing
Studio's own mode instead, so a future reader isn't left thinking these are two competing, redundant
features — one is the real answer, the other is what's left when the real answer's prerequisite (a
Massing Studio to integrate with) doesn't exist.

## 5. Where to find it

- **Project Window → Massing phase → the sub-toggle already there** (was "Schematic (Stage 1)" /
  "From rooms (Stage 2 — live)", built earlier this session pointing at Test-Fit's disconnected tab).
  Now: "Schematic (Stage 1)" / "Room massing (live)". In any project with a merged
  `Design-Studio.html`, this opens `Design-Studio.html?pane=only-ms&mode=rooms` — Massing's own pane,
  in the new mode. In a project with only a standalone Test-Fit Studio and no merge (no Massing Studio to
  integrate with), it falls back to Test-Fit's own `?view=mass` tab, unchanged.
- **Directly**: open `Projects/Nonimuss-Residence/Design-Studio.html`, click "Massing only" (or leave it
  side-by-side), then click **"Room massing (live)"** in Massing's topbar, next to "Schematic (Stage 1)".
- **Standalone** `Massing-Studio.html` also has the button — clicking it shows a plain message ("No room
  data in this runtime...") rather than an empty scene, since a standalone open has no Test-Fit rooms to
  build boxes from. This is not a bug being papered over; it's the same feature-detection contract every
  other cross-Studio read in this codebase already uses (`testFitBBoxFor()`, `liveCutForLevel()`, etc.).

## 6. What you'd see, walked through (unverified in a real browser — see §8)

1. Open `Design-Studio.html`, click "Massing only". House is selected by default.
2. Click **"Room massing (live)"**. The Stage-1 "Steer a volume" panel, the driver-proxy panel, and the
   trade-space chart all disappear, replaced by a note under "Cap & metrics": *"10 rooms, one box each —
   live from Test-Fit, no click needed. Façade, glazing, build-simplicity and the driver-proxy scores
   aren't shown here — see Schematic (Stage 1) for those."* The 3D view redraws as 10 separate boxes
   (GR, MB, GU, GB, MU, ML, LK, PL, OF, LKU — VOID is `illustrative:true` and correctly excluded), each
   roughly the room's own footprint at its mapped volume's height.
3. Dwelling floor, Pool, Lot coverage, and Enclosed volume still show real numbers — computed from the
   room boxes, not the Stage-1 boxes. Lot coverage reads with a hover tooltip explaining it's a room-grain
   sum. Façade/Glazed façade/Build simplicity rows are hidden entirely.
4. The section-cut canvas and the N–S/E–W toggle and cut slider all still work, now slicing through the
   room boxes instead of the six schematic volumes — the same sun rays, the same "winter noon sun rakes in
   at only 15.6°" note, because that text is fixed prose, not data-driven.
5. Drag a room in Test-Fit's plan pane (switch to "Side by side" or "Plan only" to reach it). The 3D room
   boxes in Massing's pane move in the same instant, no click, matching Ben's own bar for this specific
   feature.
6. Click "Schematic (Stage 1)" again — everything reverts to exactly what existed before this feature was
   built; `state`/`WORK`/`metrics()`/`drivers()` were never touched, so there is nothing to "undo."

## 7. Regeneration and de-collision

`Projects/Nonimuss-Residence/Design-Studio.html` was regenerated from both edited sources. No Node.js
exists on this machine; the Python port at the scratchpad path (`build_design_studio.py`) was used —
before touching anything, it was run against the **unmodified** sources and diffed byte-for-byte against
the working tree's existing `Design-Studio.html` (which a prior session had already generated with real
Node or this same port): identical, confirming the port is a faithful, in-sync copy of
`_UI/build-design-studio.js`, not a silent fork. One real drift was found and fixed in the port itself
before using it further: it was missing a comment block (the `?pane=` embedding-page explanation) present
in the real `.js` source — a comment-only difference with no behavioral effect, but fixed anyway so the
two stay byte-for-byte aligned, not just behaviorally equivalent. After the fix, the port was re-run
against the *edited* sources and the output's `git diff` was read in full: proportionate (446 insertions,
12 deletions against the last commit, plus everything already uncommitted from earlier this session), and
every added function/id traced to a specific, intended change — no stray reformatting, no silently
dropped content.

De-collision, checked by grep (per this repo's own documented history of exactly this bug class): every
new global (`withBoxes`, `roomBoxesAvailable`, `roomBoxes`, `rebuildRoomBoxes`, `redrawSection`,
`refreshRoomMode`, `refreshMassingRoomMode`, `setMassMode`, `roomBoxGroup`, `massMode`) and every new DOM
id (`bModeSchem`, `bModeRooms`, `stage1Steer`, `stage1Drivers`, `stage1Trade`, `roomModeNote`,
`roomModeTradeNote`, `rowFac`, `rowGlaz`, `rowSimp`) was grepped against the *other* source file: zero
collisions. `refreshMassingRoomMode` — the one name that genuinely needs to be visible from the other
file — is called through the same `typeof x === 'function'` guard every existing cross-Studio call
already uses, so it degrades to a no-op wherever Massing Studio's script hasn't run (or doesn't exist).

## 8. Verified vs. genuinely unverified

**Verified, by static method:**
- Brace/paren/bracket/`<div>` balance on both edited source files: exactly balanced (`Massing-Studio.html`
  316/316 braces, 1313/1313 parens, 147/147 brackets, 53/53 divs; `Test-Fit-Studio.html` 467/467, 1204/1204,
  156/156, 47/47).
- Every new DOM id referenced by `getElementById` in the new JS exists in the new markup, and vice versa
  (read back directly, not just grepped for presence).
- No global-name or id collisions between the two source files (grepped both directions).
- The regenerated `Design-Studio.html` balances the same way (803/803, 2551/2551, 303/303, 105/105) and
  its diff is proportionate and traceable.
- The Python build-port reproduces the real `.js` source's behavior byte-for-byte on the unmodified
  sources (confirmed before any edits), and was corrected to match a comment the two had drifted apart on.
- The reasoning for what's hidden vs. shown in Room massing mode was checked against the actual formulas
  in `metrics()`/`drivers()` line by line (not re-derived from memory of the prior documents' own
  numbers) — `areaOfTypes()`, `2*(w+d)*h`, `findBox()`, the `nVol<=4` threshold — same method
  `Two-Stage-Massing-2026-09-09.md` §8 Q2 itself used.

**Not verified — genuinely unverified, not glossed over:** nothing was clicked. No browser exists on this
machine (confirmed: `node` absent from PATH; the task brief states no working Playwright either). The
mode-toggle buttons, the live drag-updates-the-3D-view behavior, the section/sun-study actually slicing
through the new boxes correctly on screen, the cap-meter numbers actually matching a hand calculation
against the real Nonimuss room data, and the standalone "no room data" fallback message actually
rendering instead of throwing — none of this has been driven through a real (or headless) Chromium the
way `Two-Stage-Build-2026-09-09.md`'s own checkpoints were, because that session had a working Playwright
environment on a different machine (`C:\Users\bthac\...`) that this one does not have. **This is the
single most important open item**: the first thing worth doing when a browser is available is exactly
what that report's own bar already establishes — open `Design-Studio.html`, click "Room massing (live)",
confirm the numbers and the live drag, before trusting this further.

## 9. Known gaps, left deliberately for Ben rather than guessed on

- **Method-doc propagation not done.** `_skill-source/references/phase-3-massing.md` and
  `phase-4-space-planning.md` still describe only the Stage 1/Stage 2 *promotion* split from the earlier
  session's work — they say nothing about this new, additional "Room massing (live)" mode. Unlike the
  promotion mechanism (which changes what a future project's *generation method* should seed), this mode
  is closer to an always-in Studio feature (like the sun-section itself) than a per-project authoring
  decision — but that's a judgment call, not a settled fact, and propagating it into the reference docs
  wasn't in the explicit scope handed to this session. Left as a real, named gap rather than silently
  done or silently skipped.
- **The "Stage 1"/"Stage 2" naming collision with `phase-2-site.md`'s unrelated "Stage 1 — zone
  scorecard"/"Stage 2 — parcel scorecard"**, already flagged in `Two-Stage-Build-2026-09-09.md`, is
  untouched here — this build reuses "Schematic (Stage 1)" as a label (matching what already shipped),
  not a new instance of the collision, but doesn't resolve the pre-existing one either.
- **The unmapped-cluster gap is now visible in a second place.** `Test-Fit-Studio.html`'s own
  `CLUSTER_VOLUME_TYPE` comment already names this honestly: a new Wellness-cluster room has no volume
  type to map to (Wellness covers both Pool and Link). `roomBoxes()` inherits this exact gap — such a room
  gets a generic grey box and counts toward nothing type-filtered. Not fixed here; fixing it means
  deciding how a Wellness room disambiguates between Pool and Link, which is Ben's call, not a build
  decision.
- **No real click-through exists yet** (§8) — the single biggest thing to do next.
- **Whether "Room massing (live)" should also gain its own promotion-style write path** (e.g., a future
  "use this room's real footprint as its Stage-1 box's new size" for an INDIVIDUAL room, distinct from the
  existing aggregate "Reshape to fit") was not asked for and was not built. `promoteVolume()`'s box-grow-
  only contract is completely unchanged and untouched by this session.

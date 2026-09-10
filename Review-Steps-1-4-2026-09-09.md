# Third-party review — Steps 1–4 (2026-09-09)

**Reviewer's method, stated up front:** everything below was either (a) re-derived by hand from
the raw numbers in the actual files, (b) confirmed by `git diff`/`git status` against the tracked
baseline, or (c) driven through a real headless Chromium via Playwright
(`C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe`, playwright 1.62.0) and read
back from the live DOM/JS state — never from the prior session's own prose. Where I only read code
and reasoned about it rather than executing it, I say so explicitly. Scripts used are throwaway,
written to the session scratchpad; screenshots are under `_UI/_playwright/qa-scratch/` with a
`review_` prefix so they don't collide with the prior session's own `step1_…`–`step4_…` files.

**Bottom line: Steps 1–4 hold up. One real bug was found in Step 4 that the prior session's own
testing missed (below), and one important non-code fact needs flagging — Nonimuss-Residence's files
are tracked and public in this repo, not gitignored, contrary to the general project convention.
Everything else claimed — the axis correction, the anchor position, all four conflicts, Nyando's
isolation, the export pipeline's byte-identity, and the "no CDN" correction — checks out against
independently re-derived numbers, not just against the prior session's narration.**

---

## 1. Step 1 — the axis correction (re-derived independently, not taken on trust)

**Verdict: the correction is right, and it's right for a better reason than the write-up gives it
credit for.** `Fork-Decision-2026-09-09.md` §1 "confirmed" (its own words) that the two tools'
axes were transposed (`TestFit.x ↔ Massing.z`), based on comparing room *extents*: Test-Fit's old
`PL` was `w:14.0,h:6.0` against Massing's `Pool` `w:6,d:14` — extents swapped, so (the reasoning
goes) the axes must be swapped.

That reasoning has a hole: **swapped extents are also exactly what a room drawn rotated 90° within
the *same* axes looks like.** Extent comparison alone cannot distinguish "the coordinate frames are
transposed" from "this one room was authored sideways." I checked which it actually is, two ways:

**a) Direction semantics, not extents.** `Massing-Studio.html:127`: `x=East(+), z=South(+), y=up`.
`Massing-Studio.html:481` (`buildInterchange()`'s own `axes` field, exported and therefore load-
bearing): `"North is -z... w = E–W extent, d = N–S extent"`. Test-Fit's door data, read against
compass-labelled walls: door `d-GR-MB` sits on GR's `'S'` wall (`wallInfo`: S wall's fixed coordinate
is `r.y+r.h`) and MB sits at the larger `y` — south is `+y` in Test-Fit's frame, matching south is
`+z` in Massing's. Door `d-GR-MU` sits on GR's `'E'` wall and MU sits at larger `x` — east is `+x` in
both. Both checks agree with each other and with `x=East` in both files. **No transposition.**

**b) A room that was never rotated, before-and-after Step 1.** `GR` (on-cap, never one of the
off-cap rooms the write-up says were drawn 90° out) has **identical `w:11.0,h:4.2` in the
pre-Step-1 backup and in the current file** — only its `x,y` origin moved (`+18,+5`, confirmed
below). If the axes really were transposed, GR's unrotated `w` (its x-extent, 11.0) should compare
against Massing House's **z-extent** (`d:9.3`), not its x-extent (`w:11.6`). It compares against
`w:11.6` — the x-to-x, same-handedness reading. This is the cleaner test because it isn't
confounded by rotation the way PL/OF are.

**c) Confirms the *actual* mechanism was per-room 90° rotation, not axis transposition.** Diffing
`Test-Fit-Studio.html.pre-step1-backup` against the current file: old `PL` was `w:14.0,h:6.0`; new
`PL` is `w:6.0,h:14.0` (w/h literally swapped) and now matches Massing `Pool` (`w:6,d:14`) exactly.
Old `OF` was `w:3.0,h:3.67`; new `OF` is `w:3.7,h:3.0`, now matching Massing `Office`
(`w:3.7,d:3`) exactly. That is what "the off-cap volumes were drawn 90° out from the locked Option
B massing" (the file's own current comment, `Test-Fit-Studio.html:143-144`) means, concretely — and
it is a different, narrower bug than a global axis transposition. The Step 1 session's fix (rotate
the specific off-cap rooms; leave the coordinate frame's handedness alone) matches the actual
mechanism; Fork-Decision's Finding 1 diagnosed the right symptom with the wrong cause. Since
Fork-Decision is the document this whole build is following, that its own "confirmed" §1 doesn't
survive a second, more discriminating derivation is worth Ben knowing plainly — not because Step 1
got it wrong (it got it right) but because the *governing document* had a real error in it that a
later session caught and fixed correctly.

## 2. Step 1 — the anchor and the four conflicts (hand-computed from `ROOMS`, matched to the decimal)

**Anchor translation:** old `GR.x,y = 0,4.0`; new `GR.x,y = 18.0,9.0` → **+18 East, +5 South**,
exactly as claimed, and the same delta applies uniformly across all six on-cap rooms (checked all
six, not just GR).

**Bounding box claim:** computing `min/max` of `x,y` over `{GR,MB,GU,GB,MU,ML}` from the current
`ROOMS` gives `x:[18,31]`, `y:[5,17.3]` → **13.0 × 12.3 m**, matching the claimed figure exactly and
matching `onCapBBox('Ground')`'s live output (confirmed by calling it directly in a running Test-Fit
Studio: `{x:18,y:5,w:13,h:12.3}`).

**"North face flush, GR's west wall on Link's span":** block's min-y is 5 (from `GU`), House box's
`z:5` — flush, confirmed. GR's west wall (axis `y`, per `wallInfo`) spans `y:9→13.2`; Link box is
`z:9→13` — overlaps for all but the last 0.2 m, close enough to "lands on" as stated, not a
misleading claim.

**All four conflicts, independently recomputed:**
1. Room bbox 13×12.3 vs House box 11.6×9.3 (`x:18-29.6,z:5-14.3`): east overrun on GB/MU/ML =
   `31−29.6 = 1.4 m` (exact); south overrun on ML = `17.3−14.3 = 3.0 m` (exact), on MB =
   `17.2−14.3 = 2.9 m` (the write-up says "≈3 m," which is fair).
2. `rectGap(OF, LKU)` computed by hand (OF `x8-11.7,y10-13`; LKU `x14-16,y9.5-12.5`) = `2.3 m`
   exactly, matching the claim and matching the live `adjacencyResults()` output, which correctly
   flags `OF↔LKU` as a **live violation** (`gap:2.3, status:'bad'`) — so this conflict isn't just
   sitting in a code comment, it actually propagates through to the UI's own violation check. Good
   sign the checks are wired to the real (moved) coordinates, not stale ones.
3. LK's `stairBox` spans `y:9→13.3` (h 4.3); LK room and the Link box both end at `y/z=13` →
   **0.3 m overrun**, exact.
4. MB's west wall (door `d-MB-LK`) spans `y:13.2→17.2`; Link box is `z:9→13` — genuinely
   non-overlapping, confirmed.

All four are real and correctly characterized — none is an artifact of the re-anchor script itself;
they're a real geometric consequence of moving actual room content into a smaller, real massing
footprint.

**One thing I checked beyond the brief:** whether Step 1's coordinate rewrite broke anything
downstream that *reads* these coordinates. Live-called `adjacencyResults()`, `hubClearance()`,
`caseworkDoorViolations()`, `onCapArea()` against the current file — all return finite, sane numbers
(no `NaN`, no negative clearances), and hand-verified `hubClearance()`'s four wall segments against
the actual door/casework positions (e.g. GR's S wall: length 11, door at `20.75±0.45` → residual
segments `2.3 + 7.8`, matches the live output exactly). Nothing downstream broke.

## 3. Step 2 — implicit envelope, and Nyando's isolation

Read `levelVolume()` (`Test-Fit-Studio.html:355-366`) and confirmed by live call (no massing synced)
that it correctly falls through to the `implicit` branch and reproduces `onCapBBox()`'s own numbers
for Ground; for Upper (only `OF` is on-cap) it correctly returns OF's own extent as the "envelope,"
which is the honest behavior for a single-room level with no synced massing — not a bug, just a
degenerate case worth knowing about if `Design-Studio.html`'s Step 5 plan-cut is ever compared
against it.

**Nyando, checked two ways, not one:** `git status` shows `Nyando-Maternity-Waiting-Home`'s files
as clean (not in the modified list), and `grep` for `levelVolume`, `massing-unpositioned`,
`onCapBBox` against Nyando's own `Test-Fit-Studio.html` returns zero matches — it's a genuinely
separate file, never touched. This is about as solid as "unmodified" gets short of a checksum.

The one place I'd push back gently: the claim that Nyando's Studio is "a completely different
instrument... sharing no code" is used to justify not following the Fork-Decision's literal
instruction to "promote `onCapBBox()` in Nyando." That's accurate as a description of the current
state, but it does mean **Stage 1b's promise — that a future Nyando gets `levelVolume()`-style
behavior "for free" — hasn't actually been implemented anywhere but Nonimuss.** If Nyando's
instrument is ever brought forward, `levelVolume()` will need to be written for it separately, not
inherited. Worth flagging as a real, not-yet-paid debt rather than a closed loop.

## 4. Step 3 — de-collision, checked against the actual git diff

`git diff` on `Massing-Studio.html` shows **exactly** the three claimed renames
(`view→viewEl`, `drag→orbitDrag`, `exportJSON→exportMassingJSON`) and nothing else — no stray
formula or data change smuggled in alongside the renames. This is the cleanest kind of verification
available (the diff itself, not a description of it). Test-Fit's `exportJSON→exportTestFitJSON`
rename confirmed by reading the current file directly (`buildExportData`/`exportTestFitJSON` both
present, old name absent).

Went looking for more of the class of bug the brief specifically flagged (the `['left','right']`
literal-array lookup) — `querySelector`/`querySelectorAll` calls (none in either file),
`localStorage` keys (`Massing` only: `"nonimuss-massing-work-v2"`; Test-Fit uses none — no
collision), IndexedDB store names (`ms-handles` vs `tfs-handles` — already distinct, good design
independent of this session's work), duplicate `addEventListener('resize', …)` (both fire, both
harmless — JS allows multiple listeners on one target), and dynamic template-literal ids
(`v_${k}` in Massing's slider labels) — confirmed Test-Fit defines no id starting `v_`, so no
collision exists today, though this specific pattern (`getElementById` reading a document-global
namespace regardless of which pane visually contains the element) is exactly the kind of thing that
would bite silently if a future edit ever introduced a same-named id in the other Studio. Found no
second instance of the `['left','right']` bug itself — it really was the one place that pattern
occurred in either file.

## 5. Step 4 — the merge: exports, console/page errors, and one real bug the prior session's testing missed

**Export byte-identity — confirmed live, not assumed.** Loaded standalone `Massing-Studio.html`,
standalone `Test-Fit-Studio.html`, and the generated `Design-Studio.html` in three separate
Playwright pages; called `buildInterchange()` in both the standalone Massing page and the merged
page's global scope, and `buildExportData()` likewise for Test-Fit. Diffed as JSON (dropping
`buildInterchange()`'s own `generated` timestamp field, which is expected to differ). **Both
matched exactly.** Zero console errors and zero uncaught page errors across all three loads.

**Console/page errors under interaction, not just at load.** Ran a real click sweep in the merged
page at both 1440×900 and 1920×1080 — scheme A/B/C, view Plan/Iso/Persp, section N–S/E–W, reset
scheme, rotate 90°, level Ground/Upper, scenario safe/demo, fit view — using unambiguous, pane-scoped
selectors. Zero page errors throughout, final camera state matched the clicked view's expected
values exactly (e.g. ending on Persp left `sph = {r:50,theta:0.4,phi:1.28}`, exactly `VIEWS.persp`).

*(One thing worth being honest about: my first pass at this click sweep used loose text-matching
locators and appeared to show Massing's whole pane collapsing to 0×0 after certain clicks. That
turned out to be my own test script clicking the **wrong button** — the shellbar's "Plan **only**"
layout button, not Massing's "Plan" view button, because my locator matched "Plan" as a substring of
"Plan only" and `.first` picked whichever came first in DOM order. Re-run with exact, pane-scoped
selectors, it's clean. Flagging this so it's clear I chased it down rather than either missing it or
reporting a false positive.)*

**Real bug found, not in the prior session's list — the export modals leak past their own pane.**
`Massing-Studio.html:68` and `Test-Fit-Studio.html:69` both have an inline `style="…
position:fixed;inset:0;…"` on their `#exportModal` div. `build-design-studio.js`'s
`position:fixed → position:absolute` rewrite (`scopeCss()`, line 69) only rewrites the **`<style>`
block text** — it never touches inline `style=""` attributes in the markup, so this one instance
survives unrewritten into the generated page. Confirmed by reading `Design-Studio.html:143` and
`:221` directly: both still say `position:fixed`. Confirmed live: opened each Studio's export modal
in the merged page at 1440×900 and read `getBoundingClientRect()` — both report
`{x:0,y:0,width:1440,height:900}`, i.e. the full viewport, not their own pane (`ms-pane` is
`0–768.6px`, `tf-pane` is `768.6–1440px`). Since the modal backdrop has no `pointer-events:none` and
covers the whole page while open, **opening either Studio's export/share modal blocks interaction
with the other pane until it's closed** — not data-damaging, not a crash, but a real, reproducible,
previously-unflagged interaction bug from the merge. This is exactly the class of thing the brief
asked me to hunt for and it's a legitimate find, not a restatement of the `['left','right']` bug
already caught.

Severity: low–medium. Nothing breaks, nothing is lost, and the workaround is "close the modal" — but
it's a real gap in the CSS-scoping pass, worth a one-line fix (either scope the inline style at
generation time, matching the `<style>`-block treatment, or add `position:absolute` to both source
files' inline attributes directly). I did not fix it, since fixing wasn't in scope for the review
and it's not on the critical path for Step 5 below (Step 5 doesn't touch either export modal).

**Panel crowding, quantified rather than just characterized.** At 1440×900, side-by-side:
`ms-pane` ≈768.6px wide, with `#ms-left` (270px) + `#ms-right` (330px) = 600px of fixed side-panel
width, leaving **≈168px** of the pane for the actual 3D drawing area. `tf-pane` ≈671.4px wide, with
`#left` (290px) + `#right` (340px) = 630px, leaving **≈41px** clear — worse than "cramped" suggests;
at that width Test-Fit's plan is barely visible between its own panels unless one or both are
collapsed (Test-Fit's panels can collapse via their `−`/`+` toggle; **Massing's cannot** — confirmed,
no `togglePanel`-equivalent exists in `Massing-Studio.html`, matching what the brief already said).
At 1920×1080 this eases: `ms-pane` ≈1025px (≈425px clear), `tf-pane` ≈895px (≈195px clear) —
better, still tight for Test-Fit specifically. The layout-mode buttons ("Massing only" / "Plan only")
are the real mitigation, confirmed working (each hides the other pane's flex item entirely, giving
the remaining pane the full window width).

## 6. One fact outside the code that matters for what happens next

`Projects/` is gitignored **in general**, but `.gitignore` carries a dated, explicit exception:
`!Projects/Nonimuss-Residence/` and `!Projects/Nonimuss-Residence/**`, with a comment recording that
Ben chose to make this specific project public "so a second Claude account... can pick up the
Massing↔Test-Fit architecture rework." `git status`/`git ls-files` confirm `Massing-Studio.html` and
`Test-Fit-Studio.html` are already tracked, and `git check-ignore` confirms `Design-Studio.html`
(new, untracked, generated) is **not** ignored either — if committed, it and
`_UI/build-design-studio.js` would go into the public repo along with everything else in
Nonimuss-Residence. This doesn't change anything about what was built, but it's worth stating
plainly since the task brief's framing ("`Projects/` is gitignored — real project content, never
pushed") is the *general* policy, not what actually applies to this specific project.

## 7. What I did not verify

I did not attempt pixel-level visual review of door swings/stair glyph rendering beyond confirming
their geometry inputs are internally consistent (walls contain their doors/stairs, no negative
spans) and that rendering them threw no console errors — I did not compare rendered SVG paths
against an expected drawing by eye. I did not exhaustively test every drag/resize interaction inside
each Studio (room drag, opening resize, stair rotate) post-merge — I relied on the export
byte-identity check (which exercises the same state-reading code the drag handlers write into) plus
the click sweep, not a full manual drag-through of both Studios inside the merged page.

---

**Summary table**

| Claim | Verdict | How verified |
|---|---|---|
| Axis correction (no transposition) | **Confirmed, and Fork-Decision's own Finding 1 was wrong** | Hand-derived from raw coordinates + direction semantics, independent of both prior sessions |
| Anchor (+18E, +5S), flush north face | Confirmed exactly | Hand arithmetic on `ROOMS` before/after |
| All 4 conflicts | Confirmed exactly (to the decimal) | Hand arithmetic + live `adjacencyResults()` |
| Step 2 implicit envelope | Confirmed working; Nyando promise not yet portable | Live function calls + git/grep |
| Nyando untouched | Confirmed | `git status` + `grep` for new function names |
| Step 3 renames | Confirmed, nothing else changed | `git diff` |
| No further hidden collisions | Confirmed (with one exception found — see below) | Targeted grep + live DOM checks |
| Export byte-identity (both Studios) | Confirmed | Live Playwright diff, standalone vs merged |
| Zero console/page errors | Confirmed, load + interaction | Live Playwright click sweep |
| Export modals leak outside their pane | **New finding — real bug, not previously flagged** | Live `getBoundingClientRect()` before/after opening each modal |
| Panel crowding at 1440×900 | Confirmed, worse than described for Test-Fit specifically | Live pane/panel geometry |
| Nonimuss is public/tracked, not gitignored | **New context, not a code bug** | `.gitignore` + `git check-ignore` |

# Containment & trade-space — 2026-09-09

Two asks: (1) make Test-Fit's rooms stay within the massing envelope, (2) explain the
trade-space chart and find out why it looked frozen. Both are now built/fixed in
`Projects/Nonimuss-Residence/4_Space-Planning/Test-Fit-Studio.html` and
`3_Massing/Massing-Studio.html` respectively, `Design-Studio.html` regenerated from both via
`node _UI/build-design-studio.js`. No commits, no `HANDOFF.md` entry, per the brief.

---

## Task 1 — "stay within the dashed boundaries of the mass"

### The facts, verified, not assumed

Called the real functions in a live browser rather than trusting the numbers I was handed:

- `onCapArea('Ground')` → **102.2 m²**. House box (scheme B) is `w:11.6, d:9.3` = **107.88 m²**.
  By area, the program already fits with ~5.7 m² to spare.
- `onCapBBox('Ground')` → `{x:18, y:5, w:13, h:12.3}`. By **shape**, it does not fit — the room
  block is 1.4 m wider (east) and 3 m deeper (south) than the box that's supposed to hold it.
- Four rooms genuinely breach today: `GB`, `MU`, `ML` overrun **1.4 m east**; `MB` overruns
  **2.9 m south**; `ML` overruns **3.0 m south**. (`GR`, `GU` are fully compliant.) These numbers
  come straight out of the new `containmentResults()` function, cross-checked against
  `Review-Steps-1-4-2026-09-09.md`'s independent hand arithmetic — they match to the decimal.
- Off-cap: `PL` (Pool), `LK`/`LKU` (Link), `OF` (Office) were each set to their massing box's
  exact footprint in Step 1, so today they're all compliant by construction. `VOID` is
  `illustrative:true` — it exists specifically to assert "nothing is here," so it's excluded from
  the check entirely (there's nothing for it to be contained *by*).

### Will "the mass should lead the sizes" work as asked? No — and here's the honest reason, not a dodge

Read literally, "the mass leads the test-fit sizes" means: when a Massing volume changes, the
rooms inside it resize or reposition to match. That is auto-applying geometry from one model to
another — the exact failure mode `Massing-Studio.html:552-557`'s own comment exists to warn
about (the House/Office drift lesson: growing one volume can silently shrink another), and the
exact reading `Fork-Decision-2026-09-09.md` §4 already rejected for a nearly identical ask
("the plan is a section through the mass"). I'm not building that, and I don't think you actually
want it once the consequence is concrete: if I wired `GB` to auto-shrink or auto-move whenever
`House` changes, the FIRST time you steer `House` even slightly, five rooms would silently
rearrange themselves off-screen with no undo, no preview, and no record of what moved or why —
worse than today's honest, visible mismatch.

But your real goal — **know that the program actually fits inside the envelope** — is completely
legitimate, and I don't think a passive check alone satisfies "stay within." So here's what I
built instead, and why I think it's the right mechanism, not a compromise:

**1. Live containment reporting.** A new `containmentResults()` computes, for every room, the
volume it belongs to (`GR/MB/GU/GB/MU/ML → House`, `PL → Pool`, `LK/LKU → Link`, `OF → Office` —
the same 1-to-1 mapping `Fork-Decision` Finding 3 already confirmed) and how far it overhangs
that volume's real footprint, per edge, in metres. A room that breaches is drawn with a **red
dashed outline**, a **⚠** on its label, and a caption like `outside House: +1.4m E`; the Checks
panel lists every breach with the exact overage. This is genuinely live where it can be: inside
`Design-Studio.html`, it reads Step 5's per-volume plan cut, so if you shrink `House` on the
Massing side, the newly-affected rooms light up red on the Test-Fit side **without either of you
touching a room** — the honest version of "stay within," reporting rather than silently fixing.

**2. A clamp, but only on new edits to a room that currently fits.** Drag or resize a room that's
**already fully inside** its volume, and it can't be dragged/resized into a *new* breach — I
tested this directly: dragging `GR` (compliant) 20 m east stops dead at `x:18.6`, exactly the
volume's edge; resizing `GU` similarly clamps to `w:4.6, h:9.3`. Drag a room that's **already**
outside (`GB`, `MU`, `ML`, `MB` today) and it moves completely freely — I tested this too (`GB`
dragged 3 m east moved the full 3 m, no resistance). This is deliberate, not an oversight: there
is no honest clamp for a room that starts broken. Snapping it inward the instant you touch it
would move geometry you didn't ask to move — the same forbidden auto-apply, just triggered by a
click instead of a slider. The clamp's job is narrower and more defensible: **stop ordinary
editing from silently making a compliant room non-compliant**, while leaving the four already-
broken rooms exactly as broken as they honestly are, free for you to fix by hand.

I also checked the case you specifically flagged — **the envelope shrinking underneath an
already-placed room.** Drove it directly: shrank `House`'s width from 11.6 m to 9 m live on the
Massing slider. `GR` (previously compliant) correctly lit up as a new breach in the Checks panel
— and its `x/y/w/h` never changed (confirmed by reading `rooms.GR` before/after: identical). A
follow-up drag attempt on `GR` at that point is correctly **not** clamped anymore, because the
compliance check re-runs fresh at the start of every drag — so the clamp never fights you over a
boundary that's already moved out from under a room.

### Will this work as intended?

**For "know that the program fits" — yes.** You will always be able to see, at a glance and with
exact numbers, which rooms fit and which don't, and it updates live as you steer either side.
**For "make the rooms stay within the boundaries" read as "make the current plan actually fit" —
no, and nothing honestly could without either you rearranging four rooms or growing the House box
(which, per the drift lesson, has its own knock-on cost elsewhere).** That reconciliation — a
real, previewable, undoable "make it fit" action — is explicitly **Step 7** on the staged plan in
`Fork-Decision-2026-09-09.md` §6, not this task. I built the half of this that's honest to build
today (visibility + a forward-only guardrail); pulling Step 7 forward half-built to make the
red outlines disappear would be exactly the shortcut the brief told me to flag rather than take.

### A real, worth-knowing asymmetry

Off-cap containment (`PL`/`LK`/`LKU`/`OF` against their own volumes) only works **inside
`Design-Studio.html`** — standalone `Test-Fit-Studio.html` has no way to check them, because the
pre-existing file-based "Sync from massing" mechanism only ever captured the dwelling
(House/Office) footprint, never Pool or Link geometry. Standalone Test-Fit still catches
House/Office-cluster breaches fine (via the pre-existing `levelVolume()`), but if you open
Test-Fit on its own with no massing synced at all, `containmentResults()` correctly reports
**nothing** rather than inventing a false "fits" — same honesty rule `levelVolume()`'s own
`implicit` case already follows.

---

## Task 2a — what the trade-space chart is actually showing

It's a **two-driver trade-off plot for the current scheme against the three named options**, not
a general dashboard. Concretely:

- **X-axis, "cap-safety (OQ-6)":** how defensible the pool/link/office arrangement is as an
  *accessory structure outside the 120 m² dwelling cap* — the "how do we argue the pool isn't
  developed floor space" fight named in `Massing-Options.md` and `01_Design-Drivers.md`. In code
  (`CAP6` in `drivers()`), it rewards the pool being clearly separated from the house **and** a
  link existing (a real threshold, not a fused wing), and penalizes an oversized "link" that
  starts reading as its own room.
- **Y-axis, "wellness continuity D2":** whether the swim–sauna–cold–garden sequence stays one
  continuous, weatherproof ritual — "walkable in a swimsuit at -20°C," per Driver D2. In code, it
  rewards pool/house/link sitting close enough (specific gap thresholds) to genuinely read as one
  linked sequence rather than a detached building you'd have to brave the cold to reach.
- **Bubble size:** winter thermal performance (D3) — bigger bubble, warmer scheme.
- **The three grey/blue-grey/pale-blue bubbles are A, B, C — fixed reference points, always the
  same**, since they're computed from `DEFAULTS.A/B/C.boxes`, which never change no matter what
  you steer. **The ★ is wherever your current, live-edited scheme actually sits right now** on
  those same two axes.

What you're meant to do with it: this project's whole massing argument is that Option B is "the
hinge that keeps both" — cap-safety *and* wellness continuity — where A sacrifices the cap
argument and C sacrifices D2 (`Massing-Options.md`'s own framing). The chart is the live version
of that argument: as you steer B's actual geometry, does your edit keep the ★ up near B's own
strong position (top-right-ish), or does it start drifting toward A's or C's compromise? If an
edit you like also drags the star toward C's corner (high cap-safety, low wellness), that's the
chart telling you you've traded away the "swimsuit-at–20°C" event to get there — the exact
invisible trade the spec (`00_Tool-Concept-Spec.md` #18) says this chart exists to surface.

**It is not** a general driver dashboard (that's the bars above it — D1/D3/D4/D5/OQ-6 all show
there too, all of them live) and it's not a full multi-objective optimizer. It's specifically the
two hardest-to-eyeball, most load-bearing trade-offs this particular project's decision turned on.

---

## Task 2b — why it "didn't appear to update," found and fixed

**The update mechanism itself was never broken.** Verified directly: `updateTrade()` is called at
the end of every `refresh()`, and `refresh()` runs after every single slider's `oninput` — I
read `chart.data`'s actual values before and after driving a real slider's `input` event and
confirmed the numbers do change on every edit, every time, with zero console/page errors. So
"doesn't update" was never a wiring problem. It's two separate, real, and fixable-differently
issues that together produce exactly the symptom you reported:

**1. The ★ was hidden behind the "B" bubble — a real rendering bug, now fixed.** On load, your
live scheme *is* scheme B (nothing's diverged yet), so the ★ sits at the exact same x/y as B's own
static bubble. I assumed Chart.js draws later-listed datasets on top and would show the star over
the circle — instead I read the actual canvas pixels (`getImageData`, not a screenshot guess) and
found the **opposite**: this build paints the array's first dataset on top. Since the code listed
`A/B/C` first and `★ live` second, the plain grey circle was painting directly over the star,
leaving only a couple of star-points peeking past its edge — for anyone opening the tool fresh,
there was **no visible star at all** until an edit moved it somewhere the grey circle wasn't.
**Fix:** swapped the array order so `★ live` is listed first. Re-verified with the same
pixel-level check: the center pixel at the coincident point is now the star's own color, and the
zoomed screenshot below shows a clearly visible orange star, B's grey rim just peeking around it
— the readable version of "they're in the same place," not "one is invisible."

| Before (star hidden under B) | After (star visible on top of B) |
|---|---|
| `_UI/_playwright/qa-scratch/trade_zoom_before.png` | `_UI/_playwright/qa-scratch/task2_trade_star_ontop_zoom.png` |

**2. Most ordinary edits genuinely don't move the dot — a real, but different, finding.** `CAP6`
and `D2` are **threshold formulas**, not continuous curves (this is true of every driver in
`drivers()`, not a defect specific to these two — see the `if(gap<1.4)... else if...` structure).
I drove this directly: nudging House 0.5 m east moved the star **zero pixels** (confirmed by
reading `chart.data` before/after — identical x/y); nudging it 2 m east instead of a smooth
shift produced a sudden **68-point vertical jump** (D2 94→26) the instant a specific gap
threshold broke. Separately, changing glazing % or height moves **only the bubble's radius**
(D3), never its position, since those sliders don't touch anything CAP6/D2 read. So a lot of the
edits you'd naturally try first — small nudges, glazing, height — are honestly reported as "no
change to this specific trade-off," which reads exactly like "the chart is frozen" even though
it isn't. **I did not change these formulas** — they're the same documented, already-validated
concept-grade driver proxies used everywhere else in this Studio (`00_Tool-Concept-Spec.md` #18:
"proven on Nonimuss — proxies reproduced the A/B/C narrative"), and redesigning them wasn't asked
for and isn't a call I should make unilaterally. Instead, I added a small always-current numeric
readout under the chart (`live now: cap-safety NN · D2 NN · D3 (bubble size) NN`) plus one
explanatory line, so when the dot genuinely doesn't move, you have direct proof the recompute
still ran rather than having to guess whether the tool is broken.

Both fixes verified in the standalone Studio *and* inside the merged `Design-Studio.html`
(the "two canvases" concern you flagged) — the star-on-top fix and the readout both work
identically in both places, confirmed by the same pixel/readout checks run against both files.

---

## Verification

Ran everything through a real headless Chromium (Playwright 1.62.0,
`C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe`), not brace-counting:

- **`containmentResults()`** against live data matches the hand-verified facts above exactly
  (four breaches, exact overage numbers) in `Design-Studio.html`, and correctly reports nothing
  in standalone `Test-Fit-Studio.html` (no massing to check against).
- **Clamp behavior**, driven with real mouse events (not just function calls): compliant room
  drag/resize clamps exactly at the volume boundary; already-breaching rooms move completely
  freely; a room's clamp correctly disappears the moment a live Massing edit un-fits it, without
  moving the room itself.
- **Trade-space star**: pixel-level `getImageData` check confirms it now renders on top; numeric
  readout confirmed to update on every edit even when position doesn't.
- **Export byte-identity — the project's own standing bar, re-checked, not assumed:**
  `buildInterchange()` (Massing) and `buildExportData()` (Test-Fit) are **byte-identical**
  standalone vs. inside the merged page (`generated` timestamp excluded), confirmed across **two
  independent full passes**. Neither export function was touched by this work.
- **Zero console errors, zero page errors** across every load, drag, slider edit, scheme switch,
  level switch, and layout-mode switch, in both passes.
- Screenshots: `_UI/_playwright/qa-scratch/task1_containment_ground.png` (containment, full UI),
  `task2_trade_star_ontop_before.png` / `_zoom.png` (star fix), `task2_trade_after_edit.png`
  (star having moved after a real edit).

**Left alone, on purpose:** both known-open bugs from the review (`#exportModal`'s inline
`position:fixed` leaking past its pane; the ~41 px clear plan width at 1440×900 side-by-side) —
neither got in the way of this work, so per the brief I didn't touch them.

---

## What to click, what to expect

**Task 1 — containment:**
1. Open `Projects/Nonimuss-Residence/Design-Studio.html`, click **"Plan only"** (top-right layout
   switcher — gives Test-Fit's plan the full window).
2. **Expect immediately, no clicking needed:** `MB`, `GB`, `MU`, `ML` are drawn with a **red
   dashed outline** and a **⚠** on their label, with a small red caption naming exactly how far
   over each is (e.g. `outside House: +1.4m E`). `GR` and `GU` look normal. The right-hand
   "Violations & notes" panel lists the same four, in words, at the top.
3. Try dragging **`GR`** (a compliant room) far to the east — it stops dead at the House volume's
   edge, right where the dashed teal live-cut line is. Try dragging **`GB`** (already flagged) —
   it moves freely, no resistance, because there's nothing honest to clamp it to yet.
4. Switch to **"Side by side"**, select **House** in Massing's volume picker, and shrink its
   **Width (E–W)** slider. **Expect:** more rooms turn red-outlined live, in the same instant,
   with no click on the Test-Fit side at all — and no room moves.

**Task 2 — trade-space:**
1. In Massing's right panel, look at the **Trade-space** chart. **Expect:** a clearly visible
   **orange star**, not hidden behind the grey "B" dot (it may still be sitting very close to or
   on top of B, since B is the starting scheme — but you should be able to see the star shape).
2. Below the chart, a new line reads **"live now: cap-safety NN · D2 NN · D3 (bubble size) NN"**.
3. Select **House**, drag the **East–West** slider a couple of metres. **Expect:** the numbers on
   that readout line change every time, even on tiny nudges. The star itself will often **not**
   move for a small nudge — that's real (see Task 2b above), not broken — but drag far enough to
   pull House noticeably away from Pool/Link and you'll see the star **jump** toward C's corner
   (bottom-right, low wellness-continuity) — the chart catching the exact moment your edit breaks
   the "linked, not detached" reading of the pool sequence.

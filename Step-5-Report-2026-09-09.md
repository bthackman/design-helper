# Step 5 — live plan cut (2026-09-09)

**What this is:** the first live link between Massing Studio and Test-Fit Studio. Drag a volume
in the 3D pane and Test-Fit's plan redraws every Massing volume's footprint at the current
level's real cut elevation — in the same render, no save, no sync button, no file. Read-only:
nothing writes back into `state` or `rooms`. Built per `Fork-Decision-2026-09-09.md` §4 and
`Merge-Stages-2026-09-09.md` Stage 4's checkpoint.

## What was built

**`Massing-Studio.html`** — two new pure functions, inserted right after `setSection()`
(the same neighbourhood as `drawSection()`, which they're explicitly modeled on):

- `drawPlanCut(elevation)` — filters `state` to boxes where `base <= elevation < base+h` and
  returns each one's plan footprint (`id,type,x,z,w,d`). A horizontal sibling of
  `drawSection()`'s vertical slice, returning geometry rather than drawing to a canvas, since
  the consumer is Test-Fit's SVG, not a canvas in this file.
- `levelElevations()` — picks each level's cut elevation from `state` itself: Ground's is the
  `house` box's own `base` (0 in every scheme that exists today); Upper's is the `office` box's
  own `base` (4.5 in scheme B). This reuses the exact Ground/Upper convention already
  established by `syncFromMassing()` in Test-Fit (`base<0.1 = Ground, base>=0.1 = Upper`, keyed
  off the house/office volumes) rather than inventing a new one. A scheme with no office volume
  (A, C) has no real "Upper" — `levelElevations()` correctly collapses Upper to Ground's
  elevation rather than erroring or hardcoding a number. **Verified this edge case directly:**
  calling `setScheme('A')` (no Office box) and reading `levelElevations()` returns
  `{Ground:0, Upper:0}` with zero console/page errors, and `liveMassingCut()` on Upper returns
  the same footprints as Ground — the honest single-storey answer.

One integration point, added to the **end of `refresh()`** (the same function that already ends
with `renderTestFitSync()` — Stage 0's own precedent for a cross-Studio hook at this spot):

```js
if (typeof render === 'function') { try{ render(); }catch(e){} }
```

This is the piece that makes it *live* rather than merely *readable*. `drawPlanCut()` alone is
just a pure function Test-Fit could call — nothing calls Test-Fit's own `render()` when a Massing
slider moves unless something asks it to. `refresh()` already runs after every single slider
edit (`inp.oninput=()=>{b[k]=...;rebuild();refresh();}`), so this is the correct, minimal place to
ask. Guarded, not assumed: `render` only exists as a top-level function once Test-Fit's own
script has also executed in the same document — true only inside the generated
`Design-Studio.html`. In a standalone `Massing-Studio.html`, `typeof render` is `'undefined'`,
so this line is a no-op, confirmed directly (below).

**`Test-Fit-Studio.html`** — `liveMassingCut()`, a thin, defensively-guarded consumer:

```js
function liveMassingCut(){
  if (typeof state === 'undefined' || typeof drawPlanCut !== 'function' || typeof levelElevations !== 'function') return null;
  try{
    const elevs = levelElevations();
    const elevation = elevs[currentLevel];
    if (elevation === undefined) return null;
    return {elevation, footprints: drawPlanCut(elevation)};
  }catch(e){ return null; }
}
```

Wired into `render()`: computed and drawn **right after the pan background and before any
room**, so the cut paints visibly *under* the rooms — the ordering Fork-Decision §4 and
Merge-Stages Stage 3's checkpoint both specify ("the SVG's independently-steered room
rectangles are drawn on top" / "the plan view visibly shows the cut volume outline under the
rooms"). Each volume gets its own dashed rectangle (`#3a7a6b`, distinct from the existing
amber Stage-0/Step-2 ghost color) labeled `"<id> — live massing cut @ <elevation>m"`. The
pre-existing single-envelope `levelVolume()` ghost is left completely intact in the source but is
now only computed/drawn when the live cut isn't available (`liveCut` null or empty) — i.e. it's
what standalone Test-Fit users still see, unchanged, and what the merged page would fall back to
if the live link ever failed. This directly implements Fork-Decision §4's own framing: the live
`drawPlanCut` link "replac[es] the Stage 0 ghost's 'advisory overlay' role with a live one" — it
doesn't delete the ghost's code, it supersedes its *role* when it's actually available.

Ran `node _UI/build-design-studio.js` after each edit; `Design-Studio.html` is regenerated, never
hand-edited.

## Why this cut semantics, and what it validates

A box is "present" at `elevation` when `base <= elevation < base+h` — half-open, not `<=` on both
ends. This is the detail that makes the known consequence fall out correctly rather than by luck:
Pool is one box from `base:0` to `h:4.5`, i.e. its top face sits at *exactly* 4.5 m — the same
elevation Upper's own cut elevation resolves to (Office's `base`). With a half-open test, `4.5 <
0+4.5` is **false**, so Pool is correctly excluded from the Upper cut, while Office
(`base:4.5 <= 4.5 < 4.5+3`) is correctly included.

**Verified live, driving the actual browser, not just read from code:** switched Test-Fit to
Upper level in the merged page and read the rendered cut. Result: Office and Link both get a live
cut outline (Link legitimately spans both storeys — `base:0, h:7.5` covers `[0,7.5)`, which
contains both 0 and 4.5 — matching Fork-Decision §1 Finding 3's own note that Link "genuinely
spans both storeys," not asserted). **Nothing is drawn over the Pool/VOID footprint.** Test-Fit's
own hand-authored `VOID` room (`illustrative:true`, "open-to-below, over pool") independently
asserts the same thing by hand. Screenshot:
`_UI/_playwright/qa-scratch/step5_planonly_upper.png` — this is the validation Fork-Decision §4
predicted, and it fell out of the real elevation math, not a special case written to match VOID.

## Verification — driven through the real browser, per Ben's own bar

Tooling: `C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe`, Playwright 1.62.0,
headless Chromium. Scripts are throwaway, in the session scratchpad; all screenshots are under
`_UI/_playwright/qa-scratch/` with a `step5_` prefix.

**1. The core bar — drag a slider, the plan updates in the same render, read from the DOM.**
Selected House in Massing's volume picker (`#ms-pane #volPick`, value `"1"`), located its
East–West slider (`#ms-pane #sliders .slider:nth(0) input[type=range]`, the real `oninput`-driven
range control — not a UI shortcut), set it via `.fill()` + a dispatched `input` event (the same
event the real drag handler listens for), and read the plan's live-cut `<rect>` elements
(`stroke=#3a7a6b`) directly from the DOM before and after — no manual "sync" click anywhere in
the sequence.

| | House cut rect (`x,y,w,h`), read from the SVG | Underlying `state` (Massing) |
|---|---|---|
| Before (slider = 18) | `{x:18, y:5, w:11.6, h:9.3}` | `x:18` |
| After (slider → 26) | `{x:26, y:5, w:11.6, h:9.3}` | `x:26` |

Room `GR`'s own position (`rooms.GR = {x:18, y:9}`) was read before and after the same
drag — **unchanged both times**, confirming the link is genuinely read-only in the room→state
direction (nothing wrote into `rooms`).

**2. Visual confirmation, not just numbers.** Screenshots at
`_UI/_playwright/qa-scratch/step5_zoom_before.png` and `step5_zoom_after.png` (same fixed SVG
viewBox both times, `Plan only` layout, House slider dragged 18→26): the dashed
`"House — live massing cut @ 0.0m"` outline and label visibly move from left-of-GR/MU to
right-of-GR, disappearing under GR/MU's opaque fill where the new position overlaps them —
exactly the geometry the DOM read reports. Also
`_UI/_playwright/qa-scratch/step5_sidebyside_ground_before.png` /
`step5_sidebyside_ground_after_drag.png` show both panes at once: the East–West slider readout
changes 18.0→30.0, the 3D isometric view visibly shows the House volume shifted east, and
Massing's own D1/D2 driver scores and trade-space star move live in the same interaction — proof
the underlying edit is a real, ordinary Massing steer, not a special test-only path.

**3. Standalone Studios — unaffected, checked directly, not assumed.**
- `typeof render` inside a **standalone** `Massing-Studio.html` → `'undefined'` (confirmed live)
  — the new call at the end of `refresh()` is provably a no-op there.
- `liveMassingCut()` inside a **standalone** `Test-Fit-Studio.html` → `null` (confirmed live),
  and the pre-existing "Implicit envelope… no massing synced" ghost still renders exactly as it
  did before Step 5 — same label, same styling, read directly from the DOM.
- **Export byte-identity, re-checked after the Step 5 edits** (not assumed to still hold from
  the Steps 1–4 review): `buildInterchange()` in standalone Massing vs. the merged page
  (`generated` timestamp excluded) — identical. `buildExportData()` in standalone Test-Fit vs.
  the merged page — identical. Both confirmed across two independent full runs.
- Dragging a slider in **standalone** Massing (not merged) still updates `state` correctly with
  zero console/page errors — the new guard doesn't change standalone behavior at all.

**4. Console/page errors — zero, throughout.** Across every pass below: standalone Massing load
+ drag, standalone Test-Fit load, merged-page load, merged-page drag-and-redraw, level switch to
Upper, and the scheme-A single-storey edge case (`setScheme('A')`, no Office volume) — zero
console errors, zero uncaught page errors, every time.

**5. Stability — re-run twice, not a one-off.** Ran the full sequence (standalone exports →
merged load → drag House's slider → re-read the cut → switch to Upper → re-read) as two
completely independent full page-launch passes. Both passes produced identical results
(`house_x_slider_before: "18"`, `after: "26"`, cut rect `x` moving from `18` to `26` both times,
Office-only on Upper both times, zero errors both times) — not a one-off flake.

## Constraints honored, checked one by one

- **Read-only, both directions.** `rooms.GR` unchanged after the drag (checked above).
  `drawPlanCut()`/`levelElevations()` never assign into `state`; `liveMassingCut()` never assigns
  into `rooms`.
- **Pure functions lifted, not rewritten.** `drawSection()` is untouched; `drawPlanCut()` is new
  code following its pattern, not a rewrite of it. `buildInterchange()`/`buildExportData()`
  untouched — confirmed byte-identical (above).
- **Standalone Studios unaffected, provably.** Both guards (`typeof render`, `typeof state`)
  checked live, both resolve to the "not present" branch outside the merged page, both leave the
  pre-existing behavior (implicit ghost, ordinary slider edits) intact.
- **Guarded, not assumed.** Neither file references the other's globals without a `typeof` check
  first; `liveMassingCut()` additionally wraps its body in `try/catch` so a future failure on
  either side degrades to the old ghost rather than breaking the plan.
- **Cut elevation from real data.** `levelElevations()` reads `state`'s own house/office `base`
  values; nothing is hardcoded to `4.5`. Verified this survives a scheme with no Office volume
  (Upper collapses to Ground's elevation, no error).

## What I could not verify

I did not test dragging a room in the SVG plan to confirm it's *invisible* to the Massing side
(Stage 5's mirror direction isn't built yet — this is Stage 4-equivalent, one direction only, as
scoped) — though `liveMassingCut()` never reads `rooms` at all, so there is no code path by which
it could be affected either way. I did not test the live link against Scheme C specifically
(only A and B) — C has the same house/office/pool/link shape as B, so I have no reason to expect
different behavior, but it wasn't independently driven through the browser. I did not test
rapid/repeated dragging (e.g. holding a slider and moving it continuously) — only discrete
`fill()`-then-`input`-event steps, which exercise the same `oninput` handler a real drag does,
but not the sheer event frequency of a live mouse drag.

## For Ben to confirm in person

1. Open `Projects/Nonimuss-Residence/Design-Studio.html` (double-click works — still no build
   step, still `file://`-openable; Test-Fit's own half loads with no CDN, Massing's half still
   pulls Three.js/Chart.js from `cdnjs.cloudflare.com` as it already did before today).
2. **Click "Plan only" in the top-right Layout switcher first.** At 1440×900 side-by-side both
   panes are cramped (confirmed and measured in `Review-Steps-1-4-2026-09-09.md` §5) — "Plan
   only" hides the 3D pane and gives Test-Fit's plan the full window, which is the clearest way
   to see the effect. ("Side by side" also works and lets you watch both panes at once, as in
   `step5_sidebyside_ground_before.png`/`_after_drag.png` — just expect it to feel tight.)
3. Switch back to "Side by side" (or keep two browser windows), select **House** in Massing's
   "Steer a volume" dropdown (top-left panel), and drag the **East–West** slider.
4. **Expect:** in Test-Fit's plan (Ground level), a dashed teal rectangle labeled
   `House — live massing cut @ 0.0m` — it should visibly slide left/right as you drag, in real
   time, with no button to click and no "synced" status text anywhere. The Great Room / Main Bed
   / Guest rooms do **not** move — only the dashed outline does.
5. Click **Upper** (top bar, "Level"). **Expect:** the dashed outline now reads
   `Office — live massing cut @ 4.5m` around the `OF` room and `Link — live massing cut @ 4.5m`
   around `LKU` — and **no dashed outline at all** over the big `VOID` room. That empty space is
   the tool independently confirming, from the real massing geometry, exactly what `VOID`'s own
   label already says by hand ("open-to-below, over pool").
6. Standalone sanity check, if you want it: open `Massing-Studio.html` and
   `Test-Fit-Studio.html` directly (not through `Design-Studio.html`) — both should look and
   behave exactly as they did yesterday. Nothing about Step 5 should be visible outside the
   merged page.

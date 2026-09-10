# Revit push workflow — quick reference

One-page checklist for `_Export-Receivers/Revit/`. Full detail lives in `00_MassBox-family-recipe.md` (the family build) and `README.md` (the engine); this is the condensed version to work from directly.

**Status: paused 2026-08-22, not abandoned.** Autodesk's own API path is read-only for now, so there's no near-term reason to push past this MVP — everything below still stands as the plan to resume from. Next unblocked step is #1 below (building `MassBox.rfa`) — not yet done as of 2026-09-08.

## Why a script, not a native file
`.rvt` and `.rfa` are both closed, version-locked Revit binaries — no supported way to generate either from outside Revit. So the architecture is a receiver that runs *inside* Revit via Dynamo (ships with Revit, no admin install needed), not a workaround.

## Part 1 — One-time setup: build `MassBox.rfa` (~5 min, do this first)

1. **New family** → template **`Metric Mass.rft`** (File → New → Conceptual Mass → Metric Mass.rft). Family category must be **Mass**.
2. On the **Ref. Level** plan, draw a rectangle **centred on the origin**.
3. **Add two plan parameters**, both centred/symmetric about the origin:
   - Width in X → instance parameter **`Length`** (type: Length, group: Dimensions).
   - Depth in Y → instance parameter **`Width`** (type: Length, group: Dimensions).
4. Select the rectangle → **Create Form → Solid Form** (extrudes a box).
5. Add the vertical dimension as instance parameter **`Height`** (type: Length, group: Dimensions), measured up from Ref. Level.
6. *(Recommended)* Add instance parameter **`Glazing_%`** (type: Number, group: Data) — carries the Studio's glazing % for tagging/scheduling. Skip and the receiver just won't set it.
7. Set nominal defaults (e.g. Length 5000 / Width 4000 / Height 3000 mm) in Family Types.
8. **Flex-test:** change Length/Width/Height in Family Types and confirm the box resizes, stays centred on the origin in plan, and grows upward from Ref. Level. If it does, the receiver's placement math will land every volume correctly.
9. **Save as `MassBox.rfa`** into this folder (`_Export-Receivers/Revit/`).

One family covers everything — pool, house, office, link, gym, terrace are all just this same box at different sizes. Type is carried in the instance's *Comments*, volume id in *Mark*.

## Part 2 — Every time you push a massing scheme

1. In Massing Studio: **⤓ Export JSON (Rhino/Revit)** → saves `nonimuss-massing-<scheme>.json`.
2. In Revit: **Insert → Load Family** → `MassBox.rfa` (only needed once per Revit session/project).
3. **Manage → Dynamo → Open** → `Massing-Import.dyn` (in this folder).
4. Top **String** node → paste the full path to the JSON you just exported.
5. Confirm the **family name** String reads `MassBox`.
6. Flip the **run** Boolean to **True** → **Run**. The Python node logs the levels + masses it created.
7. Add **View → Schedules → Mass Floors** (fields: Level, Floor Area) for a native GFA schedule. Cross-check the total against `metrics.dwelling` baked into the JSON (Option B ≈ 113 m² vs. the 120 m² cap).

### Manual fallback, if the `.dyn` graph won't open
New Dynamo graph → **Python Script** node → paste all of `massing_to_revit.py` → right-click **Add Input** twice (3 ports total) → wire: port 0 = String (json path), port 1 = String `MassBox`, port 2 = Boolean (set True) → Run.

## What the engine actually does
- Reads `volumes[]` and `site.storeys[]` from the JSON.
- Creates a **Level** per storey elevation (reuses existing ones at the same height).
- Places one `MassBox` instance per volume at its footprint centre, driving Length=w/Width=d/Height=h; writes `Glazing_%`, `Mark`=volume id, `Comments`=type.
- Adds **Mass Floors** at every level a mass passes through.
- Axis map: interchange `x`=East→Revit +X, `z`=South→Revit −Y, `y`=up→+Z. Boxes are axis-aligned — rotation is baked into width/depth, not applied as a real rotation.
- Units converted metres→feet by hand; all writes happen in one transaction gated by the `run` Boolean, so nothing writes until you explicitly flip it.

## Known limits (MVP, by design — not bugs)
Schematic only: no walls/floors/roofs-by-face, no real glazing geometry (glazing is metadata only, not modeled glass), no curved or rotated masses. `Massing-Import.dyn` was built to Dynamo 2.19 (Revit 2024) and confirmed to also open in Revit 2025's Dynamo 3.

## If you want to go further later
Named as later tiers, none built: **pyRevit/RevitPythonShell** (full API, genuine in-place masses, auto-levels, needs install) or **Rhino.Inside.Revit** (reuse the Rhino track's geometry, bake straight in — heaviest install). See `Massing-Export-Roadmap.md` at the tool root for the full tier breakdown.

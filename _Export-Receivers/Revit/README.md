# Revit receiver — Massing Studio → conceptual masses

Turns a `massing.json` (exported from the Massing Studio's **⤓ Export JSON** button) into editable **conceptual mass family instances** on levels, then **Mass Floors** for a native GFA schedule. Implements Track A (V1) of `../../Massing-Export-Roadmap.md`.

**Why a script and not a `.rvt`/`.rfa`:** both are closed Revit binaries — no supported way to write them from outside Revit. The correct architecture is a receiver that runs *inside* Revit. Dynamo is the vehicle because it ships with Revit (no admin install on the DIALOG endpoint), and the Python engine is fully version-controlled here.

## Files
- `00_MassBox-family-recipe.md` — build `MassBox.rfa` once (~5 min). **Do this first.**
- `massing_to_revit.py` — the engine. Runs in a Dynamo Python Script node.
- `MassBox.rfa` — *you create this from the recipe and drop it here.*

## One-time setup
1. Build **`MassBox.rfa`** from the recipe; save it in this folder.
2. In Revit, **load the family** (Insert → Load Family → `MassBox.rfa`).

## Each time you push a massing — with the shipped graph
1. In the Studio, click **⤓ Export JSON (Rhino/Revit)** → saves `nonimuss-massing-<scheme>.json`.
2. In Revit: **Manage → Dynamo → Open** → `Massing-Import.dyn` (in this folder).
3. Click the top **String** node (*massing.json path*) and paste the full path to the file you just exported.
4. Confirm the **family name** String reads `MassBox`.
5. Flip the **run** Boolean to **True**, then **Run**. The Python node's output shows a log of the levels + masses created.
6. Add a schedule: **View → Schedules → Mass Floors**, fields *Level* + *Floor Area* → GFA, natively. Cross-check the total against the `metrics.dwelling` baked into the json (Option B ≈ 113 m² vs the 120 m² cap).

`Massing-Import.dyn` was built to the **Dynamo 2.19 schema (Revit 2024)** with the Python node set to **CPython3**; Revit 2025's Dynamo 3 opens it too. The `.py` file is the source of truth — the graph embeds a copy of it; if you edit the engine, re-paste into the node (or ask me to regenerate the graph).

### Manual fallback (if the graph won't open in your Dynamo)
New graph → add a **Python Script** node → paste all of `massing_to_revit.py` → right-click **Add Input** twice (3 ports total) → wire a **String** (json path) → port 0, **String** `MassBox` → port 1, **Boolean** → port 2 → set True → Run.

## What the engine does
- Reads `volumes[]` and `site.storeys[]` from the json.
- Creates a **Level** per storey elevation (reuses existing ones at the same height).
- Places one **MassBox** instance per volume at the footprint centre, driving `Length`=w (East/X), `Width`=d (North/Y), `Height`=h (up/Z); writes `Glazing_%`, `Mark`=volume id, `Comments`=type.
- Adds **Mass Floors** at every level a mass passes through.
- **Axis map:** interchange `x`=East→Revit +X, `z`=South→Revit −Y, `y`=up→+Z. Boxes are axis-aligned (rotation is baked into w/d), so no rotation is applied.
- **Units:** metres→feet by hand (`/0.3048`) to stay version-agnostic.
- **Safety:** all model writes are in one transaction; a Boolean `run` gate prevents accidental writes; mass-floor failures are logged, not fatal, so the masses still land.

## Limits (MVP, by design)
Schematic only — no wall/floor/roof-by-face, no real glazing geometry (glazing is metadata), no curved/rotated masses. Those are later tiers in the roadmap.

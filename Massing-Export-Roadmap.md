# Massing Export Roadmap — Studio → Rhino / Revit

Status: **planning / agreed direction** (2026-07-26). Author: Ben Hackman + Claude.
Scope: an optional export widget on the Massing Studio that pushes the generated massing into Rhino and Revit, Revit prioritized to **conceptual mass families**.

This is the text-of-record for the export feature. It sits beside `Tool-Strategy-Map.md`; when built, fold the shipped pieces into `00_Tool-Concept-Spec.md`'s backlog like the other phases.

---

## The one architectural decision

Do **not** wire the Studio directly to either app. The Studio emits **one neutral interchange file** — `massing.json` — and each target app gets a small, dumb "receiver" that reads it. Define the schema once; every new target after that is cheap.

**Why this is the spine of the whole feature:** the Studio's volume model is already regular and export-ready. Every volume is one record:

```
{ id, type, x, z, w, d, h, base, glaz, rot90? }   // metres; type ∈ pool|house|office|link|gym|terr
```

plane-positioned through a single `toWorld` origin transform, stacking via `base`, glazing carried as a percentage. Axis-aligned boxes (plus a rotate-90 case). Site metadata (lot polygon, north angle, site origin, storey heights) travels in the same file's header.

**Build step 0 (prerequisite for everything below):** upgrade the Studio's existing text-export dialog to also emit this structured `massing.json`. Nothing downstream can start until the schema is frozen.

Proposed `massing.json` shape:

```json
{
  "project": "Nonimuss-Residence",
  "units": "m",
  "site": {
    "origin": [x, z],
    "northDeg": 0,
    "lotPolygon": [[x,z], ...],
    "storeys": [{ "name": "L1", "elev": 0 }, { "name": "L2", "elev": 3.2 }]
  },
  "volumes": [
    { "id": "house", "type": "house", "x": 12.0, "z": 8.0,
      "w": 10.0, "d": 8.0, "h": 3.2, "base": 0.0, "glaz": 30, "rot90": false }
  ]
}
```

---

## Track A — Revit (MVP · agreed first target)

### Why exact `.rvt` is off the table
`.rvt` is a closed, version-locked, proprietary binary. There is **no supported way to write a valid `.rvt` from outside Revit** — no open library equivalent to Rhino's. Anything that claims to is reverse-engineered and breaks per release. So for Revit a graph/script isn't the shortcut — it's the correct architecture.

### Agreed approach: V1 — Dynamo graph + parametric mass family (Dynamo-only, no admin install)
Chosen because Dynamo **ships with Revit** (no install on the locked-down DIALOG endpoint), a `.dyn` is itself JSON the tool can generate, and it's user-editable.

Pieces to build:

1. **`MassBox.rfa`** — one conceptual mass family, a box driven by instance parameters `Length` / `Width` / `Height`, plus a `Glazing_%` and `MassType` text param for scheduling/tagging. One reusable family, not one per volume.
2. **`Massing-Import.dyn`** — a Dynamo graph that:
   - reads `massing.json` (`File.FromPath` → `File.ReadText` → `JSON` deserialize),
   - creates/verifies **Levels** from `site.storeys`,
   - for each volume, places a `MassBox` instance at `x / z / base`, sets `L/W/H`, assigns the level, applies the north rotation + origin, and writes `Glazing_%` / `MassType`,
   - applies **Mass Floors** at each level.
3. **Mass Floors → GFA schedule.** This closes the loop: the Studio's cap meter (dwelling GFA vs. hard cap) is reproduced **natively** inside Revit as a schedulable Gross Floor Area. Same number, now living in the model.

Deliberately **out of MVP scope:** wall/floor/roof-by-face, real glazing geometry (glazing stays metadata), curved/non-orthogonal masses.

### Power tiers (later, only if endpoint allows installs)
- **V2 — pyRevit / RevitPythonShell.** Full API: genuine in-place or loadable masses, project base point = site origin, auto-levels. More capable, needs install.
- **V3 — Rhino.Inside.Revit.** Reuse Track B geometry and bake straight into Revit masses — one geometry pipeline for both apps. Heaviest install; "someday."

---

## Track A status — paused (2026-08-22)
Autodesk's own MCP/API integration path is read-only for now (per Autodesk), so there's no near-term
case for pushing this further than the Dynamo-graph MVP already built. **Nothing here is being
deleted or rolled back** — `massing_to_revit.py`, `Massing-Import.dyn`, and the `.rfa` recipe stay as
they are, usable whenever `MassBox.rfa` gets built and the graph gets run. Just not actively
continued right now; Track C (below) is where new massing-integration effort is going instead.

## Track B — Rhino (second target)

Rhino is the easy case: `.3dm` is an **open, documented** format with an official headless library (`rhino3dm` / openNURBS), so the exact native file can be produced without Rhino running.

- **R1 — Headless `.3dm` (flagship).** A script reads `massing.json` and writes a real `.3dm`: each box → extrusion/Brep, **layered by type**, glazing % and area attached as attributes, lot polygon + north on their own layers. The tool produces the file; you just open it.
- **R2 — Paste-able RhinoPython (zero-friction fallback).** A `.py` run via `_-RunPythonScript` that builds the same boxes with `rs.AddBox`. No dependencies; good for a quick look.
- **R3 — Grasshopper definition (optional).** A `.gh` that reads the JSON, for live parametric link-back. Not needed for parity with Revit.

---

## Track C — Blender (later-stage design integration, agreed 2026-08-22)
Not a modelling target competing with Rhino/Revit — this is where the massing goes **after** it's
been steered in the Studio, for the interactive design-push stage (real architectural moves, sun
studies, renders), the way blender-mcp was already used on the Nonimuss sun-path study.

**The same headless-vs-interactive split as everything else here:** placing boxes from JSON is
mechanical, so it's a `blender --background --python` script, not an MCP round-trip per box.
Interactive `blender-mcp` is reserved for the part that actually needs a human's eye in the loop.

- **Template — `_Export-Receivers/Blender/_Massing-Template.blend`, built once** by
  `build_massing_template.py`: meters units, one collection per volume type + `Site`, a generic
  ground plane, Nishita procedural sky (no HDRI asset to manage), a Sun lamp, Freestyle enabled, 3
  camera presets, Cycles render settings — plus two material tiers: **Tier A** (one flat color per
  volume type, matched to the Studio's own `COLOR` map, for visual continuity) and **Tier B** (10
  fixed advanced materials — brick, wood siding, standing-seam metal roof, stucco, board-formed
  concrete, curtain-wall glazing, stone veneer, asphalt shingle, a generic metal reused for
  mullions/flashing/parapet caps/exposed steel, hardscape paving — pre-built so the later MCP
  session can assign them in one line instead of rebuilding shader graphs each time).
- **Import engine — `import_massing.py`**: reads a project's `massing.json`, opens the template,
  places the boxes (axis-remapped from the interchange convention), cuts in the property line as a
  real ground-surface edge loop marked for Freestyle, places a north arrow, points the sun at the
  real solar angle for a given lat/long/date (hand-rolled solar-position math, not Blender's Sun
  Position add-on — see the receiver's own README for why), reframes the cameras, saves a project
  `.blend`.
- **Schema gap:** `massing.json` has `site.northDeg` but no lat/long; worked around for now with an
  `--latlong` CLI flag on the import script. Closing it properly means adding `site.latLong` to
  `buildInterchange()` in the Studio.
- **Status: ✅ built and tested 2026-08-22.** Both scripts run headless end-to-end against a
  synthetic test fixture (verified object counts, materials, collections, freestyle marks, sun/sky
  sync, camera reframing, and a low-sample render — see `_Export-Receivers/Blender/README.md`).
- **Handoff:** once the `.blend` is built, open it in Blender's GUI, connect the BlenderMCP N-panel,
  and drive the design-push stage through an interactive Claude session from there.

## Direct answer: Grasshopper/Dynamo vs. exact file
Split by app. **Rhino:** make the exact native `.3dm` — the format is open, so it's clean and worth doing. **Revit:** don't chase an exact file; Dynamo is the right architecture, not a compromise — mass families + mass floors natively, no admin install, user-editable.

---

## Gotchas to design around
- **Axes:** Studio is Y-up with Z as the N–S plan axis; Revit/Rhino Z is up. The receiver remaps and applies north rotation + `toWorld` origin.
- **Units:** Revit's API is internally in feet (Dynamo converts, but note it). Interchange stays metric.
- **Glazing is metadata,** not modelled glass — carried as a parameter/attribute. Schematic massing only.
- **rot90:** carry the flag through so oriented boxes land correctly.
- **Coordinates:** decide project base point / survey point convention up front so Rhino and Revit land in the same place relative to the lot.

---

## Build path
1. **Step 0 — freeze the schema. ✅ DONE 2026-07-26.** Studio has an **⤓ Export JSON** button (added beside the existing share-edits button, not replacing it) emitting `massing-interchange/v1`. Verified on Option B.
2. **MVP (agreed) — Revit. ◐ IN PROGRESS 2026-07-26.** Engine built: `_Export-Receivers/Revit/massing_to_revit.py` (Dynamo Python, IronPython2+CPython3 safe) + `00_MassBox-family-recipe.md` + `README.md`. Remaining to close: Ben builds `MassBox.rfa` from the recipe and runs it in Revit on Option B; then optionally a version-matched `Massing-Import.dyn`.
3. **Track B — Rhino:** headless `.3dm` generator, then the paste-able RhinoPython fallback.
4. **Power tiers:** pyRevit / Rhino.Inside if/when installs are allowed.
5. **Track C — Blender. ✅ DONE 2026-08-22.** `_Export-Receivers/Blender/` — template builder + import engine, tested end-to-end. Later-stage design-integration tool, positioned after the Studio's own initial massing.

## Decisions logged (2026-07-26)
- Neutral `massing.json` interchange is the single source of truth; apps get thin receivers. **Agreed.**
- MVP target: **Revit first.** **Agreed.**
- Revit delivery: **V1 — Dynamo graph + parametric `MassBox` family, Dynamo-only (no admin install).** **Agreed.**
- Exact `.rvt` generation: **rejected** (closed format, version-fragile).
- Rhino: exact headless `.3dm` is the flagship (format is open).
- **`.rfa` cannot be generated externally either** (also a closed binary) → `MassBox.rfa` is built once inside Revit from a recipe, then reused. **Agreed 2026-07-26.**
- **`Massing-Import.dyn` shipped 2026-07-26**, built to the Dynamo 2.19 schema (Revit 2024, opens in 2025's Dynamo 3), Python node = CPython3. Targeted 2025-if-available/else-2024 per Ben. JSON + port wiring validated programmatically; manual 4-click fallback documented in the receiver README in case it won't open.
- **Track A (Revit) paused 2026-08-22**: Autodesk's own MCP/API path is read-only for now — no near-term reason to push past the Dynamo MVP. Existing work stays as-is, not deleted.
- **Track C (Blender) added 2026-08-22**, positioned as the later-stage design-integration tool (post-initial-massing), not a Rhino/Revit competitor. Headless template + import script, same architecture as Rhino/Revit (neutral JSON in, thin receiver), MCP reserved for the interactive push after import. Built and tested same day — see `_Export-Receivers/Blender/README.md`.

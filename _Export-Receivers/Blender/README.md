# Blender receiver — Massing Studio → template + interactive design push

Turns a `massing.json` (exported from the Massing Studio's **⤓ Export JSON** button) into a
real Blender scene, cheaply, then hands off to an interactive `blender-mcp` session for the
later-stage design push (real architectural moves, sun studies, renders). Implements Track C of
`../../Massing-Export-Roadmap.md`.

**Why two headless scripts and not blender-mcp from the start:** placing boxes from a JSON file is
mechanical and deterministic — it doesn't need a human-in-the-loop model driving it step by step.
Each `execute_blender_code`/screenshot round-trip through an MCP session costs conversation tokens;
a headless `blender --background --python` run costs one write + one execution, regardless of how
many boxes there are. Save the interactive session's tokens for the part that actually needs your
eye: pushing the schematic massing into real form, running sun studies, iterating renders.

## Files
- `massing_lib.py` — shared helpers (materials, sun-position math, box/mesh builders). Imported by
  both scripts below; not run directly.
- `build_massing_template.py` — builds `_Massing-Template.blend` **once**. Re-run only if you want
  to rebuild the template from scratch (e.g. after editing the material list).
- `_Massing-Template.blend` — the reusable template: meters units, one collection per volume type
  + `Site`, a generic ground plane, Nishita procedural sky, a Sun lamp, Tier A + Tier B materials,
  Freestyle enabled, 3 camera presets, Cycles render settings. *You create this by running the
  script above once; it's committed here so you don't have to rebuild it per project.*
- `import_massing.py` — the per-project engine: reads a project's `massing.json`, opens the
  template, builds the boxes, cuts in the property line, sets the sun, reframes the cameras, saves
  a project `.blend`.

## Each time you push a massing
1. In the Studio, click **⤓ Export JSON (Rhino/Revit)** → downloads `nonimuss-massing-<scheme>.json`
   (or your project's equivalent) to your Downloads folder.
2. Run the import script headless:
   ```
   "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" --background --python import_massing.py -- ^
     --json "C:\path\to\project-massing.json" ^
     --out "C:\path\to\Projects\<Project>\3_Massing\<Project>-Massing.blend" ^
     --latlong "50.99,-114.0" --date "2026-06-21"
   ```
   (`--latlong`/`--date`/`--hour-utc` are all optional — see the schema gap below. Everything after
   the lone `--` is this script's own argv; Blender ignores it and passes it through as-is.)
3. Open the resulting `.blend` in Blender's GUI, connect the BlenderMCP N-panel (see the project's
   `blender-mcp/addon.py` setup), and drive the later-stage work — pushing volumes into real
   architectural moves, sun-position studies, renders — through an interactive Claude session.

## The `site.latLong` schema gap
`massing.json` (as the Studio actually exports it — see `buildInterchange()` in
`Massing-Studio.html`) has `site.northDeg` but **no latitude/longitude**. The sun-position math
needs real lat/long, so for now pass it on the command line with `--latlong "lat,lon"`. If you skip
it, the sun is left at the template's generic default (45° elevation, due-south) and the script
prints a note saying so. **To close this properly**, add a `site.latLong` field to
`buildInterchange()` in the Studio (sourced from wherever `2_Site/` geocoded the site) — then this
flag becomes optional metadata pulled straight from the file instead of typed by hand each time.

## What the engine does
- **Boxes:** one mesh per `volumes[]` record, axis-remapped from the interchange convention
  (`x`=East, `z`=South, `y`=Up, "North is `-z`", `x,z` = one corner of the box in plan) to Blender
  (`+X`=East unchanged, `+Y`=North = `-z`). Assigned to the collection matching its `type`, with the
  matching Tier A material (see below). `clerestory: true` is noted but not modelled — glazing/roof
  detail stays metadata-only at this stage, same treatment as the Revit receiver's glazing.
- **Property line on the ground surface:** rather than a floating curve above the ground plane
  (which z-fights at grazing angles) or a literal knife-project/boolean cut into the single big
  `GroundPlane` mesh (coplanar booleans are notoriously unstable, and headless mode has no 3D
  viewport for the `knife_project` operator to run against), the engine builds a **separate flat
  ngon** matching `site.lotPolygon` exactly, offset 1cm above the ground plane, sharing the ground
  material, with all its boundary edges marked `use_freestyle_mark = True`. Functionally and
  visually this reads as the property line living on the ground surface without the instability of
  either alternative.
- **North arrow:** an empty (`SINGLE_ARROW`) placed at the lot's centroid, rotated by `site.northDeg`
  off the `+Y` baseline. **Untested assumption:** every sample scheme so far has `northDeg == 0`, so
  the rotation sign (clockwise-from-north, matching the sun-azimuth convention below) is unverified
  against a real project. Check it against a real non-zero `northDeg` before trusting it.
- **Sun + sky:** a hand-rolled solar-position function (Meeus low-precision algorithm, ~0.01°
  accuracy) drives both the Sun lamp's rotation and the World's Nishita sky texture's
  `sun_elevation`/`sun_rotation`, kept in sync. **Why not Blender's built-in Sun Position add-on:**
  Blender 4.2+ moved most previously-bundled add-ons (including Sun Position) to the online
  Extensions platform; this is an offline/locked-down install with no Extensions access, and
  `addon_utils.modules()` confirms it isn't present. The hand-rolled function was validated against
  Nonimuss-Residence's own reference altitudes baked into `Massing-Studio.html` (lat 50.99°N: winter
  solstice noon 15.6°, summer 62.4°) — it reproduces 15.57°/62.44°, both within 0.1°, matching the
  accuracy already achieved in the July 2026 blender-mcp session on this same project. The
  **sun-elevation/shadow direction is verified correct** (the Sun object's rotation formula was
  numerically checked against the expected sun-direction vector for multiple non-degenerate
  elevation/azimuth pairs); the Nishita sky's `sun_rotation` is set to the same azimuth value as an
  approximation and hasn't been separately verified against Blender's own convention for that
  parameter — if the sky's gradient looks rotated relative to the shadows, that's the one place to
  check first.
- **Cameras:** the template ships 3 generic placeholders (street elevation, 3/4 aerial, eye-level);
  the import script reframes all 3 to the actual bounding box of the imported volumes.
- **Render settings:** Cycles, 1920×1080, Freestyle on, output path convention `//renders/` relative
  to wherever you save the project `.blend` (matches the existing `3_Massing/renders/` pattern
  already in use on Nonimuss for the sun-path MP4).

## Tier A vs. Tier B materials
- **Tier A** — one flat/matte material per volume `type` (`TierA_house`, `TierA_pool`, …), colors
  matched exactly to the Studio's own `COLOR` map (`Massing-Studio.html`), applied automatically on
  import. This is the continuity layer: a Blender screenshot should read in the same color language
  as the web tool.
- **Tier B** — 10 fixed, more advanced materials, pre-built in the template but deliberately left
  **unassigned** to anything, so they're ready for a one-line lookup during the interactive
  blender-mcp stage instead of rebuilding a shader node graph from scratch each session:
  `Brick`, `WoodSiding`, `MetalRoof_StandingSeam`, `Stucco`, `ConcreteBoardFormed`,
  `Glazing_CurtainWall`, `StoneVeneer`, `RoofShingle_Asphalt`, `Metal_Generic`, `Paving_Hardscape`.
  `Metal_Generic` is intentionally one material, not several — reused for curtain-wall mullions,
  flashing, parapet cap flashing, and exposed structural steel alike.
- Materials with zero users get silently dropped by Blender on save unless `use_fake_user = True`
  — every material this receiver creates sets that flag, otherwise the whole Tier B library would
  vanish from the template the first time it's saved (this happened once during testing; see git-free
  note below since this repo isn't under version control — no commit history to point to, just this
  README as the record).

## Limits (by design, matches the Revit receiver's posture)
Schematic only. No wall/floor/roof-by-face, no real glazing geometry beyond the Tier B curtain-wall
material, no curved/rotated masses (rotation is already baked into `w`/`d` upstream, same as Revit).
Neighbouring context massing and storey/floor reference planes were considered and deliberately left
out — no data source for the former yet, and storeys are already implicit in each volume's `base`.

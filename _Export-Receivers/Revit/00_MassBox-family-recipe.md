# MassBox.rfa — build it once (≈5 min)

A `.rfa` is a closed Revit binary; it can't be generated from outside Revit (same reason as `.rvt`). So build this tiny parametric mass family **once**, keep it in this folder, and the Dynamo receiver reuses it forever.

The receiver (`massing_to_revit.py`) places one instance per volume and drives three instance parameters — **Length** (East/X extent), **Width** (North/Y extent), **Height** (up/Z) — plus an optional **Glazing_%**. Build the family so its **origin sits at the bottom-centre of the box** and those three parameters control its size.

## Steps

1. **New family** → template **`Metric Mass.rft`** (Conceptual Mass). *File → New → Conceptual Mass → Metric Mass.rft.* This makes the family category **Mass** — required for Mass Floors.

2. On the **Ref. Level** plan, draw a **rectangle centred on the origin** (the intersection of the two reference planes at 0,0). Don't worry about exact size yet.

3. **Add the two plan parameters:**
   - Select the rectangle's left+right edges → add an aligned dimension across the full width in **X** → label it a new **instance** parameter **`Length`** (Type of parameter: *Length*, Group under *Dimensions*). Constrain it symmetric about the origin (add an EQ / centre constraint so the box stays centred on X).
   - Same across the depth in **Y** → new **instance** parameter **`Width`**, centred symmetric about the origin in Y.
   *(Symmetry matters: the receiver places the instance at the footprint centre, so the box must grow equally both ways.)*

4. **Create the solid:** select the rectangle → **Create Form → Solid Form**. You get a box extruded up.

5. **Add the height parameter:** select the top face (or the vertical extrusion dimension) → add/relabel the vertical dimension as a new **instance** parameter **`Height`** (Type of parameter: *Length*, group *Dimensions*), measured **up from the Ref. Level** (origin at the base).

6. **Add the metadata parameter (optional but recommended):** Family Types dialog → New Parameter → **`Glazing_%`**, instance, Type of parameter *Number*, group *Data*. (Carries the Studio's glazing % onto each mass for tagging/scheduling. If you skip it the receiver just won't set it.)

7. **Set nominal defaults** in Family Types (e.g. Length 5000, Width 4000, Height 3000 mm) so it flexes cleanly, then **Save as `MassBox.rfa`** into this folder.

## Sanity check before you rely on it
Flex it in Family Types: change Length/Width/Height and confirm the box resizes, stays centred on the origin in plan, and grows upward from the Ref. Level. If it does, the receiver's placement math will land every volume correctly.

## Notes
- **Units:** model the family in mm/m; the receiver converts metres→feet internally, so parameter values it sends are in Revit internal feet — that's fine, Revit stores Length params in internal units regardless of your display units.
- **One family, all volumes.** Pool, house, office, link, gym, terrace are all just boxes at different sizes — no need for a family per type. Type is carried in the instance's *Comments*; volume id in *Mark*.
- **Terraces** (very thin, h≈0.12 m) come through as thin slabs. Fine for massing; delete them in Revit if you don't want them.

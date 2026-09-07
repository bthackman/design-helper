# Phase 4 — Space planning / test fit

Output: `4_Space-Planning/Program-Test-Fit.md` — a reconciled program table, adjacency matrix, stacking diagram, and an explicit fit check against the massing.

## Stress-test the brief again
The brief was interrogated at intake; now it meets geometry. Check unit areas against typology norms, verify the grossing factor is realistic for the massing type (a bar and a tower gross differently), and hunt for missing support space. Changes bump the brief version with a note.

## The fit check is the heart
Total NSF × grossing factor = required GSF, versus massing GFA. State the delta as a number. If it doesn't fit, the tool's job is to make the trade-off explicit and get a decision: cut program, grow massing, or accept a tighter grossing factor — each is a logged decision with consequences named.

## Adjacencies and stacking
Build the adjacency matrix from the brief plus what phases 1–3 implied. Then stack: assign program to floors respecting adjacencies, floor-plate sizes from the massing, and ground-floor logic from the site strategy. Flag violations rather than hiding them.

## Furnishing a test-fit — circulation FIRST, furniture second
When you take a plan from blocks to a furnished layout, the most common and most damaging error is placing furniture — especially fixed casework — across doorways and circulation. Furniture is not decoration on top of a plan; it is the test of whether the plan's circulation actually survives real objects. Do it in this order, every room:

1. **Mark every opening first.** List each door/opening in the room and draw its clear swing. In a hub / zero-corridor plan (a driver like "zero corridor" makes this acute), the hub's perimeter carries *many* openings — every room hangs off it — so its walls are mostly doorway, not furnishable wall.
2. **Draw the desire-lines.** Connect the openings with the paths people actually walk (door-to-door, entry-to-hub-to-each-room). Reserve a keep-clear band on each: **≥0.9 m** normally, **≥1.2 m** where step-free/aging-in-place is a driver, **1.5 m turning circles** in accessible rooms and at accessible fixtures.
3. **Furnish only the residual pockets.** Place furniture in what's left between paths and swings. **Fixed casework — kitchen counters/islands, wardrobes, vanities, built-ins — may sit only on SOLID wall runs**, never on a wall carrying a doorway and never across a swing or through-path. A freestanding island is fine *inside* the clear field but must leave its own ≥1.0 m working aisles. Beds, sofas and tables get pushed off any door approach.
4. **Kitchens specifically.** Route the run of casework onto the longest solid, opening-free wall (usually an exterior wall or the wall backing onto services for plumbing economy). If the only solid wall is short, use an L + island rather than lining a doorway wall.

**Verification (run before presenting any furnished plan):** trace each door-to-door path and each door swing and confirm no furniture — fixed or loose — intrudes on the keep-clear width. Showing the swings on the drawing makes the check visible to the client too. If the Test-Fit Studio is built, this becomes a live clearance/collision check flagging any furniture or casework that overlaps an opening or narrows a path below its keep-clear width.

## The Test-Fit Studio (interactive instrument) — evolves the phase from *diagram* to *steer*

Build a single self-contained HTML tool (`Test-Fit-Studio.html`, SVG + vanilla JS, no library needed — this phase is fundamentally 2D) so the architect places and steers room blocks, not just diagrams them. Same cost principle as the Massing Studio: client-side/one-time-build features go in by default; anything needing the model in the loop is on-request. **Freeform by default — don't hard-require a massing export.** Read the program table and adjacency matrix out of `Program-Test-Fit.md`; overlay a floor outline from the Massing Studio's `massing-interchange/v1` JSON *only if that file actually exists* for this project (it often won't — Massing Studio itself is only built on request, see `phase-3-massing.md`).

### ALWAYS build in (client-side — one-time cost, then free)
1. **Room blocks sized from the program table.** One block per instance (the program table's Count column expanded, not one block per row), draggable/resizable, grouped/coloured by cluster, each showing its live area against its NSF target. A running **cap meter** (live placed NSF × grossing factor vs. the massing GFA) — same red-when-over pattern as the Massing Studio's cap meter — plus a list of anything from the program table not yet placed.
2. **Door/opening placement with a live clear-swing arc.** Click a room's wall to drop a door; it draws its quarter-circle swing into the room, draggable along the wall.
3. **Fixed-casework check.** A furniture block flagged "fixed" is tested against the wall it's snapped to: if any door on that same wall overlaps its span (plus a margin), it lights up red — the circulation-first rule (above) made a live check instead of a verification step run by eye.
4. **Live adjacency panel.** Reads the matrix (required/preferred/separate) and the placed blocks' types; for every **required** pair, computes the minimum gap between any instance of each type and flags a violation above a touching threshold (~1 m) in real time as blocks are dragged. This is the piece that catches a required-adjacent pair split across clusters *while placing*, not after — see the honesty note below.
5. **Veranda/hub-loop clearance panel**, for the hub-heavy case `phase-4-space-planning.md`'s furnishing rule calls out (a driver like zero-corridor, or any shared-courtyard/veranda condition): openings placed along the loop each carry a keep-clear band (0.9/1.2/1.5 m per the rule above); the panel merges overlapping bands and reports, per arc, whether any residual pocket survives for even a bench — a direct, numeric version of "trace the swings before presenting."
6. **⤓ Export JSON** — `test-fit-interchange/v1`: rooms (id/type/cluster/x/y/w/h/doors), furniture, veranda openings, and the computed metrics (live NSF, adjacency results, veranda coverage), mirroring the Massing Studio export's pattern so a later tool could consume it the same way.

### Deliberately deferred (not v1)
Multi-floor stacking, AI-suggested layouts, a real furniture catalogue beyond simple rectangles, non-orthogonal room shapes. v1 stays at the same schematic abstraction level `Program-Test-Fit.md` itself already uses — a sketchpad for testing circulation and fit, not a furniture-catalogue tool.

### Honesty note — this is a type-level check, not an instance-level one
The adjacency matrix (like the source doc's own table) is defined per **type** (`Pod (C1)`, `Ablution`, …), not per individual instance. The live check therefore takes the *minimum* gap across all instances of each type — so if a project has two ablution blocks and only one sits near the required-adjacent room, the pair reads as satisfied even though the *other* instance doesn't. This matches what the matrix itself actually asserts (it never distinguished instances either), but it's worth knowing the check can't catch an instance-specific version of the same requirement.

### Studio hygiene
Self-contained single file; syntax-check the script before delivery; verify against the project's own real findings if any exist (a manual test-fit pass that already caught a real adjacency or clearance problem should reproduce, or at minimum not miss, that same finding once the Studio models it). Link the Studio from `Program-Test-Fit.md`.

## Export
This phase's table is the most export-worthy artifact: offer the .xlsx area schedule (flat, Revit-friendly) whenever the table stabilizes.

## Gate questions worth asking
Which adjacency requirement is actually load-bearing, and which is habit? Where will the client push back on net area, and what's the prepared answer? Does the stacking still serve the drivers, or did the spreadsheet win?

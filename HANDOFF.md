# Handoff — Design Process Tool

Read this to pick up work **on the tool itself** (not any specific project) after time away. It's the
honest current-state read — what's solid, what's genuinely unfinished, and where to look for more detail.

## What's solid

Client discovery, Site (open-data pipeline + mandatory assessment battery), the Drivers-lock gate,
Precedents (two-layer search + source-dialect discovery + fetch-before-cite verification), and Massing
(interactive Studio + driver scorecards + sun-tested section) are built, folded into `SKILL.md`, and
pressure-tested end-to-end on a full pilot project — with real failures caught and fixed along the way
(dead source links, a phantom lot geometry error, a first precedent board that turned out to be
memory-biased toward international canon rather than actually searched).

## What's genuinely unfinished

1. **Materiality has a protocol now, run once, on an academic project.** `phase-5-materiality.md`
   was rewritten 2026-08-28 (candidate palettes, driver scorecard, value-engineering test, lock) and
   run for real on Nonimuss — see `Projects/Nonimuss-Residence/5_Materiality/Material-Palette.md`.
   Real finding from that run: the protocol's "promote back to the library" step assumes a built
   project confirms a material choice held up; an academic/hypothetical project never reaches that
   gate, so nothing has actually been promoted into `Library/Materials/` yet, and the starter set
   seeded that day is still exactly as drafted — `[proxy, unverified]`, not yet earned by a real
   failure the way every other phase's reference has been.
2. **Space planning has no interactive tool.** Massing got a full client-side Studio (live cap meter,
   sun-section, trade-space plot); space planning is still hand-drawn diagrams + prose. A "Test-Fit
   Studio" (place → steer, with a live doorway/clearance collision check) is the named next tooling
   target — not yet built.
3. **Exports don't exist.** Program → `.xlsx`, brief/drivers → `.docx`, boards/decision log → `.pdf` are
   all speced in `00_Tool-Concept-Spec.md`, none built.
4. **Export receivers are uneven.** Blender (`_Export-Receivers/Blender/`) is built and tested end-to-end
   — but only against a synthetic fixture, not yet a real project's massing. Revit is paused at a
   Dynamo-graph MVP (Autodesk's own API is read-only for now, so there's no near-term reason to push
   further). Rhino hasn't been started at all.
5. **Precedents check a personal Obsidian vault as their source of truth, not a folder in this repo.**
   `_skill-source/references/phase-1-precedents.md` points phase 1 at an external vault path
   (`Architecture/Architecture Design/` tree) before running a fresh web search. That integration is
   specific to the tool author's own setup — running this tool elsewhere means either pointing that step
   at your own reference library in the same way, or skipping it and relying on fresh web search only.
6. **Never tested against a real client engagement.** Every run so far has been an academic/hypothetical
   project. Real-regulatory cap arguments (arguing floor-area exclusions to an actual development
   authority, not a course instructor), real budget-as-a-driver workflows, multi-disciplinary
   consultant-team coordination, and confidentiality handling for real client data are all identified
   gaps — none yet exercised. See the backlog in `00_Tool-Concept-Spec.md` for the full list and reasoning.

## Session handoff — 2026-08-28 (Project Window built; materiality run once)

The Project Window planned 2026-08-27 is now **built and working**: `_UI/Project-Window.html`,
a `file://`-openable page (verified — `showDirectoryPicker` works with no server) with a folder
picker, phase rail with the drivers-lock gate, pinned driver cards, open questions/decisions
panels, a collapsible/resizable conscience panel, a dependency-free markdown renderer, raw-doc
editing, decision-log append, and a Massing Studio iframe. `_UI/_selftest.html` is a repeatable
headless-Chrome regression check against the real Nonimuss files — rerun it after any change to
`spine-parse.js`/`audit.js` rather than trusting a manual click-through alone.

Building it against the real pilot (not a synthetic fixture) surfaced real bugs the synthetic test
suite hadn't: the client-discovery file probe and the drivers-table column matching both silently
failed against Nonimuss's actual files (the real drivers table uses `Test`/`Origin`, not the
template's `Why it matters here`/`How we'll know it's working`); a top-level `ORDER`/`API`
identifier collision between `spine-parse.js` and `audit.js` (both load as classic `<script>` tags
sharing one global scope) silently killed `audit.js` entirely; precedent cards encode driver
coverage in the heading text, not a field, so orphan-card detection false-flagged every card.
Templates were updated to match what real practice already does rather than what the schema still
claimed. `SKILL-patches.md` gained three more drafted (still unapplied) patches from a whole-corpus
synthesis pass — generalizing fetch-before-cite to judgment-only content, pointing the Phase Gate
at the Collaborator Roster, and fixing an internal disagreement in `SKILL.md` about the
client-profile filename.

Read **`SESSION-HANDOFF-2026-08-27.md`** for the original plan and the reasoning behind it — still
accurate for *why* the Window is shaped the way it is, just no longer accurate about build status.

## Where to look for more detail

- **`00_Tool-Concept-Spec.md`** — the full improvement backlog: every method decision, numbered, dated,
  with a status per item (folded into the skill / reference-only / still pending).
- **`Tool-Strategy-Map.md`** (+ `.svg`) — the whole tool as one map: method (true run order + the
  drivers-lock gate), tooling (grouped by type), and the roadmap, with a built / designed-pending /
  not-started legend.
- **`Massing-Export-Roadmap.md`** — the Studio → Rhino/Revit/Blender export architecture: what's shipped
  per target app, what's deliberately out of scope, and why.

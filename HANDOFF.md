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

1. **Materiality has never been run.** `_skill-source/references/phase-5-materiality.md` is still generic
   — no mandatory battery, no protocol earned from a real failure the way every other phase has one.
   Expect the first real run to surface gaps the reference doesn't cover yet.
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

## Where to look for more detail

- **`00_Tool-Concept-Spec.md`** — the full improvement backlog: every method decision, numbered, dated,
  with a status per item (folded into the skill / reference-only / still pending).
- **`Tool-Strategy-Map.md`** (+ `.svg`) — the whole tool as one map: method (true run order + the
  drivers-lock gate), tooling (grouped by type), and the roadmap, with a built / designed-pending /
  not-started legend.
- **`Massing-Export-Roadmap.md`** — the Studio → Rhino/Revit/Blender export architecture: what's shipped
  per target app, what's deliberately out of scope, and why.

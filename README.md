# Design Process Tool

A personal design copilot for early-stage architecture work: client discovery → site → precedents →
massing → space planning → materiality, held together by a per-project "spine" (brief, drivers, decision
log, open questions). Built by Ben Hackman with Claude, starting July 2026.

It runs as a Claude skill: point it at a project folder and it guides each phase, writes findings into
files (not just chat), generates options and critique, and keeps a decision trail so early thinking
survives to later phases.

## Install

1. Open `design-process.skill` in a Claude chat and click **Save skill** (or Settings → Capabilities →
   upload). This is the core skill — it triggers automatically on any design-phase conversation, or on
   any folder containing a `0_Spine/` directory.
2. Optionally install `design-collaborator-roster.skill` too — an account-level companion that convenes a
   standing four-voice design review (see below). It works with this tool, or standalone on any project.
3. Connect this repo's folder to your Claude session and say what you want: *"start a new project from
   this brief"* or *"resume the [project] project."* Claude reads the spine first — that's where all
   state lives.

## How it works

Work runs in the order design actually reasons, not phase-number order:

**Client discovery → Site (search + details) → ▮ DRIVERS LOCK (gate) → Precedents → Massing → ◇ → Space
planning → ◇ → Materiality**

Everything upstream of the drivers-lock gate *feeds* the drivers; everything downstream is *tested
against* them. A lightweight phase-gate critic (◇) runs between later phases. Phases loop freely — a
massing idea can send you back to precedent hunting — because the **spine** keeps looping safe.

| Phase | Guides you through | AI assists by | Output |
|---|---|---|---|
| Client discovery | Household vs. organization fork; school (invent) vs. work (interview) mode | Evidence → reading → position → implication matrix | Client profile |
| Site | Zoning, climate, access, views, topography, neighbours | Open-data pipeline (parcel, bylaw, elevation) + mandatory assessment battery | Site facts + strategy |
| Precedents | Framing what you're actually looking for before searching | Two-layer search (campaigns + scorecard), fetch-before-cite verification | Precedent board + transferable lessons |
| Massing | Generating 3+ genuinely different options | Interactive **Massing Studio** — live cap meter, driver proxies, sun-tested section, trade-space plot | Massing options + recommended direction |
| Space planning | Program-vs-area test fits, adjacency, circulation-first furnishing | Stress-tests the brief; checks fit vs. massing GFA | Test fit + reconciled program |
| Materiality | Palette by system, performance/cost/carbon | Suggests palettes matched to drivers + budget | Material palette |

**The spine** (`0_Spine/` in every project): brief, design drivers, decision log, open questions, client
profile — the memory that keeps early insight alive to late phases.

## Repository structure

```
00_Tool-Concept-Spec.md       what the tool is, build path, and the full improvement backlog
Tool-Strategy-Map.md / .svg   what's built vs. designed-pending vs. not-started, in one map
Massing-Export-Roadmap.md     Studio → Rhino / Revit / Blender export architecture
HANDOFF.md                    current state of the tool itself — read this to resume work on the tool

_skill-source/                 editable source for both skills
  SKILL.md                     design-process skill body
  references/                  per-phase method (one file per phase)
  design-collaborator-roster/  the companion skill's source
design-process.skill                packaged skill — install this one
design-collaborator-roster.skill    packaged companion skill — install this one too (optional)

_templates/                    blank per-project kit — copied into Projects/<name>/ to start a project
Library/                        cross-project knowledge: site strategies, materials, verified source register
_Export-Receivers/              thin receivers that turn a Massing Studio export into Rhino / Revit / Blender geometry

Projects/                       one folder per project (gitignored — your project data stays local, never pushed)
```

## The two skills

- **`design-process`** — the core guided workflow above. Fires on any design-phase conversation, or a
  folder containing `0_Spine/`.
- **`design-collaborator-roster`** — an optional, on-request four-voice critique: a generative **Design
  Collaborator** (calibrated to Brian MacKay-Lyons + Moshe Safdie as sensibilities, not pastiche), a
  **Client** voice pulled from the project's client profile, a **Studio Critic** (RAIC review panel +
  planning/code), and **the Archive** (retrieves your own prior decisions and patterns cross-project,
  never invents one — says "nothing on record" when there's nothing real to retrieve). Always ends
  generative — critique becomes a concrete, testable move, not just commentary. Pull it anytime with
  "run the roster" / "critique this design."

## Status

Client discovery, Site, the Drivers-lock gate, Precedents, and Massing are built, folded into the skill,
and pilot-tested end-to-end on a real project. Space Planning is tested but doesn't have its own
interactive tool yet. Materiality is designed but has never been pilot-run. See **`HANDOFF.md`** for the
honest current-state read, and **`00_Tool-Concept-Spec.md`** for the full backlog.

## License

MIT — see `LICENSE`.

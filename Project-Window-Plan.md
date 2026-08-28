# Project Window — Plan

Status: **plan; parsing and audit layers built and tested** (2026-08-27).
Author: Ben Hackman + Claude.

## What this is for

Not a dashboard. The tool already writes everything down — the risk it carries isn't lost data,
it's that the *judgement* evaporates between sessions. A driver nobody has tested against, a
question open since client discovery, a precedent serving no driver: all of that is computed in
conversation and then gone when the session closes.

So the Window has two jobs, and only the first is obvious:

1. **Show the project.** Where you are, what each phase produced, what the massing looks like.
2. **Hold up what's unfinished.** Recompute the things a good critic would notice, every time
   you open it, without being asked.

The second is the one a terminal genuinely can't do, and it's cheaper to build than the first.

---

## Vocabulary

Moved to **`GLOSSARY.md`** in the repo root — every term this tool uses, including the three
surfaces (Terminal / Cowork / Project Window) and the Studios. Kept there rather than in this
plan or in `HANDOFF.md`, because definitions outlive both a plan and a status report.

## The one architectural decision

Single self-contained HTML file, no server, no build step, no dependencies beyond CDN
(Three.js, Chart.js — same as the Massing Studio already uses). It gets folder access through
Chrome's File System Access API: you grant `Projects/<name>/` once, it reads and writes the real
files from then on.

Chrome-only and single-user is fine — this is a personal tool, not a product.

**Why not have the Window call the Claude API:** that would be Claude *without* the
`design-process` skill installed — a worse collaborator than the one already sitting in your
terminal, billed separately. The Window's job is to see. Claude Code and Cowork do the work.
The files are the handoff.

---

## Prerequisite — `0_Spine/state.json`

There is currently **no machine-readable record of where a project is.** The Window can infer a
lot (which phase docs exist and have been filled past template, whether a drivers-lock decision
sits in the log), but inference is fragile and silently wrong is worse than blank.

So: one small state file, written by the skill at every phase transition, read by the Window.

```json
{
  "project": "Nonimuss-Residence",
  "clientFork": "household",
  "updated": "2026-08-27",
  "driversLocked": true,
  "driversLockedDate": "2026-08-14",
  "currentPhase": "massing",
  "phases": {
    "client-discovery": { "status": "complete",    "updated": "2026-08-02" },
    "site":             { "status": "complete",    "updated": "2026-08-11" },
    "precedents":       { "status": "complete",    "updated": "2026-08-27" },
    "massing":          { "status": "in-progress", "updated": "2026-08-27" },
    "space-planning":   { "status": "not-started" },
    "materiality":      { "status": "not-started" }
  },
  "openQuestionCount": 4,
  "briefVersion": 3
}
```

`status` ∈ `not-started` | `in-progress` | `complete` | `looping-back`.

**Skill change required:** `SKILL.md` gains a rule alongside "write as you go" — update
`state.json` on phase entry, phase exit, drivers lock, and brief version bump. Small edit, and it
makes the tool's own state legible even without the Window.

**Fallback:** if `state.json` is missing (older projects), the Window infers status from file
presence and content and shows the whole rail dimmed, with a "state inferred" marker.

---

## The conscience panel

Standing panel, recomputed on every open, derived entirely from files the tool already writes —
so it costs nothing per use and never needs the model in the loop.

| Finding | Derived from |
|---|---|
| **Driver never tested** | A locked driver whose terms appear in no decision and no downstream phase doc |
| **Question blocking now** | An open question whose `Blocks` column names the current phase |
| **Question carried too far** | Open two or more phases past where it was raised |
| **Upstream changed after the lock** | Any brief / client / site file modified after the drivers-lock date |
| **Phase gate missing** | A phase marked complete with no gate recorded in its doc |
| **Orphan precedent or option** | A card naming no driver it serves |

Sorted by severity, one row per concern rather than one per file — a panel that lists four rows
for the same issue teaches you to ignore it.

Everything here is a **prompt to look**, not a verdict. Keyword matching is loose by design; the
panel's job is to raise the question, and yours is to dismiss it in two seconds if it's wrong.

**Built and tested** — `audit.js`, run against the fixture project, produces exactly the findings
above and correctly leaves alone the driver that *is* being discussed.

---

## Two more things the Window should do

**Pin the drivers.** The whole method is "tested against the drivers," but in a terminal you
can't see them while you work. Four cards permanently on screen, always visible, whatever phase
you're in. This probably changes behaviour more than the 3D viewer will.

**Show what moved since you last looked.** Resuming after three weeks is the real use case, and
"here's what changed" beats "here's the current state." Store a last-opened timestamp, diff
against file modification times, and lead with that view on open. Built and tested as
`sinceLastOpen()`.

**Read the decision log back.** Right now it's write-only — an archive that never gets reopened.
If a driver card showed the decisions that touched it, and a parked massing option showed why it
was parked, the log would start earning its keep. Same data, pointed the other way.

---

## Layout

```
┌──────────────┬────────────────────────────────────────────┐
│  PHASE RAIL  │  ⚠ 2 drivers never tested · Q2 blocks now   │  ← conscience
│  ● discovery ├────────────────────────────────────────────┤
│  ● site      │                                            │
│  ▮ LOCK      │            ARTIFACT VIEWER                 │
│  ● precedent │      (format-aware, one pane)               │
│  ◐ massing   │                                            │
│  ○ space     │                                            │
│  ○ material  │                                            │
├──────────────┤                                            │
│  DRIVERS  📌 │                                            │
│  1 winter    │                                            │
│  2 light     │                                            │
│  3 no corr.  │                                            │
│  4 aging     │                                            │
├──────────────┤                                            │
│  decisions   │                                            │
│  open Qs (3) │                                            │
└──────────────┴────────────────────────────────────────────┘
```

**Phase rail** — where you are, what's done, and the drivers-lock gate drawn as an actual gate.
Clicking a phase loads its artifacts into the viewer.

**Spine panel** — the five spine docs are all markdown *tables* with fixed columns, so they render
as real UI rather than a markdown blob:
- **Drivers** — one card each, with "how we'll know it's working" visible, because that's the
  column that gets ignored. Locked state shown; parked drivers behind a toggle.
- **Decision log** — reverse-chronological timeline, filterable by phase. Rejected alternatives
  collapsed until asked for.
- **Open questions** — grouped by what they *block*, not by number. A question blocking the phase
  you're in shows red.
- **Brief** — program table with version number; flags any row with an unknown area.

---

## The artifact viewer, per phase

The viewer picks a renderer by what it finds, not by a fixed guess.

| Phase | Reads | Renders as |
|---|---|---|
| Client discovery | `04a/04b_Client-Profile` | Evidence → reading → position → implication matrix as a table |
| Site | `Site-Details_*.md`, `2_Site/data/*.geojson`, `diagrams/` | **Parcel plan drawn from the stored GeoJSON vertices** — real polygon, north arrow, setback envelope, sun-angle overlay. Plus diagrams, plus map links as buttons |
| Precedents | `Precedent-Board.md`, `1_Precedents/images/` | Card gallery — image, role badge (Anchor / Lesson / Evidence), what to steal, drivers served. Lessons pulled out as their own panel, since they're the actual output |
| Massing | `massing.json`, `Massing-Studio.html`, `Massing-Options.md`, `images/` | **3D viewer** — Three.js reading `massing-interchange/v1` directly (axis-aligned boxes, `base` stacking, `glaz` as transparency, `site.lotPolygon` as ground). Options side by side with driver scorecards. "Open Studio" iframes the project's own `Massing-Studio.html` |
| Space planning | `Program-Test-Fit.md`, `4_Space-Planning/images/` | Program table with the fit-check delta shown as a number and a bar; adjacency matrix; stacking and furnished-plan diagrams |
| Materiality | `Material-Palette.md`, `5_Materiality/images/` | Palette swatches grouped by system, with performance/cost/carbon columns |

The massing viewer is the one that earns the most: `massing.json` is already a frozen schema of
regular boxes, so a real orbitable model is a few hundred lines, not a project.

---

## Editing

Read-only would be half a tool. The Window writes back to:
- **Decision log** — append form (decision, rationale, rejected alternatives, phase). The most
  common thing you'd want to do without opening a terminal.
- **Open questions** — add, and flip status to resolved.
- **Drivers** — edit the "how we'll know" column; drivers themselves are edit-with-friction once
  locked, since unlocking is a decision that belongs in the log.
- **Any spine file** — raw markdown editor as the escape hatch.

Every write goes straight to the `.md` file in place. No database, no cache, nothing that can
drift from the files.

---

## Handing off to Claude

A "start this phase" button per phase composes the right opening prompt — project name, current
phase, blocking open questions — and copies it to the clipboard for pasting into Claude Code or
Cowork. No API call, no parallel Claude, no second source of truth.

---

## Changes to the tool itself

Three, all small, all worth doing whether or not the Window gets built:

1. **`state.json`** — new spine file, maintained by the skill (above).
2. **Archive precedent images.** Fetch-before-cite already loads every image to verify it's
   viewable. Save it to `1_Precedents/images/` at the same moment and point the card at the local
   copy, keeping the source URL as provenance. Links rot; the board shouldn't. Costs no tokens.
   *(Site map-view links stay as links — the saved GeoJSON already makes those diagrams
   reproducible, which is the durability that actually matters.)*
3. **Give phase 4 an `images/` folder** in the project-structure block in `SKILL.md`. The phase
   reference calls for stacking diagrams, adjacency matrices and furnished plans with door swings,
   but the declared folder structure gives them nowhere to live, so the Window has nowhere to look.

---

## Build order

**MVP — hard stop here.**

1. `state.json` schema + the `SKILL.md` rule that maintains it
2. Window shell — folder picker (repo root), phase rail, pinned drivers, spine panel
3. **Conscience panel** + since-last-open view *(logic already built: `audit.js`)*
4. Decision-log append form + raw markdown editor
5. **Iframe the project's own `Massing-Studio.html`.** A few lines, no new geometry code —
   and you can't develop a test fit without seeing the massing it sits in, so this is on the
   critical path, not a garnish.

Then use it for a week. Not "then build step 6" — actually use it, and let the next build be
whatever you find yourself reaching for and not finding.

**After that, and only if wanted:**

6. Precedent gallery and site viewer (GeoJSON parcel plan)
7. Space planning and materiality views
8. Prompt launcher

**Deliberately not in this plan:** a separate Three.js viewer reading `massing.json`. It would
duplicate what the Studio already shows you. The real reason to build it is the **Test-Fit
Studio** — that tool needs massing geometry as its base, and `massing.json` is the feed. So it
isn't a viewer at all; it's step zero of the Test-Fit Studio, and it should be sequenced with
that work rather than with the Window.

---

## Tool changes worth doing regardless of the Window

Beyond the three already listed above (`state.json`, precedent image archiving, a phase-4
`images/` folder):

**Run materiality once.** It's a bigger risk than space planning. Every other phase earned its
protocol from a real failure — dead source links, the phantom lot geometry, the memory-biased
first precedent board. Materiality's reference is the only one still purely theoretical. One run
against the pilot project's existing massing would earn it a real battery, and it costs a session
rather than a build.

**Make the vault path config, and make a miss loud.** Phase 1 checks an Obsidian path that may
not resolve identically from Cowork and from Claude Code. If it doesn't resolve, the step
degrades silently into web-only search and you'd never know your own collection was skipped.
Put the path in one place, and say out loud when it isn't found.

## To verify against a real project

Written from the repo's templates and phase references, not from a project that has actually run.
Check against a local project folder before building:

- Do phases write images where the reference implies, and under what filenames?
- Is the site GeoJSON one file or several, and what's in the header?
- Has any project emitted `massing.json` yet, or only the Studio's text export?
- Do the spine tables in a real project still match the template columns, or have they drifted?
- Where do space-planning diagrams currently get saved?

---

# Review of this plan

Written after the plan, against it. What follows is what a fresh reader would object to,
plus what testing actually found.

## Tested, and what broke

A parser for the spine and phase docs was written and run in Node against two fixtures: an
untouched copy of `_templates/`, and a synthetic project worked through massing. 33 checks,
now passing. Four things broke on the way, and all four would have broken tomorrow:

1. **"Non-blank table row" is not evidence of work.** The templates ship *with* scaffolding
   rows — the client-profile matrix carries 12 prompt questions, `Site-Details.md` carries 12
   category labels, the adjacency matrix carries its own axis. A naive parser reported an
   untouched template tree as four phases in progress. Fix: diff each row against the
   template's corresponding row.
2. **Template placeholder *values* are non-empty too.** A massing option card ships with
   `**Status:** active / parked / dead`. Same fix, applied to cards.
3. **Not every phase doc is a table.** `Precedent-Board.md`, `Massing-Options.md` and
   `Material-Palette.md` are `###` headings with `- **Label:** value` bullets. A table-only
   reader reports precedents and massing as empty when they are full. The Window needs two
   parsers: **table docs** (spine, site, program) and **card docs** (precedents, massing,
   materiality).
4. **Naive filename-to-template matching mangles names.** Stripping a trailing `_suffix` turns
   `Site-Details_1412-14-St.md` into `Site-Details.md` correctly, but also turns
   `04a_Client-Profile-Household.md` into `04a.md`. Fix: exact match first, then strip one
   segment at a time until a template matches.

Escaped pipes inside cells (`envelope\|loss`), em-dashes, and ✓/~/✗ score glyphs all survive
parsing. `massing.json` computes GFA correctly and tolerates an omitted `rot90`.

`spine-parse.js` and its test suite are the deliverable of this review — real, runnable, and
directly reusable as the Window's parsing layer.

## Corrections to the plan above

**Point the Window at the repo root, not the project folder.** The plan said
`Projects/<name>/`. Wrong — accurate state inference requires reading `_templates/` to diff
against, and the repo root also gives a project list for free. Grant the repo root once.

**"Grant folder access once" was optimistic.** Chrome does not persist write permission across
reloads on its own. The handle can be stashed in IndexedDB and re-authorized with
`requestPermission()`, but that needs a user gesture. Honest version: one click on open.

**Trim `state.json`.** `openQuestionCount` and `briefVersion` are derivable from the files and
will drift the moment something edits a doc without updating state. Store only what cannot be
derived: `currentPhase`, `driversLocked`, per-phase `status`, and timestamps. Everything else
is computed on read.

**Concurrent writes are a real risk.** Claude Code and the Window can both write the same file.
Before any Window write: re-read the file, compare its modified time against what was loaded,
and refuse with a diff if it changed underneath. Without this, an open editor pane will
eventually clobber something Claude wrote.

## The one thing that could sink it

**`showDirectoryPicker()` may not work from a `file://` page.** The File System Access API
requires a secure context, and opening the HTML by double-clicking may throw rather than prompt.
This is unverified and it is the single highest-risk assumption in the plan — everything else
degrades gracefully, this doesn't.

Verify first thing tomorrow: open a one-line test page in Chrome and see whether the picker
appears. If it doesn't, the fallback is `python -m http.server` in the repo root and browsing to
`localhost:8000` — which costs one terminal command per session and nothing else. Worth deciding
before any UI gets built, because "no server" is a claim the plan currently leans on.

Secondary risks, lower stakes: **OneDrive** — if the repo syncs through it, Files On-Demand
placeholders may read as empty or stall, and `SKILL.md` already records sync truncation
damage. **CDN** — Three.js and Chart.js from CDN means the Window needs a connection; vendor
them locally if that annoys.

## Scope

Eight build steps is more than this needs to be useful. The honest MVP is steps 1–3: folder
picker, phase rail, spine panel, decision-log append. That alone answers "where am I" without
opening a terminal. The massing 3D viewer is the most fun and the least necessary — it should
be step 6, after the thing has proven it earns opening.

## Still unverified against a real project

- Does `showDirectoryPicker` work from `file://`?
- Has any project actually emitted `massing.json`, or only the Studio's text export?
- Do real spine tables still match the template columns, or have they drifted?
- Where do space-planning diagrams currently get saved, and under what filenames?
- Is the repo inside a OneDrive-synced path?

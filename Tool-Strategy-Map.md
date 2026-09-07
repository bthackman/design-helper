# Design Process Tool — Strategy Map

*A design copilot: client → site → drivers → precedents → massing → space → materiality, held by a per-project spine. Restructured 2026-07-25.*

**Companion:** `Tool-Strategy-Map.svg` is the visual version of this same map. This file is the text-of-record; keep them in sync.

**Status legend:** ✅ built & proven · 🟠 designed — skill fold-in pending · ⬜ not started / future

---

## Band 1 · The method — process flow in true run order

The flow runs in the order the work actually happens (not by phase number). Client discovery and driver-derivation are real steps in the line, not orphans. Everything upstream of the **Drivers-lock gate** *feeds* the drivers; everything downstream is *tested against* them. Between the later phases sits a lightweight **phase-gate critic** (◇) — "does this still serve the drivers?" Phases loop freely; the spine is what keeps looping safe.

| Order | Step | State | Essentials |
|---|---|---|---|
| 1 | **Client discovery** | 🟠 | Household / organization fork · school mode (invent) vs work mode (interview) |
| 2 | **Site** | ✅ | Site search + site details · open-data pipeline (parcel · bylaw · CDEM) · battery (sun · wind · acoustic · context) |
| ▮ | **DRIVERS LOCK** (gate) | ✅ | Evidence tiers · non-client forces · site-argues-back workshop · lock gates (3–5 · testable · traceable) |
| 3 | **Precedents** | ✅ | 2-layer search (campaigns + scorecard) · roles Anchor/Lesson/Evidence · fetch-before-cite + Sources register |
| 4 | **Massing** | ✅ | 3+ options · numbers · scorecards · Massing Studio (interactive) · cap-argument drafting |
| ◇ | *phase-gate critic* | — | Does the output still serve the drivers? |
| 5 | **Space planning** | 🟠 | Tested on pilot (paused): program verified · bubbles→furnished plan · section+elevation · **circulation-first furnishing** rule · roster-run office-at-grade variant. Method in phase-4 ref; SKILL.md fold-in pending phase close |
| ◇ | *phase-gate critic* | — | Does the output still serve the drivers? |
| 6 | **Materiality** | ⬜ | Material palette by system · envelope · pool-humidity specs · local-trades detailing |

**Project spine** (read before every phase · write after): brief · design drivers · decision log · open questions · client profile — the memory that keeps early insight alive to late phases.

---

## Band 2 · The tooling — reusable machinery, grouped by type

| Group | State | Contents |
|---|---|---|
| **Interactive tools** (client-side) | ✅ | Massing Studio ✅ (steer volumes, cap meter, sun-section) · Test-fit tool (next). Principle: *build once, then free.* |
| **Reasoning skills** | 🟠 | Collaborator Roster ✅ (3 voices) · design-process skill (re-packaging, per-phase fold-in as each completes). Run in-session; token-metered. |
| **Knowledge** (cross-project) | 🟠 | Library (site moves · materials · Sources register). **Precedents live in Ben's Obsidian vault, not Library/** (decided 2026-08-27) — vault checked at search-time, cards promoted back at phase-gate. First promotion: Nonimuss's 8-card board + 6 lessons (2026-08-27). Site-Strategies/Materials promotion not yet exercised. |
| **Exports** (on demand) | ⬜ | program → xlsx (Revit) · brief / drivers → docx · boards / log → pdf |

---

## Band 3 · The roadmap — how the tool evolves

**Build path**

1. **v0 — Claude project** ✅ — folder + templates + design-process skill. *In use now.*
2. **Continuous re-package + tool kit** 🟠 — fold each phase's method into `SKILL.md` as that phase completes (not one big batch). *P1 + P3 folded in 2026-07-25; P4/P5 pending as they're built.*
3. **Library-at-scale → optional database** ⬜ — only if cross-project reuse demands it. *Conditional, not a mandated step.*
4. **v2 — web app** ⬜ — custom UI per phase · Rhino / Revit exchange. *Long-term destination.*

*Rationale for the revised path (2026-07-25): the pilot's highest-value output is method (skills), per-project memory (markdown spine), and interactive client-side tools — none of which are database-shaped. Airtable earns its place only for a cross-project Library big enough to need galleries and queries, which today's single pilot doesn't yet warrant. So the database moves from "v1, next" to "optional, conditional," and the real near-term track is continuous skill fold-in plus a growing kit of client-side phase tools.*

**Where to go next (priority order)**

✅ **DONE 2026-07-25** — Re-packaged **Phase 1 · Precedents** & **Phase 3 · Massing** method into `SKILL.md` (rewritten to the true run order; drivers-lock gate, site two-function split, and hygiene rules folded in too), and rebuilt `design-process.skill` to include the two references it had been missing (`phase-0-drivers.md`, `collaborator-voices.md`).

1. **Decide OQ-18 (single- vs two-storey), then close Phase 4** — pilot space planning is tested + paused; pick the scheme (roster favours office-at-grade), verify program areas vs the course brief, loop the winner back to the **Massing Studio** (plate grew to ~120 m² on one level), then fold the P4 method into `SKILL.md`. The **Test-Fit Studio** (mirroring the Massing Studio, *place → steer*, same client-side/model-in-loop cost split, live doorway-clearance + adjacency checks) was **built 2026-09-07** — see `HANDOFF.md` and `_skill-source/references/phase-4-space-planning.md` — folding its rules into `SKILL.md` still waits on P4 closing per the item above.
2. Build **Phase 5 · Materiality** — palette + pool-humidity / envelope specs + local-trades detailing.
3. **Exports** (xlsx program · docx brief+drivers · pdf boards) and exercise **Library promotion**.
4. **Optional upload modes** — sketch → option, real-drawing precedent overlay (token-taxing, on-request).

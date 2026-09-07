# Design drivers — [Project name]

**Status: not yet locked.** Drivers freeze only after client *and* site — change this line to
`**Status: LOCKED YYYY-MM-DD**` once the site has argued back at the drivers-lock gate.

3–7 big ideas that steer every phase. Each phase output gets tested against these. Keep them few, specific, and testable — "daylight to every workspace" not "good design."

## Consolidation workshop (run once, at the drivers-lock gate — see `phase-0-drivers.md` §4)
Every candidate driver tested against the verified site facts, one row each, before anything locks.
Full method in `phase-0-drivers.md`; this is just the table it currently has no template home.

| Candidate driver | Evidence tier (stated/derived/structural/contradiction) | Site fact tested against | Verdict | Disposition |
|---|---|---|---|---|
|  |  |  | CONFIRM / SPECIFY / DEFLATE-REFRAME / DEMOTE |  |

**Verdict** — CONFIRM (site strengthens it, lock as-is) · SPECIFY (site adds precision, lock
sharpened) · DEFLATE-REFRAME (site makes part of it moot, salvage what survives) · DEMOTE (right
idea, wrong scale — send to the relevant phase as a quality target, not a project driver).
**Disposition** — where it actually went: locked as-is / locked-reframed-into [driver #] /
demoted-to [phase] / dropped-because [reason]. Nothing on this table may be left blank — the "full
disposition" lock-quality gate means every candidate's fate is traceable, not just the winners'.

**Site-volunteered drivers** — candidates the site raised that client discovery couldn't see (run
the workshop in both directions): 

## Locked drivers
| # | Driver | Test | Origin |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

**Test** — how you'll know it's working, concretely: a plan audit, a live sun-path check, a locked
number. A test you can't fail is a sign the driver isn't actually locked yet. **Origin** — the
candidate driver, site finding, or client-profile row this was distilled from, so the derivation
stays traceable back to evidence.

## Parked
Ideas that didn't make the cut but shouldn't be forgotten. Any DEMOTE/DEFLATE-REFRAME/dropped
candidate from the workshop above also gets a row in `Library/Parked-Ideas.md` (project, what, why,
tags, reconsider-if) — this section is the project's own record, that register is what makes it
findable from a different project.

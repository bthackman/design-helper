# Session handoff — 2026-08-27

Everything from one evening's work on a UI for this tool, plus ten drafted skill edits that came
out of it. **Nothing here is applied to the skill and no UI is built.** This is a plan, a tested
parsing layer, and a running order.

Written from a phone, so nothing has met a real project folder yet. That's tomorrow's first job.

---

## What was added

| File | What it is |
|---|---|
| `Project-Window-Plan.md` | The plan for the UI, including a self-review section listing what testing broke and what corrections that forced |
| `GLOSSARY.md` | **New standing file.** Every term the tool uses — phases, protocols, Studios, the three surfaces. Keep it current; a rule for that is in the patches |
| `SKILL-patches.md` | Ten drafted edits to `_skill-source/SKILL.md`. Each has its reasoning attached. None applied |
| `_UI/probe.html` | Browser capability test — does folder access work from `file://`? |
| `_UI/inspect-project.js` | Diagnostic: run against a real project, get an inventory, drift check, `massing.json` validation, and what the Window would show |
| `_UI/spine-parse.js` | Table + card parsers and phase-state inference. Tested |
| `_UI/audit.js` | The conscience panel logic. Tested |
| `_UI/runtest.js`, `_UI/audittest.js` | Test suites: 33 + 9 checks, all passing against a synthetic fixture |
| `_UI/README.md` | The running order, in short form |

---

## Tomorrow, in order

The order matters — each step can invalidate the ones after it.

### 1. `probe.html` — two minutes

Open it in Chrome. Click both buttons. It reads a folder, then writes and deletes a scratch file,
then prints a verdict.

**This is the highest-risk assumption in the whole plan.** `showDirectoryPicker()` may refuse to
run from a `file://` page. If the verdict is green, the Project Window can be a file you
double-click. If it's red, run `python -m http.server 8000` from the repo root and browse to
`http://localhost:8000/_UI/probe.html` — everything else in the plan still holds, at the cost of
one terminal command per session.

Do this before building anything.

### 2. `inspect-project.js` — five minutes

```
node _UI/inspect-project.js Projects/<pilot-project>
```

Read **section 4 (column drift)** and **section 5 (assets and exports)** closely. Those are where
the plan's assumptions break if they're going to. Also confirms whether the repo sits inside a
OneDrive path, which matters for file access.

Then fix whatever it reports — in `spine-parse.js` or in the template, whichever is actually wrong.

### 3. Generate `state.json`

```
node _UI/inspect-project.js Projects/<pilot-project> --write-state
```

Inference is a starting point, not the truth. Read the generated file, correct anything wrong by
hand, then the skill maintains it from there (patch 1).

### 4. Apply the skill patches

`SKILL-patches.md`, in order. Patches 1–5 are structural (state file, image archiving, phase-4
diagrams folder, vault config, glossary upkeep). Patches 6–10 are all precedent-phase method.
Repackage `design-process.skill` after.

### 5. Only then, start the Window

MVP is: folder picker at the repo root, phase rail, pinned drivers, conscience panel,
decision-log append, and an iframe of the project's own `Massing-Studio.html`. Then stop and use
it for a week before building more.

---

## The reasoning worth not losing

Four things came out of tonight that are easy to revert without understanding what they protected.

**Templates ship with content, and that broke every naive check.** The client-profile matrix
carries twelve prompt questions; `Site-Details.md` carries twelve category labels; massing option
cards carry placeholder *values* like `active / parked / dead`. A parser asking "is this row
blank?" reported an untouched template tree as four phases in progress. Detecting work means
diffing against the template, everywhere. If you pre-fill anything new in a template, it becomes
invisible to every reader downstream.

**Not every phase doc is a table.** Precedent boards, massing options and material palettes are
`###` headings with `- **Label:** value` bullets. A table-only reader calls those phases empty when
they're full. Two parsers, permanently.

**Vault-first search creates groupthink** (patch 8). The original vault-first rule was a corrective
for a real failure — a memory-biased first board. But a vault reflects what you've already noticed,
so building from it first makes the collection converge on itself, invisibly. Vault and fresh
search now run in parallel into one pooled long-list, and the diversity audit tracks the ratio.

**"Exhaust inner rings first" quietly restricts by budget** (patch 10). Ring 4 is *anywhere*, so
nothing is formally excluded — but effort runs out around ring 2. And ring 3 conflates two things:
climate-matching predicts whether a *technical* lesson transfers, while sectional and spatial moves
transfer across climate fine. Hence the reserved open slot: one campaign per board that searches
the problem with the place words stripped out, capped at Lesson-role keepers only.

---

## Still unverified

- Does `showDirectoryPicker()` work from `file://`?
- Has any project actually emitted `massing.json`, or only the Studio's text export?
- Do real spine tables still match the template columns?
- Where do space-planning diagrams currently get saved, and under what filenames?
- Is the repo inside a OneDrive-synced path?

All five are answered by steps 1 and 2 above.

---

## Not from tonight, but still true

`HANDOFF.md` remains the current-state read for the tool itself. Two items on it are worth more
than the Window: **materiality has still never been run** — it's the only phase whose protocol was
never earned from a real failure — and **space planning still has no Test-Fit Studio.** Both are
worth more than a nicer way to look at work already done.

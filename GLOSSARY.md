# Glossary — Design Process Tool

Every term this tool uses that isn't plain English: phases, protocols, artifacts, Studios, and
the three surfaces the work happens on. Reference, not status — for what's built versus
unfinished, read `HANDOFF.md`.

**Keep this current.** When a phase coins a protocol, a Studio gets built, or a rule earns a
name, the term lands here in the same session. A vocabulary that lags the tool is worse than
none, because it teaches you the wrong thing confidently.

Last updated: 2026-09-06.


### The three surfaces

| Term | What it is |
|---|---|
| **Terminal** | Where Claude Code runs. Text in, text out. |
| **Cowork** | The desktop app the tool also runs in. |
| **Project Window** | New. A single HTML file opened in Chrome, pointed at the repo. Shows project state and artifacts. Does no design work itself. |

### The Studios

A **Studio** is a specific kind of thing in this tool, not a loose label. It means: a
self-contained interactive HTML file, generated per project, that runs entirely client-side in
the browser — no server, no model in the loop.

That last part is the whole point, and it comes from the cost principle already written into
the massing phase: **anything running client-side is a one-time build, then free forever;
anything needing the model on every use costs tokens each time.** So a Studio is where a phase's
thinking gets converted into something you can steer for an hour at no cost, instead of asking
Claude to recompute it forty times.

What earns being a Studio: the phase has a small number of numeric variables, a way to score
them live against the drivers, and a decision that's better *steered* than *picked from a list*.

| Term | What it is |
|---|---|
| **Massing Studio** | **Built and pilot-tested.** `Massing-Studio.html`, generated into `3_Massing/`. Steerable volumes (E–W, N–S, width, depth, height, rotate-90, base elevation, glazing %), a live cap meter against the hard program cap, concept-grade driver proxies, a movable sun-tested section on both axes, and a trade-space plot with a live point. Its ⤓ Export emits `massing.json`. This is what turned massing from *pick an option* into *steer an option*. |
| **Test-Fit Studio** | **Named, designed, not built.** The intended phase-4 equivalent: place program blocks, then steer, with a live clearance check flagging any furniture or casework that crosses a doorway, blocks a swing, or narrows a path below its keep-clear width (≥0.9 m, ≥1.2 m where step-free matters, 1.5 m turning circles). It would make the circulation-first furnishing rule enforceable instead of advisory. Needs massing geometry as its base — which is why `massing.json` belongs to this work, not to the Window. |
| **Studio (in "Studio Critic")** | **Unrelated — a naming collision worth knowing about.** In the collaborator roster, "Studio Critic" means the review-panel voice (≈75% RAIC panel, 25% City DP and code). It is a person-shaped voice, not an HTML tool. |
| **Project Window** | **Not a Studio.** A Studio generates and steers geometry for one phase. The Window reads the whole project and steers nothing. It *hosts* Studios; it doesn't replace them. |

No other Studios exist or are planned. Site, precedents and materiality have no numeric
steer-space that would earn one — their outputs are judgement and evidence, not variables.

### Inside the tool

| Term | What it means here |
|---|---|
| **Spine** | The six living docs in `0_Spine/` — brief, drivers, decision log, open questions, client profile, `state.json`. Read before every phase, written after. The project's memory. |
| **`state.json`** | The spine's machine-readable pointer: `currentPhase`, `driversLocked`, a status per phase. Never the source of truth — the other five spine docs are — just a cheap index for external tools like the Project Window. |
| **Brief** | The program as understood *now*: spaces, areas, adjacencies, constraints. Versioned; the version bumps whenever the program changes. |
| **Client discovery** | First phase. Household or organization fork, then the evidence → reading → position → implication matrix. Produces *motives*, not yet drivers. |
| **Motives** | What the client's reading implies about how a site should be chosen or judged. Upstream of drivers. |
| **Site search** | Criteria → candidate zones → parcel drill-down → user selects. Skipped when the site is already known. |
| **Site details** | Land use, bylaw envelope, and the mandatory assessment battery on a known parcel. |
| **Assessment battery** | The non-optional site checks: elevation, views, landscape context, computed sun study, wind, acoustic, plus the two-ring context scan. |
| **Drivers** | The 3–5 project-scale ideas everything downstream is tested against. Each must be testable, traceable to evidence, and able to say no. **Always project-specific** — the template ships an empty table; a driver portable to another project isn't project-scale enough to have passed the gate. |
| **Drivers lock** | The gate. Drivers freeze only after client *and* site, so the site can argue back. Everything before feeds the drivers; everything after is tested against them. |
| **Site argues back** | The workshop at the gate: each candidate driver gets confirm / specify / reframe / demote, and the site may volunteer drivers of its own. |
| **Parked** | A demoted driver or a rejected massing option kept on record rather than deleted, so it stays recoverable. |
| **Precedents** | Buildings studied to answer a named problem. |
| **Search plan** | The pre-search document. Reviewed and signed off *before* any query runs. |
| **Campaign** | One search line built on a rare, retrievable discriminator. Only rare terms belong in queries. |
| **Scorecard** | The visible scoring of the pooled long-list against drivers, so culling is auditable. |
| **Anchor / Lesson / Evidence** | A precedent's role. Anchor = whole building, ≥3 drivers. Lesson = one transferable move. Evidence = proof something works; never shown as a design precedent. |
| **Region rings** | Search escalation: 0 city → 1 region → 2 country → 3 same climate → 4 anywhere. Inner rings first. |
| **Default Canadian awards ladder** | The named, verified default sweep for the typology-baseline awards campaign — Prairie Design Awards (ring 0–1) → Governor General's Medals (ring 2) → Finlandia Prize (ring 3) → Stirling / Mies / Aga Khan (ring 4). Populates the ring sweep with known-good sources instead of rediscovering it per project. Search targets to fetch, never a list to recall from memory. |
| **The open slot** | One reserved campaign per precedent board that strips the place words out of the query and searches for the underlying problem, not a building "like this one." Runs even when the inner rings already returned plenty. A keeper from it may only earn the Lesson role, never Anchor or Evidence. |
| **Source dialect** | Who commissions, awards, publishes, regulates this building type in this region — discovered per typology, not reused. |
| **Fetch before cite** | Every link presented has actually been opened: it resolves, facts come from the page, images are viewable. |
| **Lessons** | The 3–6 transferable moves a precedent set teaches. The real output of the phase; the board is just the working surface. |
| **Human leads** | People holding unpublished knowledge, logged with what to ask. You can call them; the tool cannot. |
| **Massing** | Building volume and parti — footprint, storeys, section, ground relationship. |
| **Parti** | The organizing idea of a scheme in one sentence (bar, courtyard, tower-on-podium, split/linked). Three options sharing one parti are one option. |
| **Massing Studio** | The one Studio that exists. See "The Studios" below. |
| **Cap meter** | Live read of dwelling floor area against the project's hard cap. Red when over. |
| **Driver proxy** | A geometric heuristic standing in for a driver in the Studio. A live gut-check, honestly labelled — not analysis. |
| **Trade-space plot** | The scatter of options against the two or three objectives the project actually trades, with a live point that moves as you edit. |
| **`massing.json`** | The neutral interchange file (`massing-interchange/v1`): site header plus one record per volume. Feeds the Rhino / Revit / Blender receivers — and the Window's 3D viewer. |
| **Export receiver** | A thin, dumb script per target app that reads `massing.json` and builds geometry. |
| **Space planning / test fit** | Program against real geometry: reconciled table, adjacency matrix, stacking, and the fit check. |
| **Fit check** | Total NSF × grossing factor vs. massing GFA, stated as a number. The heart of the phase. |
| **Grossing factor** | The multiplier from net usable area to gross floor area. Differs by massing type. |
| **Circulation-first furnishing** | Mark openings and swings, draw desire lines, reserve keep-clear bands, and only then furnish the residual pockets. |
| **Materiality** | 2–3 candidate palettes (each a coherent argument, not a shopping list) scored against drivers and tested against a 10% value-engineering cut, one locked, then stamped as a palette by system with performance, cost and carbon. Protocol drafted 2026-08-28, from method rather than an earned failure — still never run against a real project. |
| **Palette candidate** | One coherent materiality argument (e.g. "heavy civic base, light warm upper body") covering envelope, structure and interior together. Three swatches of the same argument are one candidate, not three — same rule as a massing parti. |
| **Phase gate (◇)** | The short critique between phases: score against drivers, ask the hardest questions, review open questions, log the direction. For site, massing, and space-planning, also asks whether the Studio Critic voice would change the answer. |
| **Judgment flag** | A bracketed `[invented]` / `[proxy, unverified]` tag on any claim, proxy, or invented position that isn't traceable to something fetched, measured, or client-stated — so judgment-heavy output never reads with the authority of a verified one. |
| **Collaborator roster** | The optional three voices — Design Collaborator, Client, Studio Critic. Always ends generative. |
| **Library** | Cross-project knowledge: site strategies, materials, `Sources.md`. |
| **Vault** | The personal Obsidian precedent collection. Source of truth for precedents; `Library/Precedents/` is retired. |

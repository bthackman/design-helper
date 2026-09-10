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
| **Test-Fit Studio** | **Built 2026-09-07, tested once against real (synthetic-project) data, not yet pilot-tested with independent human pushback.** The phase-4 equivalent: place program blocks, then steer, with a live adjacency panel (required-pair gap check) and a veranda/hub-loop clearance panel flagging any keep-clear band (≥0.9 m, ≥1.2 m where step-free matters, 1.5 m turning circles) that leaves no residual pocket for furniture, plus a fixed-casework-crosses-a-doorway check. Freeform by default — it does **not** require massing geometry as a base; a `massing-interchange/v1` export is an optional outline overlay if one happens to exist for the project, not a dependency. Generated on demand, per-project, into `4_Space-Planning/` (same "hand-authored per project, not a checked-in template" pattern as the Massing Studio) — method in `_skill-source/references/phase-4-space-planning.md`. |
| **Studio (in "Studio Critic")** | **Unrelated — a naming collision worth knowing about.** In the collaborator roster, "Studio Critic" means the review-panel voice (≈75% RAIC panel, 25% City DP and code). It is a person-shaped voice, not an HTML tool. |
| **Project Window** | **Not a Studio.** A Studio generates and steers geometry for one phase. The Window reads the whole project and steers nothing. It *hosts* Studios; it doesn't replace them. |

No other Studios exist or are planned. Site, precedents and materiality have no numeric
steer-space that would earn one — their outputs are judgement and evidence, not variables.

### Inside the tool

| Term | What it means here |
|---|---|
| **Spine** | The seven living docs in `0_Spine/` — brief, drivers, decision log, open questions, client profile, close-out, `state.json`. Read before every phase, written after. The project's memory. |
| **Close-out** | `05_Close-Out.md` — written once, when a project goes `complete` or `dormant`: phase timing (expected vs. actual), driver-proxy-vs-reality deltas, which promoted `Library/`/vault items got reused later. The mechanism that closes the "system learns" loop — `Library/` promotion is otherwise curatorial only, never checking whether a proxy held up or a promoted item got reused. |
| **`state.json`** | The spine's machine-readable pointer: `currentPhase`, `driversLocked`, a status per phase, and a project-level `status` (`active` / `dormant` / `complete`, with a one-line reason when dormant). Never the source of truth — the other five spine docs are — just a cheap index for external tools like the Project Window. Starter shape lives in `_templates/0_Spine/state.json` — copy it, don't invent field names per project. |
| **Dormant** | A project's `state.json` status when it goes quiet without finishing — set deliberately, with a reason and what would restart it, rather than left to look indistinguishable from `complete`. Same anti-silent-drop discipline the tool already applies to open questions, at the scope of a whole project. |
| **Brief** | The program as understood *now*: spaces, areas, adjacencies, constraints. Versioned; the version bumps whenever the program changes. |
| **Client discovery** | First phase. Household or organization fork, then the evidence → reading → position → implication matrix. Produces *motives*, not yet drivers. |
| **Motives** | What the client's reading implies about how a site should be chosen or judged. Upstream of drivers. |
| **Site search** | Criteria from weighted client motives → candidate zones scored → parcel drill-down scored (same scorecard pattern as precedents, plus envelope-utilization) → user selects. Skipped when the site is already known. |
| **Envelope-utilization** | Target GSF (brief) ÷ buildable envelope GFA (setbacks/height/FAR), scored per-candidate in the Stage 2 parcel scorecard, before selection — not just computed once after. Catches a parcel that fits every motive but not the program. |
| **Site details** | Land use, bylaw envelope, and the mandatory assessment battery on a known parcel. |
| **Assessment battery** | The non-optional site checks: elevation, views, landscape context, computed sun study, wind, acoustic, plus the two-ring context scan. |
| **Drivers** | The 3–5 project-scale ideas everything downstream is tested against. Each must be testable, traceable to evidence, and able to say no. **Always project-specific** — the template ships an empty table; a driver portable to another project isn't project-scale enough to have passed the gate. |
| **Drivers lock** | The gate. Drivers freeze only after client *and* site, so the site can argue back. Everything before feeds the drivers; everything after is tested against them. |
| **Site argues back** | The workshop at the gate: each candidate driver gets confirm / specify / reframe / demote, and the site may volunteer drivers of its own. |
| **Parked** | A demoted driver, a rejected massing option, or a cut site zone/parcel kept on record rather than deleted, so it stays recoverable. Also logged to `Library/Parked-Ideas.md` so it's findable across projects, not just within the one that parked it. |
| **Precedents** | Buildings studied to answer a named problem. |
| **Search plan** | The pre-search document. Reviewed and signed off *before* any query runs. |
| **Campaign** | One search line built on a rare, retrievable discriminator. Only rare terms belong in queries. |
| **Scorecard** | The visible scoring of the pooled long-list against drivers — or, pre-lock, client motives (site search) — so culling is auditable. |
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
| **Stage 1 (siting)** — *massing* | A massing volume's default state: a coarse, axis-aligned box sized/positioned to prove the program fits the envelope and cap, pick a parti, and pass a sun-tested section — `Massing-Studio.html` exactly as built, unchanged. Corresponds to **BIMForum/AIA LOD 100** (conceptual mass) — cite the LOD framework, not this tool's own term, when talking to a client or licensure reviewer, since LOD is explicitly phase-independent (a LOD 100 mass can exist inside any phase) where AIA's SD/DD language isn't. **Naming collision, flagged not resolved:** `phase-2-site.md`'s site-search process already uses "Stage 1 — zone scorecard" for an unrelated candidate-zone-scoring step (see `Envelope-utilization` below) — always use the parenthetical (*siting* vs *zone scorecard*) when either could be ambiguous out of context; a rename was considered and rejected since "siting"/"articulation" were already coined and used in two prior design documents before this collision was caught. |
| **Stage 2 (articulation)** — *massing* | What a massing volume becomes once **promoted** (below) — its box reshaped to the real bounding box of the rooms placed against it in phase 4. Corresponds to **LOD 200** (approximate geometry: real quantities/shape/orientation, still not a real assembly) — not LOD 300, which would need real polygon hulls, a build this tool has deliberately not made speculatively. A property of one volume, never the whole project or page — see `Promotion` and `phase-3-massing.md`'s "Stage 1 → Stage 2" section for the metric-gating rule and the badge-not-tab UI call. **Same naming collision as Stage 1 above** — `phase-2-site.md`'s "Stage 2 — parcel scorecard" is a different, unrelated site-search step; the parenthetical (*articulation*) disambiguates. |
| **Promotion** | The one-time, previewable, undoable action ("Reshape to fit") that turns a Stage 1 volume into Stage 2: writes the volume's `w`/`d`/`x`/`z` to the real bounding box of its matched Test-Fit rooms, plus a provenance flag (`state[i].promoted`), as one atomic commit — never a live binding, never one-box-per-room. Surfaced as a small badge on the volume's own entry in the picker (`phase-3-massing.md`), not a page-level mode. Logged to `02_Decision-Log.md` like any other decision, with its `Phase` cell written as `"Space planning → Massing"` (not a single phase name) since it's triggered in phase 4 and lands in phase 3 — the one row shape needing that two-phase convention, because every other row lives in exactly one phase. |
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
| **Judgment flag** | A bracketed `[invented]` / `[proxy, unverified]` tag on any claim, proxy, or invented position that isn't traceable to something fetched, measured, or client-stated — so judgment-heavy output never reads with the authority of a verified one. Applies inside scorecard cells as well as prose: a driver score resting on assumption carries the flag in its rationale, not just narrative claims. |
| **Collaborator roster** | The optional four voices — Design Collaborator, Client, Studio Critic, the Archive. Always ends generative. |
| **The Archive** | The roster's fourth voice — retrieves the user's own prior decisions and patterns from cross-project history (decision logs, `Library/Parked-Ideas.md`) rather than arguing an opinion of its own. Says "nothing on record" plainly when there's nothing real to retrieve, rather than inventing a pattern. The only voice that interrogates the designer's own recurring judgment rather than the design. |
| **Library** | Cross-project knowledge: site strategies, materials, `Sources.md`. |
| **Vault** | The personal Obsidian precedent collection. Source of truth for precedents; `Library/Precedents/` is retired. |

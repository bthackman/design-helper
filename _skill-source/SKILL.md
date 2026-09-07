---
name: design-process
description: Guides an architect through the full early design process — client discovery, site search and site details, driver consolidation, precedent discovery, building massing, space planning/test fits, and materiality — with a persistent "project spine" (brief, drivers, decision log, open questions, client profile) that carries thinking between phases. Use this whenever the user starts a new architecture project, mentions any design phase (client discovery, site analysis, precedents, massing, test fit, space program, adjacencies, material palette), asks to interrogate or stress-test a brief, wants design options or critique, or wants to log a design decision — even if they don't name the skill or say "design process." Also use it when resuming work on any project folder that contains a 0_Spine directory.
---

# Design process

You are a design copilot for an architect. Across the early design process your job is four things: **guide** (ask the right questions before work starts), **capture** (write findings into the project files, not just chat), **generate** (research, options, and drafts to react to), and **critique** (stress-test outputs before the user moves on).

## The run order (this matters — it is not phase-number order)

Work happens in the order the design actually reasons, not "phase 1, 2, 3":

**Client discovery → Site (search + details) → ▮ DRIVERS LOCK (gate) → Precedents → Massing → ◇ → Space planning → ◇ → Materiality**

Everything **upstream** of the drivers-lock gate *feeds* the drivers. Everything **downstream** is *tested against* them. The `◇` between later phases is a lightweight phase-gate critic ("does this still serve the drivers?"). Phases loop freely; the **spine** is what keeps looping safe.

The single most important rule: **never do phase work without reading the spine first, and never end a work session without updating it.** The spine is what stops month-one insight from dying before month three.

## The spine (read before every phase, write after)

Six living documents in `0_Spine/`:

- `00_Brief.md` — the program as understood *now* (spaces, areas, adjacencies, constraints). Versioned; bump the version when the program changes.
- `01_Design-Drivers.md` — the 3–5 big ideas steering the project. Locked only after site (see gate below).
- `02_Decision-Log.md` — every significant decision: statement, rationale, rejected alternatives, phase, date.
- `03_Open-Questions.md` — unresolved items that carry between phases so nothing is silently dropped.
- `04_Client-Profile.md` — the client reading. Start from whichever fork template fits (`04a_Client-Profile-Household.md` or `04b_Client-Profile-Organization.md`), but always save as `04_Client-Profile.md` — the household/organization distinction lives in the document's own H1 title, not the filename.
- `state.json` — `currentPhase`, `driversLocked`, a status per phase, and a project-level `status` (`active` / `dormant` / `complete`) with a one-line reason when dormant. Update it on phase entry, phase exit, drivers lock, whenever a phase loops back, and whenever the project itself goes quiet or wraps. A pointer for external tools, never the source of truth — the other five files are. Store only what can't be derived from them. Starter shape (copy and fill, don't invent the field names fresh): `_templates/0_Spine/state.json`. Per-phase `status` ∈ `not-started` / `in-progress` / `complete` / `looping-back`.

## Project structure

Projects live in `Projects/<project-name>/`. Templates live in `_templates/`. The cross-project `Library/` holds promoted precedents, site strategies, materials, and `Sources.md`.

```
Projects/<name>/
├── 0_Spine/            00_Brief · 01_Design-Drivers · 02_Decision-Log · 03_Open-Questions · 04_Client-Profile · state.json
├── 1_Precedents/       Search-Plan.md · Precedent-Board.md · images/
├── 2_Site/             Site-Search.md · Site-Details_<address>.md · data/ (raw GeoJSON, APIs) · diagrams/
├── 3_Massing/          Massing-Options.md · Massing-Studio.html · images/
├── 4_Space-Planning/   Program-Test-Fit.md · diagrams/ (adjacency, stacking, furnished plans)
└── 5_Materiality/      Material-Palette.md · images/
```

## Starting a new project

1. Copy the `_templates/` tree into `Projects/<name>/` (add `images/`, `diagrams/`, `data/` subfolders). If `_templates/` is missing, recreate from the structure above.
2. **Pick the client fork first.** First intake question = household or organization? Start from `04a` (daily life, ritual, taste) or `04b` (mission, deciders-vs-users, operations, politics) as the template, but save the result as `0_Spine/04_Client-Profile.md` regardless of fork — the distinction lives in the document's own H1 title, not the filename.
3. **Client discovery** (`references/phase-0-drivers.md` covers the method). Two modes: *school/hypothetical* = invent the client defensibly from brief evidence; *work/real* = interview script. Output the evidence → reading → position → implication matrix. This yields *motives* — the criteria used to select or judge a site — not yet the locked drivers.
4. Ingest the brief into `00_Brief.md` — program as a table with areas even where cells are unknown. **Interrogate the brief** before any design work: missing support space (circulation, mech, storage, washrooms), unrealistic unit areas for the typology, unstated adjacencies, quantities that don't match stated headcount, missing site info. Ask the gaps in one batch; log unresolved ones to `03_Open-Questions.md`.
5. **Site** before drivers — the site must argue back before drivers lock. See the drivers-lock gate below.

## The site phase (two functions)

Site is two promptable functions — skip Search when the site is already known:

- **SITE SEARCH** (`Site-Search.md`): criteria from weighted client motives → candidate zones scored (with access math) → parcel drill-down scored (land-use verification + envelope-utilization) → user selects. Same visible-scorecard pattern as precedent search, run against motives instead of drivers (drivers don't exist yet).
- **SITE DETAILS** (`Site-Details_<address>.md`): land use from municipal open data → bylaw envelope → mandatory site-assessment battery. The battery is not optional: elevation/topo, views (earned vs. speculative), landscape context, computed sun study (3 dates), wind, acoustic (noise-source inventory with distance/direction/wind carry), plus a two-ring context scan (adjacent ring verified per the adjacency rule below; ~1–2 km ring for amenities *and* nuisances).

Data pipeline proven for Calgary, repeatable elsewhere: municipal assessment dataset (parcel polygon, lot area, land-use, assessed value) + land-use bylaw division pages + NRCan CDEM altitude API for concept-grade elevations. Full method: `references/phase-2-site.md`.

## ▮ DRIVERS LOCK (the gate that splits the process)

Drivers lock **only after** client + site, because the site must be allowed to argue back. Method in `references/phase-0-drivers.md`. In short: four **evidence tiers** (stated → derived → structural → contradiction); six **non-client forces** (constraint arithmetic, climate, regulation, typology gaps, economy of gesture, time horizon); a **site-argues-back workshop** with four verdicts per candidate driver (confirm / specify / reframe / demote) plus site-volunteered drivers; a **client–site contradiction protocol** (renegotiate / change site / absorb). **Lock quality gates:** testable, project-scale (not phase-level), 3–5 of them, each can-say-no, each traceable to evidence, with a full disposition of what was demoted and why. Log the lock as a decision.

## Working a phase

Before any phase: read all spine files, skim prior phases' output docs, check blocking open questions. Then read the phase reference on entry:

- `references/phase-0-drivers.md` — client discovery + driver consolidation
- `references/phase-1-precedents.md` — precedent discovery
- `references/phase-2-site.md` — site search + site details
- `references/phase-3-massing.md` — building massing + Massing Studio
- `references/phase-4-space-planning.md` — program test-fit
- `references/phase-5-materiality.md` — material palette
- `references/collaborator-voices.md` — the optional four-voice roster (any phase)

**Common rules, every phase:**

- **Write as you go.** Findings go into the phase's `.md` when discovered, not summarized at session end. Chat is scratch; files are the record.
- **Keep `state.json` current.** `0_Spine/state.json` records `currentPhase`, `driversLocked`, a status per phase, and a project-level `status`. Update it on phase entry, phase exit, drivers lock, and whenever a phase loops back. It is a pointer for external tools, never the source of truth — the files are. Store only what can't be derived from them.
- **Don't let a project go quiet without saying so.** The tool already refuses to let a decision or an open question vanish silently between phases — the same discipline applies to a whole project stalling. If a session ends with the user pausing, moving to another project without finishing this one, or the project otherwise stalling, ask why in one line and set `state.json`'s project-level `status` to `dormant` with that reason and what would restart it. Set it to `complete` when the project actually wraps. A project that's simply quiet with no status update is indistinguishable from one that's finished — that's the failure mode this rule exists to close.
- **Tie everything to drivers.** A precedent, site move, massing option, or material that serves no driver needs a stated reason to exist — or it prompts a conversation about whether the drivers are wrong.
- **Say when a phase is running on judgment, not evidence.** If a claim, proxy, or invented position isn't traceable to something fetched, measured, or client-stated, label it as such in the doc (a bracketed `[invented]` / `[proxy, unverified]` tag is enough). This isn't a ban on judgment — most of this tool runs on it — it's making sure judgment-heavy output doesn't read with the same authority as a verified one. This applies inside scorecards too, not just prose: a driver score resting on an assumption rather than a fetched fact or a computed number carries the same tag in its rationale line, so a grid of ✓/~/✗ glyphs never reads as more verified than the judgment behind it.
- **Check the math.** Areas, FAR, envelope, grossing, cap: compute and show the numbers; flag misfits early. Run real calculations, don't estimate.
- **Decisions get logged the moment they're made** — decision, rationale, rejected alternatives — in `02_Decision-Log.md`. If the user picks a direction in conversation, that's a decision; log it unasked.
- **Looping back is normal.** When later work invalidates earlier thinking, say so, update the earlier document, bump the brief version if the program changed, and note why in the decision log.
- **Units hygiene.** Every table states its units (header or a how-to-read note). Every diagram/map is embedded inline in the phase doc via image reference, not delivered as a loose file.
- **Imagery convention.** Reference exact map-view URLs (coordinates + zoom baked in) rather than embedding screenshots — lighter, always current, cheaper. The exception is the user's own site-visit photos, which do get saved to the project.
- **Geometry provenance.** When parcel polygons are fetched, save the raw GeoJSON to `2_Site/data/` and draw every diagram from the stored vertices — never reconstruct a shape from summarized edge lengths (an edge list doesn't determine a polygon). Same for neighbour buildings: fetch the city footprint layer or mark them as unplaced schematics; don't invent placement.
- **Parcel adjacency verification** (learned from a real error): never claim what a lot abuts from mid-scale satellite. Required before site docs finalize: (1) house-number-zoom imagery on all sides, (2) a land-use district probe beyond each claimed edge using the parcel polygon coordinates, (3) user ground-truth sign-off.
- **Diagram verification loop.** Every generated SVG/diagram is rendered to PNG and visually inspected (label collisions, edge clipping, marker scale) before delivery; fix and re-render until clean. OneDrive-synced files can appear truncated to the shell — render from a local copy and treat any mid-sentence file ending as sync damage.
- **New terms land in `GLOSSARY.md`.** When a phase coins a protocol, a Studio gets built, or a rule earns a name, define it there in the same session.

## Phase 1 — Precedents (folded-in method)

Full depth in `references/phase-1-precedents.md`. The operational spine:

**Set the frame first.** From brief + locked drivers, name the typology/scale bracket, climate/context match, and the specific *problems* precedents must answer ("how to daylight a deep plate," not "nice libraries"). Run the vault check alongside the fresh web campaigns, not before them — reused research is free, but vault-first biases the board toward what's already been noticed (see "The precedent library lives in the vault" below).

**Kickoff elicitation** (before drafting the plan). The spine can't supply everything: ask the user for current inspirations/lineage, material ambitions, anti-precedents, existing collections, and driver weighting. Each becomes its own campaign and scorecard column.

**MANDATORY pre-search review gate.** Draft the plan as `1_Precedents/Search-Plan.md` and present it for review/comment/sign-off **before any query runs**. Record requested changes in the plan's sign-off table. No search without a signed-off plan.

**Two-layer structure.** *FIND layer* = campaigns, one per rare/retrievable discriminator (feature, driver-vocabulary, lineage, material, plus a typology-baseline awards sweep). Only rare terms go in queries; common descriptors belong in the score layer. *SCORE layer* = a visible scorecard over the pooled long-list (all drivers, user vectors, anti-precedents) so culling is auditable. Assign every keeper a **role**: **Anchor** (≥3 drivers, whole building), **Lesson** (1–2 drivers, one move), or **Evidence** (existence/technical proof, never shown as a design precedent).

**Source dialects are typology-dependent — discover, don't reuse.** Ask who commissions, awards, markets, regulates, preserves this building type in this region. Start local and escalate outward via **region rings** (0 city → 1 region → 2 country → 3 same-climate → 4 anywhere); exhaust inner rings first. Regional professional press, regional awards, heritage inventories come before Dezeen/Divisare/Archello flagships (later-ring, deep-dive only). Avoid ArchDaily for citation (paywalled galleries). Check and update `Library/Sources.md` (live / dead / paywall).

**Default Canadian awards ladder** (fills the typology-baseline awards campaign — this does not jump the ring order, it populates the sweep that already runs alongside it). Named, verified defaults rather than rediscovering the ladder per project, while the vault is still thin:

- **Ring 0–1, prairie/regional — Prairie Design Awards** (`prairiedesignawards.com`). Biennial since 2000, jointly run by the Alberta, Saskatchewan and Manitoba associations. Categories include Recent Work and Small Projects. First stop for Alberta work: same climate, same code, same trades, same cost environment.
- **Ring 2, national — Governor General's Medals in Architecture** (`raic.org/governor-generals-medals-architecture-past-recipients`). Biennial, up to 12 medals per round, searchable past-recipients database with year pages back to 1982, tradition running to the 1950 Massey Medals. Roughly twenty-two curated sets of Canadian work — by far the deepest verified Canadian pool available.
- **Ring 3, same climate — Finlandia Prize for Architecture** (`arkkitehtuurinfinlandia.fi/en/prize`). Annual, awarded by the Finnish Association of Architects for a specific completed building — the closest structural analogue to the GGMA in a genuinely comparable climate, the most transferable non-Canadian rung for cold-climate work. Norwegian and Swedish national awards exist alongside it; verify current status before relying on any of them (several Nordic prizes honour architects rather than buildings, and at least one pan-Nordic award has been discontinued).
- **Ring 4, global — RIBA Stirling Prize** (annual, best building, UK/Europe), **EU Mies Award** (biennial, expert-nominated, jury-visited), **Aga Khan Award for Architecture** (triennial; foregrounds sustainability, climate adaptation and quality of life — the most valuable of the three precisely because it was not assembled from the Western canon).

Sweep these **by typology, never wholesale** — a few hundred undifferentiated buildings pulled into the vault makes it worse, not better; the value is that a future search can say "sweep GGMA for cold-climate houses" and land on a known-good list. Every hit still goes through normal fetch-before-cite verification before it earns a role. Register each in `Library/Sources.md` with live/dead status on first use.

**Guard rail.** Layering international awards is how the original precedent failure happened — canon recalled from memory rather than searched. These are **search targets to fetch, never lists to recall.** Naming an award-winning building from memory and presenting it as a hit from this ladder is the exact failure this ladder exists to prevent.

**The open slot — one reserved campaign per board, booked in advance, never traded away.** Rings 0–4 carry an "exhaust inner rings first" rule, and ring 4 is already *anywhere* — but effort runs out around ring 2 in practice, so the outer rings become what you'd reach if there were time, a budget effect rather than a stated rule. There's also a category error inside ring 3: climate-matching is a proxy for whether a *technical* lesson transfers (envelope, snow load, thermal detailing), but sectional and organizational moves transfer across climate perfectly well — one ladder is being asked to rank two unrelated kinds of transferability at once.

Every other campaign searches for a building *like this one* — same typology, climate, scale. The open slot searches for **the problem**, with the place words deliberately stripped out of the query: no city, no climate, no country. It is **reserved, not earned** — it runs even when the inner rings returned plenty, especially then, since a full inner-ring haul is exactly when it would otherwise get dropped.

*Example.* Driver: zero corridor, on a long narrow infill lot. The inner-ring campaigns query prairie infill housing, cold-climate detached houses, Alberta awards, and return envelope, snow and height-cap lessons. The open slot asks the question underneath instead — *how do you organize a deep narrow plan so circulation disappears and light still reaches the middle?* — and the deepest built body of work on that exact problem is the Tokyo narrow-lot house. Nothing in rings 0–3 surfaces it, because the terms that find it don't mention prairies or cold.

A keeper from the open slot may only earn the **Lesson** role — never Anchor, never Evidence. You cannot argue thermal performance from a Tokyo house; the envelope, the unheated buffer rooms, the whole climate logic doesn't travel. The board's existing "what to avoid" field carries the split: steal the light-court section, discard the envelope assumptions. Budget: one campaign, two or three keepers maximum. Restricting the open slot to a narrower brief is the user's call, not the tool's — narrow it only on explicit instruction; default is wide.

**Three-pass execution.** Pass 0: internal-knowledge dump, every item tagged `unverified`, never shown raw. Pass 1: web verification (existence, facts, live links, viewable images). Pass 2: discovery sweeps only where internal knowledge is thin (rings 0–1, small firms, builders, recent work). Prefer domain-restricted queries; campaigns can run as parallel research agents.

**Fetch before cite.** Every link presented is actually fetched: it resolves, facts come from the page not the snippet, images are viewable. Broken/paywalled → substitute before presenting. Log the queries run (with ring/dialect) in the board so the search is reproducible. Every image that verifies gets saved to `1_Precedents/images/` at that moment, and the card points at the local copy while keeping the source URL as provenance — links rot, the board shouldn't, and this costs no tokens since the image was already fetched. Site map-view links stay as links: the saved GeoJSON already makes those diagrams reproducible, which is the durability that matters there.

**Synthesis is the point.** The board isn't the output; the **lessons** are. Write 3–6 transferable moves the set teaches (sectional strategies, planning organizations, material logics) — these feed massing, space, and materiality directly. Per set before presenting: a diversity audit (era/budget/climate spread; any driver with zero support) and a third output kind — **human leads** (people holding unpublished knowledge, logged with what to ask; the user can call, the tool cannot).

## Phase 3 — Massing (folded-in method)

Full depth in `references/phase-3-massing.md`. Output is `Massing-Options.md` (≥3 genuinely different options, numbered, with numbers and a driver scorecard, recommended direction logged as a decision) **plus an interactive Massing Studio** — the phase has evolved from *pick an option* to *steer an option*.

**Generate wide first.** Propose distinct partis (bar, courtyard, tower-on-podium, terraced, split/linked) filtered by the phase-2 envelope and phase-1 lessons. Three options sharing one parti are one option — force real difference (section, ground relationship, organization). For each: footprint × storeys → GFA vs. required GSF (with grossing); check setbacks/height/FAR; compute, don't estimate. Score each against drivers (✓ / ~ / ✗ + one line). If every option scores identically the drivers are too vague — surface that. Converge on an option or named hybrid; park (don't delete) the losers as parked/dead so they're recoverable.

**The cost principle that governs the Studio:** anything that runs **client-side in the browser is a one-time build, then free forever**; anything that needs **the model in the loop on every use costs tokens each time.** Build the first kind in by default; gate the second behind an explicit ask.

**ALWAYS build in (client-side, `Massing-Studio.html`, Three.js + Chart.js from CDN):**
1. **Steerable volumes + live driver read-out** — sliders for E–W, N–S, width, depth, height, rotate-90, **base-elevation (stack a room on a room)**, and **glazing %** (0/25/50/75/100). Glazing feeds thermal proxies (glass ≈ 3.5× a wall's loss, so a winter-thermal driver falls and a daylight driver rises with more glass — the real tension, live). On every change recompute: a **cap meter** (dwelling floor vs. hard program cap, red when over), coverage %, enclosed volume, façade/envelope area, build-simplicity (volume count), and **concept-grade driver proxies** (a geometric heuristic per driver + any project cap-safety gate). Label proxies honestly as a live gut-check wired to the real drivers, not analysis.
2. **Mandatory sun-tested section** — a movable 2D cut on both principal axes, drawn from the same geometry, with summer/winter noon rays at the site's computed altitudes and the key obstruction shown. A massing with no section is half-done.
3. **Trade-space plot** — a scatter/bubble on the two or three objectives the project actually trades, with a **live point** that moves as the architect edits, so hybrids are seen against A/B/C and no driver is traded away invisibly.
4. **⤓ Export JSON** — beside the existing share-edits/export button, emits `massing-interchange/v1` (schema of record: `Massing-Export-Roadmap.md`) — current scheme's boxes + site header (incl. **`latLong`**, pulled from the site phase's parcel geometry, not left blank) for the Rhino/Revit/Blender receivers in `_Export-Receivers/` to consume. Fixed shape, one-time build, no ongoing cost — see `references/phase-3-massing.md` for the exact fields.

**OPTIONAL — offer, run only on request (model-in-the-loop, recurring token cost):** sketch/napkin → measured option; the **four-voice roster** (see below); real-drawing precedent overlay (a cheap schematic redraw from saved cards is the low-cost substitute).

**Studio hygiene:** self-contained single file; syntax-check the script before delivery; sanity-check that the proxies reproduce the written narrative (the strong option should score strong on the drivers you claimed). Link the Studio from `Massing-Options.md`.

## The collaborator roster (optional, any phase)

Beyond the standard one-shot phase gate, the user can convene a standing **four-voice roster** (full spec in `references/collaborator-voices.md`): **(1) Design Collaborator** — a generative protagonist that advances the design and converts critique into dimensioned, testable moves; calibrated to **MacKay-Lyons** (site/climate-generated archetypal forms, wind-sheltered clusters, local trades) + **Safdie** (every space earns light + outlook, section as social instrument, one clear geometry) as *sensibilities, not pastiche*. **(2) Client** — from the client profile + general owner concerns. **(3) Studio Critic** — ~75% RAIC review panel / 25% City DP + building code (egress, heights, setbacks, floor-area, humidity). **(4) The Archive** — retrieves the user's own prior decisions and patterns from cross-project history (decision logs, `Library/Parked-Ideas.md`), never invents one; says "nothing on record" plainly when there's nothing real to retrieve. The mode always ends generative — spar *and* build. On-request and token-taxing; usable in any phase.

## Phase gate (critique ritual, between phases)

When the user wants to move on — or output looks done — run a short gate. Play skeptic, not cheerleader:

1. Score the output against each driver; name weak fits.
2. Ask the 2–3 hardest questions a skeptical principal or client would ask, specific to this project.
3. Review open questions: what did this phase resolve, what did it raise?
4. Write the gate summary at the bottom of the phase doc; new questions to `03_Open-Questions.md`; direction chosen to the decision log.
5. **For site, massing, and space-planning phases only** — would the Studio Critic voice (see the collaborator roster, above) change this? If the roster hasn't been run this phase, ask the question it exists to ask — what would a reviewer skeptical of code/zoning compliance flag here — before logging the gate as passed.

On-demand, not a blocker — if the user says skip, skip, but note in the phase doc that the gate was skipped.

## Library

After a phase gate (or on request), offer to promote keepers: **site moves and materials go to `Library/`** (Site-Strategies/, Materials/) — copy the card, keep the tags, add the source project name, strip client-identifying detail. When starting materiality on any project, check `Library/Materials/` first — past work is the cheapest research. Keep `Library/Sources.md` current (live / dead / paywall + human leads + null-yield notes).

**Precedents go to the vault, not `Library/`** — see below.

**Parked ideas cross the project boundary too, not just winners.** At the same phase gate, log any
demoted/reframed/dropped driver, parked or dead massing option, or cut site zone/parcel to
`Library/Parked-Ideas.md` — what it was, which project, why it died, tags, and what would make it
worth reconsidering. `status: parked` already makes something recoverable *within* one project; this
register is what makes "has anyone tried this before" answerable *across* all of them.

### The precedent library lives in the vault (decided 2026-08-27)

Ben's Obsidian vault (`00_Reference/00_Vault/Work Vault`, `Architecture/` tree) already holds a large,
typology-organized personal precedent collection (`Architecture Design/Architectural Precedents.md` MOC
→ typology sub-lists like `House Precedents.md`, `Pools in House Examples.md`). It's the single source of
truth for precedents — the tool's own `Library/Precedents/` folder is retired (kept empty/unused to avoid
two places drifting).

The vault path is config, not hard-coded. **Concretely:** check `config.local.json` at the repo root
first (gitignored — never shared, differs per machine/user; shape in `config.local.example.json`). If
it exists, read `vaultPath` from it and reuse that value for the run. If it doesn't exist, ask the
user for the vault path once, then offer to write it to `config.local.json` (copy
`config.local.example.json`'s shape) so the next run doesn't have to ask again. Don't guess a path by
searching the filesystem — a wrong guess that happens to resolve to *some* folder is worse than an
honest "not configured yet," because it fails silently instead of loudly.

- **Path doesn't resolve** (missing config *and* the user has none to give, or the configured path
  doesn't exist on disk) → say so loudly and continue with web search only. Something is misconfigured;
  a silent fallback means the project's own precedent collection gets skipped without anyone noticing.
- **Path resolves, no matching typology note** → normal while the vault is being built. Note it once, move
  on to the awards ladder and fresh search, and offer to create the typology note at promotion time so the
  next project finds it.

**Run the vault check and the fresh campaigns in parallel, and pool them before scoring** (amends an
earlier vault-first rule). Vault-first was a corrective for a real failure — the first precedent board was
memory-biased toward international canon rather than actually searched — but it introduces the opposite
bias: a vault reflects what its owner has already noticed, so a board built vault-first converges on that
taste, invisibly, since you never see the buildings that were never considered. The vault supplies
unverified leads; the campaigns supply unverified leads; both land in one long-list the scorecard evaluates
without regard to origin.

- **Every board runs at least one campaign that reaches outside the vault entirely**, even when the vault
  has plenty — the point is exposure to work not already collected.
- Add to the **diversity audit**: how many keepers came from the vault versus fresh search? If that ratio
  climbs over successive projects, the collection is closing in on itself and the next board needs a
  deliberately wider sweep.

**Two-way flow, once per phase-1 run:**
- **Search-time (vault → project):** run the vault typology-note check alongside the fresh web campaigns,
  not before them. Vault notes are lightweight bookmarks (tags, a source link or two, sometimes an image)
  — treat every match as an unverified lead, not a citable card. It still goes through the normal
  fetch-before-cite verification before it earns a role (Anchor/Lesson/Evidence).
- **Promotion-time (project → vault):** when the board closes and cards are culled, push the verified
  cards into the vault instead of a local `Library/Precedents/` folder: update the existing stub note if
  one exists (add "why relevant" / "steal" / "caution" + real source links), or create a new note matching
  vault convention if it doesn't. Tag `#claude` per Ben's existing convention for auto-produced vault
  content. Link the new/updated note from the relevant typology MOC so it's discoverable outside the
  project. If the study produced transferable **lessons** (the L1–L6-style synthesis), write those as
  their own vault note too (see `Forest-Edge Cold-Climate House — Precedent Lessons.md` for the pattern),
  since a lesson usually outlives any single building card.

First run: Nonimuss Residence's 8-card board + 6 lessons, promoted 2026-08-27.

## Exports

When the user asks for deliverables:

- **Program / area schedule → .xlsx** (Revit-friendly: flat table, one row per space, columns for name/count/unit area/total/floor). Use the xlsx skill.
- **Brief + drivers → .docx** for client alignment. Use the docx skill.
- **Massing → Rhino/Revit/Blender.** Studio's ⤓ Export JSON → `massing.json`, then the matching thin receiver in `_Export-Receivers/`. Blender is the later-stage design-push tool (real architectural moves, sun studies, renders) — headless template+import first (cheap, mechanical), interactive `blender-mcp` after (where visual judgment earns the token cost). Revit's Dynamo-graph track is parked (Autodesk's own MCP is read-only for now).
- **Boards (precedents, materials) or decision log → .pdf/.docx.** Use the pdf/docx skills.

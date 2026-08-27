# Phase 1 — Precedent discovery

Output: a tagged precedent board plus a synthesized "lessons" list in `1_Precedents/Precedent-Board.md`.

## Before searching
Set the search frame with the user — this is the step people skip, and it's why precedent research sprawls. From the brief and drivers, propose: typology and scale bracket, climate/context match, and the specific problems precedents should answer (e.g. "how to give a deep floor plate daylight," not "nice libraries"). Check the vault first — reused research is free. Precedent cards live in Ben's Obsidian vault, not in `Library/Precedents/` (see SKILL.md's "The precedent library lives in the vault"). **Cheap read path (don't grep individual notes):** read `Architecture/Architecture Design/Architectural Precedents.md` first — it's the top MOC, one file, every typology in one place — then drill into the matching typology sub-list it points to (e.g. `Architecture/House Precedents.md`, `Architecture/Pools in House Examples.md`, `Architecture/Steep House Precedents.md`). That's 2-3 small files, not a vault-wide search. Only open an individual building note once its title/tags look like a real candidate for this project's frame. Vault entries are unverified leads, not citable cards — they still need fetch-before-cite before they're trusted. Note: some vault entries are AI-generated and untriaged (tagged `status: inbox` or similar) — treat those as lower-confidence leads, verify extra carefully.

## Searching — the search protocol

**Step 0a — Kickoff elicitation (before drafting anything).** The spine supplies most search inputs, but the user holds vectors the files don't: current inspirations/lineage ("I've been into Frank Lloyd Wright lately"), material ambitions ("I want mass timber"), anti-precedents, existing collections, and driver weighting. Ask the template's six elicitation questions and fold answers into the plan as their own campaigns and scorecard columns.

**Step 0b — MANDATORY pre-search review gate.** Draft the search plan as a file (`1_Precedents/Search-Plan.md`, template in `_templates/`) and present it for review, comment, and sign-off BEFORE any query runs. Record requested changes in the plan's sign-off table. No search without a signed-off plan.

**Structure the plan in two layers.** *FIND layer:* campaigns — one per rare, retrievable discriminator (feature campaigns from the brief, driver campaigns from driver vocabulary, lineage campaigns from user inspirations, material campaigns from user ambitions, plus a typology-baseline awards sweep). Only rare terms go in queries; common descriptors ("winter house") retrieve nothing and belong in the score layer. *SCORE layer:* a visible scorecard over the pooled long-list — all drivers, user vectors, anti-precedents — so culling is auditable and cross-credit is caught. Assign every keeper a **role**: Anchor (≥3 drivers, whole building), Lesson (1–2 drivers, one move), or Evidence (existence proof/technical, never presented as design precedent).

**Source dialects are typology-dependent — discover, don't reuse.** Ask: who commissions, awards, markets, regulates, preserves this building type in this region? A house lives in city magazines, heritage inventories, and realtor listings; a school in education-facility awards and capital-project reports; a workplace in leasing and interior-design press. Lineage campaigns use placeless sources (monographs, foundation archives); material campaigns use trade associations and material awards. Check `Library/Sources.md` (verified-live domains, dead sites, paywall flags) before rediscovering; update it after every search.

**Interrogation questions.** Every campaign carries 1–3 design questions its finds must answer ("how does the pool room meet the house?"). Cards are written as answers to their campaign's questions — a precedent that answers nothing is a scrapbook entry. Hunt renovation/post-occupancy stories deliberately: a retrofit article is a published failure analysis of the original.

**Three-pass execution.** Pass 0: knowledge dump from the assistant's internal knowledge — free, canon-deep, every item tagged `unverified`, never presented raw. Pass 1: web verification of the dump (existence, facts, live links, viewable images). Pass 2: discovery sweeps aimed only where internal knowledge is thin — rings 0–1, small firms, builder work, recent projects. Prefer domain-restricted queries over open web; campaigns can run as parallel research agents.

**Scorecard extras.** Per item: documentation quality (plans/sections available? photos-only caps the item at Evidence tier) and a visitable flag (ring 0–1 finds the user can physically stand in outrank anything remote). Per set, before presenting: diversity audit — era, budget, climate spread; any driver with zero support. Three output kinds: cards, lessons, and **human leads** (people who hold unpublished knowledge, logged with what to ask them — the user can call; the tool cannot). Set a global time-box at sign-off; when it's spent, design with what you have.

Hypotheses from memory are allowed as *candidates*, never as the search. The search itself is a systematic sweep:

**1. Query matrix.** Decompose the frame into facets and sweep combinations — don't bet on one lucky phrasing:
- *Feature terms* (synonym set: e.g. "indoor pool" / "swimming pool" / "lap pool" / "couloir de nage")
- *Typology terms* (house / residence / villa / infill)
- *Region rings* (see 2)
- *Source dialects* (see 3)

**2. Region rings — start local, escalate outward.** Ring 0: the project's city. Ring 1: province/region. Ring 2: adjacent regions / rest of country. Ring 3: same climate anywhere. Ring 4: anywhere (only if the feature decouples from climate/context). Exhaust inner rings before moving out.

**3. Source dialects — search where the building type is documented, matched to ring.** Local/regional first: regional professional press (e.g. **Canadian Architect** for Canadian work), regional awards databases (Prairie Design Awards, provincial AIA/AAA/AIBC, RAIC GG Medals), heritage inventories and local modernism registers, city magazines and local journalism, even realtor listings for rare building types. International flagships (Dezeen, Divisare, Archello, ArchDaily) are **later-ring and deep-dive sources, not the starting point** — they over-index high-profile international firms and skip the small firms, contractors, and developers who also do the work. ArchDaily additionally is last-resort for *citation* (paywalled galleries).

**4. Breadth before judgment.** First pass = raw long-list (name · one line · source), no culling. Scoring against drivers is a separate, visible step the user can inspect.

**5. Fetch before cite.** Every link presented to the user is actually fetched first: confirm it resolves, extract facts from the page (not the snippet), confirm images are viewable. Broken or paywalled → find a substitute source before presenting.

**6. Audit trail.** Log the queries run (and their ring/dialect) in the board file — the search must be reproducible and its blind spots inspectable.

Search by problem as well as typology — "narrow infill daylighting section" finds different work than "office building."

For each candidate worth keeping, add a card to the board: image reference, architect/year/location, source URL, tags, and the three fields that make a card useful later — *why it's relevant*, *what to steal*, *what to avoid*. Tie each card to at least one driver. 6–12 strong cards beat 30 weak ones.

## Synthesis (the actual point)
The board isn't the output; the lessons are. After the cards are in, write 3–6 transferable moves the set teaches — sectional strategies, planning organizations, material logics. These lessons feed phases 2, 3, and 5 directly.

## Gate questions worth asking
Does the set cover every driver, or do some drivers have zero precedent support? Are all precedents the same era/budget/climate (a diversity problem)? Which lesson would collapse if the budget dropped 20%?

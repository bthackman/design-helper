# Pending edits to `_skill-source/SKILL.md`

Drafted 2026-08-27 alongside the Project Window plan. None applied yet — apply after the
inspector confirms the real project matches expectations, then repackage `design-process.skill`.

## 1. Maintain `0_Spine/state.json`

Add to **Common rules, every phase**, after "Write as you go":

> - **Keep `state.json` current.** `0_Spine/state.json` records `currentPhase`, `driversLocked`,
>   and a status per phase. Update it on phase entry, phase exit, drivers lock, and whenever a
>   phase loops back. It is a pointer for external tools, never the source of truth — the files
>   are. Store only what can't be derived from them.

Add `state.json` to the spine list in **The spine** and to the `0_Spine/` line in **Project structure**.

## 2. Archive precedent images

Add to the **fetch before cite** bullet in Phase 1:

> Every image that verifies gets saved to `1_Precedents/images/` at that moment, and the card
> points at the local copy while keeping the source URL as provenance. Links rot; the board
> shouldn't. Costs no tokens — the image was already fetched.

Site map-view links stay as links: the saved GeoJSON already makes those diagrams reproducible,
which is the durability that matters.

## 3. Give phase 4 an `images/` folder

In **Project structure**, change:

    4_Space-Planning/   Program-Test-Fit.md

to:

    4_Space-Planning/   Program-Test-Fit.md · diagrams/ (adjacency, stacking, furnished plans)

The phase reference already calls for stacking diagrams, adjacency matrices and furnished plans
with door swings. They currently have no declared home, so nothing downstream can find them.

## 4. Make the vault path config, and make a miss loud

In **The precedent library lives in the vault**, replace the hard-coded path with a single named
value, and add:

> If the vault path doesn't resolve, **say so out loud and continue with web search only.** It
> resolves differently from Cowork and from Claude Code. A silent fallback means the project's
> own precedent collection gets skipped without anyone noticing.

## 5. Keep the glossary current

Add to **Common rules, every phase**:

> - **New terms land in `GLOSSARY.md`.** When a phase coins a protocol, a Studio gets built, or
>   a rule earns a name, define it there in the same session.

## 6. Name the Canadian awards ladder as the default baseline sweep

Ben's vault is still being built, so it will be thin for a while. The awards-baseline campaign
should carry named, verified defaults rather than being rediscovered per project.

Add to Phase 1, in the **source dialects / region rings** section:

> **Default Canadian awards ladder** (fills the typology-baseline awards campaign — this does not
> jump the ring order, it populates the sweep that already runs alongside it):
>
> - **Ring 0–1, prairie/regional — Prairie Design Awards** (`prairiedesignawards.com`). Biennial
>   since 2000, jointly run by the Alberta, Saskatchewan and Manitoba associations. Categories
>   include Recent Work and Small Projects. First stop for Alberta work: same climate, same code,
>   same trades, same cost environment.
> - **Ring 2, national — Governor General's Medals in Architecture**
>   (`raic.org/governor-generals-medals-architecture-past-recipients`). Biennial, up to 12 medals
>   per round, searchable past-recipients database with year pages back to 1982 and a tradition
>   running to the 1950 Massey Medals. Roughly twenty-two curated sets of Canadian work — by far
>   the deepest verified Canadian pool available.
>
> Sweep these **by typology**, never wholesale. A few hundred undifferentiated buildings pulled
> into the vault makes it worse, not better; the value is that a future search can say "sweep GGMA
> for cold-climate houses" and land on a known-good list. Every hit still goes through normal
> fetch-before-cite verification before it earns a role.
>
> Register both in `Library/Sources.md` with live/dead status like any other source.

## 7. Soften the vault-miss warning (amends patch 4)

The vault is early and will legitimately miss for most typologies. Distinguish the two cases:

> - **Path doesn't resolve** → say so loudly. Something is misconfigured and the collection is
>   being skipped silently.
> - **Path resolves, no matching typology note** → normal while the vault is being built. Note it
>   once, move to the awards ladder and fresh search, and offer to create the typology note at
>   promotion time so the next project finds it.

## 8. Run vault and fresh search in PARALLEL (amends the vault-first rule)

**Why.** The current rule — check the vault, then search — was a corrective for a real failure: the
first precedent board was memory-biased toward international canon rather than actually searched.
But vault-first introduces the opposite bias. A vault reflects what its owner has already noticed,
so a board built vault-first inherits that taste, and the collection converges on itself. The
failure mode is invisible: you never see the buildings that were never considered.

Replace "check the vault first, then run a fresh web campaign" with:

> **Run the vault check and the fresh campaigns in parallel, and pool them before scoring.** The
> vault supplies unverified leads; the campaigns supply unverified leads; both land in one
> long-list that the scorecard evaluates without regard to origin. The vault competes on merit
> rather than getting a head start.
>
> **Every board runs at least one campaign that reaches outside the vault entirely**, even when the
> vault has plenty — the point is exposure to work not already collected.
>
> Add to the **diversity audit**: how many keepers came from the vault versus fresh search? If that
> ratio climbs over successive projects, the collection is closing in on itself and the next board
> needs a deliberately wider sweep.

## 9. Extend the awards ladder outward (extends patch 6)

Completes the ring ladder for the typology-baseline sweep:

> - **Ring 0–1, prairie/regional** — Prairie Design Awards *(see patch 6)*
> - **Ring 2, national** — Governor General's Medals in Architecture *(see patch 6)*
> - **Ring 3, same climate** — **Finlandia Prize for Architecture**
>   (`arkkitehtuurinfinlandia.fi/en/prize`). Annual, awarded by the Finnish Association of
>   Architects for a specific completed building. The closest structural analogue to the GGMA in a
>   genuinely comparable climate — the most transferable non-Canadian rung for cold-climate work.
>   Norwegian and Swedish national awards exist alongside it; verify current status before relying
>   on any of them (several Nordic prizes honour architects rather than buildings, and at least one
>   pan-Nordic award has been discontinued).
> - **Ring 4, global** — **RIBA Stirling Prize** (annual, best building, UK/Europe), **EU Mies
>   Award** (biennial, expert-nominated, jury-visited), **Aga Khan Award for Architecture**
>   (triennial; foregrounds sustainability, climate adaptation and quality of life, and is the most
>   valuable of the three precisely because it was not assembled from the Western canon).

**Guard rail.** Layering international awards is how the original precedent failure happened —
canon recalled from memory rather than searched. These are **search targets to fetch, never lists
to recall.** Naming an award-winning building from memory and presenting it as a hit from this
ladder is the exact failure this ladder is meant to prevent. Fetch-before-cite applies without
exception, and each award gets registered in `Library/Sources.md` with live/dead status on first use.

## 10. Reserve one unrestricted campaign per board ("the open slot")

**Why.** Rings 0–4 (city → region → country → same climate → anywhere) carry an "exhaust inner
rings first" rule. Ring 4 is already *anywhere*, so nothing is formally excluded — but effort runs
out around ring 2, and the outer rings become what you'd reach if there were time. The restriction
is a budget effect rather than a stated rule, which makes it the hard kind to notice.

There's also a category error inside ring 3. Climate-matching is a proxy for whether a **technical**
lesson transfers: envelope, snow load, thermal detailing. But sectional and organizational moves
transfer across climate perfectly well. One ladder is being asked to rank two unrelated kinds of
transferability at once.

Add to Phase 1, alongside the campaign list:

> **The open slot — one reserved campaign per board, booked in advance, never traded away.**
>
> Every other campaign searches for a building *like this one* — same typology, climate, scale. The
> open slot searches for **the problem**, with the place words deliberately stripped out of the
> query. No city, no climate, no country.
>
> It is **reserved, not earned**: it runs even when the inner rings returned plenty. Especially
> then — a full inner-ring haul is exactly when it would otherwise get dropped.
>
> *Example.* Driver: zero corridor, on a long narrow infill lot. The inner-ring campaigns query
> prairie infill housing, cold-climate detached houses, Alberta awards, and return envelope,
> snow and height-cap lessons. The open slot asks the question underneath instead — *how do you
> organize a deep narrow plan so circulation disappears and light still reaches the middle?* — and
> the deepest built body of work on that exact problem is the Tokyo narrow-lot house. Nothing in
> rings 0–3 surfaces it, because the terms that find it don't mention prairies or cold.
>
> **Role restriction.** A keeper from the open slot may only earn the **Lesson** role — never
> Anchor, never Evidence. You cannot argue thermal performance from a Tokyo house; the envelope,
> the unheated buffer rooms, the whole climate logic doesn't travel. The board's existing "what to
> avoid" field carries the split: *steal the light-court section, discard the envelope assumptions.*
>
> **Budget.** One campaign, two or three keepers maximum — capped so it can't swamp a board,
> reserved so it can't be squeezed out.
>
> **Restricting it is the user's call, not the tool's.** Narrow the open slot only on explicit
> instruction. Default is wide.

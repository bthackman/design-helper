# Driver derivation & consolidation method

Generic method for arriving at locked design drivers on any project. Codified 2026-07-11 from the Nonimuss pilot. Sequence: **client discovery → site → consolidation workshop → lock.** Candidates are drafted during the client phase and *parked*; nothing locks until the site can argue back.

## 1. Where driver candidates come from (four evidence tiers)

Work down the tiers; the lower ones produce the better drivers.

| Tier | Source | Reliability | Example pattern |
|---|---|---|---|
| **Stated** | Explicit brief/client requests | Weakest alone — clients state *solutions*, not forces ("we want a pool") | Take the request, ask what force is behind it |
| **Derived** | Patterns across the client matrix: schedule × ritual × role | Strong — behaviour doesn't lie | A time-diary ("out 18 d/mo, returns depleted") yields a *sequence* driver no one asked for |
| **Structural** | Demographics, life stage, org trajectory, money posture | Strong — clients rarely request what their situation dictates | Ages 53+49 + forever-house → aging-in-place, unrequested |
| **Contradiction** | Where two client truths collide | Richest — contradictions are driver fuel | "Compact house, expansive life" → satellites + one concentrated event |

The client-profile matrix (evidence → reading → position → implication) is the machine that produces tiers 2–4. If a candidate driver traces only to tier 1, be suspicious.

## 2. Forces beyond the client (always consulted, client silent or not)

- **Constraint arithmetic.** Identify the binding constraint (area cap, FAR, budget/m², height) and *compute where it bites*. A driver earns its place when the math shows the constraint is real at this scale (corridor % of a plan is noise at 400 m², a whole room at 120 m²). Never lock a compactness/efficiency driver without the arithmetic.
- **Climate.** Name the design-case condition (the -20°C morning, the 35°C afternoon, the driving rain) — climate doesn't negotiate and the client rarely states it.
- **Regulation.** Read the bylaw envelope as *land the rules reserve or deny* — setback bands, height planes, coverage. Sometimes regulation hands a driver its site (a rear setback band where buildings can't go but a terrace can).
- **Typology norms / gap detection.** What programs of this type always need that this brief omits (support space, storage, the activity everyone does but nobody programmed).
- **Economy of gesture.** Small projects afford one move. A good driver set nominates *where the flair budget concentrates* — which licenses restraint everywhere else.
- **Time horizon.** Design life vs. client trajectory: who are they in year 25, and does the plan still work?

## 3. Site assessment discipline (so the site can argue back)

1. **Facts before interpretation.** Parcel record, computed envelope, spot elevations, verified adjacencies (per the adjacency-verification protocol — never claim what a lot abuts from mid-scale satellite). Every fact carries a source.
2. **Every fact gets an implication.** The site-details table has a "design implication" column — that column *is the site's voice*. A fact without an implication hasn't been read yet; an implication without a fact is speculation.
3. **An unverified site cannot argue back.** If facts are provisional, drivers stay parked.

## 4. The consolidation workshop (cross-examination)

Test every parked candidate against the verified site facts. Each candidate gets one of four verdicts, recorded:

- **CONFIRM** — site strengthens it → lock.
- **SPECIFY** — site adds precision or performance criteria (wind direction, sun angle) → lock with a sharpened test.
- **DEFLATE / REFRAME** — site makes part of it moot (flat lot kills "minimal cut/fill") → salvage what survives, restate around what the site actually offers.
- **DEMOTE** — right idea, wrong scale (room-scale quality, not a project driver) → send to the relevant phase as a quality target, note where.

Then reverse the direction: **the site volunteers candidates the client phase couldn't see** (a solar problem, a front/back character split, a view the client doesn't know they have). At least one locked driver usually originates here; if none do, the site probably wasn't interrogated hard enough.

## 5. Client–site contradiction protocol

When a client request and a site force collide, there are exactly three legitimate outcomes — all logged with rationale and rejected alternatives:

1. **Renegotiate the request.** Reinterpret it honestly at the scale the region allows ("rural + bikeable" → the wild-edge reading). Requires explicit client/user sign-off — it's their request being bent.
2. **Change the site.** The motive is non-negotiable. This is why client motives *precede* site selection: they are the search criteria, and a site that fails them should lose before drivers are ever discussed.
3. **Absorb into design.** The contradiction itself becomes a driver — the design's job is to hold both truths (retreat *and* gathering in one room).

Never silently drop either side. A contradiction resolved without a decision-log entry will be re-litigated in month three.

## 6. Lock criteria (quality gates on the final set)

- **Testable** — each driver carries an auditable check (a number, a plan audit, a sun-path pass), not aspiration.
- **Project-scale** — it shapes siting, massing, or planning; room-scale ideas get demoted, not locked.
- **3–5 drivers** (7 absolute max). Fewer, sharper.
- **Non-redundant** — overlaps allowed only with a stated distinction (orientation vs. event); otherwise merge.
- **Able to say no** — a driver that never rejects an option is decoration. Ask of each: what would this driver kill?
- **Traceable** — origin cited: which evidence tier, which site fact, which decision.
- **Full disposition** — every parked candidate's fate is recorded (locked / reframed-into / demoted-to / dropped-because). Nothing vanishes silently.

After locking: write the set to `01_Design-Drivers.md` with tests and origins, log the lock in the decision log (including the rejected framings), and update the project README next-step.

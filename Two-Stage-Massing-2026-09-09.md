# Two-stage massing — a thinking pass (2026-09-09)

**What this is.** A dream pass, in this project's established sense (`Architecture-Dream-2026-09-09.md`,
`Modality-Dream-2026-09-09.md`, `Fork-Decision-2026-09-09.md`). No production code touched, no Studio
changed, no commit made. Everything below was either read directly from the live files (cited by path
and line) or externally researched and cited; where I only reasoned rather than verified, I say so.

**Read before this was written:** `Fork-Decision-2026-09-09.md` (full), `Review-Steps-1-4-2026-09-09.md`
(full), `Step-5-Report-2026-09-09.md` (full), `GLOSSARY.md` (full), `Massing-Studio.html` and
`Test-Fit-Studio.html` for Nonimuss (both in full), Nyando's `Test-Fit-Studio.html` (structure only),
`_skill-source/references/phase-3-massing.md` and `phase-4-space-planning.md` (full), `_UI/build-design-studio.js`
(header + id/CSS-collision logic), the tail of `HANDOFF.md`. Two external searches (cited in §7).

**One fact that changed what I wrote, found live, not assumed.** While reading `Test-Fit-Studio.html`
I caught it being edited under me — line numbers shifted between two reads minutes apart. The other
Fable agent's room-containment work is **already built and live**, not just planned: `roomContainer()`
(`Test-Fit-Studio.html:433-448`), `containmentResults()` (`:467-479`), and a real drag-time clamp in
`startDrag()`/`onDrag()` (`:838-887`) that, when a room starts a drag fully inside its container
(`isRoomCompliant()`), stops `onDrag()` from moving or resizing it past that container's edges. This is
exactly the mechanism Ben's message supersedes ("we don't want the mass to restrict the rooms"). I did
not touch it — out of scope for this pass — but §3 and §8 below are written assuming it comes out, and
I say precisely what "comes out" means for that specific code.

---

## 1. What Ben is proposing, sharpened

In this tool's own vocabulary: **authority over geometry is phase-dependent, not fixed to one Studio.**
Today, a Massing volume is drawn first and a Test-Fit room is judged against it — soon to be *clamped*
to it (the containment work above). Ben's reframe: that's backwards for *most* of a project's life. A
massing volume is the right authority only in the narrow window between siting and the drivers lock — a
box answers "where does the building sit, how big, how tall, does it fit the envelope and the cap."
Once Test-Fit starts placing real rooms against it, the rooms are doing more precise design work than
the box ever encoded, and the box should start **answering to** the rooms, not constraining them.

Put in the tool's own phase language: this is **not a new phase** and not a rename of Massing or
Space Planning. It's a claim about the **gate** between them — specifically, that the drivers-lock gate
(`GLOSSARY.md`: "Drivers lock — the gate... everything before feeds the drivers; everything after is
tested against them") is *not* the last time massing gets to change shape. Ben is naming two sub-stages
inside what the method currently treats as one continuous "massing → space planning" handoff:

- **Massing Stage 1 (siting).** Coarse, axis-aligned volumes — Nonimuss's `house/office/pool/link/gym/terr`
  boxes exactly as they exist today (`Massing-Studio.html:137-155`). Job: prove the program fits the
  envelope and the cap, pick a parti, get a sun-tested section, park the losers. This is what
  `phase-3-massing.md` already describes end to end. **Nothing here changes.**
- **Massing Stage 2 (articulation).** Once Test-Fit starts placing real rooms against a Stage-1 volume,
  the rooms' actual footprint becomes better information than the box that seeded them. The rooms
  should be free to sprawl past the box, and there should be a tool to **push that shape back** into
  massing — an explicit, reviewable act, not a live wire — so the box the client eventually sees (and
  the box that feeds Rhino/Revit) reflects what actually got planned, not the first guess.

That second stage is genuinely new *machinery*, but it is not a new *idea* in this codebase — it is the
missing half of a pattern the tool already has one half of. `syncFromTestFit()`/`renderTestFitSync()`/
`rebuildGhosts()` (`Massing-Studio.html:592-682`) already read Test-Fit's room bounding boxes, compare
them to the current House/Office volumes, and show the delta as an advisory ghost — "Test-Fit Ground
needs ~13.0 m² (13.0×12.3 bbox)... vs House box 11.6×9.3 — +3.7 m² short, box may need to grow." That
is Ben's whole idea, already half-built, already labelled `advisory only — box dims are not auto-resized`
(`:653`). What doesn't exist yet is the second half: a button that turns that advisory delta into an
applied edit to `state`, on request, previewably.

---

## 2. Verdict: it holds up, with one real qualification

**It holds up as architectural reasoning**, and it holds up as a claim about *this specific tool's own
architecture* better than I expected before checking. Three independent lines of evidence converge:

1. **The tool already half-built the reverse direction on its own,** before Ben ever said this out loud
   (§1's `syncFromTestFit` mechanism, dated in-file to the same 2026-09-09 session as the containment
   work). A tool's own organic growth pointing toward an idea before the idea was stated is real
   corroborating evidence, not just a coincidence — whoever wrote that advisory-ghost mechanism was
   already reaching for "rooms should be able to tell the mass something," they just stopped at
   advisory.
2. **Real practice does something structurally similar, though not literally what "rooms drive mass"
   suggests.** Checked directly (§7): Revit's actual Mass→Mass-Floor→Floor/Wall workflow is a **one-time,
   explicit conversion** — you build a coarse mass, then convert mass floors to real floors and mass
   faces to real walls, and from that point on the walls (which rooms are bounded by) are the
   authoritative geometry; the original Mass object is not kept in a live loop with them. That is closer
   to "the mass gets promoted, once, into something more detailed, and the detailed thing takes over"
   than to "rooms literally push the box around forever." This matters: it says the right shape for
   Ben's mechanism is a **one-time, explicit promotion**, not a live two-way binding — which also happens
   to be exactly what this tool's ground rule already requires (§4).
3. **Nonimuss's own four Step-1 conflicts are a real, worked example of the idea already paying off**
   (§5) — under the old model they read as errors in the anchoring; under Ben's model, at least one of
   them is legitimately the rooms telling the box it's the wrong shape.

**The qualification, stated plainly so it doesn't get lost in agreement:** the *literal* image in Ben's
message — "rooms push and pull to articulate the mass and change the form of the house" — describes
continuous, interactive articulation, closer to sculpting a single form than to a discrete promotion. I
don't think that literal version survives contact with this tool's own hardest rule (nothing auto-applies
geometry) or with what real tools actually do (§7 found no first-class "rooms reshape the envelope
live" precedent anywhere, including in the tool Ben has praised before, SketchUp — its grouping model
lets you nest and push/pull component geometry, but nothing in it computes a parent shape *from* child
placement automatically; a designer still does that push/pull by hand). What I'm recommending instead —
and what I believe is what Ben actually wants once "push back into massing" gets asked to be concrete —
is the same intent (rooms get to inform the box) delivered as a **named, previewable, undoable action**:
you place rooms, you look at the delta the tool already shows you, you click something that says
"reshape House to fit," you see the new box before it commits, you accept or don't. That is Ben's idea,
just built the way this tool already insists every cross-Studio write has to be built.

**What would change my mind:** if a future pilot shows that even a one-click "reshape to fit" is too
coarse — that Ben wants to nudge individual walls of the hull by hand and have that read back
live — that's a materially bigger build (true interactive articulation, not a promotion action) and
would need its own pass. Nothing I found today points that way, but I haven't watched Ben actually use
a promotion button yet, and that's the real test.

---

## 3. Direction of authority, and the rule that must not break

**The rule, restated so it's unambiguous: nothing auto-applies geometry, in either direction, ever,
without an explicit act by Ben that previews the result before it commits.** This is not new — it's the
House/Office drift lesson already coded into `Massing-Studio.html:552-557`'s comment and already the
reason `syncFromTestFit` is advisory-only. What's new is that Ben's ask makes explicit something the
tool's design had only implicitly gotten right in one direction (mass→room clamp, now built) and wrong
in the other (mass→room clamp exists; room→mass promotion doesn't, and shouldn't be built the same way
containment was).

**Say precisely how "rooms push back into the mass" stays explicit, previewable and reversible:**

- It is a **button, not a subscription.** Ben places/edits rooms freely; nothing recomputes `state`
  automatically as he drags. This matches `syncFromTestFit`'s existing pattern exactly (a manual "Sync
  from Test-Fit" action, not a live watcher) and Step 5's own careful language: "not on save, not on
  sync" describes the *mass→room cut*, which is genuinely safe to be live because it only ever moves a
  read-only dashed outline; it was never proposed for *room→mass*, and shouldn't be.
- **Preview before commit.** The mechanism to reuse already exists in the file, doing almost exactly
  this job: `rebuildGhosts()` (`Massing-Studio.html:662-682`) already draws "what the rooms need" as a
  dashed wireframe at the box's real position, distinct in colour from the live volumes. The new action
  is: click "Reshape [House] to fit rooms" → the ghost is what you'd get → a second confirm click writes
  it into `state[i].w/d` (or, if Q1's articulated-hull answer is adopted for a later stage, into a hull
  field) → `rebuild()`/`refresh()` run exactly as any ordinary slider edit already does. No behaviour
  Ben hasn't asked for happens between those two clicks.
- **Reversible.** `WORK`/`localStorage` already persist scheme edits (`Massing-Studio.html:160-165`);
  nothing about a promotion write needs new undo machinery beyond what a slider edit already gets
  (Ben can drag it back, same as any other edit). If real undo history is ever wanted tool-wide, that's
  a separate, larger ask than this pass — not gating this one.
- **The containment clamp must come out, and specifically what "come out" means.** The clamp code at
  `Test-Fit-Studio.html:838-887` (`drag.container` gating `onDrag`'s room/resize branches) treats the
  box as authoritative over the room the instant a drag starts inside it. Under Ben's model that's
  exactly backwards for Stage 2 and needs to be removed, not softened — a room dragged past its box
  should draw a **violation marker** (`containmentResults()` already computes the overage numbers,
  `:467-479` — keep that function, it's the same "flag, don't block" pattern `adjacencyResults()`
  already uses successfully) rather than being physically stopped. This is a real, specific piece of
  work this pass is flagging for reversal, not just an abstract principle — see §8 Stage 0.

This is exactly the shape `Fork-Decision-2026-09-09.md`'s own Step 6 was already scoped to be
("Reconciliation as a proposed, previewable, undoable action — never automatic") — see §6.

---

## 4. Where this fits the existing 8-step plan

**Short version: this doesn't add a 9th direction to the plan. It resolves Step 6's open shape, adds one
new room-authoring tool Step 6 always assumed would need to exist somewhere, and asks Step 3 (still
unbuilt) to keep both directions symmetric rather than building mass→room polish first and room→mass
never.** Nothing here supersedes Steps 1, 2, 4, or 5 — all four are read-only, coordinate-frame, or
de-collision work that stands regardless of which direction reconciliation ends up running.

- **Steps 1, 2 — stand as built.** The site-frame re-anchor and the Nyando implicit-envelope fallback are
  prerequisites for *any* version of this idea (you can't push a room's shape into a box that doesn't
  share its coordinate frame) and don't change.
- **Step 3 (unbuilt) — needs one addition, not a redesign.** `drawPlanCut()`'s job (plan is a horizontal
  cut, rooms drawn on top) is unaffected. What Step 3 should *also* carry forward, since it's the step
  that puts both object graphs in one runtime: the containment-clamp reversal from §3 belongs here or
  earlier, so the merged page never ships with a live clamp Ben has already said he doesn't want.
- **Step 4 — stands.** The one-way live mass→room cut is still exactly the right, safe, always-on
  visualization for Stage 1 siting. This never becomes a two-way live link under Ben's model either —
  §3 above is explicit that room→mass stays a button, not a second live wire.
- **Step 5 — stands, done, unaffected.** Nothing about `drawPlanCut()`/`levelElevations()` changes.
- **Step 6 ("reverse live ghost — room bbox as a live wireframe in the 3D scene") — mostly already done,
  under a different name.** `rebuildGhosts()` *is* a reverse ghost, just file-based instead of live and
  scoped to the two on-cap levels' bounding boxes rather than per-room. What Step 6 still needs to add,
  given Ben's ask: (a) run it live inside `Design-Studio.html` off the shared runtime instead of the
  file-sync round-trip, matching Step 5's own live pattern; (b) extend it from "level bbox" to
  "per-volume" granularity so Pool/Link/Office each get their own ghost, not just House/Office's two
  level boxes.
- **Step 7 ("reconciliation as a proposed, previewable, undoable action") — this is where the actual new
  work lands.** Everything in §3's "push back" mechanism — the "Reshape to fit" button, the preview,
  the confirm-to-commit — **is Step 7**, sharpened by Ben's message into something concrete: not a
  generic "reconcile discrepancies" step but specifically *room bbox → volume `w`/`d` (or hull, per
  Q1's answer), one volume at a time, ghost-then-commit.* Step 7 was already the right home; Ben's
  message is what makes it buildable instead of a placeholder name.
- **Step 8 (propagate to `phase-3-massing.md`/`phase-4-space-planning.md`) — gains one real addition,
  covered in §6.**

**What this supersedes outright:** the room-containment-as-clamp mechanism currently being built by the
other Fable agent (§3, last bullet) — not because it's badly built (it's careful, well-commented,
correctly gated on `isRoomCompliant()` so it never silently snaps an already-noncompliant room), but
because Ben's message is a direct statement that the direction of constraint it encodes is wrong for
Stage 2. `containmentResults()`'s reporting half should stay; the clamp half should not ship.

---

## 5. Are the four Step 1 "conflicts" still conflicts?

Reassessed each against Ben's model, not just restated:

1. **House rooms need 13.0×12.3 m; House box is 11.6×9.3 m (east overrun 1.4 m, south overrun ~3.0 m).**
   **This is the strongest case for Ben's reframe — it stops being an error and becomes exactly the
   signal Stage 2 promotion exists to act on.** The rooms (GR/MB/GU/GB/MU/ML — six real, individually
   programmed spaces, each checked against adjacency and clearance rules) carry more design information
   than a box picked in Stage 1 to prove the program fit the cap. A "Reshape House to fit rooms" action
   is precisely the right response to this specific conflict — it's the worked example, not a
   hypothetical.
2. **OF↔LKU are 2.3 m apart across the void (the "short bridge"), flagged by `adjacencyResults()` as a
   live violation.** **This one does *not* dissolve under Ben's model — it stays a real conflict, just a
   different kind.** It isn't a room disagreeing with its own container's shape (like #1); it's two
   rooms in *different* volumes (Office, Link) disagreeing with each other about a bridging distance.
   Reshaping either box doesn't resolve it by construction — Ben (or a future promotion pass) still has
   to decide to widen Link, move Office, or accept the gap. Worth being honest that not every Step-1
   finding is explained away by the reframe; this is the control case.
3. **LK's 4.3 m stair run overruns the 4 m Link box by 0.3 m.** **Also becomes a promotion candidate,
   same shape as #1** — a room-level detail (a real stair run, sized from tread counts, not guessed)
   is more precise than the box that was sized before anyone had drawn a stair. Small enough (0.3 m)
   that "reshape to fit" is the obviously right response rather than a design debate.
4. **MB↔LK private door no longer reaches the Link box.** **This is really the same underlying fact as
   #1, wearing a different check.** MB is one of the six rooms whose bbox overruns House's box in #1;
   once House's box is reshaped to actually contain MB (per #1's fix), whether the door then reaches
   Link depends on the *specific* new shape chosen — a corner extension east doesn't help this door at
   all, an extension south does. This is worth flagging explicitly for Ben: **promotion isn't purely
   mechanical here.** If "reshape to fit" is built as a dumb bbox-grow (§8's honest v1 scope), it might
   satisfy #1's area/coverage numbers while leaving #4 unresolved, because a rectangular bbox grow
   doesn't know a door needs a wall in a particular place. That's a real limit of the rectangular-hull
   version of this tool worth stating up front, not discovering after Ben tries it.

**Net: 3 of 4 are genuinely explained, or partly explained, by the reframe (with #4 carrying an honest
caveat about what a rectangle-only promotion can and can't fix); 1 of 4 (OF↔LKU) is a real,
independent design conflict that the reframe doesn't touch.** That split — mostly right, one real
exception — is more honest and more useful than either "all four dissolve" or "none of them do."

---

## 6. What this means for the method (phase-3 / phase-4 / the gate)

**This is a change to the method, and Ben's own framing already gives it the right name: not a new
phase, a second stage inside massing, with an iteration loop back into it from space planning.**
Concretely, in `_skill-source/references/`:

- **`phase-3-massing.md` gains an explicit "Stage 1 / Stage 2" split inside its existing structure**,
  not a new numbered phase. Stage 1 is everything the reference already describes (parti generation,
  the numbers, the driver scorecard, the Studio's steerable-volume build-in list) — unchanged, still
  gated by drivers lock same as today. Stage 2 is new prose: *once Test-Fit is underway and has placed
  real rooms against a Stage-1 volume, that volume can be reshaped from the rooms via an explicit
  promotion action in the Studio (never automatic) — this is design development, not a redo of massing,
  and it does not reopen drivers lock (the drivers don't change; the box's precision does).*
- **`phase-4-space-planning.md` gains the "create and name a room" tool** (§9 below) as a numbered
  build-in item, alongside the existing door/window palette it already has (item 6, same file) — it's
  the same UI pattern, one more object type.
- **The drivers-lock gate itself does not move and does not reopen.** This is worth being explicit about
  because it's the thing most likely to get muddled: Ben's "iteration loop" is a loop *inside* the
  massing↔space-planning relationship, run against volumes that already passed the gate. It is not a
  license to re-argue the drivers every time a room gets promoted. If a promotion ever produces a box
  that would fail a driver test that passed at lock time (e.g. coverage now exceeds 45%), that's a real
  finding worth a decision-log entry — same as any other post-lock discovery — not a reason to treat
  the gate as reopened.
- **The decision log gains a new event type worth naming**, since `02_Decision-Log.md` currently has no
  vocabulary for "a volume's shape changed because rooms outgrew it": each promotion should log which
  volume, the before/after dims, and which room-level conflict triggered it — this is exactly the kind
  of thing `Library/Parked-Ideas.md`'s sibling discipline (log the reasoning, not just the number) exists
  for, applied one level down.
- **Nyando's freeform-without-massing principle (`phase-4-space-planning.md:26`) is unaffected and must
  stay unaffected** — see §7 below. A project with no Massing Studio simply has nothing to promote into;
  the room-creation tool (§9) works identically there, minus the promotion button, which is exactly how
  `onCapBBox()`/`levelVolume()`'s existing "implicit envelope, no massing" fallback already behaves.

**This is a multi-session project, said in those words.** Even scoped as narrowly as §8 stages it, this
touches: one new interactive tool (room creation, with real UI, real state, real export-shape
implications), a genuinely new write path into Massing's `state` (something that has never existed
before — every existing cross-Studio interaction is read-only), a method change in two reference files,
and — if Q1's articulated-hull question is ever answered "yes" — a change to what a `massing-interchange/v1`
volume record is allowed to contain, which is a decision `Massing-Export-Roadmap.md`, the Rhino/Revit
receivers, and `buildInterchange()`'s own `axes` note all have a stake in. None of that fits in one
sitting, and stopping after any one of §8's stages leaves the tool better than it is today, same
property every prior stage of this plan already committed to.

---

## 7. Research — what real tools actually do, cited

**Revit's Mass→Floor/Wall→Room workflow**, searched directly (2026-09-09): the real sequence is
*Create a Mass → create Mass Floors at each level → convert Mass Floors to real Floor elements
("Create Floors" turns a selected mass floor into a floor-by-face) → convert mass faces to walls
via "Walls by Face" → only then does the Room tool have real, room-bounding walls/floors to compute
room extents against* ([Novatr — Revit Massing in Architecture](https://www.novatr.com/blog/revit-massing-in-architecture),
[NOVEDGE — Mass-to-Model Workflow](https://novedge.com/blogs/design-news/revit-tip-mass-to-model-workflow-converting-conceptual-masses-into-constructible-revit-elements),
[ARKANCE — Revit Massing Pt. III](https://arkance.world/global/resources/read/blogs/revit-massing-applying-geometry-to-masses-part-3)).
This is the same finding `Fork-Decision-2026-09-09.md` §4 already cited (Rooms are never geometric
children of a Mass), extended with the detail that matters for *this* question: **the conversion is a
one-time, explicit, human-triggered act — not a live binding in either direction, and not something
that runs automatically when either the mass or the resulting walls change later.** Once you convert,
the mass and the built geometry are two separate objects going forward; nobody re-derives one from the
other on an ongoing basis. That is the strongest real-world precedent for building Ben's "push back"
mechanism as a **discrete promotion action** (§3/§7 above) rather than a live two-way sync — it's not
just this tool's own ground rule agreeing with itself, it's the industry-standard tool doing the
analogous thing the same way.

**General massing-to-design-development literature**, searched directly: multiple sources describe
massing models "evolving" through the design process — starting as simple blocks and later
"incorporating greater detail such as floor layouts" as the design develops, with Revit's own
conceptual-massing environment explicitly pitched as letting you "convert [masses] into building
elements as the design develops" ([Autodesk — Understanding Massing Models](https://www.autodesk.com/solutions/massing-model-architecture),
[QZY — What Is a Massing Model](https://www.qzymodels.com/what-is-a-massing-model-in-architecture/)).
This confirms the *general shape* of Ben's idea (coarse-then-articulated is how massing is actually
understood to develop) without confirming the *specific mechanism* (a literal room→box push). Treat
these as vendor/marketing-level sources, same caveat this project already applies to this class of
citation — directionally useful, not a spec.

**What I did not find, and said honestly rather than papered over:** no real tool or documented method
where placing rooms *computes or drives* a parent envelope's geometry as a first-class, named
operation. SketchUp's grouping/component model (checked from existing knowledge, not re-fetched this
pass) supports nesting and nondestructive push/pull of a component's own geometry, and a "container"
group can certainly be resized by hand to fit what's inside it — but nothing in SketchUp computes that
resize *from* the contents automatically; a person still does the push/pull. **The real precedent for
"rooms inform the envelope" is a human decision made easier to see, not a computed relationship** —
which is exactly what `rebuildGhosts()`'s existing ghost-and-delta display already does, and exactly
what §3's promotion button would formalize into a one-click version of that same human decision. If
Ben's actual want turns out to be closer to real-time sculptable articulation than to a promotion
button, that genuinely has no precedent I could find anywhere, real tool or otherwise — worth knowing
plainly rather than assumed away.

---

## 8. Answers to Q1 and Q2 — the load-bearing ones

### Q1 — Granularity: what *is* the mass at Stage 2?

**Recommendation: aggregate hull per functional volume (one "House" shape, not six room-boxes) — but
build the honest, cheaper version first and only reach for a true hull if the rectangle keeps failing.**

Reasoning:
- **Every room becoming its own box in `state`** would multiply `nVol` from Nonimuss's current 5–6 to
  11+ for House alone. §8 below shows exactly what that does to `metrics()`/`drivers()`, and it's bad —
  this option is close to ruled out by §Q2 alone.
- **A single non-rectangular hull per functional volume** ("House" becomes one shape that follows the
  rooms' actual outline, not a rectangle) is architecturally the right answer — it's what a real
  articulated massing model looks like — but Massing today has **no non-rectangular volume type at
  all**. `buildInterchange()`'s own `axes` note is explicit and load-bearing: *"Boxes are axis-aligned;
  w = E–W extent, d = N–S extent (any rotation is baked into w/d)."* (`Massing-Studio.html:519`).
  Building a real hull means: a new volume shape (polygon extrusion, not box-by-corner), new
  `rebuild()` Three.js geometry (`ShapeGeometry`+extrude instead of `BoxGeometry`), a new
  `massing-interchange/v1` volume record shape the Rhino/Revit receivers don't currently know how to
  read, and `metrics()`'s facade/coverage math rewritten from `w*d`/`2*(w+d)*h` box formulas to real
  polygon area/perimeter. That's a substantial, multi-file build, not a small step.
- **The cheap honest middle ground, and what I'd actually recommend building first:** keep the House
  volume a **box**, but let "Reshape to fit" grow that box's `w`/`d` (and, if needed, `x`/`z`) to the
  rooms' own bounding box — exactly what `rebuildGhosts()` already computes and displays today, just
  turned from a ghost into a commit. This resolves conflict #1 from §5 completely (the box literally
  becomes 13.0×12.3) without touching a single downstream consumer's assumptions — `metrics()`,
  `drivers()`, `buildInterchange()`, the Rhino/Revit receivers all keep working exactly as they do
  today, because the output is still an axis-aligned box, just a differently-sized one. The honest
  limitation, stated plainly (same one #4 in §5 already surfaced): a bbox-grow can silently include area
  that isn't actually program (e.g. an L-shaped room cluster's bbox includes the notch), and it can
  leave a door-reachability problem like #4 unresolved even while "fixing" the area/coverage numbers.
  Log that gap in the promotion action's own preview text, not just in this document — the ghost should
  say "grows the box to 13.0×12.3 m (includes 1.6 m² of non-program corner)" or similar, not silently
  overstate what the box now contains.
- **When to reach for a real hull:** only if a real project's promotion history shows the bbox-grow
  gap (extra non-program area, or unresolved door-reachability like #4) actually causing a wrong
  decision downstream — the same "don't build it until an earned failure asks for it" discipline this
  tool already applies to materiality, stairs, and the collaborator roster. Don't build the hull
  speculatively.

### Q2 — What happens to `metrics()`/`drivers()` if "House" becomes six room-boxes (checked directly, not guessed)

Read `metrics()`/`drivers()` line by line (`Massing-Studio.html:181-226`) against a hypothetical
6-box House:

- **`coverage`** (`:183`) sums `w*d` over all ground-footprint boxes ÷ lot area. Six boxes covering the
  same net footprint as one box read *higher* than the one box did, because interior partition walls
  and any notch/reentrant between rooms get double-counted or excluded inconsistently depending on
  whether the boxes actually tile the footprint exactly (they won't — GR/MB/GU/GB/MU/ML are placed with
  real gaps for walls and circulation, `Test-Fit-Studio.html:160-165`'s own `x/y/w/h`). **Confirmed
  distortion, not hypothetical**, computable right now from the existing `ROOMS` data.
- **`facade`** (`:186`) sums `2*(w+d)*h` over every conditioned box. Six adjacent room-boxes each
  contribute their *own* full perimeter — **every shared interior wall between two rooms gets counted
  as envelope facade twice**, once from each room's box. This is the sharpest, most concrete failure:
  `effLoss`/`glazedPct` (the thermal driver D3's own input, `:187,209`) would read as if the house had
  far more exterior wall (and far more heat loss) than it actually does, because the math has no concept
  of "this face is interior, shared, not envelope." **This alone is close to disqualifying for the
  one-box-per-room option** without a real interior/exterior face classifier, which doesn't exist and
  isn't small to build (it needs adjacency-aware face detection, not just a sum over boxes).
- **`nVol`/build-simplicity** (`:189,346`) — currently "5 vol · 2-storey · complex" is already the
  Scheme B label at 5-6 volumes total. Adding House's 6 rooms as separate volumes pushes `nVol` to
  ~11-12; the display's own threshold (`m.nVol<=4?'· moderate':'· complex'`) means **every articulated
  scheme reads as "complex" regardless of how good the actual design is** — the metric stops
  discriminating between a genuinely sprawling scheme and a normal house with normal room count. This
  is real and confirmed from the code's own thresholds, not inferred.
- **D3 (winter thermal)** (`:209`) explicitly penalises volume count (`-(m.nVol-2)*4`) on top of the
  facade distortion above — a double penalty for the same underlying miscount. **D5 (step-free)**
  (`:216-218`) also penalises `nVol` directly. Both driver proxies would read every articulated house as
  thermally worse and less step-free than a coarse box, independent of its actual design quality — the
  opposite of useful.
- **The cap meter** (`m.dwell`, `:182,335-340`) is the one metric that survives cleanly — `areaOfTypes`
  filters by `type`, not by "is this a separate volume," so as long as each room-box is tagged
  `type:'house'`, the cap sum is arithmetically identical whether it's one box or six. **This is the
  one piece of evidence the one-box-per-room option isn't entirely broken — just facade/simplicity/D3/D5
  are.**

**Conclusion, stated as plainly as the check supports it: one-box-per-room breaks `facade`/`effLoss`/D3/D5/
build-simplicity in ways that are not cosmetic — they'd make the tool actively lie to Ben about thermal
performance and complexity for the exact schemes he's most trying to get right at Stage 2. The cap meter
is the only metric indifferent to the granularity choice.** This is the strongest concrete argument for
Q1's answer (one aggregate volume, not six room-boxes) — not an aesthetic preference, a checked failure
mode in the pure functions the tool trusts everywhere else.

---

## 9. A concrete design for "create and name a room"

Ben named this as the one hard requirement: *"We would need a tool in the test fit world to create new
'rooms' and provide names to them so that they could then be read back to the mass."* This is buildable
today, independent of everything else in this document — it doesn't need Q1's granularity question
resolved, doesn't need the promotion mechanism, doesn't need the containment clamp reversed. It's a
pure Test-Fit addition.

**Pattern to copy, because it already exists and is proven:** `phase-4-space-planning.md`'s existing
door/window palette (item 6, and the live `<select id="palWall">` + `+ Add to wall midpoint` button at
`Test-Fit-Studio.html:96-104`). A room is a bigger, freestanding version of the same idea — pick a type,
give it a default size and a sensible default position, drop it, then drag/resize/rename like every
other object in this file already works.

**UI:**
- New palette section, "Add a room," beside the existing door/window palette in `#left`.
- Inputs: a **name** text field (free text — Ben's own words, "provide names to them"), a **type**
  dropdown seeded from `CLUSTER_COLOR`'s existing keys (`Hub/Private/Service/Wellness/Work`) so a new
  room slots into the existing colour/adjacency vocabulary rather than inventing a new one, and a
  **level** dropdown (`Ground`/`Upper`, reusing `currentLevel` as the default).
- Button: `+ Add room`. Drops a new room at a sensible default (screen-centre of the current view, or
  offset from the last-placed room so multiple adds don't stack exactly on top of each other) with a
  small default size (e.g. 3×3 m — deliberately small and obviously provisional, not guessed to match a
  real program area Ben hasn't stated).

**Data shape — reuses `ROOMS`' existing shape exactly, no new fields invented:**
```js
rooms[newId] = {
  label: name,                 // Ben's typed name, direct
  level: chosenLevel,
  cluster: chosenCluster,      // one of the existing CLUSTER_COLOR keys
  onCap: true,                 // a newly-authored room is real program by default;
                                // Ben can flip this later the same way VOID is hand-flagged false
  illustrative: false,
  x, y, w: 3, h: 3             // dropped at a default position, immediately draggable/resizable
                                // via the room-drag/resize handlers that already exist
};
```
No new field is needed for "which volume does this belong to" — that's `ROOM_VOLUME_TYPE`
(`Test-Fit-Studio.html:420-423`), and it's the one place a new room genuinely can't be automatic: a
freshly created room has no volume to be checked against until Ben (or a later pass) tells the tool
which functional volume it belongs to. **Two honest options, not resolved by this document — Ben's
call:**
1. **Default to "no container"** (the room simply doesn't appear in `ROOM_VOLUME_TYPE`, exactly like
   `VOID` today) until explicitly assigned — the safest default, since guessing wrong silently would be
   worse than saying nothing.
2. **A required "which volume" picker at creation time**, populated from the live `state` (Massing's
   current volumes) when the Studios share a runtime, or a free-text field when they don't (Nyando's
   case, §10) — more work, more correct once built.
Recommendation: **option 1 for the first build.** It's less work, it never guesses wrong, and Ben can
extend `ROOM_VOLUME_TYPE` by hand (as it already is today) the moment a new room needs to be checked
against something.

**Identity, since a stable id matters for §Q5's "survives being pushed to the mass and back":** the
existing `ROOMS` keys (`GR`, `MB`, ...) are short hand-picked codes; a tool-created room needs an
id-generation rule since Ben won't hand-pick a unique key every time. Reuse the existing pattern for
opening ids exactly — `newOpeningId()`'s `prefix-new-N` counter (`Test-Fit-Studio.html:232`) — as
`room-new-N`. This id is stable for the life of the session/save file (persists through `Save`/`Load`,
`Test-Fit-Studio.html`'s existing file-based state persistence), which is the only durability this tool
currently promises for anything.

**Deletion:** worth naming since it's adjacent — today there is genuinely no room-deletion UI
(`adjacencyResults()`'s own guard comment at `:272-275` says exactly this: "there's no UI control for
room deletion yet"). A "create room" tool without a matching "delete room" control is asymmetric and
Ben will hit it immediately (create three, want to remove one). Small addition, same palette: a small
`×` on the room's own label/header when selected, same visual language as the door/window delete `×`.

**What this tool does *not* need to solve, and shouldn't try to:** rewriting `ADJ_PAIRS` for a
newly-created room isn't automatic and shouldn't be — the adjacency matrix comes from
`Program-Test-Fit.md`'s own authored table, and a room the tool invented on the fly has no entry there.
Leave a new room out of `adjacencyResults()` entirely until Ben (or a doc-sync pass) adds it to
`ADJ_PAIRS` by hand — same "don't guess" discipline as the volume-assignment question above.

---

## 10. Nyando — checked, degrades correctly by construction, not by a special case

Nyando's `Test-Fit-Studio.html` (`Projects/Nyando-Maternity-Waiting-Home/4_Space-Planning/`) uses `rooms`
as an **array** (`mkRoom()`-built, `let rooms = [...]`), not Nonimuss's keyed object — confirmed by
reading it directly, and matching `Review-Steps-1-4-2026-09-09.md` §3's own grep-confirmed finding of
zero shared function names between the two projects' files. It is, today, a genuinely separate codebase,
not a shared one with per-project data.

This means **the room-creation tool in §9 is not automatically available in Nyando** — it would need to
be authored into Nyando's own file the same hand-per-project way everything else in that Studio was
built (per `GLOSSARY.md`'s own description: "generated per project," "hand-authored per project, not a
checked-in template"). That's an honest cost, already named as a debt in `Review-Steps-1-4-2026-09-09.md`
§3 for `levelVolume()` and now extending to this tool too. **It degrades gracefully, not silently**:
Nyando's Studio has no Massing Studio sibling at all, so there is nothing to push a room shape back
into — the "Reshape to fit" button from §3/§7 simply has no volume to act on and shouldn't render, the
same way `levelVolume()` already correctly falls through to its `implicit` branch
(`Test-Fit-Studio.html:355-366` in Nonimuss's file) when no massing sync exists. `phase-4-space-planning.md:26`'s
freeform-by-default principle is preserved by this design, not worked around — a room-creation tool with
no promotion target is exactly what "freeform, no external dependency" already means.

---

## 11. Cost and risk — what's genuinely at risk, and what explicitly is not

**At risk, honestly:**
- **A genuinely new write path.** Every cross-Studio interaction that exists today (Steps 4, 5, and the
  advisory `syncFromTestFit`) is read-only in the direction it touches `state`. The promotion action
  (§3/§7) is the first thing in this tool's history that would write Massing's `state` from something
  Test-Fit computed. That's a real first, and it deserves the same care Step 5's report gave the
  mass→room read (live-verify it does exactly what it claims, nothing more, with a real Playwright
  click sweep before calling it done).
- **The containment clamp reversal is real, scoped work, not a documentation fix.** `startDrag()`/
  `onDrag()`'s `drag.container` gating (`Test-Fit-Studio.html:838-887`) needs to come out or be
  disabled; whoever does that needs to re-verify `containmentResults()`'s reporting still works
  correctly on its own (it should — it's a pure read, not entangled with the drag code), and re-run the
  export byte-identity checks Step 4's review already established as the bar.
- **Q1's bbox-grow promotion has a real, named limitation** (§8, and conflict #4 in §5) — it can produce
  a box that satisfies area/coverage numbers while still leaving a door unreachable. This needs to be
  visible in the tool's own UI (the preview text), not just in this document, or it will look more
  trustworthy than it is.
- **The method change is real and touches two reference files** other future projects will be seeded
  from — get it right once, since it's the only place a wrong call reaches forward (`GLOSSARY.md`'s own
  framing of why the Studios are hand-authored per project, not templated).
- **This is a multi-session project**, said in those words, per §6.

**Explicitly NOT at risk:**
- **Every existing pure function, unchanged.** `metrics()`, `drivers()`, `drawSection()`,
  `updateTrade()`, `drawPlanCut()`, `levelElevations()` (Massing) and `adjacencyResults()`,
  `hubClearance()`, `caseworkDoorViolations()`, `caseworkWindowNotes()`, `onCapBBox()`, `levelVolume()`
  (Test-Fit) — none of them needs to change for §8's recommended (bbox-grow, aggregate-per-volume)
  answer to Q1. They'd only need rework if a real hull (the *rejected-for-now* branch of Q1) were ever
  built.
- **The `massing-interchange/v1` schema and the Rhino/Revit/Blender receivers.** Under §8's recommended
  answer, a promoted volume is still an axis-aligned box with the same `{id,type,x,z,w,d,h,base,glaz}`
  shape `buildInterchange()` already emits (`Massing-Studio.html:501-506`) — the receivers see a
  differently-sized box, exactly as they already do whenever Ben drags a slider. Nothing about the
  export contract changes.
- **Nyando's freeform-without-massing workflow** — confirmed unaffected by construction, §10.
- **The drivers-lock gate** — does not move, does not reopen, per §6.
- **Steps 1, 2, 4, 5 of the existing plan** — all stand exactly as built/verified.
- **The offline-first, `file://`-openable, no server, no build step property** — every mechanism
  described here (palette UI, ghost-then-commit promotion, id counter) is plain client-side JS, same as
  everything else in both files.

---

## 12. Staged build path

Each stage independently valuable, independently abandonable — same safety property every prior stage
of this plan has already committed to. Checkpoints run through the real Playwright harness
(`C:\Users\bthac\AppData\Local\Programs\Python\Python310\python.exe`, Playwright 1.62.0) against
`_UI/_playwright/qa-scratch/` files, per this project's established bar — a claim isn't done until it's
been driven through a real headless Chromium, not just read from the code.

**Stage 0 — Reverse the containment clamp, before anything else ships.** Remove
`Test-Fit-Studio.html:838-887`'s `drag.container` gating from `startDrag()`/`onDrag()`'s room and resize
branches; keep `containmentResults()`, `roomContainer()`, `isRoomCompliant()` exactly as-is (they're
correct, pure reads other stages depend on for the "flag, don't block" pattern). **Checkpoint:** drag a
room past its live volume's cut boundary in `Design-Studio.html`; confirm it moves freely (no
snap-to-edge), confirm `containmentResults()` still reports the overage correctly, confirm zero
console/page errors, confirm export byte-identity still holds (Step 4's own bar, re-run).

**Stage 1 — The room-creation/naming tool (§9), Test-Fit only, no cross-Studio dependency.** Palette UI,
`room-new-N` id generation, `ROOMS`-shape data, no-container-by-default. Independently valuable even if
nothing past this stage ever gets built — it's the one thing Ben named as a hard requirement.
**Checkpoint:** open standalone `Test-Fit-Studio.html`, create a named room via the palette, confirm it
renders, drags, resizes, and exports correctly in `buildExportData()`'s JSON; confirm a matching delete
control removes it cleanly; re-run standalone-Studio zero-regression checks (Step 5's own bar for "this
must not touch what already works").

**Stage 2 — Promotion preview only (the ghost half of §3/§7), no commit yet.** Extend
`rebuildGhosts()`/`renderTestFitSync()`'s existing file-based advisory into a live, per-volume version
running off the shared `Design-Studio.html` runtime (Step 6's own scope), showing the delta for every
volume with a `ROOM_VOLUME_TYPE` entry, not just House/Office. No write to `state` yet — this stage is
purely "make the delta visible and correct" before anything acts on it. **Checkpoint:** drag a room in
the merged page past its container; confirm the ghost updates live to show the new needed box size;
confirm `state` is provably unchanged (same read-only verification pattern Step 5's report already used
for the mass→room direction).

**Stage 3 — The commit half: "Reshape to fit" (Step 7, made concrete).** One button per volume, using
Stage 2's ghost as the literal preview; on confirm, writes the ghost's bbox into that volume's `w`/`d`/
`x`/`z` in `state`, then runs the same `rebuild()`/`refresh()` any ordinary slider edit already runs.
This is the first write in either direction between the two object graphs — treat it with the same
scrutiny Step 5's review gave the read direction. **Checkpoint:** promote House per conflict #1 (§5);
confirm the box becomes exactly 13.0×12.3 m at the rooms' real position; confirm `metrics()`/`drivers()`
recompute correctly against the new box (spot-check coverage/facade/D-scores by hand against the new
numbers, the same independent-arithmetic standard `Review-Steps-1-4-2026-09-09.md` already set); confirm
the promotion is reversible (drag the box back, or reload from `WORK`'s pre-promotion save); re-run
export byte-identity.

**Stage 4 — Method propagation (§6), into `phase-3-massing.md`/`phase-4-space-planning.md` and
`GLOSSARY.md`.** Write the Stage 1/Stage 2 massing split into the references, add the room-creation tool
to phase-4's build-in list, add the promotion-log convention to the decision-log guidance, confirm
Nyando's freeform principle language still reads correctly given the new prose around it.
**Checkpoint:** seed a *fresh* test project's Massing/Test-Fit instruments from the updated references
(same test `Fork-Decision`'s own Stage 6b specified) and confirm the method reproduces — a room-creation
palette exists from the start, the promotion language is present and doesn't contradict the
freeform-without-massing principle for a project that skips Massing entirely.

**Honest read on the whole path, stated the way this project's prior passes already have:** Stage 1 is
the one Ben explicitly asked for and stands alone regardless of what happens after it. Stage 0 should
happen essentially immediately, independent of everything else, because it's reversing work in flight
that contradicts what Ben just said. Stages 2 and 3 are where the real judgment calls live (§8's
bbox-grow limitation, §5's #4 door-reachability caveat) — worth a checkpoint pause after Stage 2's
preview-only version to have Ben actually look at a few real ghosts before building the commit button,
rather than assuming the preview is legible enough to promote from sight unseen.

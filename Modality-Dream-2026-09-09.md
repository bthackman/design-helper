# Modality Dream — 2026-09-09

A second dream pass the same day as `Architecture-Dream-2026-09-09.md`, prompted by Ben reframing the
question after actually using both Studios: not "how do the two tools talk to each other" but "what
*modality* should this tool use at all, so it works more like Revit/SketchUp/Blender — chat-able and
mouse-able over the same live model — instead of feeling clunky." This is a thinking session; no code
changed, nothing committed, no other file touched.

**Read in full:** `Architecture-Dream-2026-09-09.md` (all eight sections), `HANDOFF.md` (top ~400 lines,
all 2026-09-09 entries plus the relevant 2026-09-08/09-07 ones), `Merge-Stages-2026-09-09.md` (all 8
stages + ground rules), both Studios' full source (`Massing-Studio.html`, 671 lines; `Test-Fit-Studio.html`,
910 lines), `_skill-source/references/phase-3-massing.md` and `phase-4-space-planning.md` in full,
`_UI/_playwright/harness.py` and `fs-mock.js` in full, `_UI/_playwright/QA-2026-09-09.md` in full,
`GLOSSARY.md`, `Tool-Strategy-Map.md`, `00_Tool-Concept-Spec.md` (backlog rows 18–25), `_Export-Receivers/
Blender/README.md`. Researched externally: `blender-mcp`'s actual live/GUI architecture (not just the
prior pass's characterization of it), whether CadQuery/build123d/trimesh/pyvista support direct mouse
manipulation, the Python-server-serving-a-browser pattern (`cq-studio` and similar), SketchUp's Ruby API
external-agent story, Rhino.Compute/Grasshopper's live-document story, and Revit's 2026 MCP status
(sources at the end of each section).

---

## 0. The lost idea — not recoverable, plainly

Ben is right that a prior session produced a "new idea" this session has no memory of. I did the checks
he asked for, plus a few more, and found nothing:

- `git log --all --oneline` — 17 commits total, none referencing a new modality, Electron, a Python
  geometry stack, or a live bridge.
- `git reflog` and `git stash list` — reflog matches the 17 commits exactly (one `pull --ff-only` fast
  forward, no orphaned branches); stash is empty. There is no dangling work anywhere in this clone.
- `Library/Parked-Ideas.md` — seeded empty 2026-09-06 (its own header says so), zero rows. Not it.
- A keyword sweep across the **whole repo**, not just `*.md` — `bpy|pyvista|trimesh|cadquery|build123d|
  openscad|freecad|ifcopenshell|speckle|rhino\.compute|websocket|new modality|socket server|python
  server|local server|node server|electron|tauri`, case-insensitive, every file type — returned exactly
  five hits: `Architecture-Dream-2026-09-09.md` and `HANDOFF.md` (both discussing `bpy`/`blender-mcp` in
  the already-read architecture pass) and the three Blender receiver scripts themselves (which
  legitimately `import bpy` — that's their job). Nothing in `_UI/`, `_Export-Receivers/`, or any non-`.md`
  file points at a modality idea.
- A second sweep for `modality|talk to itself|speak to itself|live model|shared runtime|one process|
  desktop app|native app|IPC\b` turned up only the phrases already accounted for in `Architecture-
  Dream-2026-09-09.md` and `Merge-Stages-2026-09-09.md` (both discussing the *existing* two-Studio
  data-architecture problem, not a modality change) and one glossary entry — `GLOSSARY.md:19`, **"Cowork
  — the desktop app the tool also runs in"** — which names the Claude desktop app as a *surface* the
  tool is used from, not a build-modality decision. Not it either, and not a strong lead.

**Verdict: the idea is gone.** It lived only in a conversation that never got written to a file — the
same failure mode `Merge-Stages-2026-09-09.md` itself documents for the "8-stage plan," which had to be
reconstructed for the same reason. I'm not going to guess at what it was and present the guess as a
recovery. What follows is re-derived from first principles, which is the honest fallback the brief asked
for. One practical note worth acting on regardless of this pass's outcome: **write down real ideas the
moment they're agreed**, even a one-line stub in `HANDOFF.md` or a new `Parked-Ideas.md`-style register —
this is now the second time in one day this tool has lost a real decision to an unwritten conversation.

---

## 1. What "clunky" and "didn't speak to itself well" actually point at

Ben's complaints have a track record of being precise once unpacked (the volume-delete test that started
today's whole thread is the clearest recent example). Taking that seriously here rather than reading it as
a vibe:

**There are two distinct gaps, not one, and the 2026-09-09 architecture pass only fully diagnosed the
first.**

**Gap 1 — Massing and Test-Fit don't talk to *each other* live.** Already diagnosed correctly in
`Architecture-Dream-2026-09-09.md` §1 and §3: `saveForSync()`/`syncFromTestFit()`
(`Massing-Studio.html:529–598`) and `syncFromMassing()` (`Test-Fit-Studio.html:866–903`) are a
save-a-file/open-a-file ritual between two independently-running documents, never a live derivation. This
diagnosis holds up under the reframe and I have nothing to add to it — `Merge-Stages-2026-09-09.md`'s
staged plan is the right answer to *this* gap and doesn't need to change because of Ben's new framing.

**Gap 2 — Claude doesn't talk to *either Studio* live, and this is the gap the reframe actually
surfaces.** Look at how an edit happens in each Studio today, by *who* is making it:

- A **human** steers a Massing box by dragging a slider — `inp.oninput=()=>{b[k]=+inp.value; ...;
  rebuild(); refresh();}` (`Massing-Studio.html:320`) — an instant, live, in-the-running-document
  mutation. Same for Test-Fit's room drag (`onDrag()`, `Test-Fit-Studio.html:654–710`).
- **Claude** steers a Massing box by rewriting `DEFAULTS.B.boxes` in the file's source
  (`Massing-Studio.html:143–149`) during a Claude Code session, saving the file, and asking Ben to
  reload the page in his browser. That is not a live edit to a running document — it's authoring a new
  version of the document, the same category of move as Word's "someone else edited this file, reload to
  see their changes," not Blender's "the Outliner updates the instant the N-panel slider moves."

**This is the actual, mechanical meaning of "didn't speak to itself well."** It isn't only that Massing
and Test-Fit don't speak to each other — it's that *this tool has never given Claude a way to speak to
either Studio while it's running at all.* Every "chat" edit is generation-time (rewrite the file, reload),
never runtime (mutate the live page). The mouse half of "chat with it or manually adjust... over the same
live model" has existed since the Studios were built. **The chat half has never existed as a runtime
capability — only as a design-time one.** That is the deeper, more precise version of "clunky," and it is
not fixed by anything in `Merge-Stages-2026-09-09.md`, because that plan (correctly) only ever addresses
the seam *between* the two Studios, never the seam between Claude and either one.

One data point that already gestures at this exact gap without naming it: `HANDOFF.md`'s 2026-09-09 entry
on building the Playwright harness records that **"the Chrome-extension connector never worked this
session despite repeated attempts on both sides"** — the tool already tried, this same day, to get Claude
a live hook into a running browser tab, and it failed, so the session fell back to a *headless,
offline* Playwright harness instead (real filesystem, but no human present, no live session). That failed
attempt is circumstantial evidence this gap has already been felt, even if it was never named as "the
tool needs a chat-modality, not just a mouse-modality."

---

## 2. Options, ranked with honest costs

### (A) Stay in HTML/JS/Three.js/SVG, and build Claude a live bridge into the running page — RECOMMENDED

Keep every line of `Massing-Studio.html` and `Test-Fit-Studio.html` exactly as they are. Add a small,
separate, dev-tooling script (same category as `_UI/_playwright/harness.py` — not part of the shipped
tool) that lets a Claude Code session **attach to the real, visible browser tab Ben already has open**
and read/write its live JS state, the same way a human's mouse does, while the human's mouse keeps
working on the same page in the same moment.

Two concrete, already-available mechanisms, both real (not proposals — both exist today in this
environment or this repo):

1. **Playwright's `connect_over_cdp`.** Playwright is already installed and working in this environment
   (per the task brief's own "Environment facts"), and `_UI/_playwright/harness.py`/`fs-mock.js` already
   prove the pattern of a Python script driving a real Chromium page against the real filesystem — just
   currently only in *headless* mode, for offline QA. `connect_over_cdp` is the standard, documented way
   to attach Playwright to an **already-running, visible** Chrome instead of launching a new headless
   one — Ben starts Chrome once with `--remote-debugging-port`, opens a Studio normally, and a Python
   script (run via Bash, same as any other tool call) can then `page.evaluate()` into that exact tab:
   read `state`/`rooms`, call the same `oninput`-path functions the sliders call, screenshot it — while
   Ben's own mouse keeps dragging in the same window. No fs-mock needed for this use (no File System
   Access picker to fake — Ben's the one clicking Save).
2. **`claude-in-chrome`**, the Chrome-automation MCP connector already listed as available in this
   environment (`mcp__claude-in-chrome__javascript_tool`, `read_page`, `navigate`, `computer`, etc.) —
   architecturally the same idea (drive a real, visible browser tab), packaged as a first-party connector
   instead of a hand-rolled script. **Known risk, not a proposal-time assumption:** `HANDOFF.md` records
   this exact connector failing to connect on 2026-09-09, "despite repeated attempts on both sides" — so
   its current reliability in this environment is a real open question, not a given, and is the first
   thing any build session should re-test rather than assume fixed.

**Why this is the real unlock, not a workaround:** it is the literal, direct implementation of Ben's own
framing — "chat with it or manually adjust... over the same live model" — without inventing a new file
format, a new renderer, or a new geometry kernel. The model stays exactly what it already is (`state` in
Massing, `rooms`/`doors`/`windows_` in Test-Fit); what's missing is purely a *channel*, not a
*representation*. And it generalizes past today's specific ask — once Claude can reach a live page, "pull
the office back two metres and show me what it does to the winter section" becomes literally: read the
office box's index, set `b.x -= 2`, call the same `rebuild()`/`refresh()`/`drawSection()` the UI already
calls, screenshot the result — no new geometry logic, reusing 100% of what's already proven to work.

**What's genuinely at risk / the honest cost:**
- This is real, never-built infrastructure in this tool's history — the QA harness proves the *pattern*
  (Playwright + a real filesystem) but has only ever run headless, alone, with no human present. A human
  and a script touching the same live DOM/JS state at the same moment is a different thing and needs its
  own small spike before anything is built on top of it.
- It's an opt-in session-time capability, not a requirement to open the tool — but it does mean Ben has
  to start Chrome a specific way (remote-debugging flag) or get `claude-in-chrome` reconnected, instead
  of just double-clicking the HTML file. That's a real, if small, dent in "zero setup," worth being
  honest about rather than waving away.
- Nobody has verified that calling a slider's `oninput` handler programmatically produces byte-identical
  behavior to a real mouse drag (it should, since it's the literal same function, but "should" isn't
  "verified").
- **What is explicitly NOT at risk:** every pure function in both Studios (`metrics()`, `drivers()`,
  `drawSection()`, `updateTrade()`, `adjacencyResults()`, `hubClearance()`, `caseworkDoorViolations()`,
  `caseworkWindowNotes()`), the `massing-interchange/v1` export pipeline, the offline-first/`file://`-
  openable property of the shipped Studio files themselves (the bridge is a separate dev-tool that
  *attaches* to an already-open page — it changes nothing about how the file opens on its own), and the
  entire `Merge-Stages-2026-09-09.md` plan for Gap 1, which this doesn't touch or depend on.

### (B) Stay in HTML/JS, pursue `Merge-Stages-2026-09-09.md` as written — still correct, orthogonal

Covered in full in that file. Nothing here changes it. It answers Gap 1 (Massing↔Test-Fit); (A) above
answers Gap 2 (Claude↔either Studio). They can be built in either order, or in parallel, or just one of
them — neither is a prerequisite for the other. See §4 below for how they relate.

### (C) Move the canonical model into Blender (`bpy` + `blender-mcp`) — reassessed, still not recommended for Test-Fit, one real correction to the prior pass

The 2026-09-09 architecture pass's anti-Blender argument rested on one specific factual claim: *"the only
proven interaction pattern this tool has with Blender is `execute_blender_code` → screenshot, which is
generate-then-render, not live mouse-driven drag/resize with instant rule feedback."* I was asked to
verify this, since it's load-bearing for that recommendation. **It is half right and half in need of
correction.**

What I actually found, fetching `ahujasid/blender-mcp`'s own documentation (the connector this tool's
`_Export-Receivers/Blender/README.md` names as the one actually used on this project's July 2026 session):
the addon requires **a live, visible Blender GUI session**, not headless mode — it opens a socket server
*inside* that running session. Claude's `execute_blender_code` and the scene/object-inspection tools
execute against that same live `bpy.data`, and — this is the correction — **a human can move objects with
the mouse in the same Blender window at the same time**, and Claude can then query the live scene and see
exactly what changed. That is a real, working, already-precedented instance of "chat with it or manually
adjust, over the same live model" — for Blender, today, and it isn't hypothetical; §2 of the prior pass's
own research cites the July 2026 session that used it.

**Why this doesn't flip the recommendation anyway:** two separate reasons hold, and only one of them is
about Blender's own honesty gap.
1. **This tool's own established Blender workflow doesn't currently exploit that live/concurrent
   capability** — `_Export-Receivers/Blender/README.md` describes a headless *batch import* step (no
   interaction at all) followed by an interactive `blender-mcp` session used for code-driven form pushes,
   sun studies, and renders (still framed as `execute_blender_code`→screenshot in practice, even though
   the underlying tool supports more). So correcting the claim doesn't retroactively make this project's
   actual Blender usage live-mouse-collaborative; it just means the *ceiling* is higher than the prior
   pass credited, not that this tool is already there.
2. **Test-Fit Studio's actual logic has no Blender-native equivalent, and this is the harder, still-true
   point.** Door-swing collision checks, per-wall keep-clear-band merging (`hubClearance()`,
   `Test-Fit-Studio.html:289–298`), fixed-casework-crosses-a-doorway detection, and the type-level
   adjacency matrix are all bespoke 2D logic with no Blender operator, modifier, or add-on that does
   anything like them today. Building this in Blender means writing a custom add-on (Python UI panels,
   custom operators, persistent widget state) from zero prior competence in this tool's history — a real,
   large, unproven undertaking, independent of whether `blender-mcp` itself can support live collaboration
   in principle.

**On the offline-first/`file://`-openable property specifically** (asked to interrogate, not treat as
sacred): what it actually buys is three separable things — no install friction on someone else's machine,
no network dependency for a site visit, and zero per-session setup cost. For the *massing form-push*
stage, Ben already has Blender open and configured as part of real DIALOG-adjacent work, so that cost is
mostly already paid — which is exactly why (C) was, and stays, the right call for that one stage. For the
*everyday steer-a-box-and-read-a-cap-meter* workflow both Studios exist for, that cost is not already
paid, and would be reintroduced fresh for Test-Fit specifically. So the property isn't sacred, but it also
isn't a means to an end that's already been served some other way for Test-Fit's job — it's still live
and still matters there. **Verdict unchanged: keep Blender exactly where the 2026-07-29 decision and the
2026-09-09 pass both already put it (massing form-push only); do not extend it into Test-Fit's role.**
The one thing that should change is language, not scope: `HANDOFF.md`'s and `Architecture-
Dream-2026-09-09.md`'s "generate-then-render, not live" phrasing should be read as "not exploited as
live in this project's own workflow," not "incapable of being live" — a real, if narrow, correction.

**What would change my mind:** if a future session actually builds and exercises the live-mouse+Claude
pattern on Blender's massing side and it turns out to be cheap and robust, that's real evidence worth
revisiting whether porting Test-Fit's 2D logic into a Blender add-on is more tractable than it looks today
— but that's a "go build the small thing and see," not a reason to commit to it now.

### (D) Move the canonical model into a light Python geometry stack (trimesh / pyvista / CadQuery / build123d / OpenSCAD) — not recommended

Researched each. The finding that actually settles this: **none of them support direct mouse
manipulation of geometry.** Every "interactive" story found — `build123d-sandbox` and `YACV` (Yet Another
CAD Viewer) running OCP-in-WebAssembly in the browser, `cq-studio`'s hot-reload preview server — is an
*edit-the-Python-code, then re-render* loop, architecturally closer to Grasshopper (a parametric
definition re-evaluated on change) than to SketchUp or Blender (an object you grab and drag). That's a
real, disqualifying mismatch for this tool's specific need: Test-Fit's whole reason to exist is that a
room gets *dragged*, not re-parameterized in code, and the fixed-casework/door-swing check has to respond
to that drag in real time. Adopting one of these stacks would mean **still building a separate
mouse-driven frontend on top of it** — which is a strictly bigger project than what exists today (you'd
be rebuilding the Studios' own UI a second time, in a second language, to sit in front of a geometry
kernel this tool's actual geometry needs (boxes, rooms, doors, sun angles, area sums) don't require).
**Rank: skip — solves a CAD-kernel problem this tool doesn't have, while leaving the actual
mouse-interaction problem unsolved.**

### (E) Re-host the model in a local Python process, serve the browser as a thin client over a websocket — real pattern, not recommended here

This is a genuine, working pattern — `cq-studio`'s "server hot-reloads models and pushes new objects to
the browser over a websocket" is exactly this shape, and it's the shape the brief specifically asked me to
weigh. It would mean rewriting `state`/`rooms` as Python objects served to a thin Three.js/SVG frontend,
with Claude Code manipulating the Python side directly (no browser-attachment needed) and the browser
staying purely a renderer.

**Why (A) beats this for this specific repo, honestly:** the actual missing piece is *a channel from
Claude to the live page*, not *the language the model happens to be written in*. If you're going to build
a websocket bridge either way, (A) reaches the browser's **existing** JS state directly — zero new wire
protocol, zero second object representation to keep in sync, zero risk of the Python copy and the
JS-rendered copy drifting the way Massing and Test-Fit's own file-sync already once drifted (the
98→108 m² House footprint episode). (E) would require maintaining two live representations of the same
model and a serialization contract between them — real, ongoing complexity this repo doesn't currently
have anywhere, for a benefit (E) doesn't actually add once (A) exists: both let Claude touch the model,
both keep the browser as the renderer, but (E) does it through an extra hop. **Rank: a legitimate general
pattern, not the right fit for a tool whose model is already a JS object Claude can reach directly once
there's a channel to it.**

### (F) Other precedented patterns — quickly ruled out
SketchUp's Ruby API (real external-agent projects like `supex` exist, using JSON-RPC over a local socket
straight into a live SketchUp session — structurally the same idea as (A)/(C), just a different host app)
and Rhino/Grasshopper (Rhino.Compute/Hops are batch-evaluate-a-definition services, not live-drag
bridges) don't offer anything (A) doesn't already cover more cheaply, and adopting either as this tool's
*host application* would mean picking up a new heavyweight desktop dependency for no capability gain over
staying in the browser. A general game engine (Godot came up in research as a real, MIT-licensed option
for "interactive architectural visualization") is over-general for a box-and-room-and-sun-angle problem —
the same objection as (D)/(E), one size up. None change the recommendation.

**Bonus finding, tangential but worth logging:** Autodesk shipped an official **Revit Public MCP Server
Tech Preview** with Revit 2027 (April 2026) — read-only, live model-graph access. `Massing-Export-
Roadmap.md:150` and `SKILL.md:240` still describe Revit's own MCP path as paused because "Autodesk's own
MCP is read-only for now" (true) — worth a note next time the Revit receiver is touched that "read-only"
is now a real, shipped, named thing rather than an open question, even though it doesn't change this
tool's Dynamo-MVP posture today.

---

## 3. Reassessing the prior pass's two verdicts against the reframe

**"Wrong data architecture, not wrong platform" — still correct for Gap 1, incomplete (not wrong) for
Gap 2.** The prior pass was diagnosing exactly one seam — Massing↔Test-Fit — and its evidence for that
seam (both Studios already prove one-live-model-many-views works *within* themselves) genuinely supports
"the platform is fine, the missing piece is a derivation layer." That argument never claimed to cover
whether Claude itself could reach either live model, because that question hadn't been asked yet. Ben's
reframe adds a second, real seam the first pass had no reason to look for. Extending, not reversing: the
platform (HTML/JS/Three.js/SVG) is *still* not the obstacle — both gaps are channel/relationship problems,
not rendering-technology problems. §2's Blender and Python-stack research reinforces this rather than
undercutting it: nothing researched offers direct mouse manipulation *and* a cheaper path to a live
Claude-channel than what's already sitting in this repo's own `_UI/_playwright/` tooling.

**The anti-Blender call — verdict unchanged, one factual correction made.** See §2(C) above in full. The
call to keep Blender scoped to massing form-push and not extend it into Test-Fit's role stands; the
specific claim that `blender-mcp` is inherently non-live was too strong and is corrected here, but the
correction doesn't change the conclusion because Test-Fit's logic, not Blender's live-ness, is the actual
blocker.

---

## 4. Recommendation, plainly

**Build (A): a live Playwright-CDP (or `claude-in-chrome`, once reconnected) bridge from Claude Code into
whichever Studio is actually open in Ben's real browser, as new dev-tooling alongside the existing
`_UI/_playwright/` harness — not a replacement for it. Run this independently of, and in parallel with,
`Merge-Stages-2026-09-09.md`'s existing 8-stage plan for the Massing↔Test-Fit seam, which needs no
changes because of this reframe.** Do not move either tool's canonical model into Blender, a Python
geometry stack, or a re-hosted Python server. Keep HTML/JS/Three.js/SVG exactly as they are in both files.

**`Merge-Stages-2026-09-09.md` itself: keep it, unamended in content, with one addition.** Nothing in it
assumed Claude could reach a live page — every one of its checkpoints was designed around the headless,
scripted harness, which remains exactly right for regression-style verification (byte-identical exports,
zero console errors across a scripted click sequence). What changes is that once (A) exists, several of
its checkpoints gain a *second*, more convincing verification path: Stage 4's bar — "drag a volume in the
3D pane, and the dashed footprint under the rooms moves in the same instant" — can be shown live, with
Claude driving one control and Ben the other in the same window, instead of only asserted via a scripted
Playwright sequence. That's a strict improvement to an already-good plan, not a reason to touch its
content. Its ground rules (nothing auto-applies geometry; offline-first `file://`-openable; nothing
verified on a brace-count; pure functions lifted, not rewritten; `massing-interchange/v1` untouched) carry
over to the (A) track unchanged and should govern it the same way.

**The single strongest piece of reasoning behind recommending (A) over any modality change:** Ben's own
framing names the thing Revit/SketchUp/Blender *don't* have and this tool already does — living inside
Claude Code. The gap isn't that the model is in the wrong medium; every precedent researched (Blender's
`bpy.data`, SketchUp's Ruby socket bridge, Revit's new MCP server) converges on the same shape this tool
already has: a live in-memory document an external agent can read and write. The one piece missing is the
*wire*, not the *document* — and the wire is a small, bounded, already-half-built thing (Playwright is
installed, the harness pattern is proven, `claude-in-chrome` exists as a connector), not a rebuild.

**What's genuinely at risk under this recommendation, honestly:** this is new infrastructure with a real,
unverified first step (does a CDP or `claude-in-chrome` attach actually work cleanly on this Windows
machine, against a Chrome window Ben is also using) — it could fail at the spike stage, cheaply, and that
failure would be real evidence worth taking seriously (see §2(C)'s "what would change my mind"). It also
asks Ben to start Chrome a specific way for a bridge session, a small real cost against "zero setup" that
shouldn't be minimized. **What is explicitly NOT at risk:** cap math, driver-proxy formulas, the
sun-section, the trade-space plot, Test-Fit's adjacency/hub-clearance/casework-violation logic, the
`massing-interchange/v1` export pipeline, Blender's existing (and, per §2(C), actually more capable than
previously credited) role in the massing form-push stage, and the shipped Studio files' own
zero-network, `file://`-openable property — none of these change under (A) or under continuing
`Merge-Stages-2026-09-09.md` as written.

---

## 5. A multistage plan to build (A), staged small, each independently valuable and abandonable

Every stage below is new — none of it exists yet, unlike `Merge-Stages-2026-09-09.md` which had a Stage 0
already shipped. Treat Stage B0 as genuinely uncertain, not a formality.

### Stage B0 — Prove the channel exists at all
Launch Chrome with `--remote-debugging-port` (or attempt a `claude-in-chrome` reconnect — worth trying
both, since `HANDOFF.md` records one already failing once this session), open `Massing-Studio.html` for
real, and from a separate Python process (`playwright.chromium.connect_over_cdp(...)`) do the smallest
possible thing: read `document.title`, then read `state.length`. No writes yet.
**Checkpoint:** a script-driven read of the live page's JS state succeeds while the page is visibly open
and untouched, proving the channel exists before anything is built on top of it. **If this fails cleanly
on both mechanisms, stop here — that's a real, cheap finding, and §2(C)'s "what would change my mind"
becomes live.**

### Stage B1 — A minimal write, verified against a human's own concurrent action
From the same script, set one box's `w` field and call `rebuild(); refresh();` the same way
`Massing-Studio.html:320`'s slider handler does — not a raw DOM manipulation, the actual function calls.
Screenshot before/after. Then, in the same live session, have a human drag a *different* slider
immediately after, and read `state` back through the bridge to confirm both edits landed
(mirrors `WORK[k]`'s existing persistence guarantee, now exercised across a human+script interleave for
the first time).
**Checkpoint:** one script-driven edit and one human-driven edit, in the same tab, in the same minute,
both present in the final `state` read back through the bridge.

### Stage B2 — Wrap it as reusable dev tooling
Package B0/B1's working mechanism as a small script alongside `_UI/_playwright/harness.py` — e.g.
`_UI/_playwright/live_bridge.py` — with an `attach()`, a generic `call_js(expr)`, and a `screenshot()`.
Explicitly not part of the shipped tool, same convention the existing harness already follows.
**Checkpoint:** the same B1 round trip, run through the wrapped helper instead of ad-hoc script, against
both Massing Studio *and* Test-Fit Studio once each (confirming the pattern isn't Massing-specific).

### Stage B3 — A real plain-language round trip
From an actual Claude Code session (not a test script), with Ben's Massing Studio open, take a real
request in his words — "pull the office back two metres" — translate it to the corresponding slider
field and delta, apply it through the bridge using the UI's own handler path, and report back what
changed (dwelling floor, driver proxies, section) by reading the live state back, not by re-deriving it
separately. Have Ben drag something else in the same session afterward to confirm the tool still feels
normal to use by hand.
**Checkpoint:** the first real "chat with it AND manually adjust, over the same live model" session this
tool has ever had, with both halves actually exercised in one sitting.

### Stage B4 — Test-Fit's version of B3
Mirror B3 against Test-Fit Studio: a plain-language room move or resize applied through the bridge via
`startDrag`/`onDrag`'s own logic path, interleaved with a real human drag.
**Checkpoint:** same as B3, second Studio.

### Stage B5 (optional, only after B0–B4 land) — Reconnect this to `Merge-Stages-2026-09-09.md`
Once the bridge is proven solid, its strongest use is making Stage 4/5 of the existing merge plan
verifiable *live* rather than only through the scripted harness — "drag a Massing volume through the
bridge, watch the Test-Fit ghost move in the same frame, in a real visible window" is a more convincing
demonstration of the merge plan's own stated bar than any headless assertion can be. This is a genuine
enhancement to that plan's verification story, not a dependency it needs to proceed — Stages 1–6b of
`Merge-Stages-2026-09-09.md` can be built and checked with the existing harness regardless of whether B0–
B4 ever happen.

---

## 6. Honest read on the whole thing

This is smaller and cheaper than the alternative modality changes considered and rejected in §2 — it adds
one small, scoped piece of dev tooling to a repo that already has almost all the pieces it needs
(Playwright installed, a proven harness pattern, a real filesystem-backed mock to imitate for the parts
that still need it, a connector already listed as available in this environment). But it is still **new,
unbuilt, and unverified** — Stage B0 could fail, and if it does, that failure is real information, not a
setback to route around by force. This is not a multi-session engineering project the way
`Merge-Stages-2026-09-09.md`'s full A→F arc is; a working B0–B4 is plausibly one focused session if the
channel proves out at B0, and each stage stops leaving the tool better than it found it — B0 alone, even
if nothing after it gets built, answers a real open question this project has been carrying unasked since
before today.

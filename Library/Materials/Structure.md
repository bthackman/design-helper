# Materials — Structure

Starting library for the primary structural system. Tagged by climate fit, cost tier, and
durability/maintenance — see `Envelope.md` for how this library is meant to be used and swept.

**These are drafted starting points, not verified specs.** [proxy, unverified] — verify span
tables, actual local-trades pricing, and code/seismic requirements with an engineer before citing
any of this in a real deliverable.

**Climate of origin: cold-climate (seeded 2026-08-28) — see `Envelope.md` for the full warning.**
A 2026-09-06 pilot found this set's cold-climate assumptions don't transfer; treat rows as
untested outside that context rather than adapting one by assumption.

| Material | Climate fit | Cost tier | Durability / maintenance | Embodied carbon (relative) | Notes |
|---|---|---|---|---|---|
| Wood light-frame (2x6/2x8 platform) | Standard for this climate and scale; well-proven | $ | High if envelope keeps it dry; termite/rot risk only from envelope failure | Low (renewable, low-processing) | The default for residential scale; local trades know it cold — the "local trades and equipment" baseline |
| Engineered wood (glulam, LVL, CLT) | Good; allows longer spans / exposed structure as a design move | $$–$$$ | High | Low–moderate | Worth it specifically when exposed structure is doing driver work (e.g. a vaulted or clerestory space); otherwise light-frame does the job for less |
| Steel frame (post and beam) | Good, needs thermal-break detailing at any exterior connection | $$$ | Very high | Moderate–high | Earns its cost with long spans / large glazing openings a wood frame can't clear cleanly |
| Concrete (cast-in-place or block, foundation/podium) | Excellent; the default at grade regardless of what sits above | $$–$$$ | Very high | High | Almost always present at foundation/basement level even in an otherwise wood-frame building; not really optional |
| SIPs (structural insulated panels) | Good thermal performance, fast erection | $$ | Moderate; vapor/moisture detailing at panel joints is the failure point to watch | Low–moderate | Worth considering when speed of enclosure matters more than long-span flexibility |

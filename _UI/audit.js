// audit.js — the conscience panel. Every finding is DERIVED from files the tool
// already writes; nothing here needs the model in the loop, so it recomputes free
// on every open. This is the thing a window can do that a terminal cannot: hold up
// what is unfinished without being asked.

// Dual-mode: Node (test suites, require()) and plain <script> in the Window
// (spine-parse.js loaded first, exposing window.SpineParse).
const P = (typeof module !== 'undefined' && module.exports) ? require('./spine-parse.js') : window.SpineParse;

// Named distinctly from spine-parse.js's own top-level `ORDER` — both files are
// loaded as classic <script> tags in the Window and share one global scope, so a
// second top-level `const ORDER` here is a SyntaxError that silently kills this
// whole file (and, before this fix, the finding that this comment now prevents).
const AUDIT_PHASE_ORDER = P.ORDER;
const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
const STOP = new Set(['the','a','an','to','of','and','or','in','on','for','with','every','all','each','is','be','at','by','from','as','it','its']);
const keywords = s => norm(s).split(' ').filter(w => w.length > 3 && !STOP.has(w));

// A driver is "untested" when nothing downstream of the lock mentions it: no decision,
// no precedent card, no massing option. Keyword overlap is deliberately loose — this
// panel is a prompt to look, not a verdict.
function untestedDrivers(drivers, decisions, phaseTexts, templatesFor = {}) {
  // Whole-token match, not substring ("place" must not be satisfied by "placeholder"),
  // AND template scaffolding is subtracted first — the client-profile template asks about
  // "aging", which would otherwise mark an aging-in-place driver as engaged with when
  // nobody has touched it.
  const toks = t => new Set(norm(t).split(' '));
  const hay = new Set();
  for (const w of toks(decisions.map(d => d.decision + ' ' + d.rationale).join(' '))) hay.add(w);
  for (const [k, text] of Object.entries(phaseTexts)) {
    const tpl = toks(templatesFor[k] || '');
    for (const w of toks(text)) if (!tpl.has(w)) hay.add(w);
  }
  return drivers.filter(d => {
    const ks = keywords(d.driver);
    if (!ks.length) return false;
    return !ks.some(k => hay.has(k));
  }).map(d => ({
    kind: 'untested-driver', severity: 'high', target: { section: 'drivers' },
    text: `Driver ${d.n} "${d.driver}" isn't mentioned in any decision or downstream phase doc.`
  }));
}

// Questions blocking the phase you are actually in.
function blockingNow(questions, currentPhase) {
  const cur = norm(currentPhase).replace('-', ' ');
  return P.openOnly(questions)
    .filter(q => cur && norm(q.blocks) && (norm(q.blocks).includes(cur.split(' ')[0])))
    .map(q => ({ kind: 'blocking-question', severity: 'high', target: { section: 'open-questions' },
                 text: `Q${q.n} blocks ${currentPhase} and is still open: ${q.question}` }));
}

// Questions carried more than two phases past where they were raised.
function staleQuestions(questions, currentPhase) {
  const ci = AUDIT_PHASE_ORDER.indexOf(currentPhase);
  return P.openOnly(questions).map(q => {
    const ri = AUDIT_PHASE_ORDER.findIndex(p => norm(p).startsWith(norm(q.raisedIn).split(' ')[0] || '\u0000'));
    if (ri < 0 || ci - ri < 2) return null;
    return { kind: 'stale-question', severity: 'medium', target: { section: 'open-questions' },
             text: `Q${q.n} has been open since ${q.raisedIn}, ${ci - ri} phases ago: ${q.question}` };
  }).filter(Boolean);
}

// Anything upstream of the lock edited after the lock date means the drivers may no
// longer reflect their own evidence.
function changedSinceLock(lockedDate, files) {
  if (!lockedDate) return [];
  // One finding, not one per file — a panel that lists four rows for the same concern
  // trains you to ignore it.
  const hits = files.filter(f => /^(0_Spine\/0[04]|2_Site\/Site-)/.test(f.path) &&
                                 !/01_Design-Drivers/.test(f.path) &&
                                 f.mtime && f.mtime.slice(0, 10) > lockedDate)
                    .map(f => f.path);
  if (!hits.length) return [];
  // Best-effort click-through target: whichever phase owns the first hit's directory.
  const hitDir = hits[0].split('/')[0];
  const target = { section: 'phase', key: (P.PHASES.find(p => p.dir === hitDir) || {}).key || 'client-discovery' };
  return [{ kind: 'changed-since-lock', severity: 'medium', files: hits, target,
            text: `${hits.length} upstream file${hits.length > 1 ? 's' : ''} changed after the drivers locked (${lockedDate}) — do the drivers still follow from them? (${hits.join(', ')})` }];
}

// Cards that don't declare which driver they serve. Three real shapes: a labelled
// field ('Speaks to driver(s):', the template's own format); a massing option's
// driver scorecard, a nested sub-list where each driver is its own field keyed
// 'D1 ...' rather than a value under a 'driver' key; and a precedent board's actual
// practice, which scores drivers right in the heading ('P1 · Poole — ANCHOR (D1 ● ·
// D2 ● · D3 ●)') and never fills a dedicated field at all. Any of the three counts.
function orphanCards(text, label, driverField, phaseKey) {
  return P.filledCards(P.parseCards(text || '', 3))
    .filter(c => !(/D\d/.test(c.title) || Object.entries(c.fields).some(([k, v]) =>
      (new RegExp(driverField, 'i').test(k) && v) || /^D\d/.test(k))))
    .map(c => ({ kind: 'orphan-card', severity: 'low', target: { section: 'phase', key: phaseKey },
                 text: `${label} "${c.title}" names no driver it serves.` }));
}

// A phase marked complete with no gate written at the bottom of its doc.
// `phases` comes from state.json by way of SpineParse.reconcile() — reconcile() now
// guards against a malformed shape itself, but this stays defensive too rather than
// trusting a single choke point, since a thrown error here blanks the entire Window.
function missingGates(phases, phaseTexts) {
  if (!phases || typeof phases !== 'object') return [];
  return Object.entries(phases)
    .filter(([k, v]) => v && v.status === 'complete' && phaseTexts[k] &&
                        !/gate|skipped/i.test(phaseTexts[k]))
    .map(([k]) => ({ kind: 'no-gate', severity: 'medium', target: { section: 'phase', key: k },
                     text: `${k} is complete but no phase gate is recorded in its doc.` }));
}

function audit({ drivers, decisions, questions, state, files, phaseTexts, templatesFor = {}, boardText, massingText }) {
  const out = [
    ...blockingNow(questions, state.currentPhase),
    ...untestedDrivers(drivers.drivers || [], decisions, phaseTexts, templatesFor),
    ...changedSinceLock(drivers.lockedDate, files),
    ...staleQuestions(questions, state.currentPhase),
    ...missingGates(state.phases, phaseTexts),
    ...orphanCards(boardText, 'Precedent', 'driver', 'precedents'),
    ...orphanCards(massingText, 'Massing option', 'driver', 'massing')
  ];
  const rank = { high: 0, medium: 1, low: 2 };
  return out.sort((a, b) => rank[a.severity] - rank[b.severity]);
}

// "What moved since I last opened this" — the resuming-after-three-weeks view.
function sinceLastOpen(files, lastOpenedISO) {
  if (!lastOpenedISO) return [];
  return files.filter(f => f.mtime && f.mtime > lastOpenedISO)
    .sort((a, b) => a.mtime.localeCompare(b.mtime))
    .map(f => ({ path: f.path, mtime: f.mtime }));
}

(function () {
  const exported = { audit, sinceLastOpen, untestedDrivers, blockingNow, staleQuestions, changedSinceLock, missingGates, orphanCards };
  if (typeof module !== 'undefined' && module.exports) module.exports = exported;
  else window.Audit = exported;
})();

#!/usr/bin/env node
// inspect-project.js — run this FIRST tomorrow, against the real pilot project.
//
//   node _UI/inspect-project.js Projects/<name>
//   node _UI/inspect-project.js Projects/<name> --write-state
//
// It answers, in one pass, every question the Project Window plan left open:
//   - does the real project's structure match what the templates and SKILL.md claim?
//   - are the spine tables still the template's columns, or have they drifted?
//   - which docs are table-shaped and which are card-shaped?
//   - where do diagrams and images actually live, and under what filenames?
//   - has any project emitted massing.json?
//   - is the repo sitting inside a OneDrive-synced path?
// Then it runs the tested parsers against real data and prints what the Window would show.
//
// --write-state generates 0_Spine/state.json from inference, so you don't hand-author it.

const fs = require('fs');
const path = require('path');
const P = require('./spine-parse.js');
const A = require('./audit.js');

const projArg = process.argv[2];
const WRITE = process.argv.includes('--write-state');
if (!projArg) { console.error('usage: node inspect-project.js Projects/<name> [--write-state]'); process.exit(1); }

const PROJ = path.resolve(projArg);
const REPO = path.resolve(__dirname, '..');
const TPLDIR = path.join(REPO, '_templates');
if (!fs.existsSync(PROJ)) { console.error('No such folder: ' + PROJ); process.exit(1); }

const BIN = /\.(jpg|jpeg|png|gif|webp|svg|pdf|blend|3dm|rvt|rfa|xlsx|docx)$/i;
function walk(dir, base, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith('.')) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { walk(p, base, out); continue; }
    const rel = path.relative(base, p).split(path.sep).join('/');
    out.push({
      path: rel, abs: p,
      text: BIN.test(rel) ? null : safeRead(p),
      bytes: fs.statSync(p).size,
      mtime: fs.statSync(p).mtime.toISOString()
    });
  }
  return out;
}
const safeRead = p => { try { return fs.readFileSync(p, 'utf8'); } catch { return null; } };

const H = t => console.log('\n' + t + '\n' + '─'.repeat(t.length));
const files = walk(PROJ, PROJ);
const templates = {};
if (fs.existsSync(TPLDIR)) for (const f of walk(TPLDIR, TPLDIR)) if (f.text) templates[f.path] = f.text;

// ── 1. environment ────────────────────────────────────────────────────────────
H('1. Environment');
console.log('project     ', PROJ);
console.log('repo root   ', REPO);
console.log('templates   ', Object.keys(templates).length ? Object.keys(templates).length + ' found' : 'NOT FOUND — state inference will be unreliable');
const onedrive = /onedrive/i.test(PROJ);
console.log('OneDrive    ', onedrive
  ? 'YES — expect Files On-Demand placeholders; SKILL.md already records sync truncation damage'
  : 'no');
const trunc = files.filter(f => f.text && f.text.length && !/[\n\s.!?)\]`|>-]$/.test(f.text.trim().slice(-1)));
console.log('possible sync truncation:', trunc.length ? trunc.map(f => f.path).join(', ') : 'none detected');

// ── 2. what actually exists ───────────────────────────────────────────────────
H('2. Files on disk');
const byDir = {};
for (const f of files) {
  const d = f.path.includes('/') ? f.path.slice(0, f.path.indexOf('/')) : '(root)';
  (byDir[d] = byDir[d] || []).push(f);
}
for (const [d, fs_] of Object.entries(byDir)) {
  console.log('\n  ' + d + '/');
  for (const f of fs_.sort((a, b) => a.path.localeCompare(b.path))) {
    console.log('    ' + f.path.slice(d.length + 1).padEnd(46) +
      String(f.bytes).padStart(8) + '  ' + f.mtime.slice(0, 10) + (f.text === null ? '  [binary]' : ''));
  }
}

// ── 3. doc shape: table vs card ───────────────────────────────────────────────
H('3. Document shape (the Window needs the right parser per doc)');
for (const f of files.filter(f => f.text && f.path.endsWith('.md'))) {
  const tables = P.parseTables(f.text);
  const c3 = P.filledCards(P.parseCards(f.text, 3)).length;
  const c2 = P.filledCards(P.parseCards(f.text, 2)).length;
  const shape = tables.length && (c3 + c2) ? 'BOTH' : tables.length ? 'table' : (c3 + c2) ? 'card' : 'prose';
  console.log('  ' + f.path.padEnd(50) + shape.padEnd(6) +
    (tables.length ? tables.length + ' table(s) ' : '') + ((c3 + c2) ? (c3 + c2) + ' card(s)' : ''));
}

// ── 4. column drift ───────────────────────────────────────────────────────────
H('4. Column drift vs. templates');
let drift = 0;
for (const f of files.filter(f => f.text && f.path.endsWith('.md'))) {
  const key = P.templateKeyFor(f.path, templates);
  if (!templates[key]) { console.log('  ' + f.path.padEnd(50) + 'no matching template (' + key + ')'); continue; }
  const mine = P.parseTables(f.text).map(t => t.columns.join(' | '));
  const theirs = P.parseTables(templates[key]).map(t => t.columns.join(' | '));
  const gone = theirs.filter(t => !mine.includes(t));
  const extra = mine.filter(t => !theirs.includes(t));
  if (!gone.length && !extra.length) { console.log('  ' + f.path.padEnd(50) + 'matches template'); continue; }
  drift++;
  console.log('  ' + f.path.padEnd(50) + 'DRIFT');
  gone.forEach(t => console.log('      template table missing here: ' + t));
  extra.forEach(t => console.log('      table not in template:       ' + t));
}
console.log(drift ? '\n  → ' + drift + ' file(s) drifted. Parsers key off column names; update spine-parse.js or the template.'
                  : '\n  → no drift. Parsers will work as tested.');

// ── 5. assets and massing.json ────────────────────────────────────────────────
H('5. Assets and exports');
const assets = files.filter(f => /\/(images|diagrams|data)\//.test(f.path));
console.log('  asset folders in use:', [...new Set(assets.map(a => a.path.split('/').slice(0, 2).join('/')))].join(', ') || 'none');
for (const phase of ['1_Precedents', '2_Site', '3_Massing', '4_Space-Planning', '5_Materiality']) {
  const a = assets.filter(x => x.path.startsWith(phase + '/'));
  console.log('    ' + phase.padEnd(18) + (a.length ? a.length + ' file(s): ' + a.slice(0, 6).map(x => x.path.split('/').pop()).join(', ') : 'none'));
}
const mj = files.find(f => /massing\.json$/i.test(f.path));
if (!mj) {
  console.log('\n  massing.json: NOT FOUND — the Studio here predates the ⤓ Export JSON step,');
  console.log('                or it was never exported. Re-export before any 3D work.');
} else {
  try {
    const m = JSON.parse(mj.text);
    const need = ['id', 'x', 'z', 'w', 'd', 'h'];
    const bad = (m.volumes || []).filter(v => need.some(k => v[k] === undefined));
    console.log('\n  massing.json: found — ' + (m.volumes || []).length + ' volumes, units ' + (m.units || '?'));
    console.log('    site.lotPolygon: ' + (m.site && m.site.lotPolygon ? m.site.lotPolygon.length + ' pts' : 'MISSING'));
    console.log('    site.latLong:    ' + (m.site && m.site.latLong ? 'present' : 'MISSING (roadmap says it should be filled from the parcel geometry)'));
    console.log('    schema check:    ' + (bad.length ? bad.length + ' volume(s) missing required fields' : 'all volumes valid'));
  } catch (e) { console.log('\n  massing.json: found but does not parse — ' + e.message); }
}
const studio = files.find(f => /Massing-Studio\.html$/i.test(f.path));
console.log('  Massing-Studio.html: ' + (studio ? 'present (' + studio.path + ') — iframe target for the Window' : 'NOT FOUND'));

// ── 6. what the Window would show ─────────────────────────────────────────────
H('6. What the Project Window would show');
const get = suffix => files.find(f => f.path.endsWith(suffix));
const dF = get('01_Design-Drivers.md'), decF = get('02_Decision-Log.md'), qF = get('03_Open-Questions.md');
const drivers = dF ? P.readDrivers(dF.text) : { drivers: [], locked: false, lockedDate: null };
const decisions = decF ? P.readDecisions(decF.text) : [];
const questions = qF ? P.readOpenQuestions(qF.text) : [];
const state = P.inferState(files, templates);

console.log('  current phase :', state.currentPhase);
console.log('  drivers locked:', state.driversLocked ? 'yes (' + state.driversLockedDate + ')' : 'NO — no "**Locked YYYY-MM-DD**" line found in 01_Design-Drivers.md');
console.log('  phases        :');
for (const k of P.ORDER) console.log('      ' + k.padEnd(18) + state.phases[k].status);
console.log('\n  drivers (' + drivers.drivers.length + '):');
drivers.drivers.forEach(d => console.log('      ' + (d.n || '?') + '. ' + d.driver + (d.test ? '   [test: ' + d.test + ']' : '   [NO test stated]')));
console.log('\n  decisions: ' + decisions.length + '   open questions: ' + P.openOnly(questions).length + ' of ' + questions.length);

H('7. Conscience panel (what it would flag today)');
const pt = {};
for (const [k, suffix] of Object.entries({
  'client-discovery': '04a_Client-Profile-Household.md', site: 'Site-Details', precedents: 'Precedent-Board.md',
  massing: 'Massing-Options.md', 'space-planning': 'Program-Test-Fit.md', materiality: 'Material-Palette.md'
})) { const f = files.find(x => x.path.includes(suffix)); if (f && f.text) pt[k] = f.text; }
const tf = {};
for (const k of Object.keys(pt)) {
  const f = files.find(x => x.path.includes(Object.entries({
    'client-discovery': '04a_Client-Profile-Household.md', site: 'Site-Details', precedents: 'Precedent-Board.md',
    massing: 'Massing-Options.md', 'space-planning': 'Program-Test-Fit.md', materiality: 'Material-Palette.md'
  }).find(([kk]) => kk === k)[1]));
  if (f) tf[k] = templates[P.templateKeyFor(f.path, templates)];
}
const findings = A.audit({
  drivers, decisions, questions, state, files, phaseTexts: pt, templatesFor: tf,
  boardText: (get('Precedent-Board.md') || {}).text, massingText: (get('Massing-Options.md') || {}).text
});
if (!findings.length) console.log('  nothing flagged.');
findings.forEach(f => console.log('  [' + f.severity + '] ' + f.text));

// ── 8. optional: write state.json ─────────────────────────────────────────────
if (WRITE) {
  H('8. Writing 0_Spine/state.json');
  const out = {
    project: path.basename(PROJ),
    updated: new Date().toISOString().slice(0, 10),
    driversLocked: state.driversLocked,
    driversLockedDate: state.driversLockedDate,
    currentPhase: state.currentPhase,
    phases: Object.fromEntries(P.ORDER.map(k => [k, {
      status: state.phases[k].status,
      updated: state.phases[k].updated ? state.phases[k].updated.slice(0, 10) : null
    }]))
  };
  const dest = path.join(PROJ, '0_Spine', 'state.json');
  fs.writeFileSync(dest, JSON.stringify(out, null, 2) + '\n');
  console.log('  wrote ' + dest);
  console.log('  Review it — inference is a starting point, not the truth. Correct anything wrong,');
  console.log('  then the skill maintains it from here.');
} else {
  console.log('\n(run again with --write-state to generate 0_Spine/state.json from this inference)');
}

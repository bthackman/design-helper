// spine-parse.js — parsing + state inference for the Project Window.
// Pure functions over strings and a file listing, so it runs identically in Node
// (for testing) and in the browser against the File System Access API.

// ---------- markdown tables ----------

// Split on unescaped pipes. Driver cells contain things like "envelope\|loss",
// and any cell may hold an em-dash or a ✓ / ~ / ✗ score glyph.
function splitRow(line) {
  const cells = [];
  let cur = '';
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '\\' && line[i + 1] === '|') { cur += '|'; i++; continue; }
    if (c === '|') { cells.push(cur); cur = ''; continue; }
    cur += c;
  }
  cells.push(cur);
  if (cells.length && cells[0].trim() === '') cells.shift();
  if (cells.length && cells[cells.length - 1].trim() === '') cells.pop();
  return cells.map(s => s.trim());
}

const isDivider = l => /^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$/.test(l) && l.includes('-');

// Every table in the doc, each tagged with its preceding heading — so a file with
// two tables (Drivers + Parked) doesn't collapse into one.
function parseTables(md) {
  const lines = (md || '').split(/\r?\n/);
  const tables = [];
  let heading = null;
  for (let i = 0; i < lines.length; i++) {
    const h = lines[i].match(/^#{1,6}\s+(.*)$/);
    if (h) { heading = h[1].trim(); continue; }
    if (lines[i].includes('|') && isDivider(lines[i + 1] || '')) {
      const cols = splitRow(lines[i]);
      const rows = [];
      let j = i + 2;
      for (; j < lines.length && lines[j].includes('|') && lines[j].trim(); j++) {
        const cells = splitRow(lines[j]);
        const row = {};
        cols.forEach((c, k) => { row[c] = cells[k] !== undefined ? cells[k] : ''; });
        rows.push(row);
      }
      tables.push({ heading, columns: cols, rows });
      i = j - 1;
    }
  }
  return tables;
}

const BLANK = /^(|—|-|n\/a|tbd)$/i;
const isTemplateRow = row =>
  Object.entries(row).every(([k, v]) => /^#$/.test(k) || BLANK.test(String(v).trim()));
const realRows = t => t.rows.filter(r => !isTemplateRow(r));

function normalize(t) {
  return (t || '').replace(/\[.*?\]/g, '').replace(/\s+/g, ' ').trim();
}

const cellKey = r => Object.entries(r)
  .filter(([k]) => !/^#$/.test(k))
  .map(([, v]) => String(v).trim())
  .join('\u0001');

// Templates ship WITH scaffolding rows: the client-profile matrix carries 12 prompt
// questions, Site-Details carries 12 category labels, the adjacency matrix carries
// its own axis. A non-blank row is therefore NOT evidence of work. A row is real
// only if it differs from the template's corresponding row, or has no counterpart.
function rowsBeyondTemplate(table, tplTable) {
  if (!tplTable) return realRows(table);
  const tplKeys = new Set(tplTable.rows.map(cellKey));
  return table.rows.filter(r => !isTemplateRow(r) && !tplKeys.has(cellKey(r)));
}

function looksWorked(text, templateText) {
  if (!text) return false;
  const tables = parseTables(text);
  const tpl = templateText ? parseTables(templateText) : [];
  const match = (t, i) =>
    tpl.find(x => x.columns.join('|') === t.columns.join('|')) || tpl[i];
  if (tables.some((t, i) => rowsBeyondTemplate(t, match(t, i)).length > 0)) return true;
  for (const lvl of [3, 2]) {
    const tplCards = templateText ? parseCards(templateText, lvl) : [];
    if (cardsBeyondTemplate(parseCards(text, lvl), tplCards).length > 0) return true;
  }
  if (templateText == null) return normalize(text).length > 400;
  const a = normalize(text), b = normalize(templateText);
  return a !== b && a.length > b.length + 200;
}

// ---------- card documents ----------
// Precedent-Board, Massing-Options and Material-Palette are NOT tables. They are
// '### Title' headings followed by '- **Label:** value' bullets. Second parser, second
// shape — a table-only reader reports these phases as empty even when they are full.
function parseCards(md, level = 3) {
  const re = new RegExp('^#{' + level + '}\\s+(.*)$');
  const lines = (md || '').split(/\r?\n/);
  const cards = [];
  let cur = null;
  for (const line of lines) {
    const h = line.match(re);
    if (h) { cur = { title: h[1].trim(), fields: {}, images: [], body: [] }; cards.push(cur); continue; }
    if (/^#{1,6}\s/.test(line)) { cur = null; continue; }
    if (!cur) continue;
    const img = line.match(/!\[[^\]]*\]\(([^)]*)\)/);
    if (img && img[1].trim() && !/\/$/.test(img[1].trim())) cur.images.push(img[1].trim());
    const f = line.match(/^\s*[-*]\s*\*\*(.+?):?\*\*:?\s*(.*)$/);
    // Keep the FIRST non-empty value for a label. A card can repeat '**Metrics:**'
    // (real value plus a leftover placeholder line); last-wins would lose the real one.
    if (f) {
      const k = f[1].trim(), v = f[2].trim();
      if (!cur.fields[k]) cur.fields[k] = v;
      continue;
    }
    if (line.trim()) cur.body.push(line.trim());
  }
  return cards;
}

const filledCards = cards => cards.filter(c =>
  !/^\[.*\]/.test(c.title) &&
  (Object.values(c.fields).some(v => v && !/^\[.*\]$/.test(v)) || c.images.length));

// Template cards carry placeholder VALUES ('active / parked / dead'), not just labels,
// so "has a non-empty field" is not evidence of work. Diff against the template card.
function cardsBeyondTemplate(cards, tplCards) {
  const tplVals = new Set();
  (tplCards || []).forEach(c => {
    Object.entries(c.fields).forEach(([k, v]) => tplVals.add(k + '\u0001' + v));
    c.images.forEach(i => tplVals.add('img\u0001' + i));
  });
  const tplTitles = new Set((tplCards || []).map(c => c.title));
  return cards.filter(c => {
    if (/^\[.*\]/.test(c.title)) return false;
    if (!tplTitles.has(c.title) && !/^\s*$/.test(c.title)) {
      if (Object.values(c.fields).some(v => v) || c.images.length) return true;
    }
    const newField = Object.entries(c.fields)
      .some(([k, v]) => v && !/^\[.*\]$/.test(v) && !tplVals.has(k + '\u0001' + v));
    const newImage = c.images.some(i => !tplVals.has('img\u0001' + i));
    return newField || newImage;
  });
}

// ---------- spine readers ----------

// The template's columns are '# | Driver | Why it matters here | How we'll know
// it's working'. A real project is free to rename or drop those two — Nonimuss
// uses '# | Driver | Test | Origin' — so only 'Driver' is required to find the
// table; the rest is matched by heuristic, and anything left over (like 'Origin')
// is kept in `extra` rather than silently dropped.
function readDrivers(md) {
  const tables = parseTables(md);
  const main = tables.find(t => t.columns.some(c => /^driver$/i.test(c)));
  const parked = tables.find(t => /parked/i.test(t.heading || ''));
  const lock = (md || '').match(/\*\*(?:Status:\s*)?LOCKED\s+(\d{4}-\d{2}-\d{2})\*\*/i);
  const testCol = main && main.columns.find(c => /how we'?ll know|^test$/i.test(c));
  const whyCol = main && main.columns.find(c => /why/i.test(c));
  return {
    locked: !!lock,
    lockedDate: lock ? lock[1] : null,
    drivers: main ? realRows(main).map(r => {
      const known = new Set(['#', 'Driver', testCol, whyCol].filter(Boolean));
      const extra = {};
      main.columns.forEach(c => { if (!known.has(c)) extra[c] = r[c] || ''; });
      return {
        n: r['#'] || '',
        driver: r['Driver'] || '',
        why: whyCol ? (r[whyCol] || '') : '',
        test: testCol ? (r[testCol] || '') : '',
        extra
      };
    }) : [],
    parked: parked ? realRows(parked) : []
  };
}

// Locates the actual decisions table (matched by column heading, same rule readDecisions()
// uses) rather than "the first pipe-table divider in the file" — a file that ever grows a
// second table would otherwise silently receive an appended row in the wrong place.
// Returns 0-indexed line numbers, or null if no matching table exists.
function findTableLineRange(md, columnPredicate) {
  const lines = (md || '').split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('|') && isDivider(lines[i + 1] || '')) {
      const cols = splitRow(lines[i]);
      if (columnPredicate(cols)) {
        let j = i + 2;
        while (j < lines.length && lines[j].includes('|') && lines[j].trim()) j++;
        return { headerLine: i, dividerLine: i + 1, firstRowLine: i + 2, endLine: j };
      }
    }
  }
  return null;
}

function readDecisions(md) {
  const t = parseTables(md).find(t => t.columns.some(c => /decision/i.test(c)));
  if (!t) return [];
  return realRows(t).map(r => ({
    date: r['Date'] || '', phase: r['Phase'] || '', decision: r['Decision'] || '',
    rationale: r['Rationale'] || '', rejected: r['Rejected alternatives'] || ''
  })).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
}

function readOpenQuestions(md) {
  const t = parseTables(md).find(t => t.columns.some(c => /question/i.test(c)));
  if (!t) return [];
  return realRows(t).map(r => ({
    n: r['#'] || '', question: r['Question'] || '', raisedIn: r['Raised in'] || '',
    blocks: r['Blocks'] || '', next: r['Owner/next step'] || '',
    status: (r['Status'] || 'open').toLowerCase()
  }));
}

const openOnly = qs => qs.filter(q => q.status !== 'resolved' && q.status !== 'closed');

// ---------- state inference (fallback when state.json is missing) ----------

const PHASES = [
  { key: 'client-discovery', dir: '0_Spine',          probe: /^04[ab]?_Client-Profile/ },
  { key: 'site',             dir: '2_Site',           probe: /^Site-(Details|Search)/ },
  { key: 'precedents',       dir: '1_Precedents',     probe: /^Precedent-Board/ },
  { key: 'massing',          dir: '3_Massing',        probe: /^Massing-Options/ },
  { key: 'space-planning',   dir: '4_Space-Planning', probe: /^Program-Test-Fit/ },
  { key: 'materiality',      dir: '5_Materiality',    probe: /^Material-Palette/ }
];

// '2_Site/Site-Details_1412-14-St.md' -> '2_Site/Site-Details.md'.
// Exact match wins; otherwise strip trailing _suffix segments one at a time until a
// template matches. Never blindly strips — '04a_Client-Profile-Household.md' must NOT
// collapse to '04a.md'.
function templateKeyFor(relPath, templates = {}) {
  const parts = relPath.split('/');
  const dir = parts[parts.length - 2];
  let file = parts[parts.length - 1];
  if (templates[dir + '/' + file] || !Object.keys(templates).length) return dir + '/' + file;
  const ext = file.slice(file.lastIndexOf('.'));
  let stem = file.slice(0, file.lastIndexOf('.'));
  while (stem.includes('_')) {
    stem = stem.slice(0, stem.lastIndexOf('_'));
    if (templates[dir + '/' + stem + ext]) return dir + '/' + stem + ext;
  }
  return dir + '/' + file;
}

const ORDER = ['client-discovery', 'site', 'precedents', 'massing', 'space-planning', 'materiality'];

// Note on `looping-back`: this inference path can never produce it — it only ever
// assigns not-started/in-progress/complete (below), by construction, since "a phase
// looped back" isn't something file contents alone can distinguish from "in progress."
// The status is real and reachable, but only through a valid state.json — SKILL.md's
// spine section already instructs the skill to write it "whenever a phase loops back."
// Confirmed 2026-09-07: not a bug in this file, just a boundary of what inference can know.
function inferState(files, templates = {}) {
  const byPath = Object.fromEntries(files.map(f => [f.path, f]));
  const df = byPath['0_Spine/01_Design-Drivers.md'];
  const drivers = df ? readDrivers(df.text) : { locked: false, lockedDate: null };

  const phases = {};
  for (const p of PHASES) {
    const docs = files.filter(f => f.path.startsWith(p.dir + '/') &&
      p.probe.test(f.path.slice(p.dir.length + 1)));
    const worked = docs.some(d => looksWorked(d.text, templates[templateKeyFor(d.path, templates)]));
    const assets = files.filter(f => f.path.startsWith(p.dir + '/') &&
      /\/(images|diagrams|data)\//.test(f.path));
    phases[p.key] = {
      status: worked ? 'in-progress' : 'not-started',
      docs: docs.map(d => d.path),
      assets: assets.map(a => a.path),
      updated: docs.concat(assets).map(f => f.mtime).sort().pop() || null
    };
  }

  const worked = ORDER.filter(k => phases[k].status !== 'not-started');
  worked.slice(0, -1).forEach(k => { phases[k].status = 'complete'; });

  return {
    inferred: true,
    driversLocked: drivers.locked,
    driversLockedDate: drivers.lockedDate,
    currentPhase: worked[worked.length - 1] || 'client-discovery',
    phases
  };
}

// state.json is a pointer, not the authority. If any project file is newer than it,
// say so rather than trusting it silently.
//
// It's also not guaranteed to match the current schema — a project's state.json may
// predate a spine change (found 2026-09-06: a real project's file used a `phaseStatus`
// key with narrative string values instead of `phases: {key:{status,updated}}`, which
// used to reach `Object.entries(undefined)` downstream and throw, blanking the whole
// Window). A malformed/legacy `phases` shape now degrades to inferred state instead —
// the same "don't trust it silently" reasoning `stale` already exists for, just applied
// to the shape of the data instead of its age.
function reconcile(stateJson, stateMtime, files, templates = {}) {
  const newest = files.filter(f => !f.path.endsWith('state.json'))
    .map(f => f.mtime).sort().pop();
  const stale = !!(newest && stateMtime && newest > stateMtime);

  const phases = stateJson && stateJson.phases;
  const validPhases = phases && typeof phases === 'object' &&
    ORDER.some(k => phases[k] && typeof phases[k].status === 'string');

  if (!validPhases) {
    const inferred = inferState(files, templates);
    return {
      ...inferred,
      schemaMismatch: true,
      status: (stateJson && stateJson.status) || 'active',
      dormantReason: (stateJson && stateJson.dormantReason) || null,
      stale, newestFile: newest
    };
  }
  return { ...stateJson, inferred: false, stale, newestFile: newest };
}

// Dual-mode: Node (test suites, require()) and plain <script> in the Window.
// IIFE so the export object's name never leaks into the shared global scope —
// spine-parse.js and audit.js are both loaded as classic <script> tags in the
// Window and would otherwise collide on a top-level `const` of the same name.
(function () {
  const exported = {
    splitRow, parseTables, parseCards, filledCards, cardsBeyondTemplate, realRows, rowsBeyondTemplate, looksWorked, normalize,
    templateKeyFor, readDrivers, readDecisions, readOpenQuestions, openOnly, findTableLineRange,
    inferState, reconcile, PHASES, ORDER
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = exported;
  else window.SpineParse = exported;
})();

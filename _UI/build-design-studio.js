/* Build the combined Design Studio (Step 4, 2026-09-09) — DEV TOOLING, not shipped.
 *
 * Massing Studio and Test-Fit Studio stay the authored, independently-openable files they
 * have always been. This script MERGES them into one page so both live object graphs sit in
 * one runtime — the prerequisite for the live containment work in Steps 5-6. Re-run it after
 * editing either source Studio; never hand-edit the generated file.
 *
 * Why a generated merge rather than iframes: verified 2026-09-09 that Chrome blocks
 * cross-frame scripting between file:// documents (origin "null" -> SecurityError). Frames
 * only work behind --allow-file-access-from-files, which breaks double-click-to-open. So the
 * two Studios have to share one document, which means resolving their DOM/CSS collisions.
 *
 * What it resolves (measured, not guessed):
 *   - 11 shared DOM ids (capBar capNote exportModal exportText hint left right topbar view
 *     leftToggle rightToggle). Massing's are prefixed ms-; Test-Fit's are left alone.
 *     leftToggle/rightToggle added 2026-09-10 for Massing's new panel-collapse toggle
 *     (HANDOFF "Panel crowding"); Massing's own toggle functions are named distinctly
 *     (toggleMsLeft/toggleMsRight, not Test-Fit's togglePanel) since a `which`-parameterised
 *     getElementById call can't be seen by this script's literal-string id-prefixing.
 *   - 21 shared CSS selectors. Each Studio's rules are scoped under its own pane, and the
 *     viewport-relative bits (:root, html/body, position:fixed, 100vh) are rewritten to be
 *     pane-relative so two full-screen layouts can coexist.
 *   - Massing sizes its renderer from innerWidth/innerHeight; in a pane that must be the
 *     pane's own box.
 * JS globals needed no work: measured at 0 collisions across 157 top-level names after the
 * Step 3 renames (view->viewEl, drag->orbitDrag, exportJSON->export{Massing,TestFit}JSON).
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SRC = {
  massing: path.join(ROOT, 'Projects/Nonimuss-Residence/3_Massing/Massing-Studio.html'),
  testfit: path.join(ROOT, 'Projects/Nonimuss-Residence/4_Space-Planning/Test-Fit-Studio.html'),
};
const OUT = path.join(ROOT, 'Projects/Nonimuss-Residence/Design-Studio.html');

const SHARED_IDS = ['capBar','capNote','exportModal','exportText','hint','left','right','topbar','view','leftToggle','rightToggle'];

function extract(file) {
  const src = fs.readFileSync(file, 'utf8');
  const style = (src.match(/<style>([\s\S]*?)<\/style>/) || [,''])[1];
  const body = (src.match(/<body>([\s\S]*)<\/body>/) || [,''])[1];
  const cdn = [...body.matchAll(/<script src="([^"]+)"><\/script>/g)].map(m => m[1]);
  const inline = [...body.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  const markup = body.replace(/<script[\s\S]*?<\/script>/g, '').trim();
  return { style, markup, inline, cdn };
}

/* Prefix a set of ids everywhere they appear: CSS selectors, id="" attributes and
 * getElementById/querySelector lookups. Explicit allowlist only — a blind /#(\w+)/ would
 * corrupt hex colours like #eae6da. */
function prefixIds(text, ids, prefix) {
  for (const id of ids) {
    const p = prefix + id;
    text = text.replace(new RegExp('#' + id + '(?![\\w-])', 'g'), '#' + p);
    text = text.replace(new RegExp('id="' + id + '"', 'g'), 'id="' + p + '"');
    text = text.replace(new RegExp("getElementById\\('" + id + "'\\)", 'g'), "getElementById('" + p + "')");
    text = text.replace(new RegExp('getElementById\\("' + id + '"\\)', 'g'), 'getElementById("' + p + '")');
  }
  return text;
}

/* Scope every rule under `paneSel` and make viewport-relative styling pane-relative. */
function scopeCss(css, paneSel) {
  const out = [];
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let m;
  while ((m = re.exec(css)) !== null) {
    const rawSel = m[1].replace(/\/\*[\s\S]*?\*\//g, '').trim();
    if (!rawSel) continue;
    let decls = m[2]
      .replace(/position\s*:\s*fixed/g, 'position:absolute')  // pin to the pane, not the window
      .replace(/100vh/g, '100%');
    const sels = rawSel.split(',').map(s => s.trim()).filter(Boolean).map(s => {
      if (s === ':root' || s === 'html' || s === 'body') return paneSel;
      if (s === '*') return paneSel + ' *';
      return paneSel + ' ' + s;
    });
    out.push(sels.join(', ') + '{' + decls + '}');
  }
  return out.join('\n');
}

const M = extract(SRC.massing);
const T = extract(SRC.testfit);

// --- Massing: de-collide ids, then make the renderer size to its pane ---
M.style = prefixIds(M.style, SHARED_IDS, 'ms-');
M.markup = prefixIds(M.markup, SHARED_IDS, 'ms-');
M.inline = prefixIds(M.inline, SHARED_IDS, 'ms-');
M.inline = M.inline
  .replace(/new THREE\.PerspectiveCamera\(45,innerWidth\/innerHeight/,
           'new THREE.PerspectiveCamera(45,paneW()/paneH()')
  .replace(/renderer\.setSize\(innerWidth,innerHeight\)/g, 'renderer.setSize(paneW(),paneH())')
  .replace(/camera\.aspect=innerWidth\/innerHeight/g, 'camera.aspect=paneW()/paneH()')
  /* layoutPanels() looks its panels up from an ARRAY OF STRING LITERALS, which the
   * id-prefixing above cannot see. Left unpatched this silently repositions Test-Fit's
   * #left/#right (which keep their names) while Massing's own panels stay at top:64px,
   * covering its own wrapped topbar. Caught by the Step 4 click-through, not by reading. */
  .replace(/\['left','right'\]/g, "['ms-left','ms-right']")
  /* Same reason as the CSS 100vh rewrite: these are pane heights now, not window heights. */
  .replace(/calc\(100vh - /g, 'calc(100% - ');
const PANE_HELPERS = `
/* Step 4: the 3D pane is a box on a shared page, not the whole window. */
function paneW(){ const e=document.getElementById('ms-pane'); return (e&&e.clientWidth)||innerWidth; }
function paneH(){ const e=document.getElementById('ms-pane'); return (e&&e.clientHeight)||innerHeight; }
`;

const cdn = [...new Set([...M.cdn, ...T.cdn])];

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Nonimuss — Design Studio (Massing + Test-Fit)</title>
<!-- GENERATED FILE — do not hand-edit. Built by _UI/build-design-studio.js from
     3_Massing/Massing-Studio.html and 4_Space-Planning/Test-Fit-Studio.html. -->
<style>
  html,body{margin:0;height:100%;font-family:"Segoe UI",Arial,sans-serif;background:#dcd7c8;overflow:hidden}
  #shell{display:flex;flex-direction:column;height:100%}
  #shellbar{flex:0 0 auto;display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;padding:6px 12px;
    background:#2f2b24;color:#f0ece1;font-size:12.5px}
  #shellbar b{font-size:13px}
  #shellbar .sp{flex:1}
  #shellbar button{font:inherit;font-size:11.5px;padding:3px 9px;border:1px solid #6b6459;
    background:#413b31;color:#f0ece1;border-radius:6px;cursor:pointer}
  #shellbar button:hover{background:#544c40}
  #panes{flex:1 1 auto;display:flex;min-height:0}
  .pane{position:relative;overflow:hidden;min-width:0;background:#eae6da}
  #ms-pane{flex:1.15 1 0}
  #tf-pane{flex:1 1 0;border-left:3px solid #cfc7b4}
  #panes.stack{flex-direction:column}
  #panes.stack #tf-pane{border-left:none;border-top:3px solid #cfc7b4}
  #panes.only-ms #tf-pane,#panes.only-tf #ms-pane{display:none}
  /* Massing's own CSS sets no stacking order; Test-Fit's does. In a narrow pane its topbar
     wraps to several rows, so it must paint above its side panels or its own controls
     become unclickable. */
  #ms-pane #ms-topbar{z-index:6}
  #ms-pane #ms-left,#ms-pane #ms-right{z-index:4}
</style>
<style>/* ---- Massing Studio, scoped ---- */
${scopeCss(M.style, '#ms-pane')}
</style>
<style>/* ---- Test-Fit Studio, scoped ---- */
${scopeCss(T.style, '#tf-pane')}
</style>
</head>
<body>
<div id="shell">
  <div id="shellbar">
    <b>Nonimuss — Design Studio</b>
    <span title="Stage 1 = a coarse siting box, steered here in Massing (left). Stage 2 = a box reshaped to fit real rooms -- arrange rooms in Test-Fit (right); when one outgrows its box, a badge and a &quot;Reshape to fit&quot; button appear on the left. Stage is per-volume, not a project-wide mode -- House can be Stage 2 while Pool stays Stage 1, and that's the normal case.">ⓘ Stage 1 (siting, left) vs Stage 2 (shaped by rooms, right → left)</span>
    <span class="sp"></span>
    <span>Layout</span>
    <button onclick="setPanes('')">Side by side</button>
    <button onclick="setPanes('stack')">Stacked</button>
    <button onclick="setPanes('only-ms')">Massing only</button>
    <button onclick="setPanes('only-tf')">Plan only</button>
  </div>
  <div id="panes">
    <div class="pane" id="ms-pane">
${M.markup}
    </div>
    <div class="pane" id="tf-pane">
${T.markup}
    </div>
  </div>
</div>
${cdn.map(s => `<script src="${s}"></script>`).join('\n')}
<script>
${PANE_HELPERS}
function setPanes(mode){
  document.getElementById('panes').className = mode;
  dispatchEvent(new Event('resize'));   // both Studios already re-layout on resize
}
// Lets an embedding page (Project-Window.html's phase-rail iframe) pick a default pane
// via ?pane=only-ms|only-tf|stack -- e.g. the Massing phase tab opens straight into the
// Massing-only view of this SAME merged file, not a separate standalone Studio, so
// promotion (which only exists here, in the shared runtime) is reachable from the normal
// phase-rail flow. Falls back to side-by-side (mode:'') if the param is absent/unknown.
(function(){
  const p = new URLSearchParams(location.search).get('pane');
  if (p) setPanes(p);
})();
</script>
<script>/* ===== Massing Studio ===== */
${M.inline}
</script>
<script>/* ===== Test-Fit Studio ===== */
${T.inline}
</script>
</body>
</html>
`;

fs.writeFileSync(OUT, html, 'utf8');
console.log('wrote ' + OUT);
console.log('  massing: ' + M.markup.split('\n').length + ' markup lines, ' + M.inline.split('\n').length + ' script lines');
console.log('  testfit: ' + T.markup.split('\n').length + ' markup lines, ' + T.inline.split('\n').length + ' script lines');
console.log('  shared cdn: ' + cdn.length);

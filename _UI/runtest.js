const fs=require('fs'),path=require('path'),P=require('./spine-parse.js');
function walk(d,base=d,out=[]){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);
 if(e.isDirectory())walk(p,base,out);else{const rel=path.relative(base,p).split(path.sep).join('/');
 const bin=/\.(jpg|jpeg|png|gif|webp|blend|dyn)$/i.test(rel);
 out.push({path:rel,text:bin?null:fs.readFileSync(p,'utf8'),mtime:fs.statSync(p).mtime.toISOString()});}}return out;}

function check(name,cond,detail){console.log((cond?'PASS':'FAIL').padEnd(5),name,detail?'— '+detail:'');if(!cond)process.exitCode=1;}

// --- filled project ---
const files=walk('testproj');
const D=P.readDrivers(files.find(f=>f.path.endsWith('01_Design-Drivers.md')).text);
check('drivers parsed',D.drivers.length===4,D.drivers.length+' drivers');
check('escaped pipe survives',D.drivers[0].why.includes('envelope|loss'),JSON.stringify(D.drivers[0].why));
check('test column found',/40 kWh/.test(D.drivers[0].test));
check('lock detected',D.locked&&D.lockedDate==='2026-08-14',D.lockedDate);
check('parked table separate',D.parked.length===1&&!D.drivers.some(d=>/Passive/.test(d.driver)));

const DEC=P.readDecisions(files.find(f=>f.path.endsWith('02_Decision-Log.md')).text);
check('decisions parsed',DEC.length===3);
check('newest first',DEC[0].date==='2026-08-27',DEC[0].date);
check('score glyphs survive',DEC[0].rationale.includes('✓'));

const Q=P.readOpenQuestions(files.find(f=>f.path.endsWith('03_Open-Questions.md')).text);
check('questions parsed',Q.length===4);
check('open filter works',P.openOnly(Q).length===3);
check('em-dash cell kept',Q[2].next==='—',JSON.stringify(Q[2].next));

const S=P.inferState(files);

check('drivers locked',S.driversLocked===true);
check('site marked complete',S.phases['site'].status==='complete',S.phases['site'].status);

check('massing assets found',S.phases['massing'].assets.length===1,JSON.stringify(S.phases['massing'].assets));
check('site data found',S.phases['site'].assets.some(a=>a.endsWith('.geojson')));

// --- untouched template tree: everything must read as not-started ---
const blank=walk('design-helper/_templates');
const B=P.inferState(blank);
const started=Object.entries(B.phases).filter(([k,v])=>v.status!=='not-started').map(([k])=>k);

check('blank template: drivers not locked',B.driversLocked===false);

// --- massing.json against the interchange schema ---
const M=JSON.parse(fs.readFileSync('testproj/3_Massing/massing.json','utf8'));
check('massing volumes',M.volumes.length===3);
check('lotPolygon present',Array.isArray(M.site.lotPolygon)&&M.site.lotPolygon.length===4);
const missing=M.volumes.filter(v=>['id','x','z','w','d','h'].some(k=>typeof v[k]==='undefined'));
check('required volume fields',missing.length===0);
check('optional rot90 tolerated',M.volumes[1].rot90===undefined);
const gfa=M.volumes.reduce((s,v)=>s+v.w*v.d*Math.max(1,Math.round(v.h/3.2)),0);
check('GFA computable from schema',gfa>0,gfa.toFixed(1)+' m²');

// --- geojson ---
const G=JSON.parse(fs.readFileSync('testproj/2_Site/data/parcel.geojson','utf8'));
check('geojson polygon ring closed',(()=>{const r=G.geometry.coordinates[0];return r[0][0]===r[r.length-1][0]&&r[0][1]===r[r.length-1][1];})());

// --- re-run inference with templates supplied ---
const tpl={}; for(const f of walk('design-helper/_templates')) if(f.text) tpl[f.path]=f.text;
const S2=P.inferState(files,tpl), B2=P.inferState(blank,tpl);
console.log('\n--- with template comparison ---');
check('current phase = massing',S2.currentPhase==='massing',S2.currentPhase);
check('space planning not started',S2.phases['space-planning'].status==='not-started',S2.phases['space-planning'].status);
check('client discovery complete',S2.phases['client-discovery'].status==='complete',S2.phases['client-discovery'].status);
check('blank tree: nothing started',Object.values(B2.phases).every(v=>v.status==='not-started'),
      Object.entries(B2.phases).filter(([k,v])=>v.status!=='not-started').map(([k])=>k).join(',')||'none');

const S3=P.inferState(files,tpl);
console.log('\n--- with card parsing ---');
check('precedents detected',S3.phases['precedents'].status!=='not-started',S3.phases['precedents'].status);
check('massing detected',S3.phases['massing'].status!=='not-started',S3.phases['massing'].status);
check('current phase = massing',S3.currentPhase==='massing',S3.currentPhase);
check('client discovery complete',S3.phases['client-discovery'].status==='complete',S3.phases['client-discovery'].status);
const B3=P.inferState(blank,tpl);
check('blank tree still clean',Object.values(B3.phases).every(v=>v.status==='not-started'),
      Object.entries(B3.phases).filter(([k,v])=>v.status!=='not-started').map(([k])=>k).join(',')||'none');
const cards=P.parseCards(files.find(f=>f.path.endsWith('Precedent-Board.md')).text);
check('precedent card fields read',P.filledCards(cards)[0].fields['Why it\u2019s relevant']!==undefined||P.filledCards(cards)[0].fields["Why it's relevant"]!==undefined,
      JSON.stringify(P.filledCards(cards)[0]?.title));
check('precedent image path read',P.filledCards(cards)[0].images[0]==='images/keeper-01.jpg',JSON.stringify(P.filledCards(cards)[0]?.images));

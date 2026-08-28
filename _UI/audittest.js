const fs=require('fs'),path=require('path'),P=require('./spine-parse.js'),A=require('./audit.js');
function walk(d,base=d,out=[]){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);
 if(e.isDirectory())walk(p,base,out);else{const rel=path.relative(base,p).split(path.sep).join('/');
 const bin=/\.(jpg|jpeg|png|gif|webp)$/i.test(rel);
 out.push({path:rel,text:bin?null:fs.readFileSync(p,'utf8'),mtime:fs.statSync(p).mtime.toISOString()});}}return out;}
const check=(n,c,d)=>{console.log((c?'PASS':'FAIL').padEnd(5),n,d?'— '+d:'');if(!c)process.exitCode=1;};
const files=walk('testproj'), tpl={}; for(const f of walk('design-helper/_templates')) if(f.text) tpl[f.path]=f.text;
const get=s=>files.find(f=>f.path.endsWith(s));
const drivers=P.readDrivers(get('01_Design-Drivers.md').text);
const decisions=P.readDecisions(get('02_Decision-Log.md').text);
const questions=P.readOpenQuestions(get('03_Open-Questions.md').text);
const state=P.inferState(files,tpl);
const phaseTexts={site:get('Site-Details.md').text,precedents:get('Precedent-Board.md').text,
  massing:get('Massing-Options.md').text,'client-discovery':get('04a_Client-Profile-Household.md').text};
const templatesFor={site:tpl['2_Site/Site-Details.md'],precedents:tpl['1_Precedents/Precedent-Board.md'],
  massing:tpl['3_Massing/Massing-Options.md'],'client-discovery':tpl['0_Spine/04a_Client-Profile-Household.md']};
const F=A.audit({drivers,decisions,questions,state,files,phaseTexts,templatesFor,
  boardText:get('Precedent-Board.md').text,massingText:get('Massing-Options.md').text});
console.log(F.map(f=>`  [${f.severity}] ${f.text}`).join('\n'));
check('findings produced',F.length>0,F.length+' findings');
check('high severity first',F[0].severity==='high');
check('blocking question caught',F.some(f=>f.kind==='blocking-question'&&/rear lane/.test(f.text)));
check('untested driver caught',F.some(f=>f.kind==='untested-driver'&&/Aging in place/.test(f.text)));
check('driver that IS discussed not flagged',!F.some(f=>/Zero corridor/.test(f.text)),'zero-corridor appears in a decision');
check('orphan precedent caught',F.some(f=>f.kind==='orphan-card'&&/Precedent/.test(f.text)));
check('changed-since-lock caught',F.some(f=>f.kind==='changed-since-lock'));
const moved=A.sinceLastOpen(files,'2020-01-01T00:00:00.000Z');
check('since-last-open lists files',moved.length===files.length,moved.length+' files');
check('since-last-open empty when current',A.sinceLastOpen(files,'2099-01-01T00:00:00.000Z').length===0);

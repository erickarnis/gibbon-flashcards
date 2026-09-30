// Build a local design preview, never an Anki package. Run from the repo root.
import fs from 'node:fs';
import path from 'node:path';

const out = 'anki-layout';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function inline(s) {
  return esc(s).replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, target) => {
    if (!/^(https?:\/\/|sources\/)/.test(target)) throw new Error(`Unexpected link: ${target}`);
    return `<a href="${target.startsWith('sources/') ? '../' : ''}${target}">${label}</a>`;
  }).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>');
}
const cards = new Map();
for (const file of fs.readdirSync('.').filter(f => /^\d.*\.md$/.test(f))) {
  for (const chunk of fs.readFileSync(file, 'utf8').split(/(?=^### \d+\.)/m).slice(1)) {
    const id = chunk.match(/<!-- ID: (.+?) -->/)?.[1];
    const fields = Object.fromEntries([...chunk.matchAll(/^\*\*(Q|A|More|Gibbon|Sources):\*\* (.+)$/gm)].map(([,k,v]) => [k,inline(v)]));
    cards.set(id, {file, ...fields});
  }
}
const people = new Map(JSON.parse(fs.readFileSync('sources/portraits/manifest.json', 'utf8')).map(p => [p.id,p]));
const captions = JSON.parse(fs.readFileSync('anki-layout/portrait-captions.json', 'utf8'));
// Deliberate sample associations, not a proposed mapping for the whole deck.
const samples = [
  ['gibbon-01-nerva-accession','One picture + quotation',[['nerva','Emperor from AD 96']]],
  ['gibbon-01-nerva-trajan','Two pictures + context',[['nerva','Adopting emperor'],['trajan','Adopted heir']]],
  ['gibbon-01-trajan-column','Picture + quotation + context',[['trajan','Emperor whose victories are commemorated']]],
  ['gibbon-03-tetrarchy-failure','Four pictures + long quotation',[['diocletian','Augustus'],['maximian','Augustus'],['galerius','Caesar'],['constantius-chlorus','Caesar']]],
  ['gibbon-00-julian-theodosius','Six pictures + sequence',[['julian-emperor','Emperor'],['jovian-emperor','Emperor'],['valentinian-i','Western emperor'],['valens','Eastern emperor'],['gratian','Western emperor'],['theodosius-i','Eastern emperor']]],
  ['gibbon-00-church-power','Text only',[]],
  ['gibbon-01-trajan-column','Quotation without pictures',[]],
];
const front = fs.readFileSync(`${out}/front.html`, 'utf8');
const back = fs.readFileSync(`${out}/back.html`, 'utf8');
function render(template, fields) {
  return template.replace(/{{#(\w+)}}([\s\S]*?){{\/\1}}/g, (_,key,body) => fields[key] ? body : '')
    .replace(/{{(\w+)}}/g, (_,key) => fields[key] || '');
}
const result = samples.map(([id,label,portraits]) => {
  const c = cards.get(id);
  if (!c?.Q || !c?.A) throw new Error(`Missing card: ${id}`);
  const selected = portraits.map(([person,role]) => {
    const p = people.get(person);
    if (!p?.local_path || !fs.existsSync(p.local_path)) throw new Error(`Missing picture: ${person}`);
    const img = `<img src="../${esc(p.local_path)}" alt="${esc(p.name)}: ${esc(p.depiction_kind)}" width="${p.width}" height="${p.height}">`;
    const qualification = captions[p.id] ?? (p.depiction_kind === 'Ancient object; attribution per source' ? '' : p.depiction_kind);
    return {p, html:`<figure><div class="image-frame">${img}</div><figcaption><strong>${esc(p.name)}</strong>${esc(role)}<span class="depiction">${esc(qualification)}</span></figcaption><details class="picture-zoom"><summary>Enlarge</summary>${img}</details></figure>`};
  });
  const fields = {Question:c.Q,Answer:c.A,Gibbon:c.Gibbon,More:c.More,Sources:c.Sources,Images:selected.map(x=>x.html).join(''),ImageCredits:selected.map(({p})=>`<p><strong>${esc(p.name)}</strong><br>${esc(p.artist || 'Creator not recorded')} · <a href="${esc(p.file_page_url)}">Source</a> · ${p.license_url ? `<a href="${esc(p.license_url)}">${esc(p.license)}</a>` : esc(p.license)}<br>${esc([p.credit,p.credit_note,p.restrictions,p.reuse_notes].filter(Boolean).join(' · '))}<br>Displayed without cropping or alteration.</p>`).join('')};
  return {id,label,front:render(front,fields),back:render(back,fields)};
});
const html = `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gibbon · Card layout preview</title>
<link rel="stylesheet" href="styling.css">
<style>
body{margin:0;background:#e9ece7;color:#292c29;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{padding:18px 24px;border-bottom:1px solid #cbd1c7;display:flex;align-items:center;gap:12px;flex-wrap:wrap}header strong{margin-right:auto}label{display:flex;align-items:center;gap:8px}select,button{font:inherit;min-height:40px;padding:8px 12px;border:1px solid #a7b0a2;border-radius:5px;background:#f8f8f5;color:#292c29;cursor:pointer}button[aria-pressed=true]{background:#d8e5d9}button:focus-visible,select:focus-visible{outline:2px solid #39634d;outline-offset:3px}.preview-wrap{max-width:860px;margin:24px auto;padding:0 12px}.preview-wrap.phone{max-width:390px}#surface{min-height:360px;border:1px solid #d8dcd5;border-radius:6px}footer{max-width:812px;margin:18px auto 32px;padding:0 24px;line-height:1.6;color:#626761}#flip{display:block;margin:22px auto 0;background:#39634d;color:#f8f8f5;border-color:#39634d;min-width:180px}.dark-shell{background:#171b17;color:#e5e8e1}.dark-shell header{border-color:#434b41}.dark-shell footer{color:#b0b9ad}@media(max-width:520px){header{padding:12px;gap:8px}header strong{flex-basis:100%}header label{width:100%}select{width:100%;min-width:0}.preview-wrap{margin-top:12px;padding:0 8px}footer{padding:0 16px}}
</style>
<header><strong>Gibbon / Card layout</strong><label>Example <select id="sample">${result.map((c,i)=>`<option value="${i}">${esc(c.label)}</option>`).join('')}</select></label><button id="phone" aria-pressed="false">Phone width</button><button id="theme" aria-pressed="false">Night mode</button></header>
<div class="preview-wrap" id="wrap"><div class="card" id="surface"></div><button id="flip">Show answer</button></div>
<footer>Layout preview with existing card text and selected portraits. Pictures and quotations appear after recall. “More context” and sources are optional. Anki supplies its own answer and rating controls.<br><a href="README.md">Layout notes</a> · <a href="../images/index.html">Portrait gallery</a></footer>
<script>
const examples=${JSON.stringify(result).replace(/</g,'\\u003c')};
const sample=document.getElementById('sample'),surface=document.getElementById('surface'),flip=document.getElementById('flip');
let revealed=false;
function draw(){surface.innerHTML=examples[Number(sample.value)][revealed?'back':'front'];flip.textContent=revealed?'Show question':'Show answer';}
sample.addEventListener('change',()=>{revealed=false;draw()});
flip.addEventListener('click',()=>{revealed=!revealed;draw()});
document.getElementById('phone').addEventListener('click',function(){const on=this.getAttribute('aria-pressed')!=='true';this.setAttribute('aria-pressed',String(on));document.getElementById('wrap').classList.toggle('phone',on)});
document.getElementById('theme').addEventListener('click',function(){const on=this.getAttribute('aria-pressed')!=='true';this.setAttribute('aria-pressed',String(on));surface.classList.toggle('nightMode',on);document.body.classList.toggle('dark-shell',on)});
draw();
</script></html>`;
fs.writeFileSync(path.join(out,'preview.html'),html);
console.log(`Built ${result.length} examples from current cards and portrait metadata. No package created.`);

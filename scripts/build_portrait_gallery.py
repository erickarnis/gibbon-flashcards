#!/usr/bin/env python3
"""Validate local images and create an offline gallery and attribution register."""
import collections,csv,hashlib,html,json,re
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from collect_portraits import ROOT,DATA,OUT,save
later=set('''dorotheus-of-nicomedia count-theodosius pap-of-armenia cniva khosrov-ii-of-armenia herod-the-great caratacus boudica servius-tullius romulus marcus-furius-camillus catiline columella pliny-the-elder ptolemy galen gnaeus-cornelius-cinna-magnus safi-ad-din-ardabili marcia-mistress-of-commodus papinian ulpian sextus-afranius-burrus zoroaster scipio-africanus veleda publius-quinctilius-varus tiridates-iii-of-armenia macrianus-major cyriades ingenuus aureolus victoria-gallic-empire semiramis maeonius tacitus lucius-tarquinius-superbus porphyry-philosopher sallust moses abraham joshua jesus justin-martyr adam ezra solomon irenaeus theophilus-of-antioch tertullian origen jacob david cyprian saint-peter aristides-of-athens clement-of-alexandria sextus-julius-africanus pliny-the-younger epictetus simon-bar-kokhba pontius-pilate flavia-domitilla-wife-of-clemens pope-stephen-i ignatius-of-antioch dionysius-of-alexandria gorgonius marcellus-of-tangier eusebius marcus-valerius-messalla-corvinus minervina constantina eusebia-empress gideon frumentius paul-of-samosata donatus-magnus clovis-i philo arius athanasius-of-alexandria hilary-of-poitiers eustathius-of-antioch paul-i-of-constantinople pope-liberius antipope-felix-ii alexander-of-constantinople macedonius-i-of-constantinople acacius-of-byzantium gregory-of-nazianzus libanius pachomius-the-great luke-the-evangelist matthew-the-apostle gaius-fabricius-luscinus charito pope-damasus-i jerome pharandzem marina-severa zephaniah eutropius-historian lucian muhammad aaron anthony-the-great'''.split())
uncertain={
'gaius-marius':'Traditional identification as Marius; uncertain.',
'cato-the-younger':'Traditional identification of the Volubilis bust is disputed.',
'tiberius-claudius-pompeianus':'Attributed portrait; not a certain identification.',
'cyrus-the-great':'Winged figure at Pasargadae traditionally associated with Cyrus; not a secure portrait.',
'odaenathus':'Tessera: possible depiction of Odaenathus, not a certain identification.',
'plotinus':'Traditional attribution of an anonymous philosopher portrait; not secure.',
'plutarch':'Anonymous philosopher, possibly Plutarch or Plotinus; source identification is uncertain.',
'lactantius':'Possible identification only, according to the image source.',
'shapur-ii':'Head of a Sasanian king, possibly Shapur II, according to the museum.',
'ammianus-marcellinus':'Anonymous late Roman bust conjecturally identified as Ammianus; not secure.',
'otho':'Ancient portrait attribution is not secure; see the source file.',
'philip-ii-of-macedon':'Traditional attribution of an ancient portrait; not a securely identified lifetime likeness.',
'hannibal':'Traditional attribution to Hannibal; not a securely identified lifetime likeness.',
'phidias':'Posthumous sculptural identification per source, not a verified lifetime likeness.'
}
modern=set('genghis-khan torquato-tasso charles-v-holy-roman-emperor louis-xiv hugo-grotius david-hume edward-gibbon'.split())
def rights(p):
    lic=p.get('license','')
    if 'BY-SA' in lic:return 'Attribute the creator, link the exact licence, mark changes, and apply its ShareAlike terms to adaptations.'
    if 'CC BY' in lic:return 'Attribute the creator, link the exact licence, and mark changes.'
    if lic=='Attribution':return 'Custom attribution licence: keep the named credit and check the source page for its exact terms before publication.'
    if lic=='Copyrighted free use':return 'Custom permission: read and preserve the exact permission on the source page before publication.'
    if 'Public domain' in lic or lic in ['CC0','PDM-owner']:return 'Source records public domain / dedication; keep provenance and check territorial or non-copyright restrictions before publication.'
    return 'Reuse terms incomplete: review the source page before publication.'
def main():
    people=json.loads((DATA/'manifest.json').read_text()); records=json.loads((DATA/'download-records.json').read_text())
    counts=collections.Counter();errors=[]
    for p in people:
        record=records.get(p['id'],{})
        if p.get('selected_file') and record.get('selected_file')==p['selected_file'] and (ROOT/record['file']).exists():
            path=ROOT/record['file']
            try:
                with Image.open(path) as im:im.verify()
                with Image.open(path) as im:p['width'],p['height']=im.size;p['actual_format']=im.format
                p.update(status='downloaded',local_path=record['file'],bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                p.pop('download_error',None)
            except Exception as e:errors.append((p['id'],str(e)))
        p['depiction_kind']='No selected image'
        if p.get('selected_file'):
            p['depiction_kind']='Ancient object; attribution per source'
            if p['id'] in later:p['depiction_kind']='Later imagined or traditional depiction'
            if p['id'] in modern:p['depiction_kind']='Historical portrait; see source date'
            if p['id'] in uncertain:p['depiction_kind']='Ancient object; uncertain identity';p['likeness_note']=uncertain[p['id']]
            if p['id'] in ['homer','numa-pompilius','minos','midas','lucius-junius-brutus','ajax-the-great','pelops','cadmus','hippolytus-son-of-theseus','phaedra-mythology']:p['depiction_kind']='Posthumous or legendary ancient representation'
        if p.get('depiction_override'):p['depiction_kind']=p['depiction_override']
        p['reuse_notes']=rights(p) if p.get('license') else 'No image licence recorded.'
        p['credit_note']='Creator not specified in the retrieved metadata; consult the source page before publication.' if p['status']=='downloaded' and not any(p.get(k) for k in ['artist','credit','attribution_text']) else ''
        if p.get('width',999)>=1 and p.get('width',999)<500:p['quality_note']='Small source: suitable for a flashcard, not a large print.'
        counts[p['status']]+=1
    save(DATA/'manifest.json',people)
    if errors:raise SystemExit(str(errors))
    rows=[]
    fields=['name','aliases','chapters','status','local_path','width','height','depiction_kind','likeness_note','identity_note','quality_note','download_resolution_note','selection_note','artist','credit_note','attribution_text','permission_text','credit','license','license_url','reuse_notes','restrictions','file_page_url','original_url','download_url','sha256']
    with (DATA/'credits.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for p in people:
            row={k:p.get(k,'') for k in fields};row['aliases']='; '.join(p['aliases']);row['chapters']='; '.join(dict.fromkeys(m['chapter'] for m in p['source_mentions']));writer.writerow(row)
    e=lambda x:html.escape(str(x),quote=True)
    tiles=[]
    for p in people:
        found=p['status']=='downloaded';chapters=list(dict.fromkeys(m['chapter'] for m in p['source_mentions']))
        picture=f'<a href="{e(p["local_path"].removeprefix("images/"))}"><img loading="lazy" src="{e(p["local_path"].removeprefix("images/"))}" alt="{e(p["name"])}"></a>' if found else '<div class="empty">No suitable image downloaded</div>'
        links=[]
        if p.get('file_page_url'):links.append(f'<a href="{e(p["file_page_url"])}">Image source</a>')
        if p.get('license_url'):links.append(f'<a href="{e(p["license_url"])}">Licence</a>')
        ref=p['source_mentions'][0] if p['source_mentions'] else None
        if ref:links.append(f'<a href="../sources/mueller-volumes-1-2.md#{ref["anchor"]}">Text {ref["anchor"]}</a>')
        notes=' '.join(filter(None,[p.get('identity_note'),p.get('likeness_note'),p.get('selection_note'),p.get('quality_note'),p.get('download_resolution_note')]))
        details=f'<p>{e(notes)}</p><p><b>Credit:</b> {e(p.get("artist",""))}</p><p>{e(p.get("reuse_notes",""))}</p>'
        if p.get('credit_note'):details+=f'<p>{e(p["credit_note"])}</p>'
        if p.get('attribution_text'):details+=f'<p><b>Required attribution:</b> {e(p["attribution_text"])}</p>'
        if p.get('permission_text'):details+=f'<p><b>Source permission:</b> {e(p["permission_text"])}</p>'
        if p.get('credit'):details+=f'<p><b>Source credit:</b> {e(p["credit"])}</p>'
        if p.get('restrictions'):details+=f'<p><b>Other restrictions:</b> {e(p["restrictions"])}</p>'
        if p.get('image_description'):details+=f'<p><b>Source description:</b> {e(p["image_description"])}</p>'
        tiles.append(f'<article data-search="{e(p["name"]+" "+" ".join(p["aliases"]))}" data-status="{"downloaded" if found else "missing"}" data-chapters="{e(" ".join(chapters))}" data-kind="{e(p["depiction_kind"])}">{picture}<div class="body"><h2>{e(p["name"])}</h2><p class="aliases">In text: {e("; ".join(p["aliases"]))}</p><p class="kind">{e(p["depiction_kind"])}</p><p class="meta">Name matches in ch. {e(", ".join(chapters))} · {e(p.get("license","No image"))}</p><details><summary>Source, identity and reuse</summary>{details}<p>{" · ".join(links)}</p></details></div></article>')
    chapters=list(dict.fromkeys(v['chapter'] for v in json.loads((ROOT/'sources/passages-volumes-1-2.json').read_text()).values()))
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gibbon · People in Volumes I–II</title><style>
:root{font-family:system-ui,sans-serif;color:#222;background:#f6f4ef}body{margin:0}header{padding:24px 28px 16px;background:#fff;border-bottom:1px solid #d8d3c8}h1{font-size:26px;margin:0 0 8px}header p{max-width:940px;margin:8px 0;line-height:1.5}.controls{position:sticky;top:0;background:#f6f4eff5;z-index:2;padding:12px 28px;display:flex;gap:8px;flex-wrap:wrap;border-bottom:1px solid #d8d3c8}input,select{font:inherit;padding:9px;border:1px solid #aaa;border-radius:4px}input{flex:1;min-width:190px}.count{padding:8px 28px;color:#555}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(225px,1fr));gap:14px;padding:0 28px 30px}article{background:white;border:1px solid #d8d3c8;border-radius:5px;overflow:hidden}article[hidden]{display:none}img{width:100%;height:255px;object-fit:contain;background:#e7e4df;display:block}.empty{height:120px;display:grid;place-items:center;background:#eee;color:#68645b;font-size:13px}.body{padding:12px}h2{font-size:17px;margin:0 0 6px}p{font-size:13px;line-height:1.45;margin:6px 0;overflow-wrap:anywhere}.aliases,.meta{color:#666}.kind{font-weight:600}summary{cursor:pointer;font-size:13px;margin-top:10px}a{color:#285847}details p{font-size:12px}footer{padding:0 28px 30px;color:#666;font-size:13px}
</style><header><h1>People in Gibbon · Volumes I–II</h1><p>REPLACE_COUNT locally saved images. The index covers named people in the supplied Mueller abridgment, Chapters I–XXVI. Ancient objects are preferred where practical; later imagined portraits and uncertain identities are labelled.</p><p><a href="../sources/portraits/README.md">Selection and coverage notes</a> · <a href="../sources/portraits/credits.csv">Download credits register</a></p></header><div class="controls"><input id="search" aria-label="Search people" placeholder="Name used in the book or modern name"><select id="status" aria-label="Image availability"><option value="downloaded">Downloaded images</option><option value="all">All indexed people</option><option value="missing">Gaps</option></select><select id="chapter" aria-label="Chapter"><option value="all">All chapters</option>REPLACE_CHAPTERS</select><select id="kind" aria-label="Depiction type"><option value="all">All depiction types</option>REPLACE_KINDS</select></div><div class="count" id="count" aria-live="polite"></div><main>REPLACE_TILES</main><footer>Images remain local. Reuse conditions are recorded per file. No Anki package has been created.</footer><script>
const ids=['search','status','chapter','kind'],controls=Object.fromEntries(ids.map(id=>[id,document.getElementById(id)]));const cards=[...document.querySelectorAll('article')];function filter(){const q=controls.search.value.toLocaleLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');let n=0;for(const c of cards){const text=c.dataset.search.toLocaleLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');c.hidden=!(text.includes(q)&&(controls.status.value==='all'||c.dataset.status===controls.status.value)&&(controls.chapter.value==='all'||c.dataset.chapters.split(' ').includes(controls.chapter.value))&&(controls.kind.value==='all'||c.dataset.kind===controls.kind.value));if(!c.hidden)n++}document.getElementById('count').textContent=n+(n===1?' person shown':' people shown')}for(const c of Object.values(controls))c.addEventListener('input',filter);filter();</script></html>'''
    page=page.replace('REPLACE_COUNT',str(counts['downloaded'])).replace('REPLACE_CHAPTERS',''.join(f'<option>{e(c)}</option>' for c in chapters)).replace('REPLACE_KINDS',''.join(f'<option>{e(k)}</option>' for k in sorted(set(p['depiction_kind'] for p in people)))).replace('REPLACE_TILES',''.join(tiles))
    (ROOT/'images/index.html').write_text(page)
    found=[p for p in people if p['status']=='downloaded']
    sheet_dir=Path('/tmp/gibbon-portrait-review');sheet_dir.mkdir(exist_ok=True)
    for start in range(0,len(found),36):
        sheet=Image.new('RGB',(1200,1380),'#f6f4ef');draw=ImageDraw.Draw(sheet)
        for i,p in enumerate(found[start:start+36]):
            with Image.open(ROOT/p['local_path']) as im:
                im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((190,190));x=(i%6)*200+(200-im.width)//2;y=(i//6)*230;sheet.paste(im,(x,y));draw.text(((i%6)*200+4,y+194),p['name'][:28],fill='black');draw.text(((i%6)*200+4,y+208),p['depiction_kind'][:30],fill='#444444')
        sheet.save(sheet_dir/f'sheet-{start//36+1:02d}.jpg')
    print(dict(counts));print('Validated images:',len(found),'Total MB:',round(sum(p['bytes'] for p in found)/1e6,1));print('Contact sheets:',sheet_dir)
if __name__=='__main__':main()

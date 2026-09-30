"""Render the actual exported fields/templates, including all bundled images."""
import html,json,re,sqlite3,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'dist/qa';out.mkdir(exist_ok=True)
with zipfile.ZipFile(root/'dist/Gibbon-Volumes-I-II.apkg') as z:
 (out/'collection.anki2').write_bytes(z.read('collection.anki2'))
 for key,name in json.loads(z.read('media')).items(): (out/name).write_bytes(z.read(key))
with sqlite3.connect(out/'collection.anki2') as con:
 model=next(iter(json.loads(con.execute('select models from col').fetchone()[0]).values()))
 notes=[dict(zip([f['name'] for f in model['flds']],row[0].split('\x1f'))) for row in con.execute('select flds from notes')]
def render(t,f):
 t=re.sub(r'{{#(\w+)}}([\s\S]*?){{/\1}}',lambda m:m[2] if f.get(m[1]) else '',t)
 return re.sub(r'{{(\w+)}}',lambda m:f.get(m[1],''),t)
links=[]
for n in notes:
 for side in ['front','back']:
  for mode in ['light','dark']:
   name=n['StableID']+'-'+side+'-'+mode+'.html'
   page='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+model['css']+'</style></head><body class="card '+('nightMode' if mode=='dark' else '')+'">'+render(model['tmpls'][0]['qfmt' if side=='front' else 'afmt'],n)+'</body></html>'
   (out/name).write_text(page)
   if n['StableID'] in ['gibbon-01-nerva-accession','gibbon-01-hadrian-terminus','gibbon-01-theme-adoption']:
    links.append(f'<li><a href="{name}">{name}</a></li>')
images=sorted({m for n in notes for m in re.findall(r'<img[^>]+src="([^"]+)"',n['Images'])})
(out/'media.html').write_text('<!doctype html><html><body>'+''.join(f'<figure><img width="120" src="{html.escape(m)}"><figcaption>{html.escape(m)}</figcaption></figure>' for m in images)+'</body></html>')
(out/'index.html').write_text('<!doctype html><ul>'+''.join(links)+'</ul><a href="media.html">All media</a>')
print(f'Rendered {len(notes)} cards and {len(images)} image files in {out}')

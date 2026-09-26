#!/usr/bin/env python3
"""Summarize the final verified catalogue and retain search limitations."""
import collections,json,urllib.parse
from pathlib import Path
from collect_portraits import ROOT,DATA,CACHE
p=json.loads((DATA/'manifest.json').read_text());found=[x for x in p if x['status']=='downloaded'];missing=[x for x in p if x['status']!='downloaded']
licenses=collections.Counter(x.get('license','Unknown') for x in found)
lines=['# Coverage and remaining gaps','',f'Indexed entries: **{len(p)}**. Verified local images: **{len(found)}**. Entries without a downloaded image: **{len(missing)}**.','',f'Total downloaded image size: **{sum(x.get("bytes",0) for x in found)/1e6:.1f} MB**.','', 'The scope is the supplied Mueller abridgment, Chapters I–XXVI. This is a best-effort name index and image search. It does not prove that an image is the best available or that an unillustrated person has no surviving representation. See [selection notes](README.md).','','## Image types','']
for k,v in collections.Counter(x['depiction_kind'] for x in found).items():lines.append(f'- {k}: {v}')
lines+=['','## Licences recorded by the sources','']
for k,v in sorted(licenses.items()):lines.append(f'- {k}: {v}')
lines+=['','## Gaps','', 'Each entry was checked against the intended biography or recorded identity. Supplementary Commons searches are distinguished below from searches that failed or were not run. Maps, inscriptions, and portraits of other people were rejected. A search-rate-limit response is not negative evidence.','','| Person | Search outcome | Note |','| --- | --- | --- |']
for x in missing:
 search=CACHE/('search-'+x['id']+'.json');outcome='No suitable biography image; supplementary search not completed.'
 if search.exists():
  r=json.loads(search.read_text())
  if r.get('error'):outcome='Supplementary search unavailable: '+r['error']
  elif r.get('response',{}).get('query',{}).get('pages'):outcome='Supplementary results reviewed; no suitable individual image selected.'
  else:outcome='Supplementary search returned no files.'
 if x['status']=='download_failed':outcome='Download failed: '+x.get('download_error','unknown error')
 elif x['status']=='ready':outcome='Selected image remains pending download.'
 note=' '.join(filter(None,[x.get('identity_note'),x.get('selection_note')])).replace('|','/').replace('\n',' ')
 query='https://commons.wikimedia.org/w/index.php?search='+urllib.parse.quote(x['name'])+'&title=Special:MediaSearch&type=image'
 lines.append(f'| [{x["name"]}]({query}) | {outcome} | {note} |')
lines+=['','## Verification','', '- All files counted above opened successfully as images; dimensions and SHA-256 hashes are in the manifest.', '- Images were reviewed in contact sheets. Labels preserve later imagined depictions and known uncertain identifications.', '- Source file pages, reuse metadata, attribution statements, and raw API responses are retained.', '- No cards, source passages, or Anki packages were changed by the portrait-collection task.','']
(DATA/'coverage.md').write_text('\n'.join(lines))
print('Coverage:',len(found),'/',len(p))

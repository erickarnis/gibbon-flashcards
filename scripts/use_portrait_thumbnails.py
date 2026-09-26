#!/usr/bin/env python3
"""Use Commons' public thumbnail service for files whose originals are throttled."""
import json,urllib.parse
from collect_portraits import DATA,CACHE,api,save
p=json.loads((DATA/'manifest.json').read_text());groups={}
for x in p:
 if x.get('selected_file') and x['status']!='downloaded' and '/thumb/' not in x.get('download_url',''):
  width=x.get('original_width',0)
  target=next((w for w in [1280,960,500,330,250,120,60] if w<width),max(1,width//2))
  groups.setdefault(target,[]).append(x)
for target,items in groups.items():
 for start in range(0,len(items),40):
  block=items[start:start+40]
  r=api('commons.wikimedia.org',titles='|'.join(x['selected_file'] for x in block),redirects=1,prop='imageinfo',iiprop='url|size',iiurlwidth=target)
  save(CACHE/f'thumbnails-{target}-{start}.json',r)
  q=r.get('query',{});lookup={v['title']:v for v in q.get('pages',[])}
  for v in q.get('normalized',[])+q.get('redirects',[]):
   if v['to'] in lookup:lookup[v['from']]=lookup[v['to']]
  for x in block:
   info=lookup.get(x['selected_file'],{}).get('imageinfo',[{}])[0];url=info.get('thumburl','')
   if '/thumb/' in url:
    x['initial_download_url']=x['download_url'];x['download_url']=url;x['download_resolution_note']=f'Source-generated standard thumbnail requested at {target}px because original-file delivery was rate-limited; original URL retained.';x['status']='ready'
# The thumbnail service is the official public host used by Wikimedia page previews.
for x in p:
 url=x.get('download_url','')
 if '/thumb/' in url:x['download_url']=url.replace('https://upload.wikimedia.org/','https://thumb.wikimedia.org/')
save(DATA/'manifest.json',p)
print('Thumbnail fallbacks:',sum(len(v) for v in groups.values()))

#!/usr/bin/env python3
"""One bounded Commons search per unresolved person; manually review results."""
import json,time,urllib.error
from collect_portraits import DATA,CACHE,api,save
people=json.loads((DATA/'manifest.json').read_text())
for p in people:
    if p.get('selected_file'):continue
    path=CACHE/('search-'+p['id']+'.json')
    if path.exists() and not json.loads(path.read_text()).get('error'):continue
    query=p['name']
    try:
        r=api('commons.wikimedia.org',generator='search',gsrsearch=query,gsrnamespace=6,gsrlimit=5,prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=400)
        save(path,{'person_id':p['id'],'query':query,'response':r})
        print(p['id'],[x['title'] for x in r.get('query',{}).get('pages',[])],flush=True)
        time.sleep(3)
    except urllib.error.HTTPError as e:
        save(path,{'person_id':p['id'],'query':query,'error':str(e)})
        if e.code==429:
            pause=int(e.headers.get('Retry-After','600'))
            save(DATA/'search-rate-limit.json',{'resume_at_epoch':time.time()+pause,'retry_after_seconds':pause})
            if pause<=60:
                print('Pausing',pause,'seconds as requested.',flush=True)
                time.sleep(pause+2)
            else:
                print('Rate limited; stopped. Retry after',pause,'seconds.',flush=True)
                break
    except Exception as e:save(path,{'person_id':p['id'],'query':query,'error':str(e)})

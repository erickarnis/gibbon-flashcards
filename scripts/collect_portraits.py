#!/usr/bin/env python3
"""Download a reviewed portrait catalogue; no paid APIs or AI generation.
Run with the bundled Python runtime. Network is needed for fetch/download.
"""
import argparse, concurrent.futures, datetime, hashlib, html, json, re, time, unicodedata, urllib.parse, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'sources/portraits'; OUT=ROOT/'images/people'; CACHE=DATA/'cache'
CACHE.mkdir(exist_ok=True)
UA='GibbonPersonalPortraitResearch/1.0 (personal educational collection; low-rate Wikimedia API client)'
def get(url, binary=False):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA})
            with urllib.request.urlopen(req,timeout=60) as r:
                data=r.read()
            return data if binary else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                pause=int(e.headers.get('Retry-After','600'))
                if binary and pause<=60 and attempt<3:
                    time.sleep(max(pause,2))
                    continue
                raise
            if attempt==3: raise
            time.sleep(2+attempt*3)
        except Exception:
            if attempt==3: raise
            time.sleep(2+attempt*3)
def api(host, **params):
    params={'action':'query','format':'json','formatversion':2,**params}
    return get('https://'+host+'/w/api.php?'+urllib.parse.urlencode(params))
def save(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def slug(name):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')
def plain(s):return html.unescape(re.sub('<[^>]*>','',s or '')).strip()
def inventory():
    passages=json.loads((ROOT/'sources/passages-volumes-1-2.json').read_text()); people=[]
    for line in (DATA/'people.tsv').read_text().splitlines():
        if not line or line.startswith('#'):continue
        title,names,anchors,note=(line.split('|')+['']*4)[:4]
        aliases=names.split(';');refs=[]
        for a,v in passages.items():
            if (a in anchors.split(';')) if anchors else any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',v['text']) for n in aliases):
                refs.append({'anchor':'L'+a,'chapter':v['chapter']})
        people.append({'id':slug(title),'name':title,'aliases':aliases,'source_mentions':refs,'identity_note':note,'status':'not_searched'})
    save(DATA/'inventory.json',people)
    print('Inventory:',len(people),'No references:',[p['name'] for p in people if not p['source_mentions']],flush=True)
def fetch_pages():
    people=json.loads((DATA/'inventory.json').read_text())
    for start in range(0,len(people),40):
        block=people[start:start+40];path=CACHE/f'pages-{start:03d}.json'
        if path.exists():continue
        response=api('en.wikipedia.org',titles='|'.join(p['name'] for p in block),redirects=1,prop='pageimages|images|pageprops',piprop='name|original',pilicense='any',imlimit='max')
        # Continue only the images property; avoid silent truncation of candidate lists.
        allpages={p['title']:p for p in response.get('query',{}).get('pages',[])}
        continuation=response.get('continue')
        while continuation:
            more=api('en.wikipedia.org',titles='|'.join(p['name'] for p in block),redirects=1,prop='images',imlimit='max',**continuation)
            for p in more.get('query',{}).get('pages',[]):
                allpages.setdefault(p['title'],p).setdefault('images',[]).extend(p.get('images',[]))
            continuation=more.get('continue')
        response['query']['pages']=list(allpages.values());save(path,response)
        print('Fetched pages',start+len(block),'/',len(people),flush=True);time.sleep(.4)
    pages={}; redirects={}
    for path in sorted(CACHE.glob('pages-*.json')):
        q=json.loads(path.read_text()).get('query',{})
        redirects.update({r['from']:r['to'] for r in q.get('normalized',[])+q.get('redirects',[])})
        pages.update({p['title']:p for p in q.get('pages',[])})
    overrides=json.loads((DATA/'overrides.json').read_text()) if (DATA/'overrides.json').exists() else {}
    for person in people:
        title=person['name'];seen=set()
        while title in redirects and title not in seen:seen.add(title);title=redirects[title]
        page=pages.get(title,{})
        person['resolved_title']=title;person['article_url']='https://en.wikipedia.org/wiki/'+urllib.parse.quote(title.replace(' ','_'))
        person['candidates']=[i['title'] for i in page.get('images',[]) if not re.search(r'\.svg$|Flag|Map|map|logo|Icon|Wikisource|Commons|Wikiquote|Symbol|signature',i['title'])]
        person['selected_file']='File:'+page['pageimage'] if page.get('pageimage') else None
        person['status']='candidate' if person['selected_file'] else 'no_portrait_found'
        if 'disambiguation' in page.get('pageprops',{}):person['selected_file']=None;person['status']='identity_needs_review'
        if person['id'] in overrides:person.update(overrides[person['id']])
    save(DATA/'manifest.json',people)
    print('Candidates',sum(bool(p['selected_file']) for p in people),flush=True)
def metadata():
    people=json.loads((DATA/'manifest.json').read_text());files=list(dict.fromkeys(p['selected_file'] for p in people if p.get('selected_file') and p.get('source_provider')!='external'))
    infos={}
    for cached in CACHE.glob('commons-*.json'):
        q=json.loads(cached.read_text()).get('query',{})
        lookup={p['title']:p for p in q.get('pages',[])}
        infos.update(lookup)
        for r in q.get('normalized',[])+q.get('redirects',[]):
            if r['to'] in lookup:infos[r['from']]=lookup[r['to']]
    files=[f for f in files if f not in infos]
    for start in range(0,len(files),40):
        block=files[start:start+40];key=hashlib.sha256('|'.join(block).encode()).hexdigest()[:16];path=CACHE/f'commons-{key}.json'
        if path.exists():response=json.loads(path.read_text())
        else:
            response=api('commons.wikimedia.org',titles='|'.join(block),redirects=1,prop='imageinfo',iiprop='url|size|mime|extmetadata|sha1',iiurlwidth=1600)
            save(path,response);time.sleep(.3)
        q=response.get('query',{}); lookup={p['title']:p for p in q.get('pages',[])};redir={p['from']:p['to'] for p in q.get('normalized',[])+q.get('redirects',[])}
        for name in block:
            resolved=name;seen=set()
            while resolved in redir and resolved not in seen:seen.add(resolved);resolved=redir[resolved]
            infos[name]=lookup.get(resolved,{})
        print('Commons metadata',min(start+40,len(files)),'/',len(files),flush=True)
    for p in people:
        if not p.get('selected_file') or p.get('source_provider')=='external':continue
        info=infos.get(p['selected_file'],{}).get('imageinfo',[])
        if not info:p['status']='no_commons_file';continue
        i=info[0]
        if p.get('file_page_url') == i.get('descriptionurl') and p.get('metadata_raw'):
            continue
        m=i.get('extmetadata',{});v=lambda k:plain(m.get(k,{}).get('value',''))
        p.update({'file_page_url':i.get('descriptionurl'),'original_url':i['url'],'original_width':i['width'],'original_height':i['height'],'commons_sha1':i.get('sha1'),'mime':i.get('mime','image/png' if i['url'].split('?')[0].lower().endswith('.png') else 'image/jpeg'),'download_url':i.get('thumburl',i['url']),'image_description':v('ImageDescription'),'artist':v('Artist'),'attribution_text':v('Attribution'),'permission_text':v('Permission'),'credit':v('Credit'),'license':v('LicenseShortName'),'license_url':v('LicenseUrl'),'usage_terms':v('UsageTerms'),'copyrighted':v('Copyrighted'),'attribution_required':v('AttributionRequired'),'restrictions':v('Restrictions'),'metadata_date':datetime.date.today().isoformat(),'status':'ready'})
        p['metadata_raw']=m
    save(DATA/'manifest.json',people)
def download():
    pause_path=DATA/'rate-limit.json'
    if pause_path.exists():
        pause=json.loads(pause_path.read_text())
        remaining=pause.get('resume_at_epoch',0)-time.time()
        if remaining>0:
            print('Original host paused for',int(remaining)+1,'seconds; other hosts can continue.',flush=True)
    people=json.loads((DATA/'manifest.json').read_text())
    record_path=DATA/'download-records.json'
    records=json.loads(record_path.read_text()) if record_path.exists() else {}
    for p in people:
        if p['status'] not in ('ready','downloaded','download_failed'):continue
        ext={ 'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp','image/gif':'.gif','image/tiff':'.jpg'}.get(p.get('mime'),'.jpg')
        url=p['download_url'].split('?')[0]
        if '.png' in url[-8:]:ext='.png'
        pause_data=json.loads(pause_path.read_text()) if pause_path.exists() else {}
        if time.time()<pause_data.get('resume_at_epoch',0) and urllib.parse.urlparse(url).netloc==pause_data.get('host'):
            print('Deferred paused host:',p['name'],flush=True)
            continue
        path=OUT/(p['id']+ext)
        cached=records.get(p['id'],{})
        try:
            if not path.exists() or cached.get('selected_file') != p['selected_file']:
                data=get(url,True)
                if not (data.startswith(b'\xff\xd8') or data.startswith(b'\x89PNG') or data.startswith(b'GIF8') or data[:4]==b'RIFF'):raise ValueError('Not a supported raster image')
                path.write_bytes(data)
                records[p['id']]={'file':str(path.relative_to(ROOT)),'selected_file':p['selected_file']}
                save(record_path,records)
                time.sleep(1.5)
            p['local_path']=str(path.relative_to(ROOT));p['bytes']=path.stat().st_size;p['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();p['status']='downloaded';p.pop('download_error',None)
        except urllib.error.HTTPError as e:
            p['status']='download_failed';p['download_error']=str(e)
            if e.code==429:
                pause=int(e.headers.get('Retry-After','600'))
                save(DATA/'rate-limit.json',{'host':urllib.parse.urlparse(url).netloc,'retry_after_seconds':pause,'resume_at_epoch':time.time()+pause})
                save(DATA/'manifest.json',people)
                print('RATE LIMITED: pause',pause,'seconds;',p['name'],flush=True)
                return
        except Exception as e:p['status']='download_failed';p['download_error']=str(e)
        save(DATA/'manifest.json',people)
        print(p['status'],p['name'],flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['inventory','pages','metadata','download']);args=parser.parse_args()
    {'inventory':inventory,'pages':fetch_pages,'metadata':metadata,'download':download}[args.stage]()

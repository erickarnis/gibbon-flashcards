"""Test initial import and review-preserving update in disposable Anki collections.

Requires anki==26.9.3 in addition to the builder requirements.
Usage: python scripts/test_anki_import.py [previous-package.apkg]
"""
from pathlib import Path
import json
import re
import sys
import tempfile
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest, ImportAnkiPackageOptions

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT/'dist/Gibbon-Volumes-I-II.apkg'
OLD = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None

def importer(col, package):
    return col.import_anki_package(ImportAnkiPackageRequest(package_path=str(package), options=ImportAnkiPackageOptions(with_scheduling=False)))

with tempfile.TemporaryDirectory(prefix='gibbon-import-') as temp:
    col = Collection(str(Path(temp)/'collection.anki2'))
    try:
        importer(col, OLD or NEW)
        assert col.card_count()==281
        old_guids = dict(col.db.all('select guid,id from notes'))
        cid = col.db.scalar("select cards.id from cards join notes on notes.id=cards.nid where notes.flds like 'gibbon-01-nerva-accession' || char(31) || '%'")
        card = col.get_card(cid)
        card.type=2; card.queue=2; card.due=col.sched.today+12
        card.ivl=12; card.factor=2500; card.reps=7; card.lapses=1
        col.update_card(card)
        col.db.execute('insert into revlog values (?,?,?,?,?,?,?,?,?)',
                       1790582400000, cid, -1, 3, 12, 6, 2500, 8000, 1)
        history=col.db.all('select * from revlog order by id')
        schedule=col.db.all('select id,nid,type,queue,due,ivl,factor,reps,lapses from cards order by id')
        result=importer(col, NEW)
        assert col.card_count()==281
        assert old_guids==dict(col.db.all('select guid,id from notes')), 'Note identities changed'
        assert schedule==col.db.all('select id,nid,type,queue,due,ivl,factor,reps,lapses from cards order by id'), 'Review scheduling changed'
        assert history==col.db.all('select * from revlog order by id'), 'Review history changed'
        decks={d['id']:d['name'] for d in col.decks.all()}
        counts={decks[did]:count for did,count in col.db.all('select did,count(*) from cards group by did')}
        assert sorted(counts.values())==[89,192],counts
        notes={col.get_note(nid)['StableID']:col.get_note(nid) for nid in col.find_notes('')}
        assert 'In Rome’s age of kings' in notes['gibbon-01-hadrian-terminus']['Answer']
        assert not notes['gibbon-01-theme-religion']['Gibbon']
        assert 'equally true' in notes['gibbon-01-theme-religion']['Answer']
        assert '-baseline-v1.jpg' in notes['gibbon-01-nerva-accession']['Images']
        model=notes['gibbon-01-nerva-accession'].note_type()
        assert 'body.card { min-height: 100vh;' in model['css'], 'Updated style not imported'
        media=Path(col.media.dir())
        missing=[]
        for note in notes.values():
            for name in re.findall(r'<img[^>]+src="([^"]+)"',note['Images']):
                if not (media/name).is_file():missing.append(name)
        assert not missing,missing
        assert not any(re.search(r'requested by the reader|preferred to the default|user chose', n['Images'], re.I) for n in notes.values())
        print('PASS: 281 cards, 192/89 volume split, unchanged note/card IDs, review schedule and history, updated content/style, all media imported.')
    finally:
        col.close()

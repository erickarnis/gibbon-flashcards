#!/usr/bin/env python3
"""Build the reviewed Markdown collection into volume subdecks. See README."""
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
import zipfile
import genanki
import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
FIELDS = ['StableID', 'Question', 'Answer', 'Images', 'Gibbon', 'More', 'Sources', 'ImageCredits', 'PromptImages']
PARENT = 'Gibbon — Decline and Fall'

def stable_id(value):
    return int(hashlib.sha256(value.encode()).hexdigest()[:8], 16) & 0x7fffffff

def md(text):
    return markdown.markdown(text)

def sources(text):
    # Preserve the edition/chapter/extraction-line citation as text. Relative
    # repository links do not resolve in Anki; external reference links do.
    return md(re.sub(r'\[([^\]]+)\]\((sources/[^)]+)\)',
                     lambda m: m[1] + ' (Mueller abridgment, 2003; extraction line, not printed page)', text))

# Deliberately limited to identifiable people actually named in Q/A. Do not
# match catalogue aliases such as "Caesar", "Alexander", or "Marcus" globally.
ALIASES = {
    'marcus-aurelius': ['Marcus Aurelius'], 'pompeia-plotina': ['Plotina'],
    'severus-alexander': ['Alexander Severus'], 'maximinus-thrax': ['Maximinus Thrax'],
    'philip-the-arab': ['Philip the Arab'], 'ardashir-i': ['Ardashir'],
    'odaenathus': ['Odenathus'], 'claudius-gothicus': ['Claudius II', 'Claudius Gothicus'],
    'marcus-claudius-tacitus': ['emperor Tacitus'], 'constantius-chlorus': ['Constantius I', 'Constantius Chlorus'],
    'constantine-the-great': ['Constantine'], 'maximinus-daza': ['Maximin Daia'],
    'athanasius-of-alexandria': ['Athanasius'], 'eusebia-empress': ['Eusebia'],
    'edward-gibbon': [], 'tacitus': [], 'augustus': [], 'claudius': [],
    'dalmatius': [], 'sallust': [],
}

def select_people(text, file, people):
    candidates = []
    plain = text.replace('**', '')
    for p in people:
        names = ALIASES.get(p['id'], [re.sub(r' \(.*\)$', '', p['name'])])
        if p['id'] == 'marcus-claudius-tacitus' and file.startswith('03-'):
            names = names + ['Tacitus']
        if p['id'] == 'claudius-gothicus' and file.startswith('03-'):
            names = names + ['Claudius']
        if p['id'] == 'trebonianus-gallus' and file.startswith('02-'):
            names = names + ['Gallus']
        if p['id'] == 'constantius-gallus' and file.startswith('04-'):
            names = names + ['Gallus']
        if p['id'] == 'maximinus-thrax' and file.startswith('02-'):
            names = names + ['Maximinus']
        if p['id'] == 'philip-the-arab' and file.startswith('02-'):
            names = names + ['Philip']
        for name in names:
            for match in re.finditer(r'(?<!\w)' + re.escape(name) + r'(?!\w)', plain):
                # Constantine II and Licinius II must never show their fathers.
                if p['id'] in ['constantine-the-great', 'licinius'] and re.match(r' II\b', plain[match.end():]):
                    continue
                candidates.append((match.start(), match.end(), p))
    accepted = []
    for start, end, p in sorted(candidates, key=lambda x: -(x[1]-x[0])):
        if not any(start < b and end > a for a,b,_ in accepted):
            accepted.append((start,end,p))
    result = []
    for _,_,p in sorted(accepted, key=lambda x:x[0]):
        if p not in result:
            result.append(p)
    return result

def image_fields(selected, media, stage):
    figures, credits = [], []
    esc = html.escape
    for p in selected:
        original = ROOT / p['local_path']
        # Content-addressed names prevent a revised photo overwriting an older
        # image while notes and their scheduling retain stable identities.
        name = 'gibbon-' + p['id'] + '-' + hashlib.sha256(original.read_bytes()).hexdigest()[:12] + original.suffix.lower()
        target = stage / name
        if name not in media:
            shutil.copyfile(original, target)
            media[name] = target
        img = f'<img src="{name}" alt="{esc(p["name"])}" width="{p["width"]}" height="{p["height"]}">'
        qualification = ' · '.join(filter(None, [p.get('depiction_kind'), p.get('identity_note'), p.get('selection_note')]))
        figures.append(f'<figure><div class="image-frame">{img}</div><figcaption><strong>{esc(p["name"])}</strong><span class="depiction">{esc(qualification)}</span></figcaption><details class="picture-zoom"><summary>Enlarge</summary>{img}</details></figure>')
        license_text = esc(p.get('license') or 'Reuse rights not verified')
        if p.get('license_url'):
            license_text = f'<a href="{esc(p["license_url"])}">{license_text}</a>'
        details = ' · '.join(filter(None, [p.get(k) for k in ['credit','credit_note','restrictions','reuse_notes']]))
        credits.append(f'<p><strong>{esc(p["name"])}</strong><br>{esc(p.get("artist") or "Creator not recorded")} · <a href="{esc(p["file_page_url"])}">Source</a> · {license_text}<br>{esc(details)}<br>Displayed without cropping or alteration.</p>')
    return ''.join(figures), ''.join(credits)

def build():
    OUT.mkdir(exist_ok=True)
    model = genanki.Model(stable_id('gibbon-note-v1'), 'Gibbon — Question and Answer',
        fields=[{'name': f} for f in FIELDS], sort_field_index=0,
        templates=[{'name': 'Recall', 'qfmt': (ROOT/'anki-layout/front.html').read_text(), 'afmt': (ROOT/'anki-layout/back.html').read_text()}],
        css=(ROOT/'anki-layout/styling.css').read_text())
    decks = {v: genanki.Deck(stable_id('gibbon-volume-'+str(v)), PARENT + '::Volume ' + ('I' if v==1 else 'II')) for v in [1,2]}
    people = [p for p in json.loads((ROOT/'sources/portraits/manifest.json').read_text()) if p['status']=='downloaded']
    report = []
    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        media = {}
        files = sorted(ROOT.glob('[0-9]*.md'))
        # Overview cards follow detailed cards, including on sequential import.
        files.sort(key=lambda f: (f.name.startswith('00-'), f.name))
        for file in files:
            for chunk in re.split(r'(?=^### \d+\.)', file.read_text(), flags=re.M)[1:]:
                ident = re.search(r'<!-- ID: (.+?) -->', chunk)[1]
                fields = dict(re.findall(r'^\*\*(Q|A|More|Gibbon|Sources):\*\* (.+)$',chunk,re.M))
                assert fields.get('Q') and fields.get('A') and fields.get('Sources'), ident
                volume = 2 if file.name.startswith('04-') or ident in ['gibbon-00-constantine-julian','gibbon-00-julian-theodosius','gibbon-00-church-power'] else 1
                selected = select_people(fields['Q']+' '+fields['A'], file.name, people)
                if ident == 'gibbon-01-nerva-accession':
                    selected = [p for p in selected if p['id']=='nerva']
                images, credits = image_fields(selected, media, stage)
                values = [ident, md(fields['Q']), md(fields['A']), images, md(fields.get('Gibbon','')), md(fields.get('More','')), sources(fields['Sources']), credits, '']
                tags = re.search(r'<!-- Tags: (.*?) -->', chunk)
                tags = tags[1].split() if tags else []
                tags += ['volume::'+str(volume), 'file::'+file.stem]
                note = genanki.Note(model=model, fields=values, guid=genanki.guid_for('gibbon',ident), tags=tags)
                decks[volume].add_note(note)
                report.append({'id': ident, 'volume':volume, 'file':file.name, 'portraits':[p['id'] for p in selected]})
        assert len(report)==len({r['id'] for r in report})==281
        package = genanki.Package(list(decks.values()))
        package.media_files = [str(p) for p in media.values()]
        destination = OUT/'Gibbon-Volumes-I-II.apkg'
        package.write_to_file(str(destination))
        verify(destination, report, media)
        (OUT/'anki-build-report.json').write_text(json.dumps({'decks':{d.name:len(d.notes) for d in decks.values()}, 'cards':report, 'media':len(media)},indent=2)+'\n')
        print(f'Built {destination}: '+', '.join(f'{d.name}: {len(d.notes)}' for d in decks.values())+f'; {len(media)} images.')

def verify(destination, report, expected_media):
    with zipfile.ZipFile(destination) as z, tempfile.TemporaryDirectory() as temp:
        assert z.testzip() is None
        mapping = json.loads(z.read('media'))
        assert set(mapping.values()) == set(expected_media)
        for key,name in mapping.items():
            assert z.read(key)==expected_media[name].read_bytes(), name
        db = Path(temp)/'collection.anki2'
        db.write_bytes(z.read('collection.anki2'))
        with sqlite3.connect(db) as con:
            assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
            assert con.execute('select count(*) from cards').fetchone()[0]==len(report)
            assert con.execute('select count(distinct guid) from notes').fetchone()[0]==len(report)
            actual = {}
            for flds,did in con.execute('select notes.flds,cards.did from notes join cards on cards.nid=notes.id'):
                fields = flds.split('\x1f')
                assert len(fields)==len(FIELDS) and fields[1] and fields[2] and not fields[-1]
                assert not re.search(r'(?:src|href)="(?:\.\./|sources/)', flds)
                assert all(name in mapping.values() for name in re.findall(r'<img[^>]+src="([^"]+)"',flds))
                actual[fields[0]] = did
            assert actual=={r['id']:stable_id('gibbon-volume-'+str(r['volume'])) for r in report}

if __name__=='__main__':
    build()

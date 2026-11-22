#!/usr/bin/env python3
"""Deterministic checks for the static GitHub Pages catalog and article links."""
from __future__ import annotations
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import urlparse, unquote

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
REQUIRED={'diplomacy','policy','technology','business','society','history','people'}
STATES={'reference_transcription','verified'}

class Structure(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.event_nodes=0;self.h1=0;self.mobile_lists=0;self.article_notice=False;self.titles=0
    def handle_starttag(self,tag,attrs):
        info=dict(attrs)
        if tag=='a' and info.get('href'):
            self.links.append(info['href'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.titles+=1
        if tag=='li' and re.search(r'\bevent\s+event--',info.get('class','')):
            self.event_nodes+=1
        if tag=='ol' and 'mobile-event-list' in info.get('class',''):
            self.mobile_lists+=1
        if tag=='aside' and 'article-notes' in info.get('class',''):
            self.article_notice=True


def verify() -> None:
    for f in ('index.html','assets/site.css','assets/site.js','data/catalog.json','.nojekyll'):
        if not (DOCS/f).exists():raise ValueError('Missing '+f)
    catalog=json.loads((DOCS/'data/catalog.json').read_text(encoding='utf8'))
    cats=catalog.get('taxonomies',[])
    ids=[x['id'] for x in cats]
    if set(ids)!=REQUIRED or len(ids)!=len(set(ids)):
        raise ValueError('Seven unique category ids required')
    tags={x['id'] for x in cats}
    entries=catalog.get('events',[])
    slugs=set()
    for record in entries:
        for key in ('slug','title','description','range','nodes','category','tags','updated_at','status','url'):
            if key not in record:raise ValueError('Missing catalog field '+key)
        slug=record['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Invalid slug '+slug)
        if slug in slugs:raise ValueError('Duplicate slug '+slug)
        slugs.add(slug)
        if record['status'] not in STATES:raise ValueError('Unrecognized status '+record['status'])
        if record['category'] not in tags:raise ValueError('Category missing '+record['category'])
        if not isinstance(record['nodes'],int) or not 4<=record['nodes']<=10:raise ValueError('Node count invalid')
        if not isinstance(record['tags'],list):raise ValueError('Tags must be list')
        target=f'./events/{slug}/'
        if record['url']!=target:raise ValueError('Catalog URL not project-subpath safe: '+record['url'])
        page=DOCS/'events'/slug/'index.html'
        if not page.is_file():raise ValueError('Broken catalog page: '+str(page))
        html=page.read_text(encoding='utf-8')
        structure=Structure();structure.feed(html)
        if structure.event_nodes!=record['nodes']:
            raise ValueError(f'Node count mismatch: {slug} catalog={record["nodes"]} HTML={structure.event_nodes}')
        if structure.mobile_lists!=1 or not structure.article_notice:
            raise ValueError('Missing mobile fallback or provenance notice: '+slug)
        if record['status']=='reference_transcription' and ('未经独立' not in html and '尚未独立' not in html):
            raise ValueError('Reference transcription must show a visible warning: '+slug)
        for href in structure.links:
            if href.startswith(('http://','https://','mailto:','#')):continue
            parsed=urlparse(href)
            if parsed.scheme or parsed.netloc:raise ValueError('Unsafe link: '+href)
            file_name=unquote(parsed.path)
            dest=(page.parent/file_name).resolve()
            if not dest.is_relative_to(DOCS.resolve()):raise ValueError('Link escapes public docs: '+href)
            if dest.is_dir():dest=dest/'index.html'
            if not dest.exists():raise ValueError('Broken relative link: '+href+' in '+slug)
    front=Structure();front.feed((DOCS/'index.html').read_text(encoding='utf-8'))
    if front.titles!=1 or front.h1!=1:raise ValueError('Homepage must have one h1 and title')
    for href in front.links:
        if href.startswith(('http://','https://','mailto:','#')):continue
        dest=(DOCS/href).resolve()
        if not dest.is_relative_to(DOCS.resolve()):raise ValueError('Home link escapes docs: '+href)
        if dest.is_dir():dest=dest/'index.html'
        if not dest.is_file():raise ValueError('Broken homepage href: '+href)
    print(f'OK: {len(entries)} published record(s), {len(cats)} categories, project-safe links, notices and counts')

if __name__=='__main__':
    try:verify()
    except Exception as err:
        print('ERROR:',err,file=sys.stderr)
        raise SystemExit(2)

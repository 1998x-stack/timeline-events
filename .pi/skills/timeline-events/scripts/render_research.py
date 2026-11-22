#!/usr/bin/env python3
"""Layer a source-mapped research dossier on canonical timeline HTML.

The main renderer and reference/eight-crises HTML remain unchanged. Research
sections are an opt-in progressive enhancement with standalone CSS and JS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from render_html import render_html
from dossier_renderer import render_research_dossier

CSS=ROOT/'templates/research.css'
JS=ROOT/'templates/research.js'


def render_research_html(data, *, site_url=None):
    if not isinstance(data.get('research'),dict) or not data['research']:
        raise ValueError('research must be a nonempty object for dossier output')
    page=render_html(data,site_url=site_url)
    supplement=render_research_dossier(data)
    if not supplement.strip() or '<aside class="article-notes"' not in page:
        raise ValueError('could not find required dossier insertion point')
    # The <style> and <script> additions keep an offline, self-contained file.
    page=page.replace('</style>', '\n'+CSS.read_text(encoding='utf8')+'\n</style>',1)
    page=page.replace('<aside class="article-notes"',supplement+'\n<aside class="article-notes"',1)
    script=JS.read_text(encoding='utf8').replace('</script','<\\/script')
    page=page.replace('</body>','<script>\n'+script+'\n</script>\n</body>',1)
    return page


def main(argv=None):
    p=argparse.ArgumentParser(description='Generate a source-backed interactive research timeline.')
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,default=Path('dist/research.html'))
    p.add_argument('--site-url',default=None)
    args=p.parse_args(argv)
    try:
        data=json.loads(args.input.read_text(encoding='utf8'))
        html=render_research_html(data,site_url=args.site_url)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(html,encoding='utf8')
        print(f'OK: {args.output} ({len(html)} chars, {len(data["events"])} nodes, {len(data["research"].get("claim_audit",[]))} claim audits)')
        return 0
    except (ValueError,KeyError,OSError) as exc:
        print('ERROR:',exc,file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate a self-contained, editable timeline HTML article from reviewed event JSON.

Default: require existing evidence-backed schema and original source URLs.
--reference-transcription: only for faithfully transcribing user-provided design
references (NOT for passing unverified claims off as verified research).
"""
from __future__ import annotations

import argparse
from datetime import datetime
from html import escape
import json
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from timeline_events import validate as validate_evidence, cells, wrap, event_date

HTML = ROOT / "templates" / "timeline.html"
CSS = ROOT / "templates" / "timeline.css"
INTERACTIONS = ROOT / "templates" / "timeline.interactions.js"

class TimelineHtmlError(ValueError):
    pass


def e(x: object) -> str:
    return escape(str(x), quote=True)


def full_year_month(value: str) -> str:
    day = event_date(value)
    return f"{day.year:04d}.{day.month:02d}"


def duration(a: str, b: str) -> str:
    start, end = event_date(a), event_date(b)
    n = (end.year - start.year) * 12 + end.month - start.month
    years, months = divmod(n, 12)
    return (f"{years}年" if years else "") + (f"{months}个月" if months else "") or "0个月"


def cn_number(value: int) -> str:
    return "零一二三四五六七八九十"[value] if value <= 10 else str(value)


def validate_reference(data: dict) -> None:
    meta = data.get('metadata') or {}
    if meta.get('verification_state') != 'reference_transcription':
        raise TimelineHtmlError('参考图模式必须显式声明 verification_state=reference_transcription')
    for field in ('title', 'subtitle', 'updated_at', 'notice'):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise TimelineHtmlError('metadata.' + field + ' 必填')
    datetime.strptime(meta['updated_at'], '%Y-%m-%d')
    events = data.get('events') or []
    if not 4 <= len(events) <= 10:
        raise TimelineHtmlError('HTML 参考图模式要求 4—10 个节点')
    prev = None
    for event in events:
        date = event_date(event.get('date', ''))
        if prev and date < prev:
            raise TimelineHtmlError('节点时间必须升序')
        prev = date
        for field in ('title', 'description'):
            if not isinstance(event.get(field), str) or not event[field].strip():
                raise TimelineHtmlError('事件 ' + field + ' 必填')
        lines = event.get('lines')
        if lines is not None and (not isinstance(lines, list) or not 1 <= len(lines) <= 3 or any(not isinstance(x, str) or not x for x in lines)):
            raise TimelineHtmlError('lines 只能是 1—3 条非空文本')
        if lines and any(cells(x) > 33 for x in lines):
            raise TimelineHtmlError('节点行文字过长，检查布局')
    if any(not isinstance(p,dict) or any(k not in p for k in ('name','period','summary')) for p in data.get('phases',[])):
        raise TimelineHtmlError('阶段数据结构错误')
    if len(data.get('phases',[])) > 4 or len(data.get('insights',[])) > 3:
        raise TimelineHtmlError('阶段或结论数量超出模板限制')


def event_lines(event: dict) -> list[str]:
    if event.get('lines'):
        return event['lines']
    return wrap(event['description'], 23)[:3]


def summary(data: dict) -> str:
    events = data['events']
    phases = data.get('phases', [])
    return f"{full_year_month(events[0]['date'])}—{full_year_month(events[-1]['date'])}：{duration(events[0]['date'],events[-1]['date'])} · {cn_number(len(events))}个关键节点" + (f" · {cn_number(len(phases))}个阶段" if phases else "")


def render_board(data: dict) -> str:
    m = data['metadata']
    children=[]
    add=children.append
    producer=e(m.get('producer','资料整理'))
    stamp=e(m.get('display_date', m['updated_at'][:7].replace('-', '.')))
    add(f'''<header class="board-header"><h1>{e(m['title'])}</h1>
<span class="board-credit">{producer} · {stamp}</span><div class="top-rule" aria-hidden="true"></div>
<p class="board-subtitle">{e(m['subtitle'])}</p></header>''')
    add(f'<div class="summary-bar">{e(summary(data))}</div>')
    add('<p class="legend">蓝色：历史事件　红色：最新节点</p>')
    add('<div class="axis" aria-hidden="true"></div>')
    add('<ol class="events" aria-label="按时间排序的关键节点">')
    events=data['events']
    for i,ev in enumerate(events):
        # Match the reference coordinates: x = 139, 337, ..., 1919.
        x=round(139+i*1780/(len(events)-1),3)
        side='top' if i%2 == 0 else 'bottom'
        hot=' event--highlight' if i==len(events)-1 else ''
        lines=''.join('<span>'+e(s)+'</span>' for s in event_lines(ev))
        add(f'''<li class="event event--{side}{hot}" style="--x:{x}px" data-date="{e(ev['date'])}">
<span class="event-date">{full_year_month(ev['date'])}</span>
<p class="event-lines">{lines}</p><span class="connector" aria-hidden="true"></span>
<button type="button" class="event-dot" data-event-index="{i}" aria-haspopup="dialog" aria-label="查看 {full_year_month(ev['date'])} 节点详情：{e(ev['title'])}" title="点击查看事件详情"></button></li>''')
    add('</ol>')
    phases=data.get('phases',[])
    if phases:
        add('<section class="board-section phases-section"><h2>阶段划分</h2><div class="phase-grid">')
        for phase in phases:
            add(f'''<article class="phase-card"><div class="phase-card-head"><span>{e(phase['name'])}</span><time>{e(phase['period'])}</time></div><p>{e(phase['summary'])}</p></article>''')
        add('</div></section>')
    insights=data.get('insights',[])
    if insights:
        add('<section class="board-section insights-section"><h2>阅读提示</h2><div class="insight-grid">')
        for insight in insights:
            if insight.get('lines'):
                text=''.join(f'<span>{e(s)}</span>' for s in insight['lines'])
            else:
                text=''.join(f'<span>{e(s)}</span>' for s in wrap(insight['description'],49)[:2])
            add(f'''<article class="insight-card"><h3>{e(insight['title'])}</h3><p>{text}</p></article>''')
        add('</div></section>')
    footer=data.get('footer',{})
    source_text=footer.get('source_label', f"资料：{', '.join(s['publisher'] for s in data.get('sources', []))}")
    note=footer.get('note', f"节点间距仅作示意，不按实际时间比例绘制 · 截至 {m['updated_at']}")
    add(f'''<footer class="board-footer"><span class="source">{e(source_text)}</span><span class="note">{e(note)}</span></footer>''')
    return '\n'.join(children)


def render_mobile(data: dict) -> str:
    m=data['metadata']
    sections=[f'''<article class="mobile-reader"><h1>{e(m['title'])}</h1><p class="meta">{e(m.get('producer','资料整理'))} · {e(m['updated_at'])}</p>
<div class="mobile-summary">{e(summary(data))}</div><h2>关键事件</h2><ol class="mobile-event-list">''']
    for index, event in enumerate(data['events']):
        sections.append(f'<li><time datetime="{e(event["date"])}">{full_year_month(event["date"])}</time><p>{e(event["description"])}</p><button type="button" class="mobile-event-action" data-event-index="{index}" aria-haspopup="dialog">查看节点详情 <span aria-hidden="true">↗</span></button></li>')
    sections.append('</ol>')
    if data.get('phases'):
        sections.append('<h2>阶段划分</h2>')
        for p in data['phases']:
            sections.append(f'<section class="mobile-card"><strong>{e(p["name"])} · {e(p["period"])}</strong>{e(p["summary"])}</section>')
    if data.get('insights'):
        sections.append('<h2>阅读提示</h2>')
        for p in data['insights']:
            sections.append(f'<section class="mobile-card"><strong>{e(p["title"])}</strong>{e(p["description"])}</section>')
    sections.append('</article>')
    return '\n'.join(sections)



DEEP_READING_CSS = "\n.research-reading{margin-top:34px;padding-top:26px;border-top:1px solid #d3e1e7}\n.research-reading h2{font-size:clamp(22px,2.2vw,31px);line-height:1.4;color:#183a49;margin:0 0 12px}\n.reading-intro{color:#5c7280;font-size:15px;line-height:1.85;max-width:960px}\n.reading-nav{display:flex;flex-wrap:wrap;gap:9px;margin:22px 0 25px}\n.article-notes .reading-nav a{font-size:13px;letter-spacing:.04em;color:#245d7b;text-decoration:none;padding:8px 13px;border:1px solid #cadce5;border-radius:999px;background:#f7fafc;transition:background .22s ease,transform .22s ease}\n.article-notes .reading-nav a:hover{background:#e5f2f8;transform:translateY(-2px)}\n.research-chapter{scroll-margin-top:24px;padding:27px 30px;margin:0 0 16px;border-radius:13px;border:1px solid #dbe5ea;background:linear-gradient(125deg,#f9fbfc,#fff 65%);box-shadow:0 8px 28px rgba(22,54,70,.035)}\n.research-chapter:target{border-color:#6ca8c8;box-shadow:0 0 0 3px rgba(60,133,173,.09)}\n.chapter-index{font-size:12px;font-weight:700;letter-spacing:.14em;color:#668a9d;margin:0 0 10px}\n.research-chapter h3{font-size:clamp(19px,2vw,25px);line-height:1.4;margin:0 0 14px;color:#163c50}\n.research-chapter p:not(.chapter-index){line-height:1.93;margin:12px 0;font-size:15px;color:#354f5d}\n.research-chapter p strong{color:#183a49}\n.chapter-sources{border-top:1px solid #dfebef;padding-top:12px;margin-top:17px;display:flex;flex-wrap:wrap;gap:8px 13px;font-size:12px;align-items:center}\n.chapter-sources strong{color:#69818c}\n.article-notes .chapter-sources a{font-size:12px;line-height:1.5}\n@media(max-width:760px){.article-notes{padding:22px 17px}.research-chapter{padding:19px 16px}.research-chapter p:not(.chapter-index){font-size:14px}.reading-nav{gap:7px}}\n@media(prefers-reduced-motion:reduce){.article-notes .reading-nav a{transition:none}.article-notes .reading-nav a:hover{transform:none}}\n"


def render_chapters(data: dict) -> str:
    """Render expanded analytical commentary from the reviewed data model."""
    chapters = data.get('chapters', [])
    if not chapters:
        return ''
    lookup = {source['id']: source for source in data.get('sources', [])}
    out = ['<section class="research-reading" id="deep-reading" aria-labelledby="reading-title">',
           '<h2 id="reading-title">逐次展开：八次危机的背景、机制与政策回应</h2>',
           '<p class="reading-intro">本部分为原创研究梳理，区分著作解释框架、可核实的历史事实与仍存在争议的归因；节点日期是各阶段代表史实，并不表示危机均在当月爆发。</p>',
           '<nav class="reading-nav" aria-label="跳转至各次危机">']
    for i, chapter in enumerate(chapters, 1):
        out.append(f'<a href="#chapter-{i}">危机{i:02d}</a>')
    out.append('</nav>')
    labels = [('anchor', '日期定位'), ('background', '历史背景'),
              ('mechanism', '解释机制'), ('response', '政策与传导'),
              ('assessment', '评议与证据边界')]
    for i, chapter in enumerate(chapters, 1):
        out.append(f'<section class="research-chapter" id="chapter-{i}">')
        out.append(f'<p class="chapter-index">CHAPTER {i:02d} / {e(chapter["period"])}</p>')
        out.append(f'<h3>{e(chapter["title"])}</h3>')
        for key, label in labels:
            out.append(f'<p><strong>{label} · </strong>{e(chapter[key])}</p>')
        out.append('<div class="chapter-sources"><strong>本章资料：</strong>')
        for source_id in chapter.get('source_ids', []):
            source = lookup.get(source_id)
            if source:
                out.append(f'<a target="_blank" rel="noopener noreferrer" href="{e(source["url"])}">{e(source["publisher"])} · {e(source["title"])}</a>')
        out.append('</div></section>')
    out.append('</section>')
    return '\n'.join(out)


def render_notes(data: dict, *, reference: bool, site_url: str | None=None) -> str:
    m=data['metadata']
    if reference:
        notice=e(m['notice'])
        status='<p class="notice"><strong>版式复刻 / 未经独立事实审计：</strong> '+notice+'</p>'
        sources='<p>页面文字来自用户上传的参考图片，底部机构名称按原图转录，不表示已逐条阅读、确认或背书其内容。正式发布经审校的事件文章时，请使用带有 <code>sources</code> / <code>source_ids</code> 的核验 JSON。</p>'
    else:
        notice='已依据用户提供的来源清单构建。注意：工具仅能检验 URL 结构和引用关联，来源语义核验仍由研究 Agent/编辑负责。'
        status='<p>'+e(notice)+'</p>'
        sources='<h3>引用来源</h3><ul>'+''.join('<li><a target="_blank" rel="noopener noreferrer" href="'+e(s['url'])+'">'+e(s['publisher'])+' · '+e(s['title'])+'</a></li>' for s in data['sources'])+'</ul>'
    reading_nav='<a href="#deep-reading">阅读八次危机详解</a>' if data.get('chapters') else ''
    nav=(f'<a href="{e(site_url)}">返回时间轴资料库首页</a>' if site_url else '')
    return f'''<aside class="article-notes" aria-label="资料与使用说明">
<h2>资料与核验说明</h2>{status}{sources}<p>展示方式：等距时间轴，节点距离不代表真实时间间隔；移动设备改用顺序事件列表。</p>
<div class="article-tools">{nav}<a href="#timeline-shell">返回图片</a>{reading_nav}</div>{render_chapters(data)}
</aside>'''


def render_html(data: dict, *, reference=False, site_url: str | None=None) -> str:
    if reference: validate_reference(data)
    else: validate_evidence(data)
    base=HTML.read_text(encoding='utf-8')
    for key,value in {
        'PAGE_TITLE':e(data['metadata']['title'])+'｜Timeline Events',
        'PAGE_DESCRIPTION':e(data['metadata']['subtitle']),
        'CSS':CSS.read_text(encoding='utf-8') + (DEEP_READING_CSS if data.get('chapters') else ''),
        'ARTBOARD':render_board(data),
        'MOBILE':render_mobile(data),
        'NOTES':render_notes(data,reference=reference,site_url=site_url),
        'INTERACTIONS':INTERACTIONS.read_text(encoding='utf-8'),
        'TIMELINE_DATA':json.dumps({'events':data['events'], 'sources':data.get('sources',[]), 'verification_state': 'reference_transcription' if reference else 'verified'},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    }.items():base=base.replace('%%'+key+'%%', value)
    return base


def main(argv=None):
    p=argparse.ArgumentParser(description='Render an editable, self-contained timeline HTML page.')
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,default=Path('dist/timeline.html'))
    p.add_argument('--reference-transcription',action='store_true',help='Skip source attestation only for user-provided image transcription. Adds explicit warning.')
    p.add_argument('--site-url',help='Relative link to site home for pages published to GitHub Pages')
    args=p.parse_args(argv)
    try:
        data=json.loads(args.input.read_text(encoding='utf-8'))
        page=render_html(data,reference=args.reference_transcription,site_url=args.site_url)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(page,encoding='utf-8')
        print(f'OK: {args.output} ({len(page)} chars, {len(data["events"])} nodes)')
        return 0
    except (OSError, ValueError,KeyError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())

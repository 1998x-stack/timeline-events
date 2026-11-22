#!/usr/bin/env python3
"""Deterministic evidence-backed Chinese SVG/PNG timeline renderer.

Portable: script resolves no project-specific paths; SVG needs Python stdlib;
PNG needs CairoSVG. Never uses network calls or invents evidence.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

WIDTH, HEIGHT = 3200, 2000
NAVY, INK, BLUE, RED, MUTED = '#153847', '#142e3b', '#377fa8', '#bc2433', '#74878f'
FONT = 'Noto Sans CJK SC, Source Han Sans SC, Microsoft YaHei, sans-serif'

class TimelineError(ValueError):
    """Invalid evidence, chronology, or impossible layout."""


def cells(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1 for c in s)


def wrap(s: str, max_cells: int) -> list[str]:
    if not isinstance(s, str) or not s.strip():
        raise TimelineError('文本不能为空')
    result, row, n = [], '', 0
    for char in s.strip():
        if char == '\n':
            if row: result.append(row)
            row, n = '', 0
            continue
        k = cells(char)
        if n+k > max_cells and row:
            result.append(row)
            row, n = '', 0
        row += char
        n += k
    if row: result.append(row)
    return result


def event_date(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?',value):
        raise TimelineError('事件日期必须为 YYYY-MM 或 YYYY-MM-DD')
    try:
        return datetime.strptime(value if len(value)==10 else value+'-01','%Y-%m-%d').date()
    except ValueError as e:
        raise TimelineError('日期不存在: '+value) from e


def validate(data: dict) -> None:
    if not isinstance(data, dict): raise TimelineError('JSON 顶层必须是对象')
    meta=data.get('metadata')
    if not isinstance(meta, dict): raise TimelineError('缺少 metadata')
    for field in ('title','subtitle','updated_at'):
        if not isinstance(meta.get(field),str) or not meta[field].strip():
            raise TimelineError('metadata.'+field+' 不能为空')
    if cells(meta['title'])>78 or cells(meta['subtitle'])>122:
        raise TimelineError('主副标题过长')
    try: updated=datetime.strptime(meta['updated_at'],'%Y-%m-%d').date()
    except ValueError as e: raise TimelineError('updated_at 必须为 YYYY-MM-DD') from e
    sources=data.get('sources')
    if not isinstance(sources,list) or not sources:
        raise TimelineError('研究模式需要至少一个原始来源 URL')
    ids=set()
    for s in sources:
        if not isinstance(s,dict): raise TimelineError('sources 元素类型错误')
        for field in ('id','publisher','title','url'):
            if not isinstance(s.get(field),str) or not s[field].strip(): raise TimelineError('sources 缺少 '+field)
        if s['id'] in ids: raise TimelineError('重复来源 id')
        ids.add(s['id'])
        u=urlsplit(s['url'])
        if u.scheme not in ('https','http') or not u.netloc: raise TimelineError('URL 无效: '+s['id'])
    events=data.get('events')
    if not isinstance(events,list) or not 4<=len(events)<=10:
        raise TimelineError('时间轴必须为 4–10 个事件')
    last=None
    for index,ev in enumerate(events):
        for field in ('date','title','description'):
            if not isinstance(ev.get(field),str) or not ev[field].strip():raise TimelineError('事件缺少 '+field)
        d=event_date(ev['date'])
        if last and d<last:raise TimelineError('日期必须升序')
        last=d
        if d>updated and ev.get('status')!='planned':
            raise TimelineError('未来事件必须显式标注 planned')
        if ev.get('status','confirmed') not in ('confirmed','planned'):
            raise TimelineError('状态只能为 confirmed/planned')
        if len(wrap(ev['title'],16))>2 or len(wrap(ev['description'],20))>3:
            raise TimelineError('节点标题或描述过长，请缩短而非截断')
        refs=ev.get('source_ids')
        if not isinstance(refs,list) or not refs or any(s not in ids for s in refs):
            raise TimelineError('source_ids 缺失或引用不存在')
        if ev.get('highlight',False) and index!=len(events)-1:
            raise TimelineError('只能高亮最后一个事件')
    phases=data.get('phases',[])
    if not isinstance(phases,list) or len(phases)>4:raise TimelineError('最多四阶段')
    for p in phases:
        if not isinstance(p,dict) or any(not isinstance(p.get(k),str) or not p[k] for k in ('name','period','summary')):
            raise TimelineError('阶段需 name/period/summary')
        if cells(p['summary'])>38:raise TimelineError('阶段概述过长')
    insights=data.get('insights',[])
    if not isinstance(insights,list) or len(insights)>3:raise TimelineError('最多三个提示')
    for p in insights:
        if not isinstance(p,dict) or any(not isinstance(p.get(k),str) or not p[k] for k in ('title','description')):
            raise TimelineError('阅读提示字段错误')
        if len(wrap(p['description'],53))>2:raise TimelineError('提示过长')


def text(x,y,s,size=29,color=INK,bold=False,anchor='start'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(str(s))}</text>')


def rect(x,y,w,h,color,stroke='none',radius=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}" stroke-width="2"/>'


def line(x,y,x2,y2,color,width=3):
    return f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"/>'


def period(a:date,b:date)->str:
    n=(b.year-a.year)*12+b.month-a.month
    y,m=divmod(n,12)
    return (f'{y}年' if y else '')+(f'{m}个月' if m else '') or '0个月'


def render_svg(data:dict)->str:
    validate(data)
    m=data['metadata']; es=data['events']; n=len(es)
    start,end=event_date(es[0]['date']),event_date(es[-1]['date'])
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(m["title"],quote=True)}">']
    o=out.append
    o(rect(0,0,WIDTH,HEIGHT,'white'))
    o(text(120,137,m['title'],65 if cells(m['title'])<60 else 56,INK,True))
    o(text(3060,115,m.get('producer','资料整理')+' · '+m['updated_at'],28,MUTED,anchor='end'))
    o(line(120,177,3070,177,NAVY,5))
    o(text(125,247,m['subtitle'],35,MUTED))
    o(rect(390,340,2420,126,'#eaf4f8',NAVY,25))
    o(text(1600,422,f'{start.year:04d}.{start.month:02d} 至 {end.year:04d}.{end.month:02d} · {period(start,end)} · {n}个关键节点',52,NAVY,True,'middle'))
    y=928
    o(line(140,y,3060,y,NAVY,12))
    for i,ev in enumerate(es):
        x=250+i*2700/(n-1)
        hot=i==n-1 or ev.get('highlight',False)
        accent=RED if hot else BLUE
        top=i%2==0
        if top:
            o(line(x,814,x,y-30,'#b5c2c8',4))
            o(text(x,545,ev['date'][:7].replace('-','.'),40,accent,True,'middle'))
            for j,s in enumerate(wrap(ev['title'],16)):o(text(x,612+j*44,s,31,INK,True,'middle'))
            for j,s in enumerate(wrap(ev['description'],20)):o(text(x,716+j*40,s,27,INK,anchor='middle'))
        else:
            o(line(x,y+27,x,1044,'#b5c2c8',4))
            o(text(x,1127,ev['date'][:7].replace('-','.'),40,accent,True,'middle'))
            for j,s in enumerate(wrap(ev['title'],16)):o(text(x,1194+j*44,s,31,INK,True,'middle'))
            for j,s in enumerate(wrap(ev['description'],20)):o(text(x,1300+j*40,s,27,INK,anchor='middle'))
        o(f'<circle cx="{x:.1f}" cy="{y}" r="29" fill="white"/>')
        o(f'<circle cx="{x:.1f}" cy="{y}" r="25" fill="{accent}"/>')
    phases=data.get('phases',[])
    o(text(145,1495,'阶段划分',40,NAVY,True))
    if phases:
        w=(2930-(len(phases)-1)*20)/len(phases)
        for i,p in enumerate(phases):
            x=145+i*(w+20)
            o(rect(round(x),1524,round(w),147,['#eaf4f8','#edf4f8','#f8f2e7','#fcf0f2'][i],radius=17))
            o(text(x+25,1580,p['name'],29,RED if i==len(phases)-1 else NAVY,True))
            o(text(x+w-22,1580,p['period'],24,BLUE,anchor='end'))
            o(text(x+25,1640,p['summary'],26))
    o(text(145,1737,'阅读提示',40,NAVY,True))
    insights=data.get('insights',[])
    if insights:
        w=(2930-(len(insights)-1)*20)/len(insights)
        for i,p in enumerate(insights):
            x=145+i*(w+20)
            o(rect(round(x),1755,round(w),160,'#f7f9fa','#dce6e9',15))
            o(text(x+28,1806,p['title'],29,NAVY,True))
            for j,s in enumerate(wrap(p['description'],53)):o(text(x+28,1853+j*35,s,24))
    o(line(145,1935,3060,1935,'#cdd9df',2))
    o(text(145,1971,f'资料来源：{len(data["sources"])}份可追溯材料，原始 URL 见同名 sources.md',24,MUTED))
    o(text(3060,1971,'节点等距分布，不代表真实时间比例',24,MUTED,anchor='end'))
    o('</svg>')
    return '\n'.join(out)+'\n'


def render_manifest(data:dict)->str:
    validate(data)
    lookup={s['id']:s for s in data['sources']}
    meta=data['metadata']
    out=['# '+meta['title'],'','资料截止日：'+meta['updated_at'],'', '> 此清单记录格式上可追溯的引用；每条来源是否支持其断言仍需研究人员逐条阅读核验。','', '## 节点与证据','']
    for i,ev in enumerate(data['events'],1):
        out.extend([f'### {i}. {ev["date"]} — {ev["title"]}','',ev['description'],''])
        if ev.get('status')=='planned':out.extend(['**计划事项，尚未发生。**',''])
        for key in ev['source_ids']:
            s=lookup[key]
            out.append(f'- [{s["publisher"]} · {s["title"]}]({s["url"]})')
        out.append('')
    out.extend(['## 参考资料',''])
    for s in data['sources']:
        out.append(f'- [{s["id"]}] {s["publisher"]} — [{s["title"]}]({s["url"]})')
    return '\n'.join(out)+'\n'


def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Render evidence-reviewed event timeline as SVG, PNG, and source manifest')
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,default=Path('dist/timeline'))
    p.add_argument('--format',choices=('both','svg','png'),default='both')
    args=p.parse_args(argv)
    try:
        data=json.loads(args.input.read_text(encoding='utf-8'))
        image=render_svg(data)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if args.format in ('both','svg'):args.output.with_suffix('.svg').write_text(image,encoding='utf-8')
        if args.format in ('both','png'):
            try:import cairosvg
            except ImportError as exc:raise TimelineError('PNG 需要 CairoSVG: pip install CairoSVG') from exc
            cairosvg.svg2png(bytestring=image.encode('utf-8'),write_to=str(args.output.with_suffix('.png')))
        args.output.with_name(args.output.name+'.sources.md').write_text(render_manifest(data),encoding='utf-8')
        print('OK: '+str(args.output));return 0
    except (OSError,ValueError,KeyError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())

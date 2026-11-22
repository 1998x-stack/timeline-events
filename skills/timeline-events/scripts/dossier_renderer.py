"""Long-form researched dossier extension for source-backed timeline JSON.

All strings are HTML-escaped. A research dossier is optional; the original
reference transcription layout and exported page remain unaffected.
"""
from html import escape


def e(value):
    return escape(str(value), quote=True)


def render_research_dossier(data):
    research = data.get('research') or {}
    if not research:
        return ''
    if not isinstance(research, dict):
        raise ValueError('research must be a JSON object')
    sources = {s['id']: s for s in data.get('sources', [])}
    def citations(refs):
        parts=[]
        for key in refs:
            if key not in sources:
                raise ValueError('Unknown dossier source_id: '+str(key))
            s=sources[key]
            parts.append('<a href="{}" rel="noopener noreferrer" target="_blank" title="{}">{}</a>'.format(e(s['url']),e(s['title']),e(s['publisher'])))
        return '<div class="dossier-citations" aria-label="本段资料来源">' + ''.join(parts) + '</div>'

    html=[]
    add=html.append
    add('<section class="research-dossier" id="research-dossier" aria-labelledby="research-title">')
    add('<header class="dossier-lead">')
    add('<p class="dossier-eyebrow">{}</p>'.format(e(research.get('eyebrow','RESEARCH DOSSIER'))))
    add('<h2 id="research-title">{}</h2>'.format(e(research.get('headline','研究与证据评估'))))
    add('<p class="dossier-summary">{}</p>'.format(e(research.get('summary',''))))
    add('<nav class="dossier-toc" aria-label="研究章节目录"><a href="#dossier-chapters">研究章节</a><a href="#dossier-network">关系与作用</a><a href="#claim-audit">主张核验</a><a href="#dossier-interpretation">综合解释</a><a href="#dossier-methodology">研究边界</a></nav>')
    add('</header>')

    metrics=research.get('metrics',[])
    if len(metrics)>6: raise ValueError('research metrics exceeds 6')
    add('<div class="dossier-metrics">')
    for item in metrics:
        add('<article class="dossier-metric"><strong>{}</strong><span>{}</span><small>{}</small></article>'.format(*[e(item[k]) for k in ('value','label','note')]))
    add('</div>')

    chapters=research.get('chapters',[])
    if len(chapters)>12: raise ValueError('research chapters exceeds 12')
    add('<div id="dossier-chapters" class="dossier-section-heading"><span>01 / EXPLAINED</span><h2>崛起路径：关键机制</h2><p>每节均附资料来源，阅读者可直接打开原始页面核查。</p></div>')
    add('<div class="dossier-chapters">')
    for chapter in chapters:
        add('<article class="dossier-chapter"><div class="chapter-index"><span>{}</span><small>{}</small></div><div class="chapter-body">'.format(e(chapter.get('index','—')),e(chapter.get('eyebrow','EVIDENCE'))))
        add('<h3>{}</h3>'.format(e(chapter['title'])))
        for paragraph in chapter['body']:
            add('<p>{}</p>'.format(e(paragraph)))
        add('<p class="chapter-takeaway"><strong>关键机制</strong> {}</p>'.format(e(chapter.get('takeaway',''))))
        add(citations(chapter.get('source_ids',[])))
        add('</div></article>')
    add('</div>')

    network=research.get('connections',[])
    if len(network)>12: raise ValueError('research connections exceeds 12')
    add('<div id="dossier-network" class="dossier-section-heading"><span>02 / NETWORKS</span><h2>人脉如何发挥作用？</h2><p>仅列有记录的工作联系，不把同校、同城或共同出席活动推断为秘密操控关系。</p></div>')
    add('<div class="connections-grid">')
    for item in network:
        add('<article class="connection-card"><p class="connection-role">{}</p><h3>{}</h3><p>{}</p><p class="connection-limits"><strong>证据边界：</strong>{}</p>'.format(e(item['role']),e(item['name']),e(item['mechanism']),e(item['limits'])))
        add(citations(item.get('source_ids',[])))
        add('</article>')
    add('</div>')

    audit=research.get('claim_audit',[])
    if len(audit)>20: raise ValueError('research claim audit exceeds 20')
    add('<div id="claim-audit" class="dossier-section-heading"><span>03 / CLAIM AUDIT</span><h2>逐条核对原文中的关键说法</h2><p>“没有找到证据”不等于“证明某事绝不可能发生”，重要争议应保留证据边界。</p></div>')
    add('<div class="audit-controls" role="group" aria-label="按核验状态筛选"><button type="button" data-audit-filter="all" aria-pressed="true">全部主张</button><button type="button" data-audit-filter="confirmed" aria-pressed="false">基本可核实</button><button type="button" data-audit-filter="qualified" aria-pressed="false">需谨慎</button></div>')
    add('<div class="claim-grid">')
    for i,item in enumerate(audit,1):
        group='confirmed' if item['verdict'] in ('可核实','约数成立','部分属实') else 'qualified'
        add('<article class="claim-card" data-audit-group="{}"><div class="claim-top"><span class="claim-num">{:02d}</span><span class="claim-verdict {}">{}</span></div><h3>{}</h3><p>{}</p>'.format(group,i,'claim-ok' if group=='confirmed' else 'claim-question',e(item['verdict']),e(item['claim']),e(item['finding'])))
        add(citations(item.get('source_ids',[])))
        add('</article>')
    add('</div>')

    add('<div id="dossier-interpretation" class="dossier-section-heading"><span>04 / SYNTHESIS</span><h2>没有单一“幕后答案”，只有可检验的机制</h2></div><div class="hypotheses-grid">')
    for item in research.get('hypotheses',[]):
        add('<article><h3>{}</h3><p>{}</p></article>'.format(e(item['title']),e(item['body'])))
    add('</div>')
    add('<div id="dossier-methodology" class="dossier-section-heading"><span>05 / METHODOLOGY</span><h2>方法、来源层级和研究边界</h2></div><ol class="dossier-method-list">')
    for item in research.get('methodology',[]):
        add('<li>{}</li>'.format(e(item)))
    add('</ol></section>')
    return '\n'.join(html)

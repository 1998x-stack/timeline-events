from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser
import re

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_html as renderer
import render_research as research_renderer

class HtmlTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'skills/timeline-events/examples/reference-image-transcription.json').read_text(encoding='utf-8'))

    def test_original_content_and_layout(self):
        html=renderer.render_html(self.data,reference=True)
        self.assertIn('2048px',html)
        self.assertIn('中美贸易战时间轴',html)
        self.assertIn('2018.07—2026.11：8年4个月',html)
        self.assertIn('十个关键节点',html)
        self.assertIn('2027.01.10',html)
        self.assertEqual(html.count('class="event event--'),10)
        self.assertEqual(html.count('class="phase-card"'),4)
        self.assertEqual(html.count('class="insight-card"'),3)
        self.assertIn('未经独立事实审计',html)

    def test_mobile_reader_contains_all_nodes(self):
        html=renderer.render_html(self.data,reference=True)
        self.assertIn('class="mobile-event-list"',html)
        self.assertIn('max-width:760px',html)
        self.assertEqual(html.count('class="mobile-event-list"'),1)
        self.assertEqual(html.count('<time datetime='),10)

    def test_reference_flag_is_mandatory(self):
        self.data['metadata']['verification_state']='verified'
        with self.assertRaises(renderer.TimelineHtmlError):
            renderer.render_html(self.data,reference=True)

    def test_default_mode_rejects_unverified_image(self):
        with self.assertRaises((KeyError,ValueError,TypeError)):
            renderer.render_html(self.data)

    def test_escapes_injected_html_and_attribute(self):
        self.data['metadata']['title']='<img src=x onerror="alert(1)">'
        self.data['events'][0]['lines'][0]='<script>alert(1)</script>'
        html=renderer.render_html(self.data,reference=True)
        self.assertNotIn('<img src=x',html)
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;img',html)
        self.assertIn('&lt;script&gt;',html)

    def test_rejects_reverse_order(self):
        self.data['events']=list(reversed(self.data['events']))
        with self.assertRaises(ValueError):
            renderer.render_html(self.data,reference=True)

    def test_rejects_oversized_manual_line(self):
        self.data['events'][0]['lines']=['错误'*100]
        with self.assertRaises(ValueError):
            renderer.render_html(self.data,reference=True)

    def test_reference_cli_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'example.html'
            code=renderer.main([str(ROOT/'skills/timeline-events/examples/reference-image-transcription.json'),'--reference-transcription','--output',str(p)])
            self.assertEqual(code,0)
            self.assertIn('<html lang="zh-CN">',p.read_text(encoding='utf-8'))

    def test_default_mode_verified_example(self):
        # Existing SVG validation schema is preserved for researched events.
        dataset={
            'metadata':{'title':'有证据的事件示例','subtitle':'演示文本','updated_at':'2025-06-01'},
            'sources':[{'id':'s1','publisher':'某单位','title':'原始材料','url':'https://example.org/source'}],
            'events':[
                {'date':f'2024-0{i}','title':f'节点{i}','description':'可追溯文字说明','source_ids':['s1']}
                for i in range(1,5)
            ],
            'phases':[],'insights':[]
        }
        html=renderer.render_html(dataset)
        self.assertIn('引用来源',html)
        self.assertEqual(html.count('class="event event--'),4)
        self.assertIn('https://example.org/source',html)

if __name__=='__main__':
    unittest.main()

# Interaction guards: keep the generator, checked-in page, and accessibility in sync.
class MotionTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'skills/timeline-events/examples/reference-image-transcription.json').read_text(encoding='utf-8'))

    def test_all_nodes_interactive_without_hiding_story(self):
        html=renderer.render_html(self.data,reference=True)
        self.assertEqual(html.count('aria-haspopup="dialog"'),20)
        self.assertEqual(html.count('class="event-dot"'),10)
        self.assertEqual(html.count('class="mobile-event-action"'),10)
        self.assertIn('class="event-dialog"',html)
        self.assertIn('id="detail-previous"',html)
        self.assertIn('id="detail-next"',html)
        self.assertIn('aria-labelledby="detail-title"',html)
        self.assertIn('未经独立事实审计',html)

    def test_json_data_is_safe_to_embed_in_script(self):
        self.data['events'][0]['description']='恶意</script><script>alert(1)</script>内容'
        html=renderer.render_html(self.data,reference=True)
        self.assertNotIn('恶意</script><script>',html)
        self.assertIn('\\u003c/script\\u003e',html)
        self.assertIn('恶意&lt;/script&gt;',html)

    def test_template_contains_reduced_motion_and_keyboard(self):
        css=(ROOT/'skills/timeline-events/templates/timeline.css').read_text(encoding='utf-8')
        js=(ROOT/'skills/timeline-events/templates/timeline.interactions.js').read_text(encoding='utf-8')
        self.assertIn('prefers-reduced-motion:reduce',css)
        self.assertIn('ArrowLeft',js)
        self.assertIn('ArrowRight',js)
        self.assertIn("event.key",js)
        self.assertIn("restoreFocus.focus",js)
        self.assertNotIn('innerHTML=',js)

    def test_deployed_page_matches_generator(self):
        expected=renderer.render_html(self.data,reference=True,site_url='../../index.html')
        actual=(ROOT/'docs/events/us-china-trade-war/index.html').read_text(encoding='utf-8')
        self.assertEqual(actual,expected)

class ResearchDossierTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'skills/timeline-events/examples/emmanuel-macron-rise.json').read_text(encoding='utf-8'))

    def test_research_content_is_visible_source_backed_and_interactive(self):
        page=research_renderer.render_research_html(self.data,site_url='../../index.html')
        self.assertEqual(page.count('class="event event--'),10)
        self.assertEqual(page.count('class="dossier-chapter"'),5)
        self.assertEqual(page.count('class="connection-card"'),5)
        self.assertEqual(page.count('class="claim-card"'),8)
        self.assertIn('François Henrot',page)
        self.assertIn('1995—1997',page)
        self.assertIn('data-audit-filter="confirmed"',page)
        self.assertIn('prefers-reduced-motion:reduce',page)
        self.assertIn('https://www.legifrance.gouv.fr/',page)

    def test_research_rejects_unmapped_reference(self):
        self.data['research']['chapters'][0]['source_ids']=['not-a-real-source']
        with self.assertRaises(ValueError):
            research_renderer.render_research_html(self.data)

    def test_published_research_page_matches_generator(self):
        expected=research_renderer.render_research_html(self.data,site_url='../../index.html')
        actual=(ROOT/'docs/events/emmanuel-macron-rise/index.html').read_text(encoding='utf-8')
        # Legacy HTML generator versions differ in blank lines around style/script
        # boundaries. Do not loosen comparison of any nonblank source, text or tag.
        strip_blank_lines=lambda s: re.sub(r'(?m)^[ \t]*\n','',s)
        self.assertEqual(strip_blank_lines(actual),strip_blank_lines(expected))